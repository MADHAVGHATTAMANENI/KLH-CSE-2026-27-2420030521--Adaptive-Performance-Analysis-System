import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_source_files_api_crud(client: AsyncClient):
    """
    Verifies full CRUD operations on source files via REST API:
    - Creation in project
    - List files for project
    - Retrieve by file ID with full content
    - Update file content (triggering hash recalculation)
    - Deletion
    - 404 handling on non-existent project or file
    """
    # 1. Create a parent project
    p_res = await client.post("/api/v1/projects", json={"name": "Sort Lab", "language": "c"})
    assert p_res.status_code == 201
    project_id = p_res.json()["id"]

    # 2. Upload/Create Source File
    initial_code = "#include <stdio.h>\nint main() { return 0; }\n"
    f_res = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "sort.c", "content": initial_code},
    )
    assert f_res.status_code == 201
    file_data = f_res.json()
    file_id = file_data["id"]
    initial_hash = file_data["content_hash"]
    assert file_data["filename"] == "sort.c"
    assert file_data["size_bytes"] == len(initial_code.encode("utf-8"))

    # 3. List files in project
    list_res = await client.get(f"/api/v1/projects/{project_id}/files")
    assert list_res.status_code == 200
    files_list = list_res.json()
    assert len(files_list) == 1
    assert files_list[0]["id"] == file_id

    # 4. Get specific file detail
    detail_res = await client.get(f"/api/v1/files/{file_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["content"] == initial_code

    # 5. Update file content
    updated_code = "#include <stdio.h>\nint main() { printf(\"Updated\"); return 0; }\n"
    update_res = await client.put(
        f"/api/v1/files/{file_id}",
        json={"content": updated_code},
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["content"] == updated_code
    assert updated_data["content_hash"] != initial_hash

    # 6. Delete file
    del_res = await client.delete(f"/api/v1/files/{file_id}")
    assert del_res.status_code == 204

    # 7. Verify 404 after deletion
    get_res = await client.get(f"/api/v1/files/{file_id}")
    assert get_res.status_code == 404

    # 8. Test 404 on invalid project file upload
    bad_res = await client.post(
        "/api/v1/projects/non-existent-id/files",
        json={"filename": "test.c", "content": "int x;"},
    )
    assert bad_res.status_code == 404
