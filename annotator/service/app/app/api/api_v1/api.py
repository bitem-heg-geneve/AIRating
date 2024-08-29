from fastapi import APIRouter

from .endpoints import job

api_router = APIRouter()
api_router.include_router(job.router, prefix="/jobs", tags=["job"])
