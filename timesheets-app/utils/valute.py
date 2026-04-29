import json
import asyncio
from datetime import datetime

import aiohttp

from config import cashed_currency
from crud.statistics import aggregate_valute

# the address for requesting the ruble exchange rate
URL = "https://www.cbr-xml-daily.ru/daily_json.js"


async def request_valute_info() -> dict:
    """
    Request information about the ruble exchange rate.
    """
    date = datetime.now()
    current_date: tuple = (date.year, date.month, date.day)

    if current_date in cashed_currency:
        return cashed_currency[current_date]

    async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(60)) as client:
        async with client.get(
                url=URL, headers={'Accept': 'application/json'}
        ) as response:
            if response.status == 200:
                currency: dict = json.loads(await response.text())
                cashed_currency.clear()
                cashed_currency[current_date] = currency
                return currency

            else:
                raise aiohttp.ClientResponseError


async def get_valute_info() -> dict[str, tuple[int, float]]:
    """
    Return the dictionary with information
    about the value of currencies.
    """
    data = await request_valute_info()
    return {
        "dollar": (
            int(data['Valute']['USD']['Nominal']),
            float(data["Valute"]["USD"]["Value"])
        ),
        "euro": (
            int(data['Valute']['EUR']['Nominal']),
            float(data["Valute"]["EUR"]["Value"])
        ),
        "yena": (
            int(data['Valute']['CNY']['Nominal']),
            float(data["Valute"]["CNY"]["Value"])
        ),
        "som": (
            int(data['Valute']['UZS']['Nominal']),
            float(data["Valute"]["UZS"]["Value"])
        )
    }


async def get_all_valute_for_month(
    year: int,
    month: int,
    user_id: int
) -> dict:
    """
    Get all currency data for the month.

    :return: Combined valute data from all sources.
    """
    data, data_income, data_expense = await asyncio.gather(
        aggregate_valute(year, month, user_id, "salaries"),
        aggregate_valute(year, month, user_id, "other_income"),
        aggregate_valute(year, month, user_id, "expenses")
    )

    return {
        "dollar": (
            data.get("dollar", 0) +
            data_income.get("dollar", 0) -
            data_expense.get("dollar", 0)
        ),
        "euro": (
            data.get("euro", 0) +
            data_income.get("euro", 0) -
            data_expense.get("euro", 0)
        ),
        "yena": (
            data.get("yena", 0) +
            data_income.get("yena", 0) -
            data_expense.get("yena", 0)
        ),
        "som": (
            data.get("som", 0) +
            data_income.get("som", 0) -
            data_expense.get("som", 0)
        )
    }

