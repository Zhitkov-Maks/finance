import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold

from api.auth import request_for_reset_password
from config import reset_password_url, reset_password_confirm_url
from keyboards.keyboards import cancel_, main_menu
from loader import enter_email, reset_password_confirm, success_reset
from states.reset import ResetPassword
from utils.common import remove_message_after_delay
from utils.register import is_valid_email, is_valid_password

reset_router: Router = Router()


@reset_router.callback_query(F.data == "reset")
async def start_reset_password(callback: CallbackQuery, state: FSMContext) -> None:
    """Processing the password reset command, requests an email."""
    await state.set_state(ResetPassword.email)
    await callback.message.edit_text(
        text=hbold("Введите ваш email: "),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@reset_router.message(F.text == "/reset")
async def start_reset_password(message: Message, state: FSMContext) -> None:
    """Processing the password reset command, requests an email."""
    await state.set_state(ResetPassword.email)
    await message.answer(
        text=hbold("Введите ваш email: "),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@reset_router.message(ResetPassword.email)
async def processing_email(message: Message, state: FSMContext) -> None:
    """
    The handler sends a request to the server
    to reset the password. In response, the user
    should receive email message with the uid and token,
    which we request in this handler.
    """
    valid: bool = is_valid_email(message.text)

    if not valid:
        await state.update_data(email=message.text)

        text: str = hbold("Ваш email не соответствует требованиям! ")
        await message.answer(
            text=text + enter_email, parse_mode="HTML", reply_markup=cancel_
        )
        return

    result: str | None = await request_for_reset_password(
        reset_password_url, {"email": message.text}
    )
    if result is None:
        await state.set_state(ResetPassword.token)
        await message.answer(
            text=hbold(reset_password_confirm),
            reply_markup=cancel_,
            parse_mode="HTML"
        )
    else:
        await message.answer(
            text=result,
            reply_markup=main_menu,
        )


@reset_router.message(ResetPassword.token)
async def confirm_reset_password(message: Message, state: FSMContext) -> None:
    """
    The handler checks the correctness of the input and
    saves the id and token, and asks the user
    for a new password.
    """
    data: list[str] = message.text.split()
    if len(data) != 2:
        await message.answer(
            text=hbold("Неверный формат ввода попробуйте еще раз."),
            reply_markup=cancel_,
            parse_mode="HTML"
        )
        return

    await state.update_data(uid=data[0], token=data[1])
    await state.set_state(ResetPassword.password)
    await message.answer(
        text=hbold("Введите новый пароль."),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@reset_router.message(ResetPassword.password)
async def final_reset_password(message: Message, state: FSMContext) -> None:
    """The handler sends a request to save a new password."""
    valid: bool = is_valid_password(message.text)
    asyncio.create_task(remove_message_after_delay(60, message))
    data: dict[str, str] = await state.get_data()
    if valid:
        uid, token = data["uid"], data["token"]

        result: str | None = await request_for_reset_password(
            reset_password_confirm_url,
            {"uid": uid, "token": token, "new_password": message.text}
        )

        if result is None:
            await message.answer(
                success_reset, reply_markup=main_menu, parse_mode="HTML"
            )
        else:
            await message.answer(
                text="Что-то пошло не так, попробуйте еще раз.",
                reply_markup=main_menu,
            )
        await state.clear()
    else:
        await message.answer(
            text=hbold("Введите новый пароль."), parse_mode="HTML", reply_markup=cancel_
        )
