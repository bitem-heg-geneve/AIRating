import time
import sys
import os
from pathlib import Path

from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

# from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

if sys.stdout.isatty() and os.getenv('TERM'):
    import colored_traceback
    colored_traceback.add_hook(always=True)

# from app import crud
# from app.api import deps

from app.api.api_v1.api import api_router as api_v1_router

# from app.api.api_v1.api import api_router as api_v2_router
from app.core.config import settings
from app.core.celery import create_celery
from starlette.responses import RedirectResponse

# from app.db.mongodb_utils import Database
from pymongo import MongoClient

# from motor.motor_asyncio import AsyncIOMotorClient

# from beanie import init_beanie
from bunnet import init_bunnet

from app.models.job import Job
from app.models.source import Source

BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

root_router = APIRouter()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Impaakt API", openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    app.celery_app = create_celery()
    return app


app = create_app()
celery = app.celery_app


# app = FastAPI(title="Recipe API", openapi_url=f"{settings.API_V1_STR}/openapi.json")


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@root_router.get("/", status_code=200)
def root():
    return RedirectResponse(url="/docs")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

    # Sync


client = MongoClient(settings.MONGODB_URL)
init_bunnet(client.app, document_models=[Job, Source])


# @app.on_event("startup")
# async def startup_db_clients():
# Async
# client = AsyncIOMotorClient(settings.MONGODB_URL)
# await init_beanie(client.app, document_models=[JobAsync, SourceAsync])

# Sync
# client = MongoClient(settings.MONGODB_URL)
# init_bunnet(client.app, document_models=[Job, Source])


# @app.on_event("shutdown")
# async def shutdown_db_clients():
#     await DB.disconnect()


app.include_router(api_v1_router, prefix=settings.API_V1_STR)
# app.include_router(api_v2_router, prefix=settings.API_V2_STR)
app.include_router(root_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
