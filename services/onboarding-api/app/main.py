import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.database import engine
from app.core.exceptions import AppException, app_exception_handler
from app.core.logging import configure_logging, get_logger
from app.core.metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUESTS_TOTAL
from app.models.base import Base
from app.models.customer import Customer  # noqa: F401 — register mappers
from app.models.kyc import BankRecord, KycSubmission, PanRecord  # noqa: F401
from app.models.risk import RiskAssessment  # noqa: F401
from app.routers import customer_read, customers, health, kyc, risk, verification

logger = get_logger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        path = request.url.path
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method, path=path, status=str(response.status_code)
        ).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=request.method, path=path).observe(duration)
        return response


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    Base.metadata.create_all(bind=engine)
    logger.info("application_started")
    yield
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_middleware(MetricsMiddleware)

    app.include_router(customers.router)
    app.include_router(customer_read.router)
    app.include_router(kyc.router)
    app.include_router(verification.router)
    app.include_router(risk.router)
    app.include_router(health.router)

    return app


app = create_app()
