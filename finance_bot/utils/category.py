from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from config import categories_urls, PAGE_SIZE
from api.common import get_all_objects
from keyboards.category import create_list_category
from states.category import CategoryState


async def get_url(data: dict) -> tuple[str, str]:
    """
    Get the desired url depending on the action (show expense or income).

    :param data: A dictionary with the necessary data to work with.
    :return: Returns the url and the type of action.
    """
    category_id: int = data.get("category_id")
    category_type: str = data.get("category")
    category: str = "income" if category_type == "list_incomes_category" \
        else "expense"
    return categories_urls[category].format(id=category_id), category


async def get_categories(
    page: int,
    call_back: str,
    parent: str,
    user: int
):
    url: str = categories_urls[call_back].format(
        page=page, page_size=PAGE_SIZE
    ) + f"&parent={parent}"
    return await get_all_objects(url, user)


async def create_pagination(
    state: FSMContext,
    callback: CallbackQuery,
    page: int,
    category: str,
    parent: str   
) -> InlineKeyboardMarkup:
    if callback.data in ["next_category", "next_category_child"]:
        page += 1
    else:
        page -= 1

    result: dict = await get_categories(
        page, category, "true", callback.from_user.id
    )
    await state.update_data(page=page)
    if "child" not in callback.data:
        prev, next_ = ("prev_category", "next_category")
        await state.set_state(CategoryState.show)
    else:
        prev, next_ = ("prev_category_child", "next_category_child")
        await state.set_state(CategoryState.child)
    return await create_list_category(result, prev, next_)
