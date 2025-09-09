from config import expenses_url, incomes_url, transaction_url


def choice_type_transaction(name: str) -> str:
    """
    Return the desired message depending on
    the type of transaction.

    :param name: The type of transaction.
    """
    if "exp" in name:
        return "Выперите дату расхода: "
    else:
        return "Выберите дату дохода: "


def choice_url_transaction(name: str) -> str:
    """
    Return the required url depending on the type of transaction.

    :param name: The type of transaction.
    """
    return expenses_url if "exp" in name else incomes_url


async def get_category_url(
    type_transaction: str,
    page: int,
    page_size: int = 10
) -> str:
    """
    Generate URLs for working with transaction categories lists.

    :param page: The page for the request.
    :param page_size: Page size for the request.
    :return str: The url string.
    """
    base_url = "income" if "inc" in type_transaction else "expense"
    return (transaction_url + f"category/?page={page}"
            f"&page_size={page_size}&type={base_url}")


async def create_transaction_data(
    data: dict, comment: str
) -> dict[str, float | str | int]:
    """
    Generate a message for
    detailed transaction information.

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
    Generates a message about the created transaction.

    :param data: The result of the request to the server.
    :return: A message about the created transaction.
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
    Generates a message when viewing the transaction.

    :param data: The result of the request to the server.
    :return: Transaction notification.
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
    Generate a message for
    detailed transaction information.

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
