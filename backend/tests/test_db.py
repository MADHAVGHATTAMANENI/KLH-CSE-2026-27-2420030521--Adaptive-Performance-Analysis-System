import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.source_file import SourceFile


@pytest.mark.asyncio
async def test_project_crud_lifecycle(client: AsyncClient, test_db_session: AsyncSession):
    """
    Verifies full lifecycle of Project creation, listing, retrieval, and cascading deletion.
    """
    # 1. Create Project
    create_payload = {
        "name": "Bubble Sort Benchmark",
        "description": "Evaluation of O0 to O3 loop optimizations",
        "language": "c",
    }
    res = await client.post("/api/v1/projects", json=create_payload)
    assert res.status_code == 201
    project = res.json()
    assert project["name"] == "Bubble Sort Benchmark"
    assert project["language"] == "c"
    project_id = project["id"]

    # 2. Get Project
    res = await client.get(f"/api/v1/projects/{project_id}")
    assert res.status_code == 200
    assert res.json()["id"] == project_id

    # 3. List Projects
    res = await client.get("/api/v1/projects")
    assert res.status_code == 200
    list_data = res.json()
    assert list_data["total"] >= 1
    assert any(p["id"] == project_id for p in list_data["items"])

    # 4. Create Source File in Project
    file_payload = {
        "filename": "bubblesort.c",
        "content": "#include <stdio.h>\nint main() { printf(\"Done\\n\"); return 0; }",
    }
    res = await client.post(f"/api/v1/projects/{project_id}/files", json=file_payload)
    assert res.status_code == 201
    file_data = res.json()
    assert file_data["filename"] == "bubblesort.c"
    assert file_data["project_id"] == project_id
    assert file_data["size_bytes"] > 0
    assert len(file_data["content_hash"]) == 64
    file_id = file_data["id"]

    # 5. Retrieve Source File Content
    res = await client.get(f"/api/v1/files/{file_id}")
    assert res.status_code == 200
    assert "printf(\"Done\\n\")" in res.json()["content"]

    # 6. Delete Project (Cascading to file)
    res = await client.delete(f"/api/v1/projects/{project_id}")
    assert res.status_code == 204

    # 7. Verify File Was Deleted via Cascade
    res = await client.get(f"/api/v1/files/{file_id}")
    assert res.status_code == 404
