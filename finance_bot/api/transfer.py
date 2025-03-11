from datetime import datetime as dt
from http.client import HTTPException

from api.accounts import create_client
from api.client import Client
from config import BASE_URL


async def create_transfer(
    account_in: int,
    account_out: int,
    user_id: int,
    amount: float
) -> None:
    """
    The function sends a request to create a transfer between its accounts.
    :param account_in: Which account to transfer from.
    :param account_out: Which account to transfer to.
    :param user_id: The user's ID.
    :param amoount: The transfer amount.
    """
    url: str = BASE_URL + "transfer/"
    transfer_data: dict[str, int | float | str] = {
        "source_account": account_in,
        "destination_account": account_out,
        "amount": amount,
        "timestamp": str(dt.now()),
    }
    client: Client = await create_client(user_id, url, data=transfer_data)
    status_code, response = await client.post()

    if status_code != 201:
        raise HTTPException(response.get("detail"))
