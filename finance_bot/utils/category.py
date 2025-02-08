from config import categories_urls


async def get_url(data: dict) -> tuple[str, str]:
    """
    Gets the desired url depending on the action (show expense or income).
    :param data: A dictionary with the necessary data to work with.
    :return: Returns the url and the type of action.
    """
    category_id: int = data.get("category_id")
    category_type: str = data.get("category")
    category: str = "income" if category_type == "list_incomes_category" else "expense"
    return categories_urls[category].format(id=category_id), category
