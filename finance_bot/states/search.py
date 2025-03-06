from aiogram.fsm.state import StatesGroup, State


class SearchState(StatesGroup):
    """The class of states to Search."""
    action: State = State()
    show: State = State()
