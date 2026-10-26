from datetime import date, timedelta
from decimal import Decimal

from accounts.models import Account
from budgets.models import Budget
from django.db.models import Sum
from recurring.models import RecurringTransaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from transactions.models import Transaction

from .models import FinancialGoal, Insight


class GamificationDashboardView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        today = date.today()
        month_start = today.replace(day=1)

        # ================= 1. ЦЕЛЬ МЕСЯЦА =================
        goal = FinancialGoal.objects.filter(user=user, month=month_start).first()
        goal_data = None

        if goal:
            spent = 0
            if goal.goal_type == "limit":
                qs = Transaction.objects.filter(
                    user=user,
                    category__type_transaction="expense",
                    create_at__date__gte=month_start,
                )
                if goal.category:
                    qs = qs.filter(category=goal.category)
                spent = float(qs.aggregate(s=Sum("amount"))["s"] or 0)

            goal_data = {
                "id": goal.id,
                "goal_type": goal.goal_type,
                "amount": float(goal.amount),
                "category": goal.category_id,
                "category_name": goal.category.name if goal.category else "Все расходы",
                "spent_on_backend": spent,
            }

        # ================= 2. УРОВЕНЬ ГРАМОТНОСТИ =================
        score = 0
        breakdown = []  # Будем собирать, за что дали/сняли баллы

        # --- ПОЛОЖИТЕЛЬНЫЕ БАЛЛЫ ---
        if Budget.objects.filter(user=user).exists():
            score += 2
            breakdown.append(
                {"action": "Есть бюджеты", "points": 2, "type": "positive"}
            )

        if RecurringTransaction.objects.filter(user=user).exists():
            score += 2
            breakdown.append(
                {"action": "Есть регулярные платежи", "points": 2, "type": "positive"}
            )

        if Account.objects.filter(user=user, account_type="deposit").exists():
            score += 1
            breakdown.append(
                {"action": "Есть вклад (сбережения)", "points": 1, "type": "positive"}
            )

        if Account.objects.filter(user=user, account_type="credit_card").exists():
            score += 1
            breakdown.append(
                {
                    "action": "Ведется учет кредитных карт",
                    "points": 1,
                    "type": "positive",
                }
            )

        if Insight.objects.filter(user=user).exists():
            score += 1
            breakdown.append(
                {
                    "action": "Активно используются инсайты",
                    "points": 1,
                    "type": "positive",
                }
            )

        if Transaction.objects.filter(user=user, create_at__date=today).exists():
            score += 1
            breakdown.append(
                {"action": "Запись трат сегодня", "points": 1, "type": "positive"}
            )

        if goal:
            score += 2
            breakdown.append(
                {"action": "Поставлена цель на месяц", "points": 2, "type": "positive"}
            )

        # 1. Просрочка льготного периода по кредитке
        credit_cards = Account.objects.filter(
            user=user,
            account_type="credit_card",
            balance__lt=0,
            grace_period_start__isnull=False,
        )
        has_overdue = False
        for card in credit_cards:
            if card.grace_period_start + timedelta(days=card.grace_period_days) < today:
                has_overdue = True
                break
        if has_overdue:
            score -= 3
            breakdown.append(
                {
                    "action": "Просрочка по кредитной карте",
                    "points": -3,
                    "type": "negative",
                }
            )

        # 2. Превышение бюджета в этом месяце (ищем инсайт)
        if Insight.objects.filter(
            user=user,
            insight_type=Insight.TYPE_BUDGET_OVERSPEND,
            created_at__date__gte=month_start,
        ).exists():
            score -= 2
            breakdown.append(
                {"action": "Превышение бюджета", "points": -2, "type": "negative"}
            )

        # 3. Расходы больше доходов в этом месяце
        income = Transaction.objects.filter(
            user=user,
            category__type_transaction="income",
            create_at__date__gte=month_start,
        ).aggregate(s=Sum("amount"))["s"] or Decimal(0)

        expense = Transaction.objects.filter(
            user=user,
            category__type_transaction="expense",
            create_at__date__gte=month_start,
        ).aggregate(s=Sum("amount"))["s"] or Decimal(0)

        # Проверяем только если прошло хотя бы 5 дней месяца и есть доходы/расходы
        if today.day >= 5 and income > 0 and expense > income:
            score -= 2
            breakdown.append(
                {"action": "Траты превышают доходы", "points": -2, "type": "negative"}
            )

        # Ограничиваем уровень от 1 до 10
        level = min(10, max(1, score))

        # Формируем хинт
        if has_overdue:
            hint = (
                "⚠️ У вас есть просрочка по кредитке. Погасите её, чтобы вернуть баллы."
            )
        elif expense > income and income > 0:
            hint = "⚠️ Вы тратите больше, чем зарабатываете. Пересмотрите бюджет."
        else:
            hints = {
                1: "Создайте свой первый бюджет.",
                2: "Добавьте регулярный платеж (например, подписку).",
                3: "Начните записывать траты каждый день.",
                4: "Создайте вклад, чтобы деньги работали.",
                5: "Поставьте цель на месяц.",
            }
            hint = hints.get(
                level, "Вы настоящий финансовый гуру! Продолжайте в том же духе."
            )

        return Response(
            {
                "goal": goal_data,
                "level": {
                    "score": level,
                    "raw_score": score,  # Реальный счет (может быть отрицательным)
                    "max_score": 10,
                    "hint": hint,
                    "breakdown": breakdown,  # Расшифровка
                },
            }
        )
