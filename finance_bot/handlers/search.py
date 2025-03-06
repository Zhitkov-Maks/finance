from typing import List

from aiogram.utils.markdown import hbold
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from api.common import get_full_info
from handlers.decorator_handler import decorator_errors
from keyboards.keyboards import main_menu, cancel_, create_list_incomes_expenses
from keyboards.search import get_action_options, user_choices, ACTIONS
from loader import search_text
from states.search import SearchState
from utils.search import state_dict, validate_data_search, generate_url

search: Router = Router()


@search.callback_query(F.data.in_(["sh_expenses", "sh_incomes"]))
async def command_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    user_choices[call.from_user.id].clear()
    type_: str = call.data.split("_")[1]
    await state.update_data(type=type_)
    await call.message.edit_text(
        text=search_text,
        reply_markup=await get_action_options(call.from_user.id)
    )


@search.callback_query(lambda c: c.data.startswith("toggle-"))
@decorator_errors
async def toggle_action(
    callback_query: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Обработчик выбора вариантов для поиска.
    """
    action: str = callback_query.data.split("-")[1]
    user_id: int = callback_query.from_user.id
    if action in user_choices[user_id]:
        await callback_query.answer(f"Вы убрали: {action}")
        user_choices[user_id].pop(action)

    else:
        user_choices[user_id].update({action: ACTIONS[action]})
        await callback_query.answer(
            f"Вы выбрали: {action}"
        )

    await callback_query.message.edit_reply_markup(
        reply_markup=await get_action_options(user_id)
    )


@search.callback_query(F.data == "finish")
@decorator_errors
async def finish_selection(
        call: CallbackQuery, state: FSMContext
) -> None:
    """
    Финальный обработчик прогнозирования пятидневки. Высчитывает прогнозируемый
    заработок на основе введенных пользователем данных, и отмеченных
    пользователем данных.
    """
    options = list(user_choices[call.from_user.id].keys())
    await state.update_data(options=options)
    if len(options) == 0:
        await call.answer(
            text=f"Вы ничего не выбрали",
            reply_markup=main_menu
        )
        return

    action: str = options.pop()
    await state.update_data(action=action)
    await state.set_state(SearchState.action)
    await call.message.edit_text(
        text=state_dict[action][0],
        reply_markup=cancel_
    )


@search.message(SearchState.action)
async def save_account_name(mess: Message, state: FSMContext) -> None:
    data: dict = await state.get_data()
    options: List[str] = data["options"]
    action: str = data["action"]
    is_valid : bool = await validate_data_search(action, mess.text)
    if not is_valid:
        await mess.answer(
            hbold("Неверный формат ввода, попробуйте еще раз."),
            reply_markup=cancel_,
            parse_mode="HTML"
        )
        return

    await state.update_data({action: mess.text})

    if len(options) != 0:
        action = options.pop()
        await state.set_state(state_dict[action][1])
        await state.update_data(action=action)
        await mess.answer(
            text=state_dict[action][0],
            reply_markup=cancel_
        )
        return

    data: dict = await state.get_data()
    page: int = data.get("page", 1)
    url: str = await generate_url(data, page)
    await state.update_data(page=page, url=url)
    result: dict = await get_full_info(url, mess.from_user.id)
    type_operation = "расходов" if data["type"] == "sh_expenses" else "доходов"
    keyword = await create_list_incomes_expenses(
        result, "prev_search", "next_search", type_operation
    )

    await mess.answer(
        text=hbold("Вот что я нашел!"),
        reply_markup=keyword,
        parse_mode="HTML"
    )


@search.callback_query(F.data.in_(["prev_search", "next_search"]))
@decorator_errors
async def next_prev_output_list_expenses(
    call: CallbackQuery, state: FSMContext
) -> None:
    data: dict = await state.get_data()
    page = data.get("page")

    if call.data == "next_search":
        page += 1
    else:
        page -= 1

    url: str = await generate_url(data, page)
    result: dict = await get_full_info(url, call.from_user.id)

    type_operation = "расходов" if data["type"] == "sh_expenses" else "доходов"
    keyword = await create_list_incomes_expenses(
        result, "prev_search", "next_search", type_operation
    )

    await state.set_state(SearchState.show)
    await state.update_data(page=page)
    await call.message.edit_reply_markup(reply_markup=keyword)
