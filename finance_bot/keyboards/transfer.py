from typing import Dict, List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def create_list_transfer_accounts(
    data: Dict[str, str | List[Dict[str, float | List[Dict[str, int | float | str]]]]],
    current_account: int = 0,
    transfer: bool = False,
) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard.
    :param transfer: If parameter is true,
                    then you need a name to show to the user,
                    not just an id.
    :param current_account: We do not show the current account
                            during the transfer
    :param data: Dictionary with query data.
    :return: The inline keyboard.
    """
    inline_buttons: List[List[InlineKeyboardButton]] = []
    previous, next_ = data.get("previous"), data.get("next")
    for item in data.get("results")[0].get("accounts"):
        if item.get("id") != current_account:
            id_: int = str(item.get("id")) + f"_{item.get("name")}" if transfer else item.get("id")
            inline_buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{item.get("name")} / {float(item.get('balance')):_}₽",
                        callback_data=str(id_)
                    )
                ])

    prev_data, text_prev = "None prev", "-"
    next_data, text_next = "None next", "-"

    if previous is not None:
        prev_data, text_prev = "prev_tr", "<<"

    if next_ is not None:
        next_data, text_next = "next_tr", ">>"

    inline_buttons.append(
        [
            InlineKeyboardButton(text=text_prev, callback_data=prev_data),
            InlineKeyboardButton(text="Меню", callback_data="main"),
            InlineKeyboardButton(text=text_next, callback_data=next_data),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)
