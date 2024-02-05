import sentry_sdk
import uvicorn
from sentry_sdk.integrations.logging import LoggingIntegration

from app import app as route
from app.db import SessionLocal
from app.settings import ENVIRONMENT, SENTRY_URL
from fastapi import FastAPI, Request, Response

sentry_sdk.init(
    dsn=SENTRY_URL,
    environment=ENVIRONMENT,
    integrations=[LoggingIntegration(),],
    traces_sample_rate=1.0,
    send_default_pii=True,
)


app = FastAPI()
app.include_router(route)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
