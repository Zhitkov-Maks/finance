from api.common import get_full_info
from config import statistic_url


async def get_url_and_type_message(data: str, year: int, month: int) -> tuple[str, str]:
    """
    Generates the url for the request and the type of message for the response.
    :param data: The string for determining the url.
    :param year: The year for the request.
    :param month: The month for the request.
    :return: Url and text to add to the message.
    """
    if data == "statistic_exp":
        url: str = statistic_url.get("statistic_expenses")
        message: str = "Ваши расходы по категориям: " + f"\n{50 * "-"}"
    else:
        url: str = statistic_url.get("statistic_incomes")
        message: str = "Ваши доходы по категориям: " + f"\n{50 * "-"}"
    return url.format(year=year, month=month), message


async def get_statistic_current_month(url: str, user_id: int, accounts=False) -> float:
    """
    Returns monthly statistics on income and expenses,
    or the sum of all accounts at the moment.
    :param url: Url for the request
    :param user_id: The telegram chat ID.
    :param accounts: A Boolean value for selecting an option to receive the amount.
    :return: The amount received.
    """
    result: dict = await get_full_info(url, user_id)
    if not accounts:
        return float(result.get("total_amount"))
    return float(result.get("results")[0].get("total_balance"))


async def gen_message_statistics(data: dict) -> str:
    """
    The function generates a message for expenses and incomes by category.
    :param data: The result of the request to the server.
    :return: A message in the form of a string.
    """
    message: str = ""
    total_amount: float = float(data["total_amount"])

    for item in data["statistics"]:
        category_name: str = item.get("category_name")
        category_amount: float = float(item['total_amount'])
        percent: float = category_amount / total_amount * 100

        # Используем вертикальные линии как разделители
        message += f"{category_name} => {category_amount:,.2f}₽ => {percent:.02f}%\n"

    if len(message) == 0:
        message = "За данный месяц нет данных."

    return message
