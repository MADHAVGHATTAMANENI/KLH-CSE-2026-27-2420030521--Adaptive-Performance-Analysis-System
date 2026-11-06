from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.core.exceptions import EntityNotFoundError
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project workspace",
)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    project = Project(
        name=payload.name,
        description=payload.description,
        language=payload.language.value,
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        language=project.language,
        file_count=0,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List all project workspaces",
)
async def list_projects(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    
    # Total count query
    total_query = select(func.count()).select_from(Project)
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()

    # Paginated select
    stmt = (
        select(Project)
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    projects = result.scalars().all()

    items = [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            language=p.language,
            file_count=len(p.source_files),
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in projects
    ]

    return ProjectListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project workspace details",
)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise EntityNotFoundError("Project", project_id)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        language=project.language,
        file_count=len(project.source_files),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project workspace",
)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise EntityNotFoundError("Project", project_id)

    await db.delete(project)
    return None
