"""A module with a decorator for error handling and logging."""
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
from typing import TypeVar, ParamSpec, Callable
from http.client import HTTPException

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from config import BOT_TOKEN
from keyboards.keyboards import main_menu
from loader import not_auth

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    filename="/finance_bot/logs/bot.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=10,
    encoding="utf-8",
)

handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

# Добавляем обработчик к логгеру
logger.addHandler(handler)

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
            # Логируем информацию о функции и её аргументах
            logger.info(
                f"Executing function: {func.__name__}\n"
                f"State: {await state.get_data()}\n"
                f"User ID: {arg.from_user.id}\n"
                f"User: {arg.from_user.full_name} \
                    (@{arg.from_user.username})\n\n"
            )
            await func(arg, state)

        except KeyError:
            logger.error(
                "KeyError occurred\n"
                f"Function: {func.__name__}\n"
                f"State: {await state.get_data()}\n"
                f"User ID: {arg.from_user.id}\n"
                f"User: {arg.from_user.full_name} \
                    (@{arg.from_user.username})\n",
                exc_info=True,
            )
            await state.clear()
            await bot.send_message(
                arg.from_user.id,
                hbold(not_auth),
                reply_markup=main_menu,
                parse_mode="HTML",
            )

        except HTTPException as err:
            logger.error(
                f"HTTPException occurred: {err}\n"
                f"Function: {func.__name__}\n"
                f"State: {await state.get_data()}\n"
                f"User ID: {arg.from_user.id}\n"
                f"User: {arg.from_user.full_name} \
                    (@{arg.from_user.username})\n",
                exc_info=True,
            )
            await state.clear()
            await bot.send_message(
                arg.from_user.id,
                text=hbold(str(err)),
                parse_mode="HTML",
                reply_markup=main_menu,
            )

        except (FileNotFoundError, PermissionError, ValueError) as err:
            logger.error(
                f"Exception occurred: {err}\n"
                f"Function: {func.__name__}\n"
                f"State: {await state.get_data()}\n"
                f"User ID: {arg.from_user.id}\n"
                f"User: {arg.from_user.full_name} \
                    (@{arg.from_user.username})\n",
                exc_info=True,
            )
            await state.clear()
            await bot.send_message(
                arg.from_user.id,
                text=hbold(str(err)),
            )
    return wrapper
