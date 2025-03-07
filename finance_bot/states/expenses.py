from aiogram.fsm.state import StatesGroup, State


class ExpensesState(StatesGroup):
    """The class of states to work with Expenses."""

    show: State = State()
    action: State = State()
    remove: State = State()


class CreateExpenseState(StatesGroup):
    """The class of states to work with create Expenses."""

    date: State = State()
    account: State = State()
    expense_category: State = State()
    amount: State = State()
    comment: State = State()


class EditExpenseState(StatesGroup):
    """The class of states to work with edition Expenses."""

    amount: State = State()
    comment: State = State()
