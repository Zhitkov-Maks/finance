from config import incomes_url


async def get_incomes_url(page: int, page_size: int = 10) -> str:
    """
    Generating URLs for working with income lists.
    :param page: The page for the request.
    :param page_size: Page size for the request.
    :return: The url string.
    """
    return incomes_url + f"?page={page}&page_size={page_size}"


async def get_incomes_category_url(page: int, page_size: int = 10) -> str:
    """
    Generating URLs for working with income categories lists.
    :param page: The page for the request.
    :param page_size: Page size for the request.
    :return str: The url string.
    """
    return incomes_url + f"category/?page={page}&page_size={page_size}"


async def incomes_by_id(income_id: int) -> str:
    """
    The function of generating the url of a specific income.
    :param income_id: Income ID.
    :return str: The url string.
    """
    return incomes_url + f"{income_id}/"


async def generate_message_income_info(
    data: dict[str, int | str | dict[str, int | str]]
) -> str:
    """
    A function for generating a message for detailed income information.
    :param data: A dictionary with data for forming a message.
    :return str: A message for the user.
    """
    if data.get("comment"):
        comment = f"Комментарий: {data.get("comment")}"

    else:
        comment = ""
    return (
        f"Дата операции 📆: "
            f"{data['create_at'][8:10]}-{data['create_at'][5:7]}.\n"
        f"Сумма дохода 💰: {float(data.get('amount')):,}₽. \n"
        f"Счет: {data.get('account').get('name')}.\n"
        f"Текущий баланс счета 💵: "
            f"{float(data.get('account').get('balance')):,}₽.\n"
        f"Категория дохода: {data.get('category').get('name')}.\n"
        f"{comment}"
    )


async def create_new_incomes_data(
    data: dict, comment: str
) -> dict[str, float | str | int]:
    """
    A function for generating a dictionary to create a new income record.
    :param data: A dictionary with data.
    :param comment: The comment.
    :return dict: Dictionary.
    """
    return {
        "amount": data.get("amount"),
        "create_at": data.get("date"),
        "category": data.get("income_category"),
        "account": data.get("account_id"),
        "comment": comment,
    }


async def gen_answer_message(
        data: dict[str, int | dict[str, int | str]]
) -> str:
    """
    The function generates a message when a new income is
    successfully generated.
    :param data: A dictionary with data for forming a message.
    :return str: A message for the user.
    """
    if data.get("comment"):
        comment = f"Комментарий: {data.get("comment")}"

    else:
        comment = ""

    return (
        f"Доход на {data.get('amount')}₽ 💷,\n"
        f"В категории {data.get('category').get('name')},\n"
        f"На счет {data.get('account').get('name')}.\n"
        f"Денег 💰💰💰 на счете: {data.get('account').get('balance')}\n"
        f"{comment}"
    )
