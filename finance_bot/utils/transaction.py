from config import expenses_url, incomes_url


def choice_type_transaction(name: str) -> str:
    if "exp" in name:
        return "Выперите дату расхода: "
    else:
        return "Выберите дату дохода: "


def choice_url_transaction(name: str) -> str:
    if "exp" in name:
        return expenses_url
    else:
        return incomes_url


async def get_category_url(
    type_transaction: str,
    page: int,
    page_size: int = 10
) -> str:
    """
    Generating URLs for working with expenses categories lists.
    :param page: The page for the request.
    :param page_size: Page size for the request.
    :return str: The url string.
    """
    base_url = expenses_url
    if "inc" in type_transaction:
        base_url = incomes_url
    return base_url + f"category/?page={page}&page_size={page_size}"


async def create_transaction_data(
    data: dict, comment: str
) -> dict[str, float | str | int]:
    """
    A function for generating a message for detailed expense information.
    :param data: A dictionary with data for forming a message.
    :param comment: The comment to send.
    :return str: A message for the user.
    """
    return {
        "amount": data.get("amount"),
        "create_at": data.get("date"),
        "category": data.get("category"),
        "account": data.get("account_id"),
        "comment": comment,
    }


async def gen_answer_message_transaction(
    type_transaction: str,
    data: dict[str, int | dict[str, int | str]]
) -> str:
    """
    Generates a message about the created expense.
    :param data: The result of the request to the server.
    :return: A message about the created expense.
    """
    if data.get("comment"):
        comment = f"Комментарий: {data.get("comment")}"
    else:
        comment = ""

    transaction = "Расход" if "exp" in type_transaction else "Доход"

    return (
        f"{transaction} на {data.get('amount')}₽ 💷,\n"
        f"В категории {data.get('category').get('name')},\n"
        f"Со счета {data.get('account').get('name')}.\n"
        f"{comment}"
    )


async def generate_message_transaction_info(
    data: dict[str, int | str | dict[str, int | str]]
) -> str:
    """
    Generates a message when viewing the expense.
    :param data: The result of the request to the server.
    :return: Expense notification.
    """
    if data.get("comment"):
        comment = f"Комментарий: {data.get("comment")}"
    else:
        comment = ""

    return (
        f"Дата операции 📆: {data['create_at'][8:10]}-{data['create_at'][5:7]}.\n"
        f"Сумма 💰: {float(data.get('amount')):,}₽. \n"
        f"Счет: {data.get('account').get('name')}.\n"
        f"Категория: {data.get('category').get('name')}.\n"
        f"{comment}"
    )


async def create_new_data(
    data: dict, comment: str
) -> dict[str, float | str | int]:
    """
    A function for generating a message for detailed expense information.
    :param data: A dictionary with data for forming a message.
    :param comment: The comment to send.
    :return str: A message for the user.
    """
    return {
        "amount": data.get("amount"),
        "create_at": data.get("date"),
        "category": data.get("category"),
        "account": data.get("account_id"),
        "comment": comment,
    }
