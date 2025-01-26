from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
            )
        ]
    ]

cancel_button: List[List[InlineKeyboardButton]] = [
    [InlineKeyboardButton(text="Отмена", callback_data="main")]
]
cancel = InlineKeyboardMarkup(inline_keyboard=cancel_button)
main_menu = InlineKeyboardMarkup(inline_keyboard=menu_bot)
