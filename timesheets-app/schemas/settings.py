from pydantic import Field
from pydantic import BaseModel


class SettingsSchema(BaseModel):
    """
    A class for describing fields and the types of these
    fields when working with salary settings.
    """
    price_time: float = Field(..., description="Hourly wage")
    price_overtime: float = Field(..., description="Extra pay for overtime")
    price_cold: float = Field(
        ...,
        description="Additional payment for working in the cold"
    )
    price_award: float = Field(..., description="The cost of the operation")
