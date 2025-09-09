import re

from aiogram.fsm.context import FSMContext

from config import accounts_url
from loader import is_active_balance, is_not_active_balance

balance_pattern: re.Pattern = re.compile(r"^-?\d+(\.\d+)?$")


def is_valid_balance(balance: str) -> bool:
    """
    Check if the provided balance is a valid integer or float.

    :param balance: The passed string for verification.
    :return: Boolean value.
    """
    return bool(balance_pattern.match(balance))


async def account_url(page: int, page_size: int = 10) -> str:
    """
    Generate a url for receiving user invoices.

    :param page: The page for the request.
    :param page_size: Page size for the request.
    :return str: URL.
    """
    return accounts_url + f"?page={page}&page_size={page_size}"


async def account_by_id(account_id: int) -> str:
    """Return the url for working with a specific account."""
    return accounts_url + f"{account_id}/"


async def generate_message_answer(
    data: dict[str, list[dict[str, int]] | dict[str, str] | float]
) -> str:
    """
    Generate a message for the user.

    :param data: Necessary data to generate a message.
    :return str:A message to show to the user
    """
    message: str = f"{data.get("name")} 👉🏻 "
    message += f"{float(data.get('balance')):_}₽\n"
    is_active = data.get('is_active')
    if is_active:
        message += is_active_balance
    else:
        message += is_not_active_balance
    return message


async def update_account_state(
    state: FSMContext, response: dict[str, str | int | bool]
) -> None:
    """
    Update the state with account information.

    :param state: FSMContext for updating data.
    :param response: The result of the request.
    :return: None.
    """
    is_active: bool = response.get("is_active")

    await state.update_data(
        account_id=response.get("id"),
        account=response.get("name"),
        is_active=is_active,
    )
