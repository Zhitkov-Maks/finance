from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.common import create_pagination_buttons


async def create_list_incomes_expenses(
    data: dict[str, list],
    call_data: str,
    type_transaction: str,
    prev: str = "prev_inc",
    next_d: str = "next_inc",
) -> InlineKeyboardMarkup:
    """
    Create buttons from the list of transactions.

    :param data: A data dictionary that contains a list of expenses or income.
    :param prev: The name for the prev button.
    :param next_d: The name for the next button.
    :param call_data: The data to send to the call.
    :return: An inline keyboard with expenses or income.
    """
    inline_buttons: List[List[InlineKeyboardButton]] = []
    previous, next_ = data.get("previous"), data.get("next")
    mark: str = "-" if "exp" in type_transaction else "+"
    for item in data.get("results"):
        id_: int = item.get("id")
        dt: str = f"📆 {item['create_at'][8:10]}-{item['create_at'][5:7]}"
        text: str = (f"{dt}  💰 {mark}{item.get("amount")}₽  "
                     f"{item.get('category').get('name')}")

        inline_buttons.append(
            [InlineKeyboardButton(text=text, callback_data=str(id_))]
        )

    lst_menu: list = await create_pagination_buttons(
        previous, next_, prev, next_d
    )
    lst_menu.insert(
        1, InlineKeyboardButton(text="🔎", callback_data=call_data)
    )
    inline_buttons.append(lst_menu)
    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)


async def confirmation(action: str) -> InlineKeyboardMarkup:
    """Create confirmation buttons."""
    confirm: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="△", callback_data=action),
            InlineKeyboardButton(text="㊂", callback_data="main"),
            InlineKeyboardButton(text="➤", callback_data="continue"),
        ]
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=confirm
    )


async def cancel_action() -> InlineKeyboardMarkup:
    """Create cancellation buttons when working with transactions."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙",
                    callback_data="current_category",
                ),
                InlineKeyboardButton(
                    text="㊂",
                    callback_data="main",
                )
            ]
        ]
    )


# The main menu of the bot.
menu_bot: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="⬊",
                callback_data="statistic_exp"
            ),
            InlineKeyboardButton(
                text="₱",
                callback_data="accounts_data"
            ),
            InlineKeyboardButton(
                text="⇅",
                callback_data="expenses_by_incomes"
            ),
            InlineKeyboardButton(
                text="⬈",
                callback_data="statistic_inc"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⤴",
                callback_data="incomes_add"
            ),
            InlineKeyboardButton(
                text="↯",
                callback_data="analytics"
            ),
            InlineKeyboardButton(
                text="‰",
                callback_data="accounts_add"
            ),
            InlineKeyboardButton(
                text="⤵",
                callback_data="expense_add"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Доходы",
                callback_data="incomes_history"
            ),
            InlineKeyboardButton(
                text="Счета",
                callback_data="accounts"
            ),
            InlineKeyboardButton(
                text="Расходы",
                callback_data="expenses_history"
            )
        ],
        [
            InlineKeyboardButton(
                text="Категории",
                callback_data="categories"
            ),
            InlineKeyboardButton(
                text="Долги",
                callback_data="debt_and_lends"
            )
        ]
    ]

# Inline keyboard for the main menu of the bot
main_menu = InlineKeyboardMarkup(inline_keyboard=menu_bot)


# Cancel action button
cancel_button: List[List[InlineKeyboardButton]] = [
    [InlineKeyboardButton(text="Отмена", callback_data="main")]
]

# Inline undo button
cancel_ = InlineKeyboardMarkup(inline_keyboard=cancel_button)
