import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_count_primes_workflow():
    """
    Full workflow test example:
    1. Submit a prime-counting job
    2. Poll the job status until it completes
    3. Verify results
    """
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/count-primes", json={"n": 100, "chunks": 4})
        assert response.status_code == 202, f"Expected 202, got {response.status_code}"
        data = response.json()
        assert "job_id" in data
        job_id = data["job_id"]

        max_attempts = 10
        for attempt in range(max_attempts):
            status_resp = await client.get(f"/api/job-status/{job_id}")
            assert status_resp.status_code == 200
            status_data = status_resp.json()
            if status_data.get("status") == "completed":
                break
            await asyncio.sleep(0.5) 
        else:
            pytest.fail("Job did not complete in time")

        result_resp = await client.get(f"/api/job-result/{job_id}")
        assert result_resp.status_code == 200
        result_data = result_resp.json()
        assert "prime_count" in result_data
        assert isinstance(result_data["prime_count"], int)
        assert result_data["prime_count"] > 0

@pytest.mark.asyncio
async def test_health_check():
    """
    Simple test to ensure the FastAPI app is running
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
