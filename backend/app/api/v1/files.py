from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.core.exceptions import EntityNotFoundError
from app.models.project import Project
from app.models.source_file import SourceFile
from app.schemas.source_file import (
    SourceFileCreate,
    SourceFileDetailResponse,
    SourceFileResponse,
    SourceFileUpdate,
)

router = APIRouter(tags=["Source Files"])


@router.post(
    "/projects/{project_id}/files",
    response_model=SourceFileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or upload a source code file to a project",
)
async def create_source_file(
    project_id: str,
    payload: SourceFileCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify project exists
    p_stmt = select(Project).where(Project.id == project_id)
    p_result = await db.execute(p_stmt)
    project = p_result.scalar_one_or_none()
    if not project:
        raise EntityNotFoundError("Project", project_id)

    content_hash = SourceFile.compute_hash(payload.content)
    size_bytes = len(payload.content.encode("utf-8"))

    source_file = SourceFile(
        project_id=project_id,
        filename=payload.filename,
        content=payload.content,
        content_hash=content_hash,
        size_bytes=size_bytes,
    )
    db.add(source_file)
    await db.flush()
    await db.refresh(source_file)

    return source_file


@router.get(
    "/projects/{project_id}/files",
    response_model=List[SourceFileResponse],
    summary="List all source files in a project",
)
async def list_project_files(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(SourceFile)
        .where(SourceFile.project_id == project_id)
        .order_by(SourceFile.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/files/{file_id}",
    response_model=SourceFileDetailResponse,
    summary="Get source file content and metadata",
)
async def get_source_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SourceFile).where(SourceFile.id == file_id)
    result = await db.execute(stmt)
    source_file = result.scalar_one_or_none()

    if not source_file:
        raise EntityNotFoundError("SourceFile", file_id)

    return source_file


@router.put(
    "/files/{file_id}",
    response_model=SourceFileDetailResponse,
    summary="Update source file content or filename",
)
async def update_source_file(
    file_id: str,
    payload: SourceFileUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SourceFile).where(SourceFile.id == file_id)
    result = await db.execute(stmt)
    source_file = result.scalar_one_or_none()

    if not source_file:
        raise EntityNotFoundError("SourceFile", file_id)

    if payload.filename:
        source_file.filename = payload.filename
    if payload.content is not None:
        source_file.content = payload.content
        source_file.content_hash = SourceFile.compute_hash(payload.content)
        source_file.size_bytes = len(payload.content.encode("utf-8"))

    await db.flush()
    await db.refresh(source_file)
    return source_file


@router.delete(
    "/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a source file",
)
async def delete_source_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SourceFile).where(SourceFile.id == file_id)
    result = await db.execute(stmt)
    source_file = result.scalar_one_or_none()

    if not source_file:
        raise EntityNotFoundError("SourceFile", file_id)

    await db.delete(source_file)
    return None
