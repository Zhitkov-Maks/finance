from functools import wraps
from typing import TypeVar, ParamSpec, Callable
from http.client import HTTPException

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from config import BOT_TOKEN
from keyboards.keyboards import main_menu
from loader import not_auth

bot = Bot(token=BOT_TOKEN)


T = TypeVar("T")
P = ParamSpec("P")


def decorator_errors(func: Callable[P, T]) -> Callable[P, T]:
    """
    A decorator for the callback and message processing function.
    """

    @wraps(func)
    async def wrapper(arg: P, state: FSMContext) -> None:
        """
        Wrapper for error handling when executing a function
        """
        try:
            await func(arg, state)

        except KeyError:
            await state.clear()
            await bot.send_message(
                arg.from_user.id,
                hbold(not_auth),
                reply_markup=main_menu,
                parse_mode="HTML",
            )

        except HTTPException as err:
            await state.clear()
            await bot.send_message(
                arg.from_user.id,
                text=hbold(str(err)),
                parse_mode="HTML",
                reply_markup=main_menu,
            )
        except (FileNotFoundError, PermissionError, ValueError):
            await state.clear()
            await bot.send_message(
                arg.from_user.id,
                text=hbold(str(FileNotFoundError)),
            )
    return wrapper
