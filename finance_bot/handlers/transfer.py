from typing import Dict, List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.markdown import hbold

from api.common import get_all_objects
from api.transfer import create_transfer
from config import PAGE_SIZE, transfer_history_url
from handlers.decorator_handler import decorator_errors
from keyboards.keyboards import cancel_, main_menu
from keyboards.transfer import create_list_transfer_accounts, generate_keyboard
from states.accounts import TransferStates
from utils.accounts import is_valid_balance, account_url
from utils.transfer import generate_message_answer

transfer: Router = Router()


@transfer.callback_query(F.data == "transfer")
@decorator_errors
async def start_transfer(callback: CallbackQuery, state: FSMContext) -> None:
    """
    The handler for selecting the account to transfer.
    """
    page: int = 1
    account_id: int = (await state.get_data()).get("account_id")
    url: str = await account_url(page, page_size=PAGE_SIZE)
    result: Dict[
        str, str | List[Dict[str, float | List[Dict[str, int | float | str]]]]
    ] = await get_all_objects(url, callback.from_user.id)

    await state.update_data(page=page)
    keyword: InlineKeyboardMarkup = await create_list_transfer_accounts(
        result, int(account_id), transfer=True
    )
    await state.set_state(TransferStates.action)
    await callback.message.edit_text(
        text=hbold("Выберите счет куда перевести 💵"),
        reply_markup=keyword,
        parse_mode="HTML"
    )


@transfer.callback_query(F.data.in_(["next_tr", "prev_tr"]))
@decorator_errors
async def next_prev_output_list_habits(
        call: CallbackQuery, state: FSMContext
) -> None:
    """Show more invoices if any."""
    page: int = (await state.get_data()).get("page")
    account_id = (await state.get_data()).get("account_id")

    if call.data == "next_tr":
        page += 1
    else:
        page -= 1

    url: str = await account_url(page, page_size=PAGE_SIZE)

    result: dict = await get_all_objects(url, call.from_user.id)

    keyword: InlineKeyboardMarkup = await create_list_transfer_accounts(
        result, int(account_id), transfer=True
    )
    await state.update_data(page=page)
    await state.set_state(TransferStates.action)
    await call.message.edit_reply_markup(reply_markup=keyword)


@transfer.callback_query(TransferStates.action)
async def get_account_transfer_out(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """We save the account and request the balance."""
    await state.update_data(transfer_out=callback.data.split("_")[0])
    await state.update_data(account_out=callback.data.split("_")[1])
    await state.set_state(TransferStates.amount)
    await callback.message.edit_text(
        text=hbold("Введите сумму перевода 💰💰💰."),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@transfer.message(TransferStates.amount)
async def get_amount_transfer(message: Message, state: FSMContext) -> None:
    """We are sending the data for the transfer."""
    data: dict = await state.get_data()
    transfer_in, transfer_out = data.get("account_id"), \
        data.get("transfer_out")
    usr_id: int = message.from_user.id
    amount: str = message.text
    name, name_out = data.get("account"), data.get("account_out")

    if not is_valid_balance(message.text):
        await message.answer(
            "Invalid balance format. Please enter a valid number.",
            reply_markup=cancel_
        )
        return

    await create_transfer(
        transfer_in, transfer_out, usr_id, float(message.text)
    )
    await state.clear()
    await message.answer(
        text=hbold(f"Перевод с {name} 👉🏻 {name_out} на сумму {amount}₽."),
        reply_markup=main_menu,
        parse_mode="HTML",
    )


@transfer.callback_query(F.data == "transfer_history")
async def get_transfer_history(
    callback: CallbackQuery, state: FSMContext
) -> None:
    url = transfer_history_url.format(page=1, page_size=PAGE_SIZE)
    result: dict = await get_all_objects(url, callback.from_user.id)
    await state.update_data(page=1)
    answer = await generate_message_answer(result)
    keyboard: InlineKeyboardMarkup = await generate_keyboard(
        bool(result.get("next")), bool(result.get("previous"))
    )
    await callback.message.answer(
        text=hbold(answer),
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@transfer.callback_query(
    F.data.in_(["next_page_transfer", "prev_page_transfer"])
)
async def get_page_transfer_history(
    callback: CallbackQuery, state: FSMContext
) -> None:
    page = (await state.get_data())["page"]
    if callback.data == "next_page_transfer":
        page += 1
    else:
        page -= 1

    url = transfer_history_url.format(page=page, page_size=PAGE_SIZE)
    result: dict = await get_all_objects(url, callback.from_user.id)
    await state.update_data(page=page)
    answer = await generate_message_answer(result)
    keyboard: InlineKeyboardMarkup = await generate_keyboard(
        bool(result.get("next")), bool(result.get("previous"))
    )
    await callback.message.edit_text(
        text=hbold(answer),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
