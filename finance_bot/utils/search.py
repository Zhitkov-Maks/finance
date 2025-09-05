import re

from config import PAGE_SIZE, transaction_url
from states.search import SearchState


pattern = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
number_pattern = r'^-?\d+(\.\d+)?$'

state_dict: dict[str, tuple] = {
    "account_name": (
        "Введите название счета по которому вас интересуют операции.",
        SearchState.action,
    ),
    "amount_gte": (
        "Введите сумму, выше которой вас интересуют операции.",
        SearchState.action
    ),
    "amount_lte": (
        "Введите сумму, до которой вас интересуют операции.",
        SearchState.action
    ),
    "create_at_before": (
        "Введите дату меньше которой вас интересуют операции",
        SearchState.action,
    ),
    "create_at_after": (
        "Введите дату больше которой вас интересуют операции. Дата вводить в "
        "формате гггг-мм-дд .",
        SearchState.action,),

    "category_name": (
        "Введите имя категории, по которой вас интересуют операции. Дату "
        "вводить в формате гггг-мм-дд .",
        SearchState.action,
    )
}


async def validate_data_search(action: str, text: str) -> bool:
    """
    Checking the validity of some data.
    :param action: Command.
    :param text: The message that the user entered.
    """
    if action in ["create_at_after", "create_at_before"]:
        return bool(re.match(pattern, text))

    elif action in ["amount_gte", "amount_lte"]:
        return bool(re.match(number_pattern, text))

    elif action in ["account_name", "category_name"]:
        return True

    else:
        return False


async def generate_url(data: dict, page) -> str:
    """
    Forming the url for the request to the server, \
    depending on the transmitted data.

    :param data: Data collected from the user.
    :param page: Number of page.
    """
    type_ = data["type"]
    if type_ == "sh_expenses":
        add_type = "expense"
    else:
        add_type = "income"

    base_url = f"{transaction_url}?page={page}&page_size={PAGE_SIZE}"

    if data.get("account_name"):
        base_url += f"&account_name={data['account_name']}"

    if data.get("create_at_before"):
        base_url += f"&create_at_before={data['create_at_before']}"

    if data.get("create_at_after"):
        base_url += f"&create_at_after={data['create_at_after']}"

    if data.get("category_name"):
        base_url += f"&category_name={data['category_name']}"

    if data.get("amount_gte"):
        base_url += f"&amount_gte={data['amount_gte']}"

    if data.get("amount_lte"):
        base_url += f"&amount_lte={data['amount_lte']}"
    return base_url + f"&type={add_type}"
