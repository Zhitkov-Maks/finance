from typing import Dict

from decouple import config


BOT_TOKEN: str = config("TOKEN")
API_ADDRESS: str = config("API_ADDRESS")
BASE_URL: str = API_ADDRESS + "/api/v1/"
PAGE_SIZE = 5

token_data: Dict[int, dict] = {}

# -------------------AUTH----------------------------------------------------

register_url: str = BASE_URL + "auth/users/"
login_url: str = BASE_URL + "auth/token/login/"

# ----------------EXPENSES INCOMES ACCOUNTS----------------------------------

accounts_url: str = BASE_URL + "accounts/"
transaction_url: str = BASE_URL + "transaction/"
incomes_url: str = transaction_url + "?page={p}&page_size={ps}&type=income"
expenses_url: str = transaction_url + "?page={p}&page_size={ps}&type=expense"

# ------------------STATISTICS-----------------------------------------------

statistic_url: dict = {
    "statistic_expenses": transaction_url +
    "statistics/?month={month}&year={year}&type=expense",

    "statistic_incomes": transaction_url +
    "statistics/?month={month}&year={year}&type=income"
}

# -------------------CATEGORIES-----------------------------------------------

categories_urls: dict = {
    "add_income": transaction_url + "category/?type=income",
    "add_expense": transaction_url + "category/?type=expense",
    "list_expenses_category": transaction_url +
    "category/?page={page}&page_size={page_size}&type=expense",

    "list_incomes_category": transaction_url +
    "category/?page={page}&page_size={page_size}&type=income",

    "income": transaction_url + "category/{id}/",
    "expense": transaction_url + "category/{id}/"
}

# -------------------RESET PASSWORD-------------------------------------------

reset_password_url = BASE_URL + "auth/users/reset_password/"
reset_password_confirm_url = BASE_URL + "auth/users/reset_password_confirm/"


# -------------------DEBT-----------------------------------------------------
debts_url: str = (BASE_URL + "debts/"
                             "?type={type}"
                             "&page={page}"
                             "&page_size={page_size}"
                  )

debts_url_by_id: str = (BASE_URL + "debts/{debt_id}/")
debts_repay_url: str = (BASE_URL + "debts/repay-debt/")
debt_create_url: str = (BASE_URL + "debts/create-debt/")
debt_create_accounts_url: str = (
        BASE_URL + "debts/create-debt-accounts/"
)
