from aiogram.utils.markdown import hbold
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.decorator_handler import decorator_errors
from handlers.utils import generate_results, handle_response
from keyboards.keyboards import main_menu, cancel_
from keyboards.search import get_action_options, user_choices, ACTIONS
from loader import search_text
from states.search import SearchState
from utils.search import state_dict, validate_data_search

search: Router = Router()


@search.callback_query(F.data.in_(["sh_expenses", "sh_incomes"]))
@decorator_errors
async def command_start(call: CallbackQuery, state: FSMContext) -> None:
    """
    The handler shows a menu with a selection of fields to search for.
    """
    user_choices[call.from_user.id].clear()
    type_: str = call.data
    await state.update_data(type=type_)
    show: str = (await state.get_data())["show"]
    await call.message.edit_text(
        text=search_text,
        reply_markup=await get_action_options(call.from_user.id, show)
    )


@search.callback_query(lambda c: c.data.startswith("toggle-"))
@decorator_errors
async def toggle_action(
    callback_query: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Processes and saves the selected fields to the dictionary.
    """
    action: str = callback_query.data.split("-")[1]
    user_id: int = callback_query.from_user.id
    show: str = (await state.get_data()).get("show")
    if action in user_choices[user_id]:
        await callback_query.answer(f"Вы убрали: {ACTIONS[action]}")
        user_choices[user_id].pop(action)

    else:
        user_choices[user_id].update({action: ACTIONS[action]})
        await callback_query.answer(
            f"Вы выбрали: {ACTIONS[action]}"
        )

    await callback_query.message.edit_reply_markup(
        reply_markup=await get_action_options(user_id, show)
    )


@search.callback_query(F.data == "finish")
@decorator_errors
async def finish_selection(
        call: CallbackQuery, state: FSMContext
) -> None:
    """
    The beginning of processing the selected fields for the search.
    """
    options: list[str] = list(user_choices[call.from_user.id].keys())
    await state.update_data(options=options, show="search", page=1)
    if len(options) == 0:
        await call.answer(
            text="Вы ничего не выбрали",
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
@decorator_errors
async def save_account_name(mess: Message, state: FSMContext) -> None:
    """The handler is called while there are raw fields."""
    data: dict = await state.get_data()
    options: list = data["options"]
    action: str = data["action"]

    if not await validate_data_search(action, mess.text):
        await mess.answer(
            hbold("Неверный формат ввода, попробуйте еще раз."),
            reply_markup=cancel_,
            parse_mode="HTML"
        )
        return

    await state.update_data({action: mess.text})

    if options:
        action = options.pop()
        await state.set_state(state_dict[action][1])
        await state.update_data(action=action)
        await mess.answer(text=state_dict[action][0], reply_markup=cancel_)
        return

    page = data.get("page", 1)
    text, keyboard, _ = await generate_results(
        state, mess.from_user.id, page
    )
    await state.update_data(page=page)
    await handle_response(mess, state, text, keyboard)


@search.callback_query(F.data == "search")
@decorator_errors
async def show_search(call: CallbackQuery, state: FSMContext) -> None:
    """
    The handler for the request and processing the response
    from the server based on the found result.
    """
    data: dict = await state.get_data()
    page: int = data.get("page", 1)
    text, keyboard, _ = await generate_results(
        state, call.from_user.id, page
    )
    await state.update_data(page=page)
    await handle_response(call, state, text, keyboard)


@search.callback_query(F.data.in_(["prev_search", "next_search"]))
@decorator_errors
async def next_prev_output_list_expenses(
    call: CallbackQuery, state: FSMContext
) -> None:
    """The handler implements pagination when working with the search."""
    data: dict = await state.get_data()
    page: int = data.get("page", 1)
    page: int = page + 1 if call.data == "next_search" else page - 1
    text, keyboard, _ = await generate_results(
        state, call.from_user.id, page
    )
    await state.update_data(page=page)
    await handle_response(call, state, text, keyboard)
