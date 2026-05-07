from pydantic import BaseModel, Field


class SuccessSchema(BaseModel):
    """The response scheme, if the request was completed successfully."""

    result: bool = Field(
        ...,
        description="The boolean value is whether the request was "
                    "completed successfully or not."
    )


class NotFound(BaseModel):
    """A class for dealing with errors that occur if no result is found."""
    result: bool = Field(
        ...,
        description="False when a 404 error occurs."
    )
    description: str = Field(
        ...,
        description="A detailed description of the circumstances under"
                    " which the error occurred."
    )

class NotFoundShift(BaseModel):
    """A class that provides detailed information about the error."""
    detail: NotFound
