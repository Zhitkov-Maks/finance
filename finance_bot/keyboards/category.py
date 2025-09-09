from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_categories_action(back: str) -> InlineKeyboardMarkup:
    """
    Create a keyboard for working with categories.

    :param back: A string that will indicate which action
                    to assign to the back button.
    :return: A keyboard for working with categories.
    """
    actions_buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="❌", callback_data="del_category"),
            InlineKeyboardButton(text="㊂", callback_data="main"),
            InlineKeyboardButton(text="✎", callback_data="edit_category"),
            InlineKeyboardButton(text="🔙", callback_data=f"{back}"),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=actions_buttons)


async def create_list_category(
    data: dict[str, int | list[dict[str, int | str]]],
    prev: str = "prev_cat_inc",
    next_cat: str = "next_cat_inc",
) -> InlineKeyboardMarkup:
    """
    Create a keyboard for working with a list of categories.

    :param next_cat: The name for the callback_data when
        forming the keyboard.
    :param prev: The name for the callback_data when
        forming the keyboard.
    :param data: Dictionary with query data.
    :return: The inline keyboard.
    """
    inline_buttons: List[List[InlineKeyboardButton]] = []
    previous, next_ = data.get("previous"), data.get("next")
    for item in data.get("results"):
        inline_buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{item.get("name")}",
                    callback_data=f"{item.get("id")}_{item.get("name")}"
                )
            ]
        )

    prev_data, text_prev = "None prev", "-"
    next_data, text_next = "None next", "-"

    if previous is not None:
        prev_data, text_prev = prev, "<<"

    if next_ is not None:
        next_data, text_next = next_cat, ">>"

    inline_buttons.append(
        [
            InlineKeyboardButton(text=text_prev, callback_data=prev_data),
            InlineKeyboardButton(text="︽", callback_data="categories"),
            InlineKeyboardButton(text="⸬", callback_data="main"),
            InlineKeyboardButton(text=text_next, callback_data=next_data),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)


type_category_buttons: list[list[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(
            text="✎ ⬈",
            callback_data="add_income"
        ),
        InlineKeyboardButton(
            text="㊂",
            callback_data="main"
        ),
        InlineKeyboardButton(
            text="✎ ⬊",
            callback_data="add_expense"
        ),
    ],
    [
        InlineKeyboardButton(
            text="Список категорий доходов.",
            callback_data="list_incomes_category"
        ),
    ],
    [

        InlineKeyboardButton(
            text="Список категорий расходов.",
            callback_data="list_expenses_category"
        ),
    ]
]

# The keyboard is used to select an action when clicking
# on the Work with categories button.
inline_type_categories: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=type_category_buttons
)
