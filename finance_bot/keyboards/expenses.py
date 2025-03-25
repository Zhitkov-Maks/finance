from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_action(show: str) -> InlineKeyboardMarkup:
    """
    An inline keyboard with options for actions for a specific expense.
    :return: The inline keyboard.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✗",
                    callback_data="remove_expense",
                ),
                InlineKeyboardButton(
                    text="㊂",
                    callback_data="main",
                ),
                InlineKeyboardButton(
                    text="✍️",
                    callback_data="edit_expense",
                ),
                InlineKeyboardButton(
                    text="🔙",
                    callback_data=show,
                )
            ],
        ]
    )


async def choice_edit(expense_id) -> InlineKeyboardMarkup:
    """
    Creating a inline keyboard for editing expenses.

    :param action: Commands for a button on the keyboard.
    :return InlineKeyboardMarkup: The keyboard.
    """
    choice_list: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="✎",
                callback_data="edit_expense_full",
            ),
            InlineKeyboardButton(
                text="🔙",
                callback_data=f"{expense_id}",
            ),
            InlineKeyboardButton(
                text="㊂",
                callback_data="main",
            ),
            InlineKeyboardButton(
                text="₱",
                callback_data="edit_expense_balance",
            ),
        ]
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=choice_list
    )
