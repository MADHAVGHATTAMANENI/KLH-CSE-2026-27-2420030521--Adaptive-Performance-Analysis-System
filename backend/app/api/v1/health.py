import os
import shutil
import subprocess
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.core.config import settings

router = APIRouter(tags=["Health & System"])


@router.get("/health", summary="System Health & Toolchain Diagnostic")
async def get_health(db: AsyncSession = Depends(get_db)):
    """
    Returns live health telemetry for CompilerX:
    - Application status & version
    - Database connectivity check
    - Clang compiler availability & local version
    - Docker daemon socket accessibility
    """
    # 1. Database Check
    db_status = "CONNECTED"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    # 2. Clang Toolchain Check
    clang_path = shutil.which("clang")
    clang_version = "NOT_INSTALLED"
    clang_status = "UNAVAILABLE"
    if clang_path:
        try:
            res = subprocess.run(
                ["clang", "--version"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res.returncode == 0:
                clang_status = "AVAILABLE"
                clang_version = res.stdout.splitlines()[0] if res.stdout else "Unknown"
        except Exception as e:
            clang_status = f"ERROR: {str(e)}"

    # 3. Docker Socket Check
    docker_socket_path = settings.DOCKER_SOCKET.replace("unix://", "")
    docker_status = "CONNECTED" if os.path.exists(docker_socket_path) else "DISCONNECTED"

    return {
        "status": "HEALTHY" if db_status == "CONNECTED" else "DEGRADED",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "status": db_status,
            "engine": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgres",
        },
        "compiler": {
            "status": clang_status,
            "path": clang_path or "N/A",
            "version": clang_version,
        },
        "docker": {
            "status": docker_status,
            "socket": settings.DOCKER_SOCKET,
        },
    }

