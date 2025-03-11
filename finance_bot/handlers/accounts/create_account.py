from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold

from api.common import create_new_object
from config import accounts_url
from handlers.decorator_handler import decorator_errors
from keyboards.keyboards import cancel_, main_menu
from states.accounts import AccountsCreateState
from utils.accounts import is_valid_balance

create_acc_route: Router = Router()


@create_acc_route.callback_query(F.data == "accounts_add")
@decorator_errors
async def account_input_name(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """Handler for entering the name of the new account."""
    await state.set_state(AccountsCreateState.name)
    await callback.message.edit_text(
        text=hbold("Введите название счета."),
        reply_markup=cancel_,
        parse_mode="HTML",
    )


@create_acc_route.message(AccountsCreateState.name)
@decorator_errors
async def save_name_input_balance(message: Message, state: FSMContext) -> None:
    """
    The handler saves the account name and asks you to enter
    the account balance.
    """
    await state.set_state(AccountsCreateState.balance)
    await state.update_data(name=message.text)
    await message.answer(
        text=hbold("Введите баланс счета: "),
        reply_markup=cancel_,
        parse_mode="HTML",
    )


@create_acc_route.message(AccountsCreateState.balance)
@decorator_errors
async def create_account(message: Message, state: FSMContext) -> None:
    """The handler sends a request to create a new account."""
    data: dict[str, str | int] = await state.get_data()
    usr_id: int = message.from_user.id
    if not is_valid_balance(message.text):
        await message.answer(
            "Invalid balance format. Please enter a valid number.",
            reply_markup=cancel_
        )
        return

    await create_new_object(
        usr_id, accounts_url,
        {"name": data["name"], "balance": message.text}
    )

    answer_message: str = (f"Счет <{data["name"]}>, "
                           f"баланс: {float(message.text):,}₽ создан.")
    await state.clear()
    await message.answer(
        text=hbold(answer_message), parse_mode="HTML", reply_markup=main_menu
    )
