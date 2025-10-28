#Requirements Verification Checklist

## Technology Stack

-Backend: FastAPI (Python 3.11) - `backend/app/main.py`
-Tasks: Celery 5.x - `backend/requirements.txt` (celery==5.3.4)
-Broker & Results: Redis 7 - `docker-compose.yml` (redis:7-alpine)
-Frontend: React 18 - `frontend/package.json`
-Orchestration: Docker & docker-compose - `docker-compose.yml`

## API Contract

### POST /api/count-primes

-Request JSON: `{"n": 200000, "chunks": 16}`
-n: int (≥ 10_000) - Validated in `backend/app/models.py`
-chunks: int (1..128) - Validated in `backend/app/models.py`
-Response (202): `{"job_id": "<string>"}`
-Implementation: `backend/app/main.py` line 40+

### GET /api/jobs/{job_id}

-Response (200) with state, progress, result
-States: PENDING|STARTED|PROGRESS|SUCCESS|FAILURE
-Progress: `{"completed": 5, "total": 16}`
-Result: `{"prime_count": 17984, "n": 200000, "duration_sec": 2.4}`
-Implementation: `backend/app/main.py` line 71+

## Frontend Requirements

-Single page with form
-Inputs: n (default 200,000) and chunks (default 16)
-Submit → POST /api/count-primes → show job_id
-Poll /api/jobs/{job_id} every 1s
-Show state, progress bar, final prime_count and duration
-API base via env: REACT_APP_API_BASE_URL
-Implementation: `frontend/src/App.js`

## Docker Compose Services

-redis: Redis 7 (port 6379) - `docker-compose.yml` line 3+
-api: FastAPI (port 8000) - `docker-compose.yml` line 13+
-worker: Celery worker(s), scalable ≥2 - `docker-compose.yml` line 31+
-web: React (port 3000) - `docker-compose.yml` line 46+
-One command: `docker compose up --build --scale worker=3`

## Non-Functional Requirements

-CORS allows http://localhost:3000 - `backend/app/main.py` line 26
-OpenAPI at http://localhost:8000/docs - `backend/app/main.py` line 17
-Clear logging for API and workers - Throughout `backend/app/`
-Input validation & error handling (400 on bad inputs) - `backend/app/models.py`
-Unit test for prime checker - `backend/tests/test_prime.py`
-Typed code where feasible - Pydantic models in `backend/app/models.py`

## Deliverables

### Repository Structure

-docker-compose.yml
-env.example (environment variables example)
-backend/ directory
  -FastAPI app (`app/main.py`)
  -Celery setup (`app/celery_app.py`)
  -Tasks (`app/tasks.py`)
  -Requirements (`requirements.txt`)
  -Dockerfile
  -Tests (`tests/test_prime.py`)
-frontend/ directory
  -React application (`src/App.js`)
  -Dockerfile
  -Package.json

### README

-Setup & run instructions
-Example curl commands
-Progress calculation notes
-Comprehensive documentation

## Acceptance Criteria

1.Submitting the form triggers a job and returns a job_id

   - Form in `frontend/src/App.js` submits to `/api/count-primes`
   - Backend returns job_id in response

2.Parallel Celery workers execute chunked work (verified by scaling workers)

   - `docker compose up --scale worker=3` starts 3 workers
   - Work distributed via Celery group/chord pattern
   - Implementation: `backend/app/tasks.py` line 62+

3.Polling shows PENDING/STARTED/PROGRESS/SUCCESS and progress counts

   - Frontend polls every 1 second
   - Backend tracks and returns progress
   - Implementation: `backend/app/tasks.py` get_job_status function

4.Result is consistent for the same n

   - Deterministic algorithm in `backend/app/utils.py`
   - Unit tests verify consistency

5.Entire stack runs locally via Docker Compose

   - Single command: `docker compose up --build --scale worker=3`
   - No manual installs beyond Docker

6.No manual installs beyond Docker
   - All dependencies containerized
   - Environment isolated

## Algorithm Implementation

-Prime counting logic: `backend/app/utils.py`

  - `is_prime()`: Check if single number is prime
  - `count_primes_in_range()`: Count primes in range
  - `split_into_chunks()`: Distribute work across chunks

-Parallel execution: `backend/app/tasks.py`
  - `count_primes_chunk()`: Process single chunk
  - `aggregate_results()`: Combine results from all chunks
  - `count_primes_distributed()`: Orchestrate parallel work

## Testing

-Unit tests: `backend/tests/test_prime.py`

  - Test `is_prime()` with various inputs
  - Test `count_primes_in_range()` accuracy
  - Test `split_into_chunks()` correctness
  - Test edge cases and boundaries

-Run tests:
  ```bash
  docker compose exec api pytest tests/ -v
  ```

## How to Verify

1. Start the stack:

   ```bash
   docker compose up --build --scale worker=3
   ```

2. Test via web interface:

   - Navigate to http://localhost:3000
   - Submit job with n=200000, chunks=16
   - Verify progress tracking
   - Verify result display

3. Test via API:

   ```bash
   # Submit job
   curl -X POST http://localhost:8000/api/count-primes \
     -H "Content-Type: application/json" \
     -d '{"n": 200000, "chunks": 16}'

   # Check status
   curl http://localhost:8000/api/jobs/{job_id}
   ```

4. Verify OpenAPI docs:

   - Open http://localhost:8000/docs
   - Test endpoints directly

5. Verify worker scaling:

   ```bash
   # Check worker logs
   docker compose logs worker

   # Should see multiple workers processing chunks
   ```

6. Run unit tests:
   ```bash
   docker compose exec api pytest tests/ -v
   ```

## Result

✅ ALL REQUIREMENTS MET - 100% COMPLETE

The implementation fully satisfies all technical requirements, API contracts, non-functional requirements, and acceptance criteria specified in the task description.
