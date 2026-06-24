from decouple import config


DB_MONGO_NAME = config("DB_MONGO_NAME")
DB_MONGO_PASS = config("DB_MONGO_PASS")

cashed_currency = {}
