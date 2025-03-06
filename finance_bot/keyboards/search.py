from collections import defaultdict
from typing import List, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ACTIONS: Dict[str, str] = {
    "account_name": "Имя счета",
    "amount_gte": "Сумма от",
    "category_name": "Имя категории",
    "create_at_after": "Дата больше",
    "create_at_before": "Дата меньше"
}
user_choices: Dict[int, dict] = defaultdict(dict)


async def get_action_options(user_id: int) -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру для выбора дней недели и часов.

    :return: Объект InlineKeyboardMarkup, представляющий инлайн-клавиатуру с
                кнопками.
    """
    keyboard: List[List[InlineKeyboardButton]] = [[]]
    for action in ACTIONS:
        # Добавляем кнопку с состоянием
        button_text = f"{ACTIONS[action]}    [✘] " if action not in user_choices[user_id] \
            else f"{action}    [✔️]"
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=button_text, callback_data=f"toggle-{action}")
            ]
        )

    keyboard.append([
        InlineKeyboardButton(text="Завершить выбор", callback_data="finish"),
        InlineKeyboardButton(text="Меню", callback_data="main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
