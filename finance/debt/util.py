from datetime import datetime

from django.utils import timezone
from django.db import transaction

from accounts.models import Account
from app_user.models import CustomUser
from debt.models import Debt
from transfer.models import Transfer


def create_debt_accounts(user: CustomUser) -> tuple:
    """
    Создает два новых счета у пользователя для взятия и дачи в долг.

    :param user: Пользователь у которого создаем счета.
    """
    with transaction.atomic():
        # Проверка существования счетов
        debt_account, _ = Account.objects.get_or_create(
            user=user,
            name="debt",
            defaults={
                "balance": 0,
                "is_active": False,
                "is_system_account": True
            }
        )
        lend_account, _ = Account.objects.get_or_create(
            user=user,
            name="lend",
            defaults={
                "balance": 0,
                "is_active": False,
                "is_system_account": True
            }
        )

        return debt_account, lend_account


def update_amount_accounts(
        source: Account, destination: Account, data: dict
) -> None:
    """
    Обновляем и сохраняем данные счетов.

    :param source: Счет с которого буде взятие или отдача долга.
    :param destination: Счет на который будем переводить.
    :param data: Словарь с данными.
    """
    if data["type"] == "debt":
        source.balance += data["amount"]
        destination.balance -= data["amount"]

    else:
        source.balance -= data["amount"]
        destination.balance += data["amount"]
    source.save(), destination.save()


def create_debt_or_lend_transfer(user: CustomUser, data: dict) -> tuple:
    """
    Создание нового перевода между счетами при работе с долгами.

    :param user: Пользователь у которого проходит операция с долгами.
    :param data: Словарь с данными для перевода.
    """
    try:
        source_account: Account = Account.objects.get(
            id=data["account_id"], user=user
        )
    except Account.DoesNotExist:
        return {"status": "error", "message": "Счет не найден"}, 404

    dest_account: Account = Account.objects.get(user=user, name=data["type"])

    datetime_obj = datetime.combine(data["date"], datetime.min.time())
    aware_datetime = timezone.make_aware(
        datetime_obj,
        timezone=timezone.get_current_timezone()
    )

    transfer = Transfer.objects.create(
        source_account=source_account,
        destination_account=dest_account,
        amount=data["amount"],
        timestamp=aware_datetime
    )
    update_amount_accounts(source_account, dest_account, data)
    Debt.objects.create(
        transfer=transfer, borrower_description=data["description"]
    )

    return {"status": "success", "message": "Долг успешно создан"}, 201


def repay_debt(user: CustomUser, data: dict) -> tuple:
    """
    Функция для работы с погашением долгов.

    :param user: Пользователь для работы.
    :param data: Словарь с нужными данными.
    """
    try:
        debt: Debt = Debt.objects.get(id=data["debt_id"])
    except Debt.DoesNotExist:
        return {"status": "error", "message": "Долг не найден"}, 404

    if debt.transfer.destination_account.user != user:
        return {"status": "error", "message": "Нет доступа к этому долгу"}, 403

    debt_account: Account = debt.transfer.destination_account
    user_account: Account = debt.transfer.source_account

    Transfer.objects.create(
        source_account=user_account,
        destination_account=debt_account,
        amount=-data["amount"],
        timestamp=timezone.now()
    )

    update_amount_accounts(user_account, debt_account, {
        "type": data["type"],
        "amount": -data["amount"]
    })

    # Обновление суммы долга
    debt.transfer.amount -= data["amount"]
    debt.transfer.save()

    if debt.transfer.amount == 0:
        debt.delete()

    return {"status": "success", "message": "Долг успешно погашен"}, 201
