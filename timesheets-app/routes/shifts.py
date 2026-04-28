from fastapi import APIRouter, status

from schemas.create_shift import ShiftSchema
from schemas.general import SuccessSchema
from utils.shifts import earned_per_shift


shift_router = APIRouter(prefix="/shifts", tags=["SHIFTS"])


@shift_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema
)
async def create_shift(
    user_id: str,
    data: ShiftSchema
) -> SuccessSchema:
    data = data.model_dump()
    time, date = data.get("time"), data.get("date")
    notes = data.get("current_day", {}).get("notes")
    await earned_per_shift(
        time,
        user_id,
        date,
        notes,
        data=data
    )
    return SuccessSchema(result=True)
