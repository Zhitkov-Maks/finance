from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def generate_inline_keyboard_reset() -> InlineKeyboardMarkup:
    """
    Create password reset buttons.

    :return InlineKeyboardMarkup: An inline keyboard with options.
    """
    inline_reset: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="Сброс пароля", callback_data="reset"),
            InlineKeyboardButton(text="Выйти в меню", callback_data="main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_reset)
