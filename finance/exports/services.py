import csv
import io
import json
import logging
import zipfile
from datetime import date, datetime
from decimal import Decimal

from django.apps import apps
from django.core.exceptions import FieldError
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)

# Предохранитель от OOM и таймаутов. Случайные 500k строк от импорта
# уронят контейнер — лучше отдать 50k с предупреждением, чем 500.
MAX_ROWS_PER_SECTION = 50_000


# =============================================================================
# Утилиты сериализации
# =============================================================================


def _json_value(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return str(value)  # не теряем точность
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _csv_value(value):
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, default=str)
    return str(value)


def _resolve(obj, path):
    """Безопасно обходит связи: 'account.name' → obj.account.name (или None)."""
    for part in path.split("."):
        if obj is None:
            return None
        obj = getattr(obj, part, None)
    return obj


def _parse_field(field):
    """
    Поддерживает два вида:
      ('Заголовок CSV', 'path')                      → json_key = path
      ('Заголовок CSV', 'json_key', 'related.path')  → явный ключ
    """
    if isinstance(field, str):
        return field, field, field
    if len(field) == 2:
        return field[0], field[1], field[1]
    return field


def _display_user(user) -> str:
    """
    Человеко-читаемый идентификатор пользователя.

    CustomUser: USERNAME_FIELD = 'email', username = None.
    Поэтому email — единственный осмысленный идентификатор.
    Fallback на user{id} — на случай, если email когда-нибудь окажется пустым
    (не должен, unique=True, но защищаемся).
    """
    email = getattr(user, "email", None)
    return email if email else f"user{user.id}"


# =============================================================================
# Что экспортируем
# =============================================================================
#
# Порядок = порядок секций в JSON и файлов в ZIP.
# Поля связанных моделей — через точку ('account.name').
# user_lookup:
#   по умолчанию 'user' — модель фильтруется по прямому полю user;
#   список путей — OR + distinct (Transfer и Debt: user нет, есть счета).
# filter и order_by обёрнуты в try/except: невалидное поле не роняет экспорт.

EXPORT_SPEC = [
    # --- Accounts --------------------------------------------------------
    {
        "name": "accounts",
        "label": "Счета",
        "app_model": "accounts.Account",
        "fields": [
            ("ID", "id"),
            ("Название", "name"),
            ("Тип", "account_type"),
            ("Баланс", "balance"),
            ("Активен", "is_active"),
            ("Системный", "is_system_account"),
            ("Ставка, %", "interest_rate"),
            ("Кредитный лимит", "credit_limit"),
            ("Льготный период, дней", "grace_period_days"),
            ("Начало льготного периода", "grace_period_start"),
        ],
        "order_by": ["name"],
    },
    # --- Categories ------------------------------------------------------
    {
        "name": "categories",
        "label": "Категории",
        "app_model": "transactions.Category",
        "fields": [
            ("ID", "id"),
            ("Название", "name"),
            ("Тип", "type_transaction"),
            ("Родитель", "parent_name", "parent.name"),
            ("Уровень", "level"),
        ],
        "select_related": ["parent"],
        "order_by": ["level", "name"],
    },
    # --- Transactions ----------------------------------------------------
    {
        "name": "transactions",
        "label": "Транзакции",
        "app_model": "transactions.Transaction",
        "fields": [
            ("ID", "id"),
            ("Дата", "create_at"),
            ("Сумма", "amount"),
            ("Счёт", "account_name", "account.name"),
            ("Категория", "category_name", "category.name"),
            ("Тип категории", "category_type", "category.type_transaction"),
            ("Комментарий", "comment"),
        ],
        "select_related": ["account", "category"],
        "order_by": ["-create_at"],
    },
    # --- Transfers -------------------------------------------------------
    {
        "name": "transfers",
        "label": "Переводы",
        "app_model": "transfer.Transfer",
        "user_lookup": ["source_account__user", "destination_account__user"],
        "fields": [
            ("ID", "id"),
            ("Дата", "timestamp"),
            ("Сумма", "amount"),
            ("Со счёта", "source_account_name", "source_account.name"),
            ("На счёт", "destination_account_name", "destination_account.name"),
        ],
        "select_related": ["source_account", "destination_account"],
        "order_by": ["-timestamp"],
    },
    # --- Budgets ---------------------------------------------------------
    {
        "name": "budgets",
        "label": "Бюджеты",
        "app_model": "budgets.Budget",
        "fields": [
            ("ID", "id"),
            ("Категория", "category_name", "category.name"),
            ("Сумма", "amount"),
            ("Тип периода", "period_type"),
            ("Активен", "is_active"),
            ("Дата создания", "created_at"),
            ("Дата обновления", "updated_at"),
        ],
        "select_related": ["category"],
        "order_by": ["-created_at"],
    },
    # --- Recurring -------------------------------------------------------
    {
        "name": "recurring",
        "label": "Регулярные операции",
        "app_model": "recurring.RecurringTransaction",
        "fields": [
            ("ID", "id"),
            ("Название", "title"),
            ("Тип", "type_transaction"),
            ("Сумма", "amount"),
            ("Счёт", "account_name", "account.name"),
            ("Категория", "category_name", "category.name"),
            ("Периодичность", "schedule_type"),
            ("Следующий запуск", "next_run_date"),
            ("Последний запуск", "last_run_date"),
            ("Дата начала", "start_date"),
            ("Дата окончания", "end_date"),
            ("Активна", "is_active"),
            ("Комментарий", "comment"),
        ],
        "select_related": ["account", "category"],
        "order_by": ["-next_run_date"],
    },
    # --- Debts -----------------------------------------------------------
    # Debt: id, transfer (OneToOne), borrower_description — других полей нет.
    # Принадлежность — через Transfer → source/destination → Account → user.
    {
        "name": "debt",
        "label": "Долги",
        "app_model": "debt.Debt",
        "user_lookup": [
            "transfer__source_account__user",
            "transfer__destination_account__user",
        ],
        "fields": [
            ("ID", "id"),
            ("Описание заёмщика", "borrower_description"),
            ("ID перевода", "transfer_id"),
            ("Сумма перевода", "transfer_amount", "transfer.amount"),
            ("Дата перевода", "transfer_timestamp", "transfer.timestamp"),
            ("Со счёта", "transfer_from", "transfer.source_account.name"),
            ("На счёт", "transfer_to", "transfer.destination_account.name"),
        ],
        "select_related": [
            "transfer",
            "transfer__source_account",
            "transfer__destination_account",
        ],
        "order_by": ["-id"],
    },
    # --- Notifications ---------------------------------------------------
    # Точный состав полей Notification неизвестен — поля заданы по местам
    # использования. Отсутствующее поле просто даст пустую ячейку,
    # секция не упадёт. Невалидный order_by перехватит try/except в _iter_sections.
    {
        "name": "notifications",
        "label": "Уведомления",
        "app_model": "notifications.Notification",
        "fields": [
            ("ID", "id"),
            ("Тип", "notification_type"),
            ("Заголовок", "title"),
            ("Текст", "message"),
            ("Прочитано", "is_read"),
            ("Дата", "created_at"),
        ],
        "order_by": ["-created_at"],
    },
]


# =============================================================================
# Сервис
# =============================================================================


class ExportService:
    """Собирает данные пользователя и сериализует в JSON или CSV-архив."""

    def __init__(self, user):
        self.user = user
        self.exported_at = timezone.now()
        self._truncated: dict[str, int] = {}  # section name → original count

    # --- Внутреннее ------------------------------------------------------

    @staticmethod
    def _resolve_model(dotted: str):
        try:
            app_label, model_name = dotted.split(".")
            return apps.get_model(app_label, model_name)
        except (LookupError, ValueError):
            return None

    def _build_queryset(self, spec) -> "QuerySet | None":
        """
        Возвращает queryset для секции по правилам user_lookup.
        None — если модель не найдена или фильтр невозможен.
        """
        model = self._resolve_model(spec["app_model"])
        if model is None:
            return None

        user_lookup = spec.get("user_lookup", "user")
        try:
            if isinstance(user_lookup, (list, tuple)):
                q = Q()
                for path in user_lookup:
                    q |= Q(**{path: self.user})
                return model.objects.filter(q).distinct()
            return model.objects.filter(**{user_lookup: self.user})
        except FieldError:
            return None

    def _iter_sections(self):
        """Генерирует (spec, queryset) для каждой доступной секции."""
        for spec in EXPORT_SPEC:
            qs = self._build_queryset(spec)
            if qs is None:
                logger.warning(
                    "Export: cannot build queryset for %s, skipping",
                    spec["app_model"],
                )
                continue

            if spec.get("select_related"):
                # NB: select_related валидирует поля лениво — при исполнении
                # запроса, а не здесь. Если поле неверное — упадёт в
                # _serialize_csv/export_json. Проблема должна быть видна
                # разработчику, а не глотаться.
                qs = qs.select_related(*spec["select_related"])

            if spec.get("order_by"):
                # order_by валидирует сразу — оборачиваем.
                try:
                    qs = qs.order_by(*spec["order_by"])
                except FieldError as exc:
                    logger.warning(
                        "Export: cannot order %s by %s (%s), using default",
                        spec["app_model"],
                        spec["order_by"],
                        exc,
                    )

            # Защита от гигантских выгрузок
            total = qs.count()
            if total > MAX_ROWS_PER_SECTION:
                logger.warning(
                    "Export: %s has %d rows, truncating to %d",
                    spec["name"],
                    total,
                    MAX_ROWS_PER_SECTION,
                )
                self._truncated[spec["name"]] = total
                qs = qs[:MAX_ROWS_PER_SECTION]

            yield spec, qs

    def _collect_sections(self):
        """Материализует список секций — чтобы не проходить EXPORT_SPEC дважды."""
        return list(self._iter_sections())

    # --- Публичное -------------------------------------------------------

    def export_info(self) -> dict:
        """
        Возвращает количество записей в каждой секции БЕЗ генерации файла.
        Нужно фронтенду, чтобы:
          — показать пользователю «что будет выгружено»;
          — не дать скачать пустой архив;
          — предупредить об обрезке.
        """
        sections = []
        total = 0

        for spec in EXPORT_SPEC:
            qs = self._build_queryset(spec)
            if qs is None:
                sections.append(
                    {
                        "name": spec["name"],
                        "label": spec["label"],
                        "count": 0,
                        "truncated": False,
                        "available": False,
                    }
                )
                continue

            count = qs.count()
            sections.append(
                {
                    "name": spec["name"],
                    "label": spec["label"],
                    "count": count,
                    "truncated": count > MAX_ROWS_PER_SECTION,
                    "available": True,
                }
            )
            total += count

        return {"sections": sections, "total": total}

    def export_json(self) -> dict:
        result = {
            "exported_at": self.exported_at.isoformat(),
            "user": {
                "id": self.user.id,
                "email": getattr(self.user, "email", None) or "",
            },
            "data": {},
        }
        for spec, qs in self._collect_sections():
            rows = []
            for obj in qs.iterator():
                row = {}
                for field in spec["fields"]:
                    _, json_key, path = _parse_field(field)
                    row[json_key] = _json_value(_resolve(obj, path))
                rows.append(row)
            result["data"][spec["name"]] = rows
        return result

    def export_csv_zip(self) -> io.BytesIO:
        buffer = io.BytesIO()
        sections = self._collect_sections()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for spec, qs in sections:
                zf.writestr(f"{spec['name']}.csv", self._serialize_csv(spec, qs))
            zf.writestr("README.txt", self._build_readme(sections))
        buffer.seek(0)
        return buffer

    @staticmethod
    def _serialize_csv(spec, qs) -> bytes:
        text = io.StringIO()
        writer = csv.writer(text, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([_parse_field(f)[0] for f in spec["fields"]])
        for obj in qs.iterator():
            writer.writerow(
                [_csv_value(_resolve(obj, _parse_field(f)[2])) for f in spec["fields"]]
            )
        # BOM в начале — чтобы Excel открыл кириллицу без плясок
        return "\ufeff".encode("utf-8") + text.getvalue().encode("utf-8")

    def _build_readme(self, sections=None) -> str:
        if sections is None:
            sections = self._collect_sections()
        lines = [
            "Экспорт данных из приложения «Финансы»",
            "=" * 50,
            f"Пользователь: {_display_user(self.user)}",
            f"Дата экспорта: {self.exported_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Файлы в архиве:",
        ]
        for spec, _ in sections:
            lines.append(f"  • {spec['name']}.csv — {spec['label']}")

        if self._truncated:
            lines += [
                "",
                "⚠️ Некоторые секции обрезаны (слишком много записей):",
            ]
            for name, original in self._truncated.items():
                lines.append(
                    f"  • {name}: всего {original}, выгружено {MAX_ROWS_PER_SECTION}"
                )

        lines += [
            "",
            "Формат: CSV, разделитель «;», кодировка UTF-8 с BOM.",
            "Открывается в Excel и Google Sheets без настроек.",
        ]
        return "\n".join(lines)
