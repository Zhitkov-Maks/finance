from pydantic import BaseModel


class StatisticForYearSchema(BaseModel):
    total_hours: float
    total_earned: float
    total_award: float | None = None
    dollar: float
    euro: float
    yena: float
    som: float


class AggregateSchema(BaseModel):
    total_base_hours: float
    total_earned: float
    total_earned_hours: float
    total_earned_cold: float | None = None
    total_award: float | None = None
    total_operations: int | None = None
    total_overtime: float | None = None
    total_hours_overtime: float | None = None
    dollar: float
    euro: float
    yena: float
    som: float


class StatisticForMonth(BaseModel):
    period_one: AggregateSchema | None = None
    period_two: AggregateSchema | None = None
    total: AggregateSchema | None = None
