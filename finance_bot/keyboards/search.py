from collections import defaultdict
from typing import List, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ACTIONS: Dict[str, str] = {
    "account_name": "Имя счета",
    "amount_gte": "Сумма от",
    "amount_lte": "Сумма до",
    "category_name": "Имя категории",
    "create_at_after": "Дата больше",
    "create_at_before": "Дата меньше"
}
user_choices: Dict[int, dict] = defaultdict(dict)


async def get_action_options(
        user_id: int, show: str
) -> InlineKeyboardMarkup:
    """
    Generating a keyboard for searching for expenses or income.

    :param user_id: The user's ID.
    :param show: The command that should trigger a specific handler.
    :return InlineKeyboardMarkup: The Inline keyboard.
    """
    keyboard: List[List[InlineKeyboardButton]] = [[]]
    for action in ACTIONS:
        # Добавляем кнопку с состоянием
        button_text = f"{ACTIONS[action]}    [✘] " \
            if action not in user_choices[user_id] \
            else f"{ACTIONS[action]}    [✔️]"
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=button_text, callback_data=f"toggle-{action}")
            ]
        )

    keyboard.append([
        InlineKeyboardButton(text="🆗", callback_data="finish"),
        InlineKeyboardButton(text="🔙", callback_data=show)
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
