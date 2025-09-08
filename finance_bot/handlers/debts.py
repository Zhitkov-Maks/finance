import re
from datetime import datetime as dt

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext

from config import (
    debts_url,
    PAGE_SIZE,
    debts_url_by_id,
    debts_repay_url,
    debt_create_url
)
from handlers.decorator_handler import decorator_errors
from keyboards.accounts import create_list_account
from keyboards.create_calendar import create_calendar
from keyboards.debts import (
    debts_markup,
    debts_keyboard_generate,
    generate_debts_actions
)
from api.common import get_all_objects, get_full_info, create_new_object
from keyboards.keyboards import main_menu, cancel_
from states.debts import DebtsStates
from utils.accounts import is_valid_balance, account_url
from utils.common import date_pattern
from utils.create_calendar import get_date
from utils.debts import generate_debts_message, create_debt_data_for_request

debt_router: Router = Router()


@debt_router.callback_query(F.data == "debt_and_lends")
@decorator_errors
async def debts_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """The handler shows a menu with possible actions."""
    await callback.message.edit_text(
        text=hbold("Выберите действие."),
        reply_markup=debts_markup,
        parse_mode="HTML"
    )


@debt_router.callback_query(F.data.in_(["show_debts", "show_lends"]))
@decorator_errors
async def debts_list(callback: CallbackQuery, state: FSMContext) -> None:
    """A handler for displaying a list of debts or debtors."""
    page: int = (await state.get_data()).get("page", 1)
    type_: str = "lend"
    text: str = "Список ваших должников"

    if callback.data == "show_debts":
        type_ = "debt"
        text = "Вот список ваших долгов."

    debt_url: str = debts_url.format(
        type=type_, page=page, page_size=PAGE_SIZE
    )
    await state.update_data(page=page, type_=type_, text=text)

    result: dict = await get_all_objects(debt_url, callback.from_user.id)
    if len(result.get("results")) == 0:
        text = "Записей не найдено. 🤷"

    await state.set_state(DebtsStates.detail)
    await callback.message.edit_text(
        text=hbold(text),
        reply_markup=await debts_keyboard_generate(result),
        parse_mode="HTML"
    )


@debt_router.callback_query(F.data.in_(["prev_debt", "next_debt"]))
@decorator_errors
async def next_prev_output_list_debts(
    call: CallbackQuery,
    state: FSMContext
) -> None:
    """Show the following debt page."""
    data: dict = await state.get_data()
    page, type_, text = data.get("page", 1), data.get("type_"), \
        data.get("text")

    if call.data == "next_debt":
        page += 1
    else:
        page -= 1

    url: str = debts_url.format(type=type_, page=page, page_size=PAGE_SIZE)
    await state.update_data(page=page, type_=type_)
    result: dict = await get_all_objects(url, call.from_user.id)

    await state.set_state(DebtsStates.detail)
    await call.message.edit_text(
        text=hbold(text),
        reply_markup=await debts_keyboard_generate(result),
        parse_mode="HTML"
    )
    

@debt_router.callback_query(DebtsStates.detail, F.data.isdigit())
@decorator_errors
async def detail_debt_by_id(call: CallbackQuery, state: FSMContext) -> None:
    """A handler for displaying complete information about the debt."""
    type_ = (await state.get_data())["type_"]
    url: str = debts_url_by_id.format(debt_id=call.data)
    result: dict = await get_full_info(url, call.from_user.id)
    amount: str = result.get("transfer").get("amount")

    await state.update_data(amount=amount, id_=call.data, result=result)
    await call.message.edit_text(
        text=hbold(await generate_debts_message(result)),
        parse_mode="HTML",
        reply_markup=await generate_debts_actions(type_)
    )


@debt_router.callback_query(F.data == "current_debt")
async def current_debts_lends(
        call: CallbackQuery, state: FSMContext
    ) -> None:
    """
    A handler for displaying the latest information 
    about a specific debt.
    """
    data = await state.get_data()
    type_ = data.get("type_")
    result = data.get("result")
    await call.message.edit_text(
        text=hbold(await generate_debts_message(result)),
        parse_mode="HTML",
        reply_markup=await generate_debts_actions(type_)
    )


@debt_router.callback_query(F.data == "close_debt")
@decorator_errors
async def close_debt_or_lend(call: CallbackQuery, state: FSMContext) -> None:
    """Debt repayment handler."""
    url: str = debts_repay_url
    data: dict = await state.get_data()
    data_for_request: dict = {
        "debt_id": data.get("id_"),
        "amount": data.get("amount"),
        "type": data.get("type_"),
    }
    await create_new_object(call.from_user.id, url, data_for_request)
    await call.message.edit_text(
        text=hbold(f"Вы погасили долг в размере {data.get("amount")}₽"),
        reply_markup=main_menu,
        parse_mode="HTML"
    )


@debt_router.callback_query(F.data == "repay_part")
@decorator_errors
async def repay_part_debt(call: CallbackQuery, state: FSMContext) -> None:
    """A handler for confirming partial repayment."""
    await state.set_state(DebtsStates.confirm)
    type_ = (await state.get_data())["type_"]
    action = "show_debts" if type_ == "debt" else "show_lends"
    text = "долгов." if type_ == "debt" else "должников." 
    await call.message.edit_text(
        text=hbold("Введите сумму для погашения."),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙",
                    callback_data="current_debt"
            ),
                InlineKeyboardButton(
                    text="㊂",
                    callback_data="main"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"К списку {text}",
                    callback_data=action
                )
            ]
        ]),
        parse_mode="HTML"
    )


@debt_router.message(DebtsStates.confirm)
@decorator_errors
async def confirm_repay(message: Message, state: FSMContext) -> None:
    """Confirmation of partial repayment of the debt."""
    if not is_valid_balance(message.text):
        await message.answer(
            "Invalid balance format. Please enter a valid number.",
            reply_markup=cancel_
        )
        return
    amount = message.text
    await state.update_data(amount=amount)
    await message.answer(
        text=hbold(f"Внести погашение долга в размере {amount}"),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Погасить",
                    callback_data="close_debt"
                ),
                InlineKeyboardButton(
                    text="Отмена",
                    callback_data="main"
                )
            ]
        ])
    )


@debt_router.callback_query(F.data.in_(["to_lend", "to_borrow"]))
@decorator_errors
async def to_lend_or_borrow(call: CallbackQuery, state: FSMContext) -> None:
    """The handler will request a date to start creating the debt."""
    type_: str = "debt"
    if call.data == "to_lend":
        type_ = "lend"
    await state.set_state(DebtsStates.date)

    year, month = dt.now().year, dt.now().month
    keypad: InlineKeyboardMarkup = await create_calendar(
        year, month, "prev_cal_debt", "next_cal_debt"
    )
    await state.update_data(type=type_, year=year, month=month)
    await call.message.edit_text(
        text=hbold("Выберите дату дачи в долг."),
        reply_markup=keypad,
        parse_mode="HTML"
    )


@debt_router.callback_query(
    F.data.in_(["next_cal_debt", "prev_cal_debt"])
)
@decorator_errors
async def next_and_prev_month_for_debt(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """A handler for flipping through the calendar."""
    data: dict = await state.get_data()
    action: str = "prev" if callback.data == "prev_cal_debt" else "next"
    year, month = await get_date(data, action)

    await state.update_data(year=year, month=month)
    await state.set_state(DebtsStates.date)
    await callback.message.edit_reply_markup(
        reply_markup=await create_calendar(
            year, month, "prev_cal_exp", "next_cal_exp"
        )
    )


@debt_router.callback_query(
    DebtsStates.date,
    lambda callback_query: re.match(date_pattern, callback_query.data),
)
@decorator_errors
async def select_account_to_debit(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """The handler for selecting an account for debiting money."""
    page: int = 1
    url: str = await account_url(page, PAGE_SIZE)

    result: dict = await get_all_objects(url, callback.from_user.id)

    await state.update_data(page=page, date=callback.data)
    keyword: InlineKeyboardMarkup = await create_list_account(
        result, "prev_debt_acc", "next_debt_acc"
    )

    await state.set_state(DebtsStates.account)
    await callback.message.edit_text(
        text=hbold("Выберите счет: "),
        reply_markup=keyword,
        parse_mode="HTML"
    )


@debt_router.callback_query(F.data.in_(["next_debt_acc", "prev_debt_acc"]))
@decorator_errors
async def next_or_prev_account_to_debt(
    call: CallbackQuery,
    state: FSMContext
) -> None:
    """Scrolling through the invoice pages."""
    page: int = (await state.get_data()).get("page")

    if call.data == "next_debt_acc":
        page += 1
    else:
        page -= 1

    url: str = await account_url(page, PAGE_SIZE)
    result: dict = await get_all_objects(url, call.from_user.id)
    keyword: InlineKeyboardMarkup = await create_list_account(
        result, "prev_debt_acc", "next_debt_acc"
    )

    await state.set_state(DebtsStates.account)
    await state.update_data(page=page)
    await call.message.edit_reply_markup(reply_markup=keyword)


@debt_router.callback_query(
    DebtsStates.account, F.data.split("_")[0].isdigit()
)
@decorator_errors
async def save_account_input_amount(
    call: CallbackQuery,
    state: FSMContext
) -> None:
    """A handler for saving the account ID and requesting the loan amount."""
    await state.update_data(account_id=call.data.split("_")[0])
    await state.set_state(DebtsStates.description)
    await call.message.edit_text(
        text=hbold("Введите сумму заема."),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@debt_router.message(DebtsStates.description)
@decorator_errors
async def save_amount_and_input_description(
    message: Message,
    state: FSMContext
) -> None:
    """
    A handler for saving the loan amount and
    requesting a description of the debt.
    """
    if not is_valid_balance(message.text):
        await message.answer(
            "Invalid balance format. Please enter a valid number.",
            reply_markup=cancel_
        )
        return

    await state.update_data(amount=message.text)
    await state.set_state(DebtsStates.save)
    await message.answer(
        text=hbold("Введите короткое описание долга, Имя должника например."),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@debt_router.message(DebtsStates.save)
@decorator_errors
async def save_debt_or_lend(message: Message, state: FSMContext) -> None:
    """The handler saves the previously entered data to save the debt."""
    await state.update_data(description=message.text)
    data: dict = await state.get_data()
    data_for_request = await create_debt_data_for_request(data)
    await create_new_object(
        message.from_user.id,
        debt_create_url,
        data_for_request
    )

    if data["type"] == "debt":
        text = f"Вы взяли взаймы {data["amount"]}₽. "
    else:
        text = f"Вы дали {data["amount"]}₽. \n"
    text += "Подробности можно посмотреть в разделе с долгами."
    await message.answer(
        text=hbold(text),
        reply_markup=main_menu,
        parse_mode="HTML"
    )
