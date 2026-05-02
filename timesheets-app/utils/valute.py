import json
from datetime import datetime

import aiohttp

from config import cashed_currency

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
