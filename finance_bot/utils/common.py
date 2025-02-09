import asyncio
from typing import Dict

from aiogram.types import Message

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


async def remove_message_after_delay(delay: int, message: Message):
    """
    Deleting important user data with a delay.

    :param delay: Delay by seconds.
    :param message: Message for removing.
    :return: None.
    """
    await asyncio.sleep(delay)
    await message.delete()
