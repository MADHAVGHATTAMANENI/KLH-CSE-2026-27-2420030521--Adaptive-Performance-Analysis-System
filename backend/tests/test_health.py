import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """
    Verifies that GET /api/v1/health returns HTTP 200 with complete system telemetry.
    """
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()

    assert data["app_name"] == "CompilerX"
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert "version" in data
    assert "timestamp" in data
    assert data["database"]["status"] == "CONNECTED"
    assert "compiler" in data
    assert "docker" in data

