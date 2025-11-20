from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


base_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Расходы ↘",
                callback_data="expense_analytics"
            ),
            InlineKeyboardButton(
                text="Доходы ↗",
                callback_data="income_analytics"
            )
        ]
    ]
)


async def generate_keyboard_analytics(
    data: list[dict]
) -> InlineKeyboardMarkup:
    """
    Create a keyboard for displaying analytics for the year.
    
    :param data: Dictionary with analytics data.
    """
    keyboard = []
    for i, item in enumerate(data):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=(
                        f"{item['month_name']} => " 
                        f"{float(item['total_amount']):,.0f}₱"
                    ),
                    callback_data=f"analytics_{i}"
                )
            ]
        )

    keyboard.append(
        [   
            InlineKeyboardButton(text="<<", callback_data="prev_an"),
            InlineKeyboardButton(text="Меню", callback_data="main"),
            InlineKeyboardButton(text=">>", callback_data="next_an")
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def analytic_detail_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Меню", callback_data="main"),
            InlineKeyboardButton(text="🔙", callback_data="curr_an")
        ]
    ])
