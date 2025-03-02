from typing import Dict, List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.common import create_pagination_buttons


async def create_list_transfer_accounts(
    data: dict,
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
            id_: int = str(item.get("id")) + f"_{item.get("name")}" \
                if transfer else item.get("id")

            inline_buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{item.get("name")} / "
                             f"{float(item.get('balance')):_}₽",
                        callback_data=str(id_)
                    )
                ])

    lst_menu: list = await create_pagination_buttons(
        previous, next_, "prev_tr", "next_tr"
    )
    inline_buttons.append(lst_menu)
    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)
