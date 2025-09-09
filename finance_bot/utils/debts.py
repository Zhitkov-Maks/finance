async def generate_debts_message(data: dict) -> str:
    """
    Generate a message to show detailed information about the debt.
    :param data: A dict with debt data.
    """
    amount: str = data.get("transfer").get("amount")
    dt: str = data.get("transfer").get("timestamp")
    dt_str = f"{dt[8:10]}-{dt[5:7]}-{dt[0:4]}"
    source_account: str = (data.get("transfer")
                           .get("source_account")
                           .get("name"))
    descr: str = data.get("borrower_description")

    type_: str = "Я должен."
    if data.get("transfer").get("destination_account").get("name") == "lend":
        type_ = "Мне должны!"

    return (f"Тип: {type_}\n"
            f"Сумма долга: {amount}₽.\n"
            f"Дата дачи/взятия: {dt_str}.\n"
            f"С/На счет: {source_account}.\n"
            f"Кто/Что/кому: {descr}.\n")


async def create_debt_data_for_request(data: dict) -> dict:
    """
    Create a dictionary to save debt.

    :param data: A dict with debt data.
    """
    return {
        "account_id": data.get("account_id"),
        "type": data.get("type"),
        "amount": data.get("amount"),
        "description": data.get("description"),
        "date": data.get("date"),
    }
