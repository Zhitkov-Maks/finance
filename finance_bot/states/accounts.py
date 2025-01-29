from aiogram.fsm.state import StatesGroup, State


class AccountsState(StatesGroup):
    """The class of states to work with Accounts."""
    show: State = State()
    action: State = State()
    remove: State = State()


class AccountsEditState(StatesGroup):
    """The class of states to work with Edit Accounts."""
    name: State = State()
    balance: State = State()


class TransferStates(StatesGroup):
    action: State = State()
    amount: State = State()
