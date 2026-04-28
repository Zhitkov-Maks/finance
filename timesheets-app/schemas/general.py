from pydantic import BaseModel, Field


class SuccessSchema(BaseModel):
    """The response scheme, if the request was completed successfully."""

    result: bool = Field(
        ...,
        description="The boolean value is whether the request was "
                    "completed successfully or not."
    )

