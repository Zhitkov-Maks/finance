from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_action(show) -> InlineKeyboardMarkup:
    """
    An inline keyboard with options for actions for a specific income.
    :return: The inline keyboard.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✗",
                    callback_data="remove_income",
                ),
                InlineKeyboardButton(
                    text="㊂",
                    callback_data="main",
                ),
                InlineKeyboardButton(
                    text="✍️",
                    callback_data="edit_income",
                ),
                InlineKeyboardButton(
                    text="⏎",
                    callback_data=show,
                )
            ],
        ]
    )


async def choice_edit(income_id: str) -> InlineKeyboardMarkup:
    """
    Creating a inline keyboard for editing incomes.

    :param action: Commands for a button on the keyboard.
    :return InlineKeyboardMarkup: The keyboard.
    """
    choice_list: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="✎",
                callback_data="edit_income_full",
            ),
            InlineKeyboardButton(
                text="🔙",
                callback_data=f"{income_id}",
            ),
            InlineKeyboardButton(
                text="㊂",
                callback_data="main",
            ),
            InlineKeyboardButton(
                text="₱",
                callback_data="edit_income_balance",
            ),
        ]
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=choice_list
    )
