from datetime import datetime
import stat

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

from api.common import get_all_objects
from utils.analytics import generate_detail_analytics
from handlers.decorator_handler import decorator_errors
from states.analitics import AnalyticsState
from keyboards.analytics import (
    analytic_detail_keyboard,
    base_keyboard,
    generate_keyboard_analytics
)
from config import analytics_url


analytics_router = Router()


@analytics_router.callback_query(F.data == "analytics")
@decorator_errors
async def show_menu_analytics(
    call: CallbackQuery,
    state: FSMContext
) -> None:
    """Show me the keyboards for selecting the type of analytics."""
    await call.message.edit_text(
        text=hbold("Выберите тип аналитики:"),
        reply_markup=base_keyboard,
        parse_mode="HTML"
    )
    

@analytics_router.callback_query(
    F.data.in_(["expense_analytics", "income_analytics"])
)
async def get_monthly_analytics(
    call: CallbackQuery,
    state: FSMContext
) -> None:
    year = datetime.now().year
    type_analytics = call.data.split("_")[0]

    url = analytics_url.format(type=type_analytics, year=year)
    result = await get_all_objects(url, call.from_user.id)
    data = result["results"]

    keyboard = await generate_keyboard_analytics(data)
    if len(data) > 0:
        await state.set_state(AnalyticsState.show)
        await state.update_data(
            results=data,
            ta=type_analytics,
            year=year
        )
        await call.message.edit_text(
            text=hbold(f"Данные за {year} год."),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await call.message.edit_text(
            text=hbold(f"Данные за {year} не найдены."),
            reply_markup=keyboard,
            parse_mode="HTML"
        )


@analytics_router.callback_query(
    AnalyticsState.show, F.data.split("_")[1].isdigit())
@decorator_errors
async def show_detail_monthly_analytics(
    call: CallbackQuery,
    state: FSMContext
) -> None:
    """Show detailed analytics for the month."""
    data = await state.get_data()
    index = int(call.data.split("_")[1])
    result = data.get("results")[index]
    type_analytics = data.get("ta")

    text = await generate_detail_analytics(result, type_analytics)
    keyboard = await analytic_detail_keyboard()

    await call.message.edit_text(
        text=hbold(text),
        parse_mode="HTML",
        reply_markup=keyboard
    )


@analytics_router.callback_query(
    F.data.in_(["next_an", "prev_an", "curr_an"])
)
@decorator_errors
async def prev_next_year_analytics(
    call: CallbackQuery,
    state: FSMContext
) -> None:
    action = call.data.split("_")[0]
    st_data = await state.get_data()
    type_analytics = st_data.get("ta")
    year = st_data.get("year", datetime.now().year)

    if action == "next":
        year += 1

    elif action == "prev":
        year -= 1
    await state.update_data(year=year)

    url = analytics_url.format(type=type_analytics, year=year)
    result = await get_all_objects(url, call.from_user.id)
    data = result["results"]

    keyboard = await generate_keyboard_analytics(data)

    if len(data) > 0:
        await state.set_state(AnalyticsState.show)
        await state.update_data(results=data)
        await call.message.edit_text(
            text=hbold(f"Данные за {year} год."),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await call.message.edit_text(
            text=hbold(f"Данные за {year} не найдены."),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
