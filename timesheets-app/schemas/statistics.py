from pydantic import BaseModel, Field


class StatisticForYearSchema(BaseModel):
    """A class for displaying statistics for the year."""
    total_hours: float = Field(
        ...,
        description="How many hours worked in a year."
    )
    total_earned: float = Field(
        ...,
        description="How much you earned in a year."
    )
    total_award: float | None = Field(
        None,
        description="How much is earned in the form of a bonus."
    )
    dollar: float
    euro: float
    yena: float
    som: float


class AggregateSchema(BaseModel):
    """Aggregation of data by period and per month."""
    total_base_hours: float = Field(
        ...,
        description="The total number of hours worked."
    )
    total_earned: float = Field(
        ...,
        description="How much you earned in a month."
    )
    total_earned_hours: float = Field(
        ...,
        description="How much is earned in hours."
    )
    total_earned_cold: float | None = Field(
        None,
        description="How much is the surcharge for working in the cold."
    )
    total_award: float | None = Field(
        None,
        description="How much is earned in the form of a bonus."
    )
    total_operations: int | None = Field(
        None,
        description="How many operations were performed during the period."
    )
    total_overtime: float | None = Field(
        None,
        description="How much will be paid for overtime."
    )
    total_hours_overtime: float | None = Field(
        None,
        description="How many hours of overtime."
    )
    dollar: float
    euro: float
    yena: float
    som: float


class StatisticForMonth(BaseModel):
    """Returns statistics for periods and for the month."""
    period_one: AggregateSchema | None = None
    period_two: AggregateSchema | None = None
    total: AggregateSchema | None = None
