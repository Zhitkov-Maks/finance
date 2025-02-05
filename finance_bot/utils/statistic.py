from api.common import get_full_info


async def get_statistic_current_month(url: str, user_id: int, accounts=False) -> float:
    """
    A function for getting the amount of income,
    expenses for the current month, as well as the
    balance of all accounts.

    :param url: url for the request.
    :param user_id: Telegram user's ID chat.
    :param accounts: For accounts, you need other keys to access the balance.
    :return: We will refund the amount received.
    """
    result: dict = await get_full_info(url, user_id)
    if not accounts:
        return float(result.get("total_amount"))
    return float(result.get("results")[0].get("total_balance"))
