from typing import Dict

from api.client import Client
from config import register_url, login_url
from utils.login import update_token


async def request_for_reset_password(
        url: str, data: dict[str, str]
) -> int | None:
    """
    Request for user reset password.
    :param url: URL for request.
    :param data: Dictionary with user data.
    """
    client = Client(url, data)
    status_code, result = await client.post()
    if status_code != 204:
        return status_code


async def registration(data: Dict[str, str]) -> str | None:
    """
    Request for user registration.
    :param data: Dictionary with user data.
    """
    client: Client = Client(register_url, data)
    status_code, response = await client.post()
    if status_code != 201:
        return str(response)


async def login_user(data: Dict[str, str], user_id: int) -> str | None:
    """
    The function sends a request for authentication, in case of a
    successful request, we must return a token, which we will
    substitute in all requests in the future.
    :param data: Dictionary with user data.
    :param user_id: ID user.
    """
    client: Client = Client(url=login_url, data=data)
    status_code, response = await client.post()
    if status_code != 200:
        return str(response)
    else:
        await update_token(response, user_id)
