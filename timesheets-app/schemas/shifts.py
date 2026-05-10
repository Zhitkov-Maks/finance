from datetime import datetime

from pydantic import Field, BaseModel, field_validator


class ShiftSchema(BaseModel):
    """A class for requesting the addition of a work shift."""
    date: str = Field(..., description="A specific date.")
    time: float = Field(..., description="Number of hours worked")

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, dt: str) -> str:
        try:
            datetime.strptime(dt, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "Переданная дата не соответствует требованию формата "
                "YYYY-MM-DD"
            )
        return dt

    @field_validator("time")
    @classmethod
    def validate_time_format(cls, tm: float) -> float:
        if 0 > tm or tm > 24:
            raise ValueError("Передано недопустимое кол-во часов.")
        return tm


class SimpleShiftSchema(BaseModel):
    """
    A class for returning the minimum necessary
    information for substitution in the calendar.
    """
    day_id: str = Field(
        ...,
        description="The line is the ID of the work shift, for mongodb."
    )
    base_hours: float = Field(
        ...,
        description="Describes how many hours the user worked per shift."
    )
    date: str = Field(
        ...,
        description="Date of the work shift as a string."
    )
    earned: float = Field(
        ...,
        description="How much the user earned during the work shift."
    )


class ListShiftSchema(BaseModel):
    """A class for sending the user a list of work shifts for the month."""
    result: list[SimpleShiftSchema]


class Valute(BaseModel):
    """A class for returning earnings in the currency to the user."""
    dollar: float
    euro: float
    yena: float
    som: float


class SpecificShift(BaseModel):
    """
    A class for returning detailed information about
    earnings per shift to the user.
    """
    day_id: str = Field(
        ...,
        description="The line is the ID of the work shift, for mongodb."
    )
    base_hours: float = Field(
        ...,
        description="Describes how many hours the user worked per shift."
    )
    date: str = Field(
        ...,
        description="Date of the work shift as a string."
    )
    earned: float = Field(
        ...,
        description="How much the user earned during the work shift."
    )
    earned_cold: float | None = Field(
        None,
        description="How much will be the extra payment for working in the cold."
    )
    earned_overtime: float | None = Field(
        None,
        description="How much will be the extra payment for overtime hours."
    )
    earned_hours: float = Field(
        ...,
        description="How much does it cost to pay for hours per shift."
    )
    period: int = Field(
        ...,
        description="What is the period of the month(1 if the date is from "
                    "1-15, 2 if the date is from the 16th)."
    )
    valute: Valute = Field(
        ...,
        description="Describes how much the user earned in a foreign currency."
    )
    award_amount: float | None = Field(
        None,
        description="How much the user earned in the form of a bonus."
    )
    count_operations: float | None = Field(
        None,
        description="How many operations the user performed per shift."
    )


class ManyAddShifts(BaseModel):
    """A class for adding group shifts per month."""
    hours: float = Field(
        ...,
        description="How many hours should I put in per shift?"
    )
    dates: list[str] = Field(
        ...,
        description="A list of dates for recording shifts."
    )
    @field_validator("hours")
    @classmethod
    def validate_time_format(cls, tm: float) -> float:
        if 0 > tm or tm > 24:
            raise ValueError("Передано недопустимое кол-во часов.")
        return tm
