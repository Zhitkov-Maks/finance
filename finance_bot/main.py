import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold
from config import BOT_TOKEN
from handlers.accounts import account, create_acc_route, edit_acc_router
from handlers.category import category_route
from handlers.debts import debt_router
from handlers.decorator_handler import decorator_errors
from handlers.expenses import (
    create_exp_router,
    exp_edit_router,
    expense_router,
)
from handlers.incomes import create_inc_router, incomes
from handlers.incomes.edit_income import inc_edit_router
from handlers.invalid_handlers import invalid_router
from handlers.login import auth
from handlers.registration import register_route
from handlers.reset_password import reset_router
from handlers.search import search
from handlers.statistic import statistic_route
from handlers.transfer import transfer
from keyboards.keyboards import main_menu
from loader import greeting, main_menu_text, info_message

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

routes: list[Router] = [
    register_route,
    auth,
    account,
    edit_acc_router,
    transfer,
    incomes,
    create_inc_router,
    inc_edit_router,
    exp_edit_router,
    create_exp_router,
    expense_router,
    category_route,
    create_acc_route,
    statistic_route,
    reset_router,
    debt_router,
    search,
    invalid_router,
]

for route in routes:
    dp.include_router(route)


@dp.message(F.text == "/info")
async def info(message: Message):
    """
    The handler shows a message to the user about the basics of working
    with the bot.
    """
    await message.answer(
        text=info_message,
        reply_markup=main_menu
    )


@dp.message(CommandStart())
@decorator_errors
async def greeting_handler(message: Message, state: FSMContext) -> None:
    """Welcome Handler."""
    await message.answer(text=greeting, reply_markup=main_menu)


@dp.callback_query(F.data == "main")
@decorator_errors
async def handler_main_callback(call: CallbackQuery, state: FSMContext) -> None:
    """Show base bot's menu."""
    await state.clear()
    await call.message.edit_text(
        text=hbold(main_menu_text), reply_markup=main_menu, parse_mode="HTML"
    )


@dp.message(F.text == "/main")
@decorator_errors
async def handler_main_message(message: Message, state: FSMContext) -> None:
    """Show base bot's menu."""
    await state.clear()
    await message.answer(
        text=hbold(main_menu_text), reply_markup=main_menu, parse_mode="HTML"
    )


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
