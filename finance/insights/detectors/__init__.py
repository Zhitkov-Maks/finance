from .budget import detect_budget_overspends_for_user
from .cash_gap import detect_cash_gaps_for_user
from .category import detect_category_spikes_for_user
from .credit_card import detect_credit_card_grace_for_user
from .deposit import detect_deposit_forecasts_for_user
from .engagement import detect_monthly_report_for_user
from .hidden_leak import detect_hidden_leaks_for_user
from .opportunities import (
    detect_budget_reallocation_for_user,
    detect_debt_vs_deposit_for_user,
    detect_idle_cash_for_user,
)
from .salary import detect_salary_spikes_for_user
from .savings import detect_savings_improved_for_user

__all__ = [
    "detect_category_spikes_for_user",
    "detect_salary_spikes_for_user",
    "detect_hidden_leaks_for_user",
    "detect_budget_overspends_for_user",
    "detect_cash_gaps_for_user",
    "detect_deposit_forecasts_for_user",
    "detect_credit_card_grace_for_user",
    "detect_monthly_report_for_user",
    "detect_savings_improved_for_user",
    "detect_idle_cash_for_user",
    "detect_debt_vs_deposit_for_user",
    "detect_budget_reallocation_for_user",
]
