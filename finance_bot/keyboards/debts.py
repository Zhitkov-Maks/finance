from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.common import create_pagination_buttons


async def generate_debts_actions(action: str) -> InlineKeyboardMarkup:
    """
    Create buttons to select actions with debt.

    :param type_: The type of the debt to show.
    """
    action = "show_debts" if action == "debt" else "show_lends"
    return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌",
                    callback_data="close_debt"
                ),
                InlineKeyboardButton(
                    text="㊂",
                    callback_data="main",
                ),
                InlineKeyboardButton(
                    text="🔙",
                    callback_data=action,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Вернуть часть суммы.",
                    callback_data="repay_part"
                )
            ]
        ]
    )


async def debts_keyboard_generate(
    debt_data: dict,
    prev: str = "prev_debt",
    next_d: str = "next_debt"
) -> InlineKeyboardMarkup:
    """
    Create buttons to work with the list of debts.
    
    :param debt_data: A dictionary containing a list of debts.
    :param prev: The name for the callback_data for the prev button.
    :param next_d: The name for the callback_data for the next button.
    """
    keyboards: List[List[InlineKeyboardButton]] = []
    previous, next_ = debt_data.get("previous"), debt_data.get("next")

    for item in debt_data.get("results"):
        message: str = f"{item.get("borrower_description")} 😒 / "
        message += f"{item.get("transfer").get("amount")}₽."
        keyboards.append(
            [
                InlineKeyboardButton(
                    text=message,
                    callback_data=f"{item.get('id')}",
                ),
            ]
        )

    lst_menu: list = await create_pagination_buttons(
        previous, next_, prev, next_d
    )
    lst_menu.insert(1, InlineKeyboardButton(
        text="🔙", callback_data="debt_and_lends")
    )
    keyboards.append(lst_menu)
    return InlineKeyboardMarkup(inline_keyboard=keyboards)


# Options for actions with debts.
debts_buttons: List[List[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(
            text="Должники",
            callback_data="show_lends"
        ),
        InlineKeyboardButton(
            text="Кредиторы",
            callback_data="show_debts"
        )
    ],
    [
        InlineKeyboardButton(
            text="Занять",
            callback_data="to_borrow"
        ),
        InlineKeyboardButton(
            text="㊂",
            callback_data="main"
        ),
        InlineKeyboardButton(
            text="Одолжить",
            callback_data="to_lend"
        )
    ]
]


debts_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=debts_buttons
)
