from fastapi import FastAPI
from fastapi.responses import JSONResponse

from routes.settings import settings_router
from routes.shifts import shift_router
from routes.statistic import statistic

app = FastAPI(
    root_path="/api/v2",
    title="TimeSheetsApp",
    description="An application for recording working hours and earnings.",
    version="0.1.0",
    contact={"name": "Maksim Zhitkov", "email": "m-zhitkov@inbox.ru"},
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


app.include_router(settings_router)
app.include_router(shift_router)
app.include_router(statistic)


@app.get("/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    """It is needed to inform about readiness for work."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "timesheets_app"}
    )
