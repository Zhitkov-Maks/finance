from aiogram.fsm.state import StatesGroup, State


class ResetPassword(StatesGroup):
    """The class of states to reset password."""
    
    email: State = State()
    token: State = State()
    password: State = State()
