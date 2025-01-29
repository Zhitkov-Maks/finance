from http.client import HTTPException

from api.client import Client
from config import accounts_url
from utils.common import create_header


async def create_client(user_id: int, url: str, data=None) -> Client:
    """A function for configuring the client."""
    client: Client = Client(url=url, data=data)
    client.header.update(Authorization=await create_header(user_id))
    return client


async def get_all_accounts(user_id: int, page=1, page_size=10) -> dict:
    """
    Making a request to receive user accounts
    :param page_size: Page size.
    :param page: Number of the page to request.
    :param user_id: ID user.
    :return str: If the request was not successful, then we return an
                    error string.
    """
    url: str = accounts_url + f"?page={page}&page_size={page_size}"
    client: Client = await create_client(user_id, url)
    status_code, response = await client.get()

    if status_code == 200:
        return response
    else:
        raise HTTPException(response.get("detail"))


async def get_full_info(
    account_id: int, user_id: int
) -> dict[str, list[dict[str, int]] | dict[str, str] | float | bool]:
    """
    Request for detailed account information.
    :param account_id: ID account.
    :param user_id: ID user.
    :return dict: Detailed information about the account.
    """
    url: str = accounts_url + f"{account_id}/"
    client: Client = await create_client(user_id, url)
    status_code, response = await client.get()

    if status_code == 200:
        return response
    else:
        raise HTTPException(response.get("detail"))


async def delete_account_by_id(account_id: int, user_id: int) -> None:
    """
    Request to delete an account.
    :param account_id: ID account.
    :param user_id: ID user.
    """
    url: str = accounts_url + f"{account_id}/"
    client: Client = await create_client(user_id, url)
    status_code, response = await client.delete()
    if status_code != 204:
        raise HTTPException(response.get("detail"))


async def edit_account(account_id: int, user_id: int, data: dict) -> None:
    """
    Request for account change.
    :param data: Dictionary with data for editing.
    :param account_id: ID account.
    :param user_id: ID user.
    """
    url: str = accounts_url + f"{account_id}/"
    client: Client = await create_client(user_id, url, data)
    if data["name"] is None:
        status_code, response = await client.patch()
    else:
        status_code, response = await client.put()

    if status_code != 200:
        raise HTTPException(response.get("detail"))


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
