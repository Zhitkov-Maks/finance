from datetime import datetime as dt
from http.client import HTTPException

from api.accounts import create_client
from api.client import Client
from config import accounts_url


async def create_transfer(
    account_in: int,
    account_out: int,
    user_id: int,
    amount: float
) -> None:
    url: str = accounts_url + "transfer/"
    transfer_data = {
        "source_account": account_in,
        "destination_account": account_out,
        "amount": amount,
        "timestamp": str(dt.now()),
    }
    client: Client = await create_client(user_id, url, data=transfer_data)
    status_code, response = await client.post()

    if status_code != 201:
        raise HTTPException(response.get("detail"))
