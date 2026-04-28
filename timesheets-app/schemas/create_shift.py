from pydantic import Field, BaseModel


class ShiftSchema(BaseModel):
    date: str = Field(..., description="A specific date.")
    time: float = Field(..., description="Number of hours worked")
