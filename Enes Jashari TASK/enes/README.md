
A high-performance distributed application for counting prime numbers using parallel processing. Built with FastAPI, Celery, Redis, and React.


- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Progress Calculation](#progress-calculation)
- [Troubleshooting](#troubleshooting)


This application demonstrates distributed background computation by splitting prime number counting into parallel tasks executed by multiple Celery workers. Users can submit jobs through a web interface or API, and track progress in real-time.

### Use Case

Count all prime numbers from 1 to N by:
1. Splitting the range [1, N] into configurable chunks
2. Processing each chunk in parallel across multiple workers
3. Aggregating results and tracking progress
4. Displaying results with execution time

## 🏗️ Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI   │─────▶│    Redis    │
│  Frontend   │◀─────│   Backend   │◀─────│   Broker    │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   Celery    │
                     │   Workers   │
                     │  (Scalable) │
                     └─────────────┘
```


- Backend: FastAPI (Python 3.11)
- Task Queue: Celery 5.x
- Message Broker & Results Backend: Redis 7
- Frontend: React 18
- Orchestration: Docker & Docker Compose


- Distributed parallel processing with scalable workers
- Real-time progress tracking
- RESTful API with OpenAPI documentation
- Modern, responsive web interface
- Input validation and error handling
- Comprehensive logging
- Unit tests for core functionality
- One-command deployment with Docker Compose


- Docker (version 20.10+)
- Docker Compose (version 2.0+)

No other installations required! Everything runs in containers.


### 1. Clone the Repository

```bash
git clone <repository-url>
cd enes
```

### 2. Start All Services

Run the entire stack with 3 Celery workers:

```bash
docker compose up --build --scale worker=3
```

This will start:
- Redis on port 6379
- FastAPI on port 8000
- 3 Celery Workers (scalable)
- React Frontend on port 3000

### 3. Access the Application

- Web Interface: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- API Base URL: http://localhost:8000

### 4. Submit Your First Job

Via Web Interface:
1. Open http://localhost:3000
2. Enter N (e.g., 200000) and chunks (e.g., 16)
3. Click "Count Primes"
4. Watch real-time progress!

Via curl:
```bash
curl -X POST http://localhost:8000/api/count-primes \
  -H "Content-Type: application/json" \
  -d '{"n": 200000, "chunks": 16}'
```

### 5. Stopping the Application

```bash
docker compose down
```


### POST /api/count-primes

Submit a job to count prime numbers.

Request:
```json
{
  "n": 200000,
  "chunks": 16
}
```

Parameters:
- `n` (integer, required): Maximum number to check. Must be ≥ 10,000
- `chunks` (integer, required): Number of parallel tasks. Range: 1-128

Response (202 Accepted):
```json
{
  "job_id": "3c7e9f2a-4d5b-4c3a-9e8d-7f6a5b4c3d2e"
}
```

---

### GET /api/jobs/{job_id}

Get the status of a submitted job.

Response (200 OK):

While Processing:
```json
{
  "state": "PROGRESS",
  "progress": {
    "completed": 5,
    "total": 16
  },
  "result": null
}
```

When Complete:
```json
{
  "state": "SUCCESS",
  "progress": {
    "completed": 16,
    "total": 16
  },
  "result": {
    "prime_count": 17984,
    "n": 200000,
    "duration_sec": 2.4
  }
}
```

Job States:
- `PENDING`: Job queued, not started yet
- `STARTED`: Job has been picked up by a worker
- `PROGRESS`: Job is actively processing (some chunks completed)
- `SUCCESS`: Job completed successfully
- `FAILURE`: Job failed with an error


### Example 1: Basic Request

```bash
# Submit job
curl -X POST http://localhost:8000/api/count-primes \
  -H "Content-Type: application/json" \
  -d '{"n": 100000, "chunks": 8}'

# Response
# {"job_id": "abc123..."}
```

### Example 2: Check Job Status

```bash
# Get job status (replace with your job_id)
curl http://localhost:8000/api/jobs/abc123...

# Response
# {
#   "state": "SUCCESS",
#   "progress": {"completed": 8, "total": 8},
#   "result": {"prime_count": 9592, "n": 100000, "duration_sec": 1.2}
# }
```

### Example 3: Large Dataset with Many Workers

```bash
# Start with 8 workers
docker compose up --build --scale worker=8 -d

# Submit large job
curl -X POST http://localhost:8000/api/count-primes \
  -H "Content-Type: application/json" \
  -d '{"n": 1000000, "chunks": 64}'
```

### Example 4: Monitoring Logs

```bash
# View all logs
docker compose logs -f

# View only worker logs
docker compose logs -f worker

# View API logs
docker compose logs -f api
```


### Run Unit Tests

The project includes comprehensive unit tests for the prime counting logic.

```bash
# Enter the API container
docker compose exec api bash

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html
```

### Test Coverage

Tests cover:
- Prime number detection (`is_prime`)
- Range-based prime counting (`count_primes_in_range`)
- Work distribution (`split_into_chunks`)
- Edge cases and boundary conditions

### Manual Testing

```bash
# Test with minimum n
curl -X POST http://localhost:8000/api/count-primes \
  -H "Content-Type: application/json" \
  -d '{"n": 10000, "chunks": 4}'

# Test with single chunk
curl -X POST http://localhost:8000/api/count-primes \
  -H "Content-Type: application/json" \
  -d '{"n": 50000, "chunks": 1}'

# Test with maximum chunks
curl -X POST http://localhost:8000/api/count-primes \
  -H "Content-Type: application/json" \
  -d '{"n": 500000, "chunks": 128}'
```

### How Progress is Tracked

1. Job Submission: When a job is submitted, the range [1, N] is split into the requested number of chunks
2. Task Distribution: Each chunk is assigned to an available Celery worker as a separate task
3. Progress Updates: As workers complete their chunks, the system tracks:
   - `completed`: Number of finished chunks
   - `total`: Total number of chunks
4. State Transitions:
   - `PENDING` → `STARTED` → `PROGRESS` → `SUCCESS`
   - Progress percentage = (completed / total) × 100

### Example Progress Flow

For N=200,000 with 16 chunks:
### Chunk Distribution

The range [1, N] is divided into approximately equal chunks:

```python
# Example: N=100, chunks=4
# Chunk 1: [1, 25]
# Chunk 2: [26, 50]
# Chunk 3: [51, 75]
# Chunk 4: [76, 100]  # Last chunk may be slightly larger if N % chunks != 0
```


### Scaling Workers

Scale workers dynamically to match workload:

```bash
# Scale to 2 workers
docker compose up --scale worker=2

# Scale to 10 workers
docker compose up --scale worker=10
```

### Environment Variables

Create a `.env` file (optional):

```env
# Redis Configuration
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Frontend Configuration
REACT_APP_API_BASE_URL=http://localhost:8000
```


### Common Issues

1. Port Already in Use

```bash
# Error: port 3000 already allocated
# Solution: Stop the conflicting service or change the port in docker-compose.yml
docker compose down
lsof -ti:3000 | xargs kill -9
```

2. Workers Not Processing

```bash
# Check worker status
docker compose logs worker

# Restart workers
docker compose restart worker
```

3. Redis Connection Failed

```bash
# Check Redis health
docker compose ps redis

# Restart Redis
docker compose restart redis
```

4. CORS Errors

The API is configured to allow requests from http://localhost:3000. If using a different port, update `backend/app/main.py`:

```python
allow_origins=["http://localhost:YOUR_PORT"]
```

### Debug Mode

Enable detailed logging:

```bash
# View all container logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f redis
```

## 📝 Project Structure

```
enes/
├── docker-compose.yml          # Orchestration configuration
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
│
├── backend/                    # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .dockerignore
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application
│   │   ├── celery_app.py      # Celery configuration
│   │   ├── tasks.py           # Celery tasks
│   │   ├── models.py          # Pydantic models
│   │   └── utils.py           # Prime counting logic
│   └── tests/
│       ├── __init__.py
│       └── test_prime.py      # Unit tests
│
└── frontend/                   # React frontend
    ├── Dockerfile
    ├── package.json
    ├── .dockerignore
    ├── public/
    │   └── index.html
    └── src/
        ├── index.js
        ├── index.css
        ├── App.js             # Main application component
        └── App.css
```


- Submitting the form triggers a job and returns a job_id
- Parallel Celery workers execute chunked work (verified by scaling workers)
- Polling shows PENDING/STARTED/PROGRESS/SUCCESS and progress counts
- Result is consistent for the same n
- Entire stack runs locally via Docker Compose
- No manual installs beyond Docker required
- CORS configured for http://localhost:3000
- OpenAPI docs at http://localhost:8000/docs
- Clear logging for API and workers
- Input validation with 400 errors on bad inputs
- Unit tests for prime checker
- Typed code with Pydantic models


### Performance Tips

1. Optimal Chunk Size: For best performance, set chunks = number_of_workers × 2-4
2. Large N Values: For N > 1,000,000, use 32+ chunks and 8+ workers
3. Resource Limits: Each worker uses ~100-200MB RAM

### Algorithm Details

The prime checking algorithm uses trial division with optimizations:
- Early exit for even numbers (except 2)
- Check only up to √n
- Skip even divisors after checking for 2

Time Complexity: O(N√N / chunks) with parallel processing



This project is created as a technical assessment and is provided as-is for evaluation purposes.

