from django.db import transaction
from django.db.models.query_utils import Q
from rest_framework.authentication import (
    TokenAuthentication,
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Debt
from accounts.schemas import (
    DebtListSchema,
    DebtDetailSchema,
    DebtRepaySchema,
    DebtCreateSchema,
    DebtCreateAccountsSchema
)
from accounts.serializers.serializers_debt import (
    DebtCreateSerializer,
    DebtRepaymentSerializer,
    DebtDetailSerializer,
    DebtListSerializer
)
from accounts.views.util import (
    create_debt_accounts,
    create_debt_or_lend_transfer,
    repay_debt
)
from app_user.models import CustomUser


@DebtCreateAccountsSchema
class CreateDebtAccountsView(APIView):
    """Класс для создания двух счетов для работы с долгами."""

    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def post(self, request) -> Response:
        """Метод для создания счетов для работы с долгами."""
        user: CustomUser = request.user
        try:
            create_debt_accounts(user)
            return Response({
                    "status": "success",
                    "message": "Счета для долга и кредита успешно созданы"
                }, status=201
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=400
            )


@DebtCreateSchema
class CreateDebtView(APIView):
    """Класс для создания долга."""

    permission_classes = [IsAuthenticated]
    serializer_class = DebtCreateSerializer
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def post(self, request) -> Response:
        """Метод для обработки данных для создания долга."""
        serializer = DebtCreateSerializer(data=request.data)

        if serializer.is_valid():
            data: dict = {
                "account_id": serializer.validated_data['account_id'],
                "type": serializer.validated_data['type'],
                "amount": serializer.validated_data['amount'],
                "description": serializer.validated_data['description'],
                "date": serializer.validated_data['date']
            }

            with transaction.atomic():
                answer, status_code = create_debt_or_lend_transfer(
                        request.user, data
                    )
                return Response(data=answer, status=status_code)

        else:
            return Response(serializer.errors, status=400)


@DebtRepaySchema
class RepayDebtView(APIView):
    """Класс для работы с возвратом долгов."""

    permission_classes = [IsAuthenticated]
    serializer_class = DebtRepaymentSerializer
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def post(self, request) -> Response:
        """Метод для обработки возврата долга."""
        serializer = DebtRepaymentSerializer(data=request.data)
        if serializer.is_valid():
            data: dict = {
                "debt_id": serializer.validated_data['debt_id'],
                "amount": serializer.validated_data['amount'],
                "type": serializer.validated_data['type'],
            }
            with transaction.atomic():
                answer, status_code = repay_debt(
                    request.user, data
                )
                return Response(data=answer, status=status_code)

        else:
            return Response(serializer.errors, status=400)


@DebtListSchema
class DebtListView(APIView):
    """Класс для получения списка долгов."""
    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request) -> Response:
        """Переопределяем метод для фильтрации долгов."""
        debt_type: str = request.GET.get('type')

        if debt_type == 'debt' or debt_type == 'lend':
            debts = (Debt.objects.filter(
                transfer__source_account__user=request.user
            ).filter(transfer__destination_account__name=debt_type))

        else:
            debts = Debt.objects.filter(
                Q(transfer__source_account__user=request.user) |
                Q(transfer__destination_account__user=request.user)
            )

        serializer = DebtListSerializer(debts, many=True)
        return Response(serializer.data)


@DebtDetailSchema
class DebtDetailView(APIView):
    """Класс для получения подробной информации о конкретном долге."""

    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request, debt_id: int) -> Response:
        """Переопределили метод для добавления логики."""
        try:
            debt = Debt.objects.get(id=debt_id)
        except Debt.DoesNotExist:
            return Response(
                {"status": "error", "message": "Долг не найден"},
                status=404
            )

        if (debt.transfer.source_account.user != request.user
                and debt.transfer.destination_account.user != request.user):
            return Response(
                {
                    "status": "error",
                    "message": "Нет доступа к этому долгу"
                }, status=403
            )

        serializer = DebtDetailSerializer(debt)
        return Response(serializer.data)
