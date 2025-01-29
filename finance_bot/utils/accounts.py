import re
from typing import Dict, List

from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold


balance_pattern = re.compile(r'^-?\d+(\.\d+)?$')

def is_valid_balance(balance: str) -> bool:
    """Check if the provided balance is a valid integer or float."""
    return bool(balance_pattern.match(balance))


async def get_last_incomes_expenses(
    data: List[Dict[str, int | float | str]]
) -> str:
    """
    We collect lines for expenses and income.
    :param data: A list with income or expenses.
    :return str: String
    """
    if len(data) == 0:
        return f'\n{35 * '-'}\nДанные отсутствуют.'

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
    message: str = f"{hbold(data.get("name"))} 👉🏻 "
    message += f"{float(data.get('balance')):_}₽\n"
    message += hbold("\nПоследние доходы 😉\n") + await get_last_incomes_expenses(
        data.get("incomes")
    )
    message += hbold("\nПоследние расходы 🫢\n") + await get_last_incomes_expenses(
        data.get("incomes")
    )
    return message


async def update_account_state(state: FSMContext, response: dict) -> None:
    """Helper function to update the state with account information."""
    is_active = response.get("is_active")

    await state.update_data(
        account_id=response.get("id"),
        account=response.get("name"),
        is_active=is_active,
    )
