from typing import Dict

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold

from api.common import get_all_objects, get_full_info, delete_object_by_id
from config import PAGE_SIZE
from handlers.decorator_handler import decorator_errors
from keyboards.incomes import incomes_keyboards, get_action
from keyboards.keyboards import confirm_menu, create_list_incomes_expenses
from states.incomes import IncomesState
from utils.incomes import get_incomes_url, generate_message_income_info, incomes_by_id

incomes = Router()


@incomes.callback_query(F.data == "incomes")
async def start_work_incomes(callback: CallbackQuery) -> None:
    """A handler for selecting the next action."""
    await callback.message.answer(
        text="Выберите операцию с доходами.", reply_markup=incomes_keyboards
    )


@incomes.callback_query(F.data == "incomes_history")
@decorator_errors
async def incomes_get_history(callback: CallbackQuery, state: FSMContext) -> None:
    """A handler for displaying the latest incomes."""
    data: dict[str, str | int] = await state.get_data()
    page: int = data.get("page", 1)
    url: str = await get_incomes_url(page, page_size=PAGE_SIZE)
    result: dict[str, int | list[dict[str, int | str | dict[str, str]]]] = (
        await get_all_objects(url, callback.from_user.id)
    )

    await state.update_data(page=page)
    keyword: InlineKeyboardMarkup = await create_list_incomes_expenses(result)

    await state.set_state(IncomesState.show)
    await callback.message.answer(
        text=f"Ваши доходы.",
        reply_markup=keyword,
    )


@incomes.callback_query(F.data.in_(["next_inc", "prev_inc"]))
@decorator_errors
async def next_prev_output_list_incomes(call: CallbackQuery, state: FSMContext) -> None:
    """Show more incomes if any."""
    page: int = (await state.get_data()).get("page")

    if call.data == "next_inc":
        page += 1
    else:
        page -= 1

    url: str = await get_incomes_url(page, page_size=PAGE_SIZE)
    result: Dict[str, list] = await get_all_objects(url, call.from_user.id)
    keyword: InlineKeyboardMarkup = await create_list_incomes_expenses(result)

    await state.set_state(IncomesState.show)
    await state.update_data(page=page)
    await call.message.edit_reply_markup(reply_markup=keyword)


@incomes.callback_query(IncomesState.show, F.data.isdigit())
@decorator_errors
async def detail_incomes(call: CallbackQuery, state: FSMContext) -> None:
    """Show detailed income information."""
    income_id: int = int(call.data)
    url: str = await incomes_by_id(income_id)

    response: dict[str, int | str | dict[str, int | str]] = await get_full_info(
        url, call.from_user.id
    )
    await state.update_data(income_id=income_id)
    text: str = await generate_message_income_info(response)

    await state.set_state(IncomesState.action)
    await call.message.answer(
        text=hbold(text),
        parse_mode="HTML",
        reply_markup=await get_action(),
    )


@incomes.callback_query(F.data == "remove_income", IncomesState.action)
async def remove_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirmation of deletion."""
    await state.set_state(IncomesState.remove)
    await callback.message.answer(text="Вы уверены?", reply_markup=confirm_menu)


@incomes.callback_query(IncomesState.remove, F.data == "continue")
@decorator_errors
async def remove_income_by_id(callback: CallbackQuery, state: FSMContext) -> None:
    """
    The final income deletion handler.
    """
    data: dict[str, str | int] = await state.get_data()
    income_id: int = data.get("income_id")
    url: str = await incomes_by_id(income_id)

    await delete_object_by_id(url, callback.from_user.id)

    page: int = data.get("page", 1)
    url: str = await get_incomes_url(page, page_size=PAGE_SIZE)
    result: dict[str, int | list[dict[str, int | str | dict[str, str]]]] = (
        await get_all_objects(url, callback.from_user.id)
    )

    await state.update_data(page=page)
    keyword: InlineKeyboardMarkup = await create_list_incomes_expenses(result)

    await state.set_state(IncomesState.show)
    await callback.message.answer(
        text=f"Запись была удалена.",
        reply_markup=keyword,
    )
