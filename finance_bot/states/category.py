from aiogram.fsm.state import StatesGroup, State


class CategoryState(StatesGroup):
    """The class of states to work with Category."""

    type_category: State = State()
    show: State = State()
    action: State = State()
    remove: State = State()
    edit: State = State()
