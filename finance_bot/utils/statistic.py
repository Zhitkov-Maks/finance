import os

import matplotlib.pyplot as plt
import pandas as pd

from api.common import get_full_info
from config import statistic_url
from loader import category_statistic_text
from utils.create_calendar import MONTH_DATA


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
        message: str = category_statistic_text.format(operation="расходы")
    else:
        url: str = statistic_url.get("statistic_incomes")
        message: str = category_statistic_text.format(operation="доходы")
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
        message += f"{category_name} ... {category_amount:,.2f}₽ ... {percent:.02f}%\n{50 * '-'}\n"

    if len(message) == 0:
        message = "За данный месяц нет данных."

    return message


async def get_message_incomes_by_expenses(
    amount_inc: float, amount_exp: float, usr_id: int, year: int, month: int
) -> str:
    """
    Generating a graphic image of the income-to-expense ratio.
    :param month:
    :param year:
    :param usr_id: The telegram user's ID
    :param amount_inc: The amount of incomes.
    :param amount_exp: The amount of expenses.
    :return: A message in the form of a string.
    """
    data: dict = {"Категория": ["Доходы", "Расходы"], "Сумма": [amount_inc, amount_exp]}
    df: pd.DataFrame = pd.DataFrame(data)

    try:
        plt.figure(figsize=(8, 7))
        plt.bar(df["Категория"], df["Сумма"], color=["green", "red"])
        plt.title(f"{MONTH_DATA[month]} {year}г")
        plt.xlabel("Категория")
        plt.ylabel("Сумма (₽)")

        for i, v in enumerate(df["Сумма"]):
            offset = 200

            plt.text(
                i,
                v + offset if v >= 0 else v - abs(offset),
                str(v),
                color="black",
                ha="center",
            )

        filename = f"finances_{usr_id}_graph.png"

        # Saving the graph to a file (temporary file)
        plt.savefig(filename)

        # Cleaning up the current Matplotlib instance
        plt.clf()
        return os.path.abspath(filename)

    except (FileNotFoundError, PermissionError, ValueError):
        pass
