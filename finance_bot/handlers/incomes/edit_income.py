from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold

from api.common import edit_object, get_full_info
from handlers.decorator_handler import decorator_errors
from keyboards.incomes import choice_edit, get_action
from keyboards.keyboards import cancel_
from states.incomes import EditIncomesState, IncomesState
from utils.accounts import is_valid_balance
from utils.incomes import (
    incomes_by_id,
    generate_message_income_info,
    create_new_incomes_data
)

inc_edit_router: Router = Router()


@inc_edit_router.callback_query(F.data == "edit_income")
async def edit_income_choice(callback: CallbackQuery) -> None:
    """A handler for selecting an income editing option."""
    text = "Выберите вариант редактирования."
    await callback.message.edit_text(
        text=hbold(text),
        reply_markup=choice_edit,
        parse_mode="HTML"
    )


@inc_edit_router.callback_query(F.data == "edit_income_balance")
async def edit_balance(callback: CallbackQuery, state: FSMContext) -> None:
    """
    The handler for requesting the amount of income when editing only
    the balance.
    """
    await state.set_state(EditIncomesState.comment)
    await state.update_data(method="PATCH")
    await callback.message.edit_text(
        text=hbold("Введите новую сумму дохода."),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@inc_edit_router.message(EditIncomesState.amount)
async def ask_add_comment(message: Message, state: FSMContext) -> None:
    if not is_valid_balance(message.text):
        await message.answer(
            hbold("Ошибка ввода, необходимо ввести число."),
            reply_markup=cancel_
        )
        return

    await state.update_data(amount=message.text)
    await state.set_state(EditIncomesState.comment)
    await message.answer(
        text=hbold("Введите комментарий. Если комментарий не нужен, "
                   "то, отправьте один любой символ."),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@inc_edit_router.message(EditIncomesState.comment)
@decorator_errors
async def edit_income_request(message: Message, state: FSMContext) -> None:
    """The final handler for editing."""
    data: dict[str, str | int] = await state.get_data()
    income_id, usr_id = data["income_id"], message.from_user.id
    url: str = await incomes_by_id(income_id)
    method: str = ""

    if data.get("method"):
        method = data.pop("method")
        if not is_valid_balance(message.text):
            await message.answer(
                "Invalid balance format. Please enter a valid number.",
                reply_markup=cancel_
            )
            return
        edit_data: dict = {"amount": float(message.text)}

    else:
        comment: str = message.text
        if comment in ["no comment", "no", "нет"] or len(comment) < 3:
            comment = ""
        edit_data: dict = await create_new_incomes_data(
            data, comment
    )

    await edit_object(url, usr_id, edit_data, method)
    response: dict = await get_full_info(url, usr_id)
    text: str = await generate_message_income_info(response)

    await state.set_state(IncomesState.action)
    await message.answer(
        text=hbold(text),
        parse_mode="HTML",
        reply_markup=await get_action(),
    )
