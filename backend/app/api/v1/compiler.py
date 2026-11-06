from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.core.exceptions import EntityNotFoundError
from app.models.compilation import Compilation
from app.schemas.compilation import (
    CompilationHistoryItem,
    CompileRequest,
    CompileResponse,
)
from app.services.compiler_service import CompilerService

router = APIRouter(tags=["Compiler Engine"])


@router.post(
    "/files/{file_id}/compile",
    response_model=CompileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Compile a C/C++ source file with Clang",
)
async def compile_file(
    file_id: str,
    payload: CompileRequest,
    db: AsyncSession = Depends(get_db),
):
    compiler_service = CompilerService(db)
    compilation = await compiler_service.compile_source_file(
        source_file_id=file_id,
        optimization_level=payload.optimization_level.value,
        compiler_flags=payload.compiler_flags,
    )
    return compilation


@router.get(
    "/compilations/{compilation_id}",
    response_model=CompileResponse,
    summary="Get compilation details by ID",
)
async def get_compilation(
    compilation_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Compilation).where(Compilation.id == compilation_id)
    result = await db.execute(stmt)
    compilation = result.scalar_one_or_none()
    if not compilation:
        raise EntityNotFoundError("Compilation", compilation_id)
    return compilation


@router.get(
    "/files/{file_id}/compilations",
    response_model=List[CompilationHistoryItem],
    summary="Get compilation history for a source file",
)
async def get_file_compilations(
    file_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Compilation)
        .where(Compilation.source_file_id == file_id)
        .order_by(Compilation.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()

