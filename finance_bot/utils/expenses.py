from config import expenses_url


async def get_expense_url(page: int, page_size: int = 10) -> str:
    """
    Generating URLs for working with expenses lists.
    :param page: The page for the request.
    :param page_size: Page size for the request.
    :return: The url string.
    """
    return expenses_url + f"?page={page}&page_size={page_size}"


async def get_expenses_category_url(page: int, page_size: int = 10) -> str:
    """
    Generating URLs for working with expenses categories lists.
    :param page: The page for the request.
    :param page_size: Page size for the request.
    :return str: The url string.
    """
    return expenses_url + f"category/?page={page}&page_size={page_size}"


async def expense_url_by_id(expense_id: int) -> str:
    """
    The function of generating the url of a specific income.
    :param expense_id: Income ID.
    :return str: The url string.
    """
    return expenses_url + f"{expense_id}/"


async def create_new_expenses_data(
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
        "category": data.get("expense_category"),
        "account": data.get("account_id"),
        "comment": comment,
    }


async def gen_answer_message_expense(
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

    return (
        f"Расход на {data.get('amount')}₽ 💷,\n"
        f"В категории {data.get('category').get('name')},\n"
        f"Со счета {data.get('account').get('name')}.\n"
        f"{comment}"
    )


async def generate_message_expense_info(
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
        f"Сумма расхода 💰: {float(data.get('amount')):,}₽. \n"
        f"Счет: {data.get('account').get('name')}.\n"
        f"Категория расхода: {data.get('category').get('name')}.\n"
        f"{comment}"
    )
