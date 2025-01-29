from typing import Dict

from decouple import config

BOT_TOKEN: str = config("TOKEN")
API_ADDRESS: str = config("API_ADDRESS")
BASE_URL: str = "/api/v1/"

token_data: Dict[int, dict] = {}
register_url: str = API_ADDRESS + BASE_URL + "auth/users/"
login_url: str = API_ADDRESS + BASE_URL + "auth/token/login/"
accounts_url: str = API_ADDRESS + BASE_URL + "accounts/"
