import asyncio
from typing import Dict, List

from aiogram.types import Message, InlineKeyboardButton

from config import token_data


date_pattern: str = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"


async def create_header(user_id: int) -> str:
    """
    Forming a header to send it in a request for
    user authentication on the backend side.
    :param user_id: ID user.
    :return str: Returns a token for working with requests.
    """
    try:
        token: Dict[str, str] = token_data[user_id]
        return f"Token {token.get("auth_token")}"
    except KeyError:
        raise KeyError("Вы не авторизованы!")


async def remove_message_after_delay(delay: int, message: Message | list[Message]):
    """
    Deleting important user data with a delay.

    :param delay: Delay by seconds.
    :param message: Message for removing.
    :return: None.
    """
    await asyncio.sleep(delay)
    if isinstance(message, Message):
        await message.delete()
    else:
        for mess in message:
            await mess.delete()


async def create_pagination_buttons(
    previous: bool,
    next_: bool,
    prev: str,
    next_d: str
) -> List[InlineKeyboardButton]:
    """
    A function for forming buttons for adding pagination.
    :param previous: Previous button.
    :param next_: Next button.
    :param prev: Name the previous button.
    :param next_d: Name the next button.
    """
    prev_data, text_prev = "None prev", "-"
    next_data, text_next = "None next", "-"

    if previous is not None:
        prev_data, text_prev = prev, "<<"

    if next_ is not None:
        next_data, text_next = next_d, ">>"

    return [
        InlineKeyboardButton(text=text_prev, callback_data=prev_data),
        InlineKeyboardButton(text="Меню", callback_data="main"),
        InlineKeyboardButton(text=text_next, callback_data=next_data),
    ]
