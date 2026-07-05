import logging
import sys
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.logger import logger as fastapi_logger

from routes.settings import settings_router
from routes.shifts import shift_router
from routes.statistic import statistic


app = FastAPI(
    root_path="/api/v1",
    title="TimeSheetsApp",
    description="An application for recording working hours and earnings.",
    version="0.1.0",
    contact={"name": "Maksim Zhitkov", "email": "m-zhitkov@inbox.ru"},
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s %(name)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# ⚠️ ОТКЛЮЧАЕМ DEBUG-логи от MongoDB
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("pymongo.topology").setLevel(logging.WARNING)
logging.getLogger("pymongo.connection").setLevel(logging.WARNING)
logging.getLogger("pymongo.command").setLevel(logging.WARNING)
logging.getLogger("pymongo.serverSelection").setLevel(logging.WARNING)

# Получаем логгер
logger = logging.getLogger(__name__)
worker_id = os.getpid()


# Middleware для логирования всех запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"[Worker {worker_id}] 📥 Запрос: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"[Worker {worker_id}] 📤 Ответ: {response.status_code}")
    return response


app.include_router(settings_router)
app.include_router(shift_router)
app.include_router(statistic)


@app.get("/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    """It is needed to inform about readiness for work."""
    return JSONResponse(
        status_code=200, content={"status": "healthy", "service": "timesheets_app"}
    )
