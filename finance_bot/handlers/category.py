from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.markdown import hbold

from api.common import (
    create_new_object,
    get_all_objects,
    get_full_info,
    delete_object_by_id,
    edit_object,
)
from config import categories_urls, PAGE_SIZE
from handlers.decorator_handler import decorator_errors
from keyboards.category import (
    inline_type_categories,
    create_list_category,
    get_categories_action,
)
from keyboards.keyboards import cancel_, confirmation, cancel_action
from loader import categories_message, category_menu
from states.category import CategoryState
from utils.category import get_url


category_route: Router = Router()


@category_route.callback_query(F.data == "categories")
async def start_working_category(callback: CallbackQuery) -> None:
    """
    The handler for getting started with categories shows
    the keyboard with possible actions.
    """
    await callback.message.edit_text(
        text=hbold(category_menu),
        reply_markup=inline_type_categories,
        parse_mode="HTML"
    )


@category_route.callback_query(
    F.data.in_(["list_expenses_category", "list_incomes_category"])
)
@decorator_errors
async def show_categories(callback: CallbackQuery, state: FSMContext) -> None:
    """A handler for displaying income or expense categories."""
    data: dict = await state.get_data()
    page: int = data.get("page", 1)
    url: str = categories_urls[callback.data].format(
        page=page, page_size=PAGE_SIZE
    )

    result: dict = await get_all_objects(url, callback.from_user.id)
    await state.set_state(CategoryState.show)
    await state.update_data(page=page, category=callback.data)

    keyword: InlineKeyboardMarkup = await create_list_category(
        result, "prev_category", "next_category"
    )
    await callback.message.edit_text(
        text=hbold(categories_message[callback.data]),
        reply_markup=keyword,
        parse_mode="HTML"
    )


@category_route.callback_query(F.data.in_(["next_category", "prev_category"]))
@decorator_errors
async def next_and_prev_category(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """A function for getting the next or previous categories."""
    page: int = (await state.get_data()).get("page")
    category: str = (await state.get_data()).get("category")

    if callback.data == "next_category":
        page += 1
    else:
        page -= 1

    url: str = categories_urls[category].format(page=page, page_size=PAGE_SIZE)
    result: dict = await get_all_objects(url, callback.from_user.id)

    keyword: InlineKeyboardMarkup = await create_list_category(
        result, "prev_category", "next_category"
    )
    await state.set_state(CategoryState.show)
    await state.update_data(page=page)
    await callback.message.edit_reply_markup(reply_markup=keyword)


@category_route.callback_query(CategoryState.show, F.data.isdigit())
@decorator_errors
async def detail_category(call: CallbackQuery, state: FSMContext) -> None:
    """Show detailed category information."""
    await state.update_data(category_id=int(call.data))
    data: dict = await state.get_data()

    url, category = await get_url(data)
    response: dict = await get_full_info(url, call.from_user.id)
    text: str = response.get("name")

    await state.set_state(CategoryState.action)
    await call.message.edit_text(
        text=hbold("Категория: <" + text + ">. Выберите действие."),
        parse_mode="HTML",
        reply_markup=await get_categories_action(data["category"]),
    )


@category_route.callback_query(F.data.in_(["add_income", "add_expense"]))
async def choice_category(callback: CallbackQuery, state: FSMContext) -> None:
    """A handler for entering a new income or expense category."""
    await state.update_data(category=callback.data)
    await state.set_state(CategoryState.type_category)
    await callback.message.edit_text(
        text=hbold("Введите название категории"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=
            [
                [
                    InlineKeyboardButton(
                        text="㊂",
                        callback_data="main"
                    ),
                    InlineKeyboardButton(
                        text="▲",
                        callback_data="categories"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )


@category_route.message(CategoryState.type_category)
@decorator_errors
async def create_category(message: Message, state: FSMContext) -> None:
    """The handler sends a request to save the category."""
    data: dict[str, str] = await state.get_data()
    category: str = data["category"]
    result: dict = await create_new_object(
        message.from_user.id, categories_urls[category],
        {"name": message.text}
    )
    await state.update_data(category_id=result.get("id"))

    await state.set_state(CategoryState.action)
    await message.answer(
        text=hbold(categories_message[category].format(message.text)),
        reply_markup=inline_type_categories,
        parse_mode="HTML"
    )


@category_route.callback_query(F.data == "del_category", CategoryState.action)
async def remove_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirmation of deletion."""
    await state.set_state(CategoryState.remove)
    category: str = (await state.get_data())["category"]
    await callback.message.edit_text(
        text=hbold("Вы уверены?"),
        reply_markup=await confirmation(category),
        parse_mode="HTML"
    )


@category_route.callback_query(CategoryState.remove, F.data == "continue")
@decorator_errors
async def remove_category_by_id(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """
    The final handler for category deletion.
    """
    data: dict[str, str | int] = await state.get_data()
    url, category = await get_url(data)
    await delete_object_by_id(url, callback.from_user.id)

    page: int = data.get("page", 1)
    type_ = (
        "list_incomes_category"
        if category == "income" else "list_expenses_category"
    )
    url: str = categories_urls[type_].format(page=page, page_size=PAGE_SIZE)

    result: dict = await get_all_objects(url, callback.from_user.id)
    await state.update_data(page=page)
    await state.set_state(CategoryState.show)

    keyword: InlineKeyboardMarkup = await create_list_category(
        result, "prev_category", "next_category"
    )
    await callback.message.edit_text(
        text=hbold("Ok, Категория удалена!"),
        reply_markup=keyword,
        parse_mode="HTML"
    )


@category_route.callback_query(F.data == "edit_category")
async def edit_route_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Handler for editing categories."""
    await state.set_state(CategoryState.edit)
    show: str = (await state.get_data())["category"]
    await callback.message.edit_text(
        text=hbold("Введите название категории: "),
        reply_markup=await cancel_action(show),
        parse_mode="HTML"
    )


@category_route.message(CategoryState.edit)
async def edit_category(message: Message, state: FSMContext) -> None:
    """Handler for the request to save category changes."""
    data: dict[str, str | int] = await state.get_data()
    url, category = await get_url(data)

    response: dict = await edit_object(
        url, message.from_user.id, {"name": message.text}, "PUT"
    )
    text: str = response.get("name")

    await state.set_state(CategoryState.action)
    await message.answer(
        text=hbold("Категория: <" + text + ">. Выберите действие."),
        parse_mode="HTML",
        reply_markup=await get_categories_action(data["category"]),
    )
