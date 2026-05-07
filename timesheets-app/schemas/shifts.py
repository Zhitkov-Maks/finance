from pydantic import Field, BaseModel

class ShiftSchema(BaseModel):
    date: str = Field(..., description="A specific date.")
    time: float = Field(..., description="Number of hours worked")


class SimpleShiftSchema(BaseModel):
    day_id: str
    base_hours: float
    date: str
    earned: float


class ListShiftSchema(BaseModel):
    result: list[SimpleShiftSchema]


class Valute(BaseModel):
    dollar: float
    euro: float
    yena: float
    som: float


class SpecificShift(BaseModel):
    day_id: str
    base_hours: float
    date: str
    earned: float
    earned_cold: float | None = None
    earned_overtime: float | None = None
    earned_hours: float
    period: int
    valute: Valute
    award_amount: float | None = None
    count_operations: float | None = None


class ManyAddShifts(BaseModel):
    hours: float
    dates: list[str]
