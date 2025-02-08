import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import BOT_TOKEN
from handlers.category import category_route
from handlers.expenses import exp_edit_router, create_exp_router, expense_router
from handlers.incomes import incomes, create_inc_router
from handlers.incomes.edit_income import inc_edit_router
from handlers.invalid_handlers import invalid_router
from handlers.login import auth
from handlers.registration import register_route
from handlers.accounts import account, edit_acc_router, create_acc_route
from handlers.transfer import transfer
from keyboards.keyboards import main_menu
from loader import greeting
from handlers.statistic import statistic_route

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
dp.include_router(statistic_route)
dp.include_router(invalid_router)


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
