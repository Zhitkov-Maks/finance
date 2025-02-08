from aiogram.fsm.state import StatesGroup, State


class IncomesState(StatesGroup):
    """The class of states to work with Incomes."""

    show: State = State()
    action: State = State()
    remove: State = State()


class CreateIncomes(StatesGroup):
    """The class of states to work with create Incomes."""

    date: State = State()
    account: State = State()
    income_category: State = State()
    amount: State = State()


class EditIncomesState(StatesGroup):
    """The class of states to work with edition of Incomes."""

    amount: State = State()
