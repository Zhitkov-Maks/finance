from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_action() -> InlineKeyboardMarkup:
    """
    An online keyboard with options for actions for a specific expense.
    :return: The inline keyboard.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Удалить",
                    callback_data="remove_expense",
                ),
                InlineKeyboardButton(
                    text="Меню",
                    callback_data="main",
                ),
                InlineKeyboardButton(
                    text="Ред-ть",
                    callback_data="edit_expense",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data="expenses_history",
                )
            ]
        ]
    )


expenses_buttons: List[List[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(
            text="Посмотреть расходы",
            callback_data="expenses_history"
        )
    ],
    [
        InlineKeyboardButton(
            text="Создать расход",
            callback_data="expense_add",
        )
    ]
]

expenses_keyboard = InlineKeyboardMarkup(inline_keyboard=expenses_buttons)


choice_edit_buttons_expense: List[List[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(
            text="Все данные",
            callback_data="edit_expense_full",
        ),
        InlineKeyboardButton(
            text="Сумму расхода",
            callback_data="edit_expense_balance",
        ),
    ]
]


choice_expense_edit: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=choice_edit_buttons_expense
)
