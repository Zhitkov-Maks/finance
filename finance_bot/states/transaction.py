from aiogram.fsm.state import StatesGroup, State


class TransactionState(StatesGroup):
    """The class of states to work with Expenses."""

    show: State = State()
    action: State = State()
    remove: State = State()


class CreateTransactionState(StatesGroup):
    """The class of states to work with create Expenses."""

    date: State = State()
    account: State = State()
    category: State = State()
    amount: State = State()
    comment: State = State()


class EditTransactionState(StatesGroup):
    """The class of states to work with edition Expenses."""

    amount: State = State()
    comment: State = State()
