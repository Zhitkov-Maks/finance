from aiogram.fsm.state import StatesGroup, State


class AnalyticsState(StatesGroup):
    """The class of states to work with Accounts."""

    show: State = State()