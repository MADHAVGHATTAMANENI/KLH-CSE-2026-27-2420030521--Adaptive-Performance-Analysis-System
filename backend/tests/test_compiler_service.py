import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_compile_valid_c_program(client: AsyncClient):
    """
    Verifies successful Clang compilation of valid C code:
    - Exit code 0
    - Binary size recorded
    - Compilation duration recorded
    """
    # 1. Create project & file
    p_res = await client.post("/api/v1/projects", json={"name": "Compiler Test", "language": "c"})
    project_id = p_res.json()["id"]

    code = """
    #include <stdio.h>
    int main() {
        int sum = 0;
        for (int i = 0; i < 100; i++) sum += i;
        printf("Sum: %d\\n", sum);
        return 0;
    }
    """
    f_res = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "loop.c", "content": code},
    )
    file_id = f_res.json()["id"]

    # 2. Trigger Compilation with -O2 and -Wall
    c_res = await client.post(
        f"/api/v1/files/{file_id}/compile",
        json={"optimization_level": "-O2", "compiler_flags": ["-Wall"]},
    )
    assert c_res.status_code == 201
    compilation = c_res.json()
    assert compilation["success"] is True
    assert compilation["exit_code"] == 0
    assert compilation["optimization_level"] == "-O2"
    assert compilation["compilation_time_ms"] > 0
    assert compilation["binary_size_bytes"] is not None
    assert compilation["binary_size_bytes"] > 0

    # 3. Check compilation history
    h_res = await client.get(f"/api/v1/files/{file_id}/compilations")
    assert h_res.status_code == 200
    assert len(h_res.json()) >= 1


@pytest.mark.asyncio
async def test_compile_syntax_error_captures_diagnostics(client: AsyncClient):
    """
    Verifies that Clang compilation syntax errors:
    - Return success = False
    - Non-zero exit code
    - Captured stderr diagnostics containing line numbers and error message
    """
    p_res = await client.post("/api/v1/projects", json={"name": "Error Test", "language": "c"})
    project_id = p_res.json()["id"]

    bad_code = """
    #include <stdio.h>
    int main() {
        invalid_token_syntax_error;;;
        return 0;
    }
    """
    f_res = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "syntax_err.c", "content": bad_code},
    )
    file_id = f_res.json()["id"]

    c_res = await client.post(
        f"/api/v1/files/{file_id}/compile",
        json={"optimization_level": "-O0"},
    )
    assert c_res.status_code == 201  # HTTP 201 records the failed compilation entity
    compilation = c_res.json()
    assert compilation["success"] is False
    assert compilation["exit_code"] != 0
    assert "error:" in compilation["stderr"]


@pytest.mark.asyncio
async def test_compiler_flag_whitelist_rejection(client: AsyncClient):
    """
    Verifies that unwhitelisted/hostile flags are blocked by security validation (HTTP 422).
    """
    p_res = await client.post("/api/v1/projects", json={"name": "Sec Test", "language": "c"})
    project_id = p_res.json()["id"]

    f_res = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "sec.c", "content": "int main(){return 0;}"},
    )
    file_id = f_res.json()["id"]

    # Try passing a disallowed flag
    bad_res = await client.post(
        f"/api/v1/files/{file_id}/compile",
        json={"optimization_level": "-O2", "compiler_flags": ["-Xclang", "-load"]},
    )
    assert bad_res.status_code == 422
    assert "not permitted" in bad_res.json()["message"]
