from decimal import Decimal

from asgiref.sync import async_to_sync
from debt.models import Debt
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q, QuerySet, Sum
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers, status
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from transfer.models import Transfer

from accounts.balance_history.service import build_balance_history
from accounts.cache import (
    BALANCE_HISTORY_CACHE_TTL,
    invalidate_balance_history_cache,
    make_balance_history_cache_key,
)
from accounts.models import Account
from accounts.schemas import RetrieveUpdateDeleteAccountSchema, listAccountSchema
from accounts.serializers import (
    AccountSerializer,
    AccountToggleStatusSerializer,
    BalanceHistoryQuerySerializer,
    BaseAccountSerializer,
)
from accounts.services import reconcile_grace_period


class AccountPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


def _schedule_account_cache_invalidation(user_id: int) -> None:
    """
    Инвалидация кэша истории баланса только после успешного коммита.
    Если транзакция откатится — кэш останется нетронутым.
    """
    transaction.on_commit(lambda: invalidate_balance_history_cache(user_id))


@extend_schema(tags=["Accounts"])
@listAccountSchema
class ListAccounts(generics.ListCreateAPIView):
    """
    Список счетов пользователя или создание нового счёта.
    """

    pagination_class = AccountPagination
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BaseAccountSerializer
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        qs = Account.objects.filter(
            user=self.request.user.pk, is_system_account=False
        ).order_by("-balance")

        include_archived = self.request.query_params.get("include_archived") == "true"
        if not include_archived:
            qs = qs.filter(deleted_at__isnull=True)
        return qs

    @transaction.atomic
    def perform_create(self, serializer: AccountSerializer) -> None:
        """
        Создаёт счёт. Если это кредитка с готовым долгом,
        сразу стартует grace period.
        """
        account: Account = serializer.save(user=self.request.user)

        # Для нового счёта старый баланс — это 0.
        # Если баланс отрицательный, таймер запустится.
        reconcile_grace_period(account, old_balance=Decimal("0"))

        _schedule_account_cache_invalidation(self.request.user.pk)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        total_balance = (
            queryset.filter(is_active=True, deleted_at__isnull=True).aggregate(
                total=Sum("balance")
            )["total"]
            or 0
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                [{"accounts": serializer.data, "total_balance": total_balance}]
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response([{"accounts": serializer.data, "total_balance": total_balance}])


@extend_schema(tags=["Accounts"])
@RetrieveUpdateDeleteAccountSchema
class RetrieveUpdateDeleteAccount(generics.RetrieveUpdateDestroyAPIView):
    """
    Редактирование, удаление и просмотр конкретного счёта.
    """

    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        return Account.objects.filter(user=self.request.user, deleted_at__isnull=True)

    @transaction.atomic
    def perform_update(self, serializer: AccountSerializer) -> None:
        """
        Сохраняет счёт. Если баланс кредитки изменился с положительного
        (или нуля) на отрицательный — перезапускает grace period.
        """
        # Запоминаем баланс ДО сохранения
        old_balance = serializer.instance.balance

        account: Account = serializer.save()

        # Передаем old_balance для корректного определения "нового долга"
        reconcile_grace_period(account, old_balance=old_balance)

        _schedule_account_cache_invalidation(self.request.user.pk)

    @transaction.atomic
    def perform_destroy(self, instance: Account) -> None:
        """
        Soft delete: не удаляем физически — переносим в архив.
        Проверяем: системный счёт, долги, кредитка с непогашенным долгом.
        """
        if instance.is_system_account:
            raise serializers.ValidationError(
                {"detail": "Системный счёт нельзя удалить."}
            )

        # Активные долги привязаны к счёту через Transfer
        related_transfers = Transfer.objects.filter(
            Q(source_account=instance) | Q(destination_account=instance)
        )
        active_debts_count = Debt.objects.filter(transfer__in=related_transfers).count()

        if active_debts_count > 0:
            raise serializers.ValidationError(
                {
                    "detail": (
                        f"Нельзя архивировать счёт «{instance.name}»: "
                        f"с ним связано {active_debts_count} долг(ов). "
                        "Сначала погасите или удалите связанные долги."
                    )
                }
            )

        # Кредитка с непогашенным долгом — блокируем
        if instance.account_type == Account.TYPE_CREDIT and instance.balance < 0:
            raise serializers.ValidationError(
                {
                    "detail": (
                        f"Нельзя архивировать кредитку «{instance.name}»: "
                        f"есть непогашенный долг {abs(instance.balance):.2f} ₽. "
                        "Сначала погасите задолженность."
                    )
                }
            )

        # ✅ Архивация
        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save(update_fields=["deleted_at", "is_active"])

        _schedule_account_cache_invalidation(instance.user_id)


@extend_schema(tags=["Accounts"])
class ToggleAccountActiveStatusView(generics.UpdateAPIView):
    """
    Переключение активности счёта. Использует select_for_update
    для защиты от race condition при двойном клике.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = AccountToggleStatusSerializer
    http_method_names = ["patch"]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user.pk)

    def get_object(self):
        qs = self.get_queryset()
        if self.request.method == "PATCH":
            qs = qs.select_for_update()
        obj = generics.get_object_or_404(qs, pk=self.kwargs.get("pk"))
        if obj.user_id != self.request.user.pk:
            raise PermissionDenied(
                "You do not have permission to modify this account."
            )
        return obj

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        account = self.get_object()

        if account.deleted_at is not None:
            return Response(
                {"detail": "Счёт в архиве. Сначала восстановите его."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        account.is_active = not account.is_active
        account.save(update_fields=["is_active"])
        _schedule_account_cache_invalidation(request.user.pk)
        return Response(
            AccountToggleStatusSerializer(account).data,
            status=status.HTTP_200_OK,
        )


class BalanceHistoryView(APIView):
    """
    Ежедневный баланс счетов пользователя за период.
    Включает IDOR-защиту и кэширование.
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request):
        query = BalanceHistoryQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        data = query.validated_data

        date_from = data["date_from"]
        date_to = data["date_to"]
        account_id = data.get("account_id")
        include_inactive = data.get("include_inactive", False)

        # Защита: пользователь может запросить историю только своих счетов
        if account_id is not None:
            if not Account.objects.filter(pk=account_id, user=request.user).exists():
                return Response(
                    {"detail": "Счёт не найден."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        cache_key = make_balance_history_cache_key(
            user_id=request.user.pk,
            date_from=date_from,
            date_to=date_to,
            account_id=account_id,
            include_inactive=include_inactive,
        )

        cached = cache.get(cache_key)
        if cached is not None:
            response = Response(cached)
            response["X-Cache"] = "HIT"
            return response

        result = async_to_sync(build_balance_history)(
            user=request.user,
            date_from=date_from,
            date_to=date_to,
            account_id=account_id,
            include_inactive=include_inactive,
        )

        cache.set(cache_key, result, timeout=BALANCE_HISTORY_CACHE_TTL)

        response = Response(result)
        response["X-Cache"] = "MISS"
        return response


@extend_schema(tags=["Accounts"])
class RestoreAccountView(generics.GenericAPIView):
    """
    Восстанавливает счёт из архива.
    Счёт вернётся в баланс (is_active=True), пользователь сможет его скрыть.
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def post(self, request, pk):
        account = Account.objects.filter(
            user=request.user, pk=pk, deleted_at__isnull=False
        ).first()

        if not account:
            return Response(
                {"detail": "Счёт не найден в архиве."},
                status=status.HTTP_404_NOT_FOUND,
            )

        account.deleted_at = None
        account.is_active = True
        account.save(update_fields=["deleted_at", "is_active"])
        _schedule_account_cache_invalidation(request.user.pk)

        return Response(AccountSerializer(account).data, status=status.HTTP_200_OK)
