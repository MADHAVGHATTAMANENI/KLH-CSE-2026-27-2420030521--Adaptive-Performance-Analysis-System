from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.projects import router as projects_router
from app.api.v1.files import router as files_router
from app.api.v1.compiler import router as compiler_router
from app.api.v1.benchmark import router as benchmark_router

api_v1_router = APIRouter()

# Register sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(projects_router)
api_v1_router.include_router(files_router)
api_v1_router.include_router(compiler_router)
api_v1_router.include_router(benchmark_router)
