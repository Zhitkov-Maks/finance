import re
from typing import Dict, List

from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from config import accounts_url

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
    Generates a url for receiving user invoices.
    :param page: The page for the request.
    :param page_size: Page size for the request.
    :return str: URL.
    """
    return accounts_url + f"?page={page}&page_size={page_size}"


async def account_by_id(account_id: int) -> str:
    return accounts_url + f"{account_id}/"


async def get_last_incomes_expenses(data: List[Dict[str, int | float | str]]) -> str:
    """
    We collect lines for expenses and income.
    :param data: A list with income or expenses.
    :return str: String
    """
    if len(data) == 0:
        return f"{35 * '-'}\nДанные отсутствуют."

    text: str = f"{35 * '-'}\n"
    for item in data:
        dt: str = (
            f"{item['create_at'][8:10]}/{item['create_at'][5:7]}/{item["create_at"][11:16]}"
        )
        text += f"{hbold(dt)}   {float(item['amount']):.2f}₽\n"
    return text


async def generate_message_answer(
    data: dict[str, list[dict[str, int]] | dict[str, str] | float]
) -> str:
    """
    A function for generating a message for the user.
    :param data: Necessary data to generate a message.
    :return str:A message to show to the user
    """
    message: str = f"{data.get("name")} 👉🏻 "
    message += f"{float(data.get('balance')):_}₽\n"
    message += "\nПоследние доходы 😉\n" + await get_last_incomes_expenses(
        data.get("incomes")
    )
    message += "\nПоследние расходы 🫢\n" + await get_last_incomes_expenses(
        data.get("expenses")
    )
    return message


async def update_account_state(
    state: FSMContext, response: dict[str, str | int | bool]
) -> None:
    """
    Helper function to update the state with account information.
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
