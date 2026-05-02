from fastapi import APIRouter, status

from schemas.settings import SettingsSchema
from schemas.general import SuccessSchema
from crud.settings import (
    create_settings,
    get_settings_user_by_id,
    delete_settings
)


settings_router = APIRouter(prefix="/settings", tags=["SETTINGS"])


@settings_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema
)
async def create_user_settings(
    user_id: int,
    settings: SettingsSchema
):
    """Create user settings for working with salary calculation."""
    await create_settings(settings.model_dump(), user_id)
    return SuccessSchema(result=True)


@settings_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=SettingsSchema
)
async def get_user_settings(user: int):
    """Get user settings by ID."""
    settings_data: dict = await get_settings_user_by_id(user_id=user)
    return SettingsSchema(**settings_data)


@settings_router.delete(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=SettingsSchema
)
async def delete_user_settings(user: int):
    """Delete user settings by ID."""
    return await delete_settings(user_id=user)
