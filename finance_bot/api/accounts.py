from http.client import HTTPException

from api.client import Client
from api.common import create_client
from config import accounts_url


async def change_toggle_active(account_id: int, user_id: int, is_active: bool) -> None:
    """
    Request to change account status.
    :param account_id:
    :param user_id:
    :param is_active:
    :return:
    """
    url: str = accounts_url + f"{account_id}/toggle-active/"
    client: Client = await create_client(user_id, url, {"is_active": is_active})
    status_code, response = await client.patch()
    if status_code != 200:
        raise HTTPException(response.get("detail"))
