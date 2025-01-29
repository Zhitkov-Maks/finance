import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import BOT_TOKEN
from handlers.login import auth
from handlers.registration import register_route
from handlers.accounts import account, edit
from handlers.transfer import transfer
from keyboards.keyboards import main_menu
from loader import greeting

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(register_route)
dp.include_router(auth)
dp.include_router(account)
dp.include_router(edit)
dp.include_router(transfer)


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


async def main():
    """
    The function launches the bot and also launches the notification
    scheduler to launch notifications for users who have
    there are notification settings.
    """
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Main program interrupted.")
