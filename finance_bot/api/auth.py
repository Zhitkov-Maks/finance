from typing import Dict

from api.client import Client
from config import register_url, login_url
from utils.login import update_token


async def request_for_reset_password(
        url: str, data: dict[str, str]
) -> int | None:
    """
    Reset the password.

    :param url: URL for request.
    :param data: Dictionary with user data.
    :return: Int if the request failed, None if everything was successful.
    """
    client: Client = Client(url, data)
    status_code, _ = await client.post()
    if status_code != 204:
        return status_code


async def registration(data: Dict[str, str]) -> str | None:
    """
    Register the user.

    :param data: Dictionary with user data.
    :return: Str if the request failed, None if everything was successful.
    """
    client: Client = Client(register_url, data)
    status_code, response = await client.post()
    if status_code != 201:
        return str(response)


async def login_user(data: Dict[str, str], user_id: int) -> str | None:
    """
    Get a token for authentication.

    :param data: Dictionary with user data.
    :param user_id: ID user.
    :return: Str, if the request was not completed,
        if everything was successful, then save the token and return None.
    """
    client: Client = Client(url=login_url, data=data)
    status_code, response = await client.post()
    if status_code != 200:
        return str(response)
    else:
        await update_token(response, user_id)
