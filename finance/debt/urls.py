from django.urls import path


from .views import (
    CreateDebtAccountsView,
    CreateDebtView,
    RepayDebtView,
    DebtListView,
    DebtDetailView
)


urlpatterns = [
    path(
        'create-debt-accounts/',
        CreateDebtAccountsView.as_view(),
        name='create_debt_accounts'),
    path(
        'create-debt/',
        CreateDebtView.as_view(),
        name='create_debt'
    ),
    path(
        'repay-debt/',
        RepayDebtView.as_view(),
        name='repay_debt'
    ),
    path('', DebtListView.as_view(), name='debts'),
    path(
        '<int:debt_id>/',
        DebtDetailView.as_view(),
        name='debt_detail'
    ),
]
