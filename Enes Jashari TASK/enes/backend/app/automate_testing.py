import pytest
import time
from httpx import AsyncClient
from app.main import app

# --------------------------
# Config
# --------------------------
MIN_N = 10000
MAX_CHUNKS = 128
DEFAULT_N = 200_000
DEFAULT_CHUNKS = 16

# --------------------------
# Helper function to poll job
# --------------------------
async def wait_for_job(client: AsyncClient, job_id: str, timeout: int = 30):
    """
    Polls /api/jobs/{job_id} until job completes or timeout.
    Returns final JSON result.
    """
    start = time.time()
    while True:
        resp = await client.get(f"/api/jobs/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        if data["state"] in ("SUCCESS", "FAILURE"):
            return data
        if time.time() - start > timeout:
            pytest.fail(f"Job {job_id} did not complete in {timeout}s")
        time.sleep(1)


@pytest.mark.asyncio
async def test_submit_basic_job():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {"n": DEFAULT_N, "chunks": DEFAULT_CHUNKS}
        resp = await client.post("/api/count-primes", json=payload)
        assert resp.status_code == 202
        job_id = resp.json().get("job_id")
        assert job_id

        result = await wait_for_job(client, job_id)
        assert result["state"] == "SUCCESS"
        assert result["result"]["prime_count"] > 0
        assert result["result"]["n"] == DEFAULT_N
        assert "duration_sec" in result["result"]

@pytest.mark.asyncio
async def test_submit_single_chunk_job():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {"n": 50_000, "chunks": 1}
        resp = await client.post("/api/count-primes", json=payload)
        job_id = resp.json()["job_id"]
        result = await wait_for_job(client, job_id)
        assert result["state"] == "SUCCESS"
        assert result["progress"]["total"] == 1
        assert result["progress"]["completed"] == 1

@pytest.mark.asyncio
async def test_submit_max_chunks_job():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {"n": 100_000, "chunks": MAX_CHUNKS}
        resp = await client.post("/api/count-primes", json=payload)
        job_id = resp.json()["job_id"]
        result = await wait_for_job(client, job_id)
        assert result["state"] == "SUCCESS"
        assert result["progress"]["total"] <= MAX_CHUNKS
        assert result["progress"]["completed"] == result["progress"]["total"]


@pytest.mark.asyncio
async def test_invalid_n_too_small():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post("/api/count-primes", json={"n": 9999, "chunks": 4})
        assert resp.status_code == 400

@pytest.mark.asyncio
async def test_invalid_chunks_too_large():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post("/api/count-primes", json={"n": 20_000, "chunks": 129})
        assert resp.status_code == 400

@pytest.mark.asyncio
async def test_invalid_chunks_zero():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post("/api/count-primes", json={"n": 20_000, "chunks": 0})
        assert resp.status_code == 400

@pytest.mark.asyncio
async def test_invalid_n_type():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post("/api/count-primes", json={"n": "abc", "chunks": 4})
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_deterministic_results():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {"n": 50_000, "chunks": 4}
        resp1 = await client.post("/api/count-primes", json=payload)
        resp2 = await client.post("/api/count-primes", json=payload)
        job_id1 = resp1.json()["job_id"]
        job_id2 = resp2.json()["job_id"]
        result1 = await wait_for_job(client, job_id1)
        result2 = await wait_for_job(client, job_id2)
        assert result1["result"]["prime_count"] == result2["result"]["prime_count"]
