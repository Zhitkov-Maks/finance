async def generate_message_answer(data: dict) -> str:
    """
    Generates a message on transfers between accounts
    to be shown to the user.

    :param data: The result of the request to the server.
    """
    message = "История переводов между счетами.\n\n"
    for item in data.get("results", []):
        message += f"Со счета -> {item.get('source_account_name')};\n"
        message += f"На счет -> {item.get('destination_account_name')};\n"
        message += f"На сумму -> {item.get('amount')}₽;\n"
        message += f"Дата перевода -> {item.get('timestamp')[:10]}.\n\n"
    return message
