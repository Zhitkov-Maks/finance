from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def create_list_incomes_expenses(
    data: dict[str, list],
    prev: str = "prev_inc",
    next_d: str = "next_inc"
) -> InlineKeyboardMarkup:
    """
    Generate expenses or income in the form of an online keyboard.
    :param data: A data dictionary that contains a list of expenses or income.
    :param prev: The name for the prev button.
    :param next_d: The name for the next button.
    :return: An inline keyboard with expenses or income.
    """
    inline_buttons: List[List[InlineKeyboardButton]] = []
    previous, next_ = data.get("previous"), data.get("next")
    for item in data.get("results"):
        id_: int = item.get("id")
        dt: str = f"📆 {item['create_at'][8:10]}-{item['create_at'][5:7]}"
        text: str = f"{dt}  💰{item.get("amount")}₽  {item.get('category').get('name')}"

        inline_buttons.append([InlineKeyboardButton(text=text, callback_data=str(id_))])

    prev_data, text_prev = "None prev", "-"
    next_data, text_next = "None next", "-"

    if previous is not None:
        prev_data, text_prev = prev, "<<"

    if next_ is not None:
        next_data, text_next = next_d, ">>"

    inline_buttons.append(
        [
            InlineKeyboardButton(text=text_prev, callback_data=prev_data),
            InlineKeyboardButton(text="Меню", callback_data="main"),
            InlineKeyboardButton(text=text_next, callback_data=next_data),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)


# The main menu of the bot.
menu_bot: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="📉",
                callback_data="statistic_exp"
            ),
            InlineKeyboardButton(
                text="💰",
                callback_data="accounts_data"
            ),
            InlineKeyboardButton(
                text="💲",
                callback_data="expenses_by_incomes"
            ),
            InlineKeyboardButton(
                text="📈",
                callback_data="statistic_inc"
            ),
        ],
        [
            InlineKeyboardButton(
                text="➕",
                callback_data="incomes_add"
            ),
            InlineKeyboardButton(
                text="🏦",
                callback_data="accounts_add"
            ),
            InlineKeyboardButton(
                text="➖",
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


# Action confirmation buttons
confirm: List[List[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(text="Отмена", callback_data="main"),
        InlineKeyboardButton(text="Продолжить", callback_data="continue"),
    ]
]

# Inline action confirmation buttons
confirm_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=confirm)
