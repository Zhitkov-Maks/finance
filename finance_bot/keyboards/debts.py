from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.common import create_pagination_buttons


async def debts_keyboard_generate(
    debt_data: dict,
    prev: str = "prev_debt",
    next_d: str = "next_debt"
) -> InlineKeyboardMarkup:
    """Generating a keyboard for further debt management."""
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
    keyboards.append(lst_menu)
    return InlineKeyboardMarkup(inline_keyboard=keyboards)


# Options for actions with debts.
debts_buttons: List[List[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(
            text="Показать список должников",
            callback_data="show_lends"
        )
    ],
    [
        InlineKeyboardButton(
            text="Показать кому вы должны",
            callback_data="show_debts"
        )
    ],
    [
        InlineKeyboardButton(
            text="Взять в долг",
            callback_data="to_borrow"
        ),
        InlineKeyboardButton(
            text="Дать взаймы",
            callback_data="to_lend"
        )
    ]
]


debts_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=debts_buttons
)
