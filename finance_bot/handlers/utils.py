from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold

from api.common import get_full_info
from keyboards.keyboards import create_list_incomes_expenses
from states.expenses import ExpensesState
from states.incomes import IncomesState
from utils.search import generate_url


async def _generate_results(
        state: FSMContext,
        user_id: int,
        page: int,
        prev_action: str = "prev_search",
        next_action: str = "next_search"
) -> tuple:
    data = await state.get_data()
    url = await generate_url(data, page)
    result = await get_full_info(url, user_id)

    type_operation = "расходов" if data["type"] == "sh_expenses" else "доходов"
    operation_type = data["type"]

    keyboard = await create_list_incomes_expenses(
        result,
        type_operation,
        operation_type,
        prev_action,
        next_action
    )

    text = "Вот что я нашел!" if result.get(
        "results") else "Записей не найдено. 😔"
    return text, keyboard, operation_type


async def _handle_response(
        context: Message | CallbackQuery,
        state: FSMContext,
        text: str,
        keyboard: InlineKeyboardMarkup,
        operation_type: str
) -> None:
    state_class = ExpensesState if operation_type == "sh_expenses" \
        else IncomesState
    await state.set_state(state_class.show)

    if isinstance(context, CallbackQuery):
        await context.message.edit_text(
            text=hbold(text),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await context.answer(
            text=hbold(text),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
