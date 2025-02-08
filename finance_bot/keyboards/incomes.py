from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_action() -> InlineKeyboardMarkup:
    """
    An inline keyboard with options for actions for a specific income.
    :return: The inline keyboard.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Удалить",
                    callback_data="remove_income",
                ),
                InlineKeyboardButton(
                    text="Меню",
                    callback_data="main",
                ),
                InlineKeyboardButton(
                    text="Ред-ть",
                    callback_data="edit_income",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data="incomes_history",
                )
            ]
        ]
    )


choice_edit_buttons: List[List[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(
            text="Полностью",
            callback_data="edit_income_full",
        ),
        InlineKeyboardButton(
            text="Сумму",
            callback_data="edit_income_balance",
        )
    ]
]

# Keyboard for editing selection.
choice_edit: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=choice_edit_buttons)
