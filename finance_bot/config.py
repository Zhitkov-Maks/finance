from typing import Dict

from decouple import config


BOT_TOKEN: str = config("TOKEN")
API_ADDRESS: str = config("API_ADDRESS")
BASE_URL: str = API_ADDRESS + "/api/v1/"
PAGE_SIZE = 5

token_data: Dict[int, dict] = {}
register_url: str = BASE_URL + "auth/users/"
login_url: str = BASE_URL + "auth/token/login/"
accounts_url: str = BASE_URL + "accounts/"
incomes_url: str = BASE_URL + "incomes/"
expenses_url: str = BASE_URL + "expenses/"

statistic_url: dict = {
    "statistic_expenses": expenses_url + "statistics/?month={month}&year={year}",
    "statistic_incomes": incomes_url + "statistics/?month={month}&year={year}"
}

categories_urls: dict = {
    "add_income": incomes_url + "category/",
    "add_expense": expenses_url + "category/",
    "list_expenses_category": expenses_url + "category/?page={page}&page_size={page_size}",
    "list_incomes_category": incomes_url + "category/?page={page}&page_size={page_size}",
    "income": incomes_url + "category/{id}/",
    "expense": expenses_url + "category/{id}/"
}
