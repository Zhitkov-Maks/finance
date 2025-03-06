from typing import List, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.common import create_pagination_buttons


async def create_list_account(
    data: dict,
    prev: str = "prev_acc",
    next_d: str = "next_acc"
) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard.
    :param next_d: The name for the callback_data when
                        forming the keyboard.
    :param prev: The name for the callback_data when
                        forming the keyboard.
    :param data: Dictionary with query data.
    :return: The inline keyboard.
    """
    keyboards: List[List[InlineKeyboardButton]] = []
    previous, next_ = data.get("previous"), data.get("next")
    for item in data.get("results")[0].get("accounts"):
            id_: int = item.get("id")
            keyboards.append(
                [
                    InlineKeyboardButton(
                        text=f"{item.get("name")} /"
                             f" {float(item.get('balance')):_}₽",
                        callback_data=str(id_)
                    )
                ])

    lst_menu: list = await create_pagination_buttons(
        previous, next_, prev, next_d
    )
    keyboards.append(lst_menu)
    return InlineKeyboardMarkup(inline_keyboard=keyboards)


async def get_action_accounts(is_active: bool) -> InlineKeyboardMarkup:
    """
    The function generates a keyboard for the action
    according to a specific account.
    :return InlineKeyboardMarkup: Use the keyboard to select actions.
    """
    toggle =  "✔️" if is_active else"✘"
    inline_actions = [
        [
            InlineKeyboardButton(
                text="Удалить",
                callback_data="remove"
            ),
            InlineKeyboardButton(
                text="Меню",
                callback_data="main"
            ),
            InlineKeyboardButton(
                text="Счета",
                callback_data="accounts"
            )
        ],
        [
            InlineKeyboardButton(
                text="Ред-ть",
                callback_data="edit"
            ),
            InlineKeyboardButton(
                text=toggle,
                callback_data="change-toggle"
            ),
            InlineKeyboardButton(
                text="Перевести",
                callback_data="transfer"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_actions)


choice_edit_button: list[list[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(
            text="Полное",
            callback_data="edit_full"
        ),
        InlineKeyboardButton(
            text="Баланс",
            callback_data="edit_balance"
        )
    ]
]

# Keyboard for editing selection.
choice_inline_edit = InlineKeyboardMarkup(inline_keyboard=choice_edit_button)
