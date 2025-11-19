from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold

from api.common import get_full_info
from keyboards.keyboards import create_list_incomes_expenses
from states.transaction import TransactionState
from utils.search import generate_url


async def generate_results(
    state: FSMContext,
    user_id: int,
    page: int,
    prev_action: str = "prev_search",
    next_action: str = "next_search"
) -> tuple:
    """
    The function processes the previously entered data, makes a request 
    to the server, and processes the incoming data.

    :param state: FSMContext.
    :param user_id: The user's ID.
    :param page: The page for pagination.
    :param prev_action: The command for the previous page button to work.
    :param next_action: The command for the next page button to work.
    :return tuple: A tuple of a message, a keyboard, and the type of operation.
    """
    data: dict = await state.get_data()
    url: str = await generate_url(data, page)
    result: dict = await get_full_info(url, user_id)

    operation_type: str = data["type"]
    call_data = "sh_expenses" if "exp" in operation_type else "sh_incomes"
    keyboard: InlineKeyboardMarkup = await create_list_incomes_expenses(
        data=result,
        call_data=call_data,
        type_transaction=operation_type,
        prev=prev_action,
        next_d=next_action
    )

    text = "Вот что я нашел!" if result.get(
        "results"
    ) else "Записей не найдено. 😔"
    return text, keyboard, operation_type


async def handle_response(
        context: Message | CallbackQuery,
        state: FSMContext,
        text: str,
        keyboard: InlineKeyboardMarkup
) -> None:
    """
    A function for responding to the user, since the same actions 
    were repeated many times.

    :param context: Type of response processing.
    :param state: FSMContext.
    :param text: Message for user.
    :param keyboard: Inline keyboard.
    """
    await state.set_state(TransactionState.show)

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
