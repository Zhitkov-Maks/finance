from aiogram.fsm.state import StatesGroup, State


class DebtsStates(StatesGroup):
    """The class of states to work with debts."""

    detail: State = State()
    part_repay: State = State()
    confirm: State = State()
    date: State = State()
    account: State = State()
    description: State = State()
    save: State = State()