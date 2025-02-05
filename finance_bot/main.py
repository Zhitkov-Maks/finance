import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import BOT_TOKEN, statistic_url, accounts_url
from handlers.category import category_route
from handlers.expenses import exp_edit_router, create_exp_router, expense_router
from handlers.incomes import incomes, create_inc_router
from handlers.incomes.edit_income import inc_edit_router
from handlers.login import auth
from handlers.registration import register_route
from handlers.accounts import account, edit_acc_router, create_acc_route
from handlers.transfer import transfer
from keyboards.keyboards import main_menu
from loader import greeting, MONTH_DATA
from utils.statistic import get_statistic_current_month

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(register_route)
dp.include_router(auth)
dp.include_router(account)
dp.include_router(edit_acc_router)
dp.include_router(transfer)
dp.include_router(incomes)
dp.include_router(create_inc_router)
dp.include_router(inc_edit_router)
dp.include_router(exp_edit_router)
dp.include_router(create_exp_router)
dp.include_router(expense_router)
dp.include_router(category_route)
dp.include_router(create_acc_route)


@dp.message(CommandStart())
async def greeting_handler(message: Message) -> None:
    """Welcome Handler."""
    await message.answer(text=greeting, reply_markup=main_menu)


@dp.callback_query(F.data == "main")
async def handler_main(call: CallbackQuery, state: FSMContext) -> None:
    """Show base bot's menu."""
    await state.clear()
    await call.message.answer(text="Меню", reply_markup=main_menu)


@dp.message(F.text == "/main")
async def handler_main(message: Message, state: FSMContext) -> None:
    """Show base bot's menu."""
    await state.clear()
    await message.answer(text="Меню", reply_markup=main_menu)


@dp.callback_query(F.data.in_(["statistic_expenses", "statistic_incomes"]))
async def get_expenses_for_month(call: CallbackQuery) -> None:
    """A handler for displaying the amount of income or expense."""
    month: int = datetime.now().month
    year: int = datetime.now().year
    url: str = statistic_url[call.data].format(month=month, year=year)

    amount: float = await get_statistic_current_month(url, call.from_user.id)
    answer, sign = ("расходы", "-") if call.data == "statistic_expenses" else ("доходы", "+")
    await call.answer(text=f"{MONTH_DATA[month]}, {answer}: {sign}{amount}₽.", show_alert=True)


@dp.callback_query(F.data == "accounts_data")
async def get_expenses_for_month(call: CallbackQuery) -> None:
    """Handler for displaying the balance of all accounts."""
    url: str = accounts_url + "?page=1&page_size=1"
    amount: float = await get_statistic_current_month(
        url, call.from_user.id, True
    )
    answer: str = f"На ваших счетах {amount}₽"
    await call.answer(answer, show_alert=True)


@dp.callback_query(F.data == "expenses_by_incomes")
async def incomes_to_expenses(call: CallbackQuery) -> None:
    """
    A handler for showing the ratio of income to expenses.
    """
    month, year = datetime.now().month, datetime.now().year

    # Запускаем оба запроса одновременно
    amount_expenses, amount_incomes = await asyncio.gather(
        get_statistic_current_month(
            statistic_url["statistic_expenses"].format(month=month, year=year),
            call.from_user.id,
        ),
        get_statistic_current_month(
            statistic_url["statistic_incomes"].format(month=month, year=year),
            call.from_user.id,
        )
    )

    message: str = f"Доходы / Расходы  {round(amount_incomes - amount_expenses, 2)}₽"
    await call.answer(text=message, show_alert=True)


async def main() -> None:
    """
    The function launches the bot.
    """
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Main program interrupted.")
