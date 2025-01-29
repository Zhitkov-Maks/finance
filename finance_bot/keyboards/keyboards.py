from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Основное меню бота.
menu_bot: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Войти",
                callback_data="login"
            ),
             InlineKeyboardButton(
                 text="Регистрация",
                 callback_data="register"
            )
        ],
        [
            InlineKeyboardButton(
                text="Счета",
                callback_data="accounts"
            ),
            InlineKeyboardButton(
                text="Доходы",
                callback_data="incomes"
            ),
            InlineKeyboardButton(
                text="Расходы",
                callback_data="expenses"
            )
        ],
        [
            InlineKeyboardButton(
                text="Добавление/Удаление категорий",
                callback_data="categories"
            )
        ]
    ]

main_menu = InlineKeyboardMarkup(inline_keyboard=menu_bot)


# Кнопка отмены действия
cancel_button: List[List[InlineKeyboardButton]] = [
    [InlineKeyboardButton(text="Отмена", callback_data="main")]
]

cancel_ = InlineKeyboardMarkup(inline_keyboard=cancel_button)


# Подтверждение действия
confirm: List[List[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(text="Отмена", callback_data="main"),
        InlineKeyboardButton(text="Продолжить", callback_data="continue"),
    ]
]

confirm_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=confirm)
