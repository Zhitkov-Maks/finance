from typing import Dict

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from api.auth import login_user
from config import BOT_TOKEN
from keyboards.keyboards import main_menu, cancel_
from keyboards.reset import generate_inline_keyboard_reset
from loader import enter_email, password, success_auth
from states.login import LoginState
from utils.register import is_valid_email, is_valid_password, create_data

auth = Router()
bot = Bot(token=BOT_TOKEN)


@auth.message(F.text == "/login")
async def input_email(message: Message, state: FSMContext) -> None:
    """The handler for the email request."""
    await state.set_state(LoginState.email)
    await message.answer(text=enter_email, parse_mode="HTML", reply_markup=cancel_)


@auth.message(LoginState.email)
async def input_password(mess: Message, state: FSMContext) -> None:
    """The handler for the password request."""
    valid: bool = is_valid_email(mess.text)

    if valid:
        await state.update_data(email=mess.text)
        await state.set_state(LoginState.password)
        await mess.answer(
            text=password, parse_mode="HTML", reply_markup=cancel_
        )

    else:
        text: str = "Ваш email не соответствует требованиям! "
        await mess.answer(
            text=text + enter_email, parse_mode="HTML", reply_markup=cancel_
        )


@auth.message(LoginState.password)
async def final_authentication(message: Message, state: FSMContext) -> None:
    """The handler authenticates the user."""
    valid: bool = is_valid_password(message.text)

    if valid:
        email: str = (await state.get_data())["email"]
        data: Dict[str, str] = await create_data(email, message.text)
        result: str | None = await login_user(data, message.from_user.id)
        if result is None:
            await message.answer(success_auth, reply_markup=main_menu, parse_mode="HTML")
        else:
            await message.answer(
                result, reply_markup=await generate_inline_keyboard_reset()
            )
        await state.clear()

    else:
        text: str = "Ваш пароль не соответствует требованиям! "
        await message.answer(
            text=text + password, parse_mode="HTML", reply_markup=cancel_
        )
