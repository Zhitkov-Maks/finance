from http.client import HTTPException

from api.client import Client
from utils.common import create_header


async def create_client(user_id: int, url: str, data=None) -> Client:
    """A function for configuring the client."""
    client: Client = Client(url=url, data=data)
    client.header.update(Authorization=await create_header(user_id))
    return client


async def create_new_object(user_id, url: str, data: dict) -> dict:
    client: Client = await create_client(user_id, url, data)
    status_code, response = await client.post()
    if status_code != 201:
        raise HTTPException(response.get("detail"))
    return response


async def get_all_objects(url: str, user_id: int) -> dict:
    """
    Making a request to receive user accounts
    :param url: Url.
    :param user_id: ID user.
    :return str: If the request was not successful, then we return an
                    error string.
    """
    client: Client = await create_client(user_id, url)
    status_code, response = await client.get()

    if status_code == 200:
        return response
    else:
        raise HTTPException(response.get("detail"))


async def get_full_info(
    url: str, user_id: int
) -> dict[str, list[dict[str, int]] | dict[str, str] | float | bool]:
    """
    Request for detailed account information.
    :param url: URL.
    :param user_id: ID user.
    :return dict: Detailed information about the account.
    """
    client: Client = await create_client(user_id, url)
    status_code, response = await client.get()

    if status_code == 200:
        return response
    else:
        raise HTTPException(response.get("detail"))


async def delete_object_by_id(url: str, user_id: int) -> None:
    """
    Request to delete an account.
    :param url: URL.
    :param user_id: ID user.
    """
    client: Client = await create_client(user_id, url)
    status_code, response = await client.delete()
    if status_code != 204:
        raise HTTPException(response.get("detail"))


async def edit_object(url: str, user_id: int, data: dict, method: str) -> dict:
    """
    Request for account change.
    :param method:
    :param data: Dictionary with data for editing.
    :param url: URL.
    :param user_id: ID user.
    """
    client: Client = await create_client(user_id, url, data)
    if method == "PATCH":
        status_code, response = await client.patch()
    else:
        status_code, response = await client.put()

    if status_code != 200:
        raise HTTPException(response.get("detail"))

    return response
