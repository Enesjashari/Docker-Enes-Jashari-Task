

## Prerequisites
- Docker (20.10+)
- Docker Compose (2.0+)

## Start the Application

```bash
# Clone and navigate to project
cd enes

# Start all services with 3 workers
docker compose up --build --scale worker=3
```

## Access

- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000

## Test It

### Via Web Interface
1. Open http://localhost:3000
2. Enter N=200000, chunks=16
3. Click "Count Primes"
4. Watch the progress!

### Via curl
```bash
# Submit job
curl -X POST http://localhost:8000/api/count-primes \
  -H "Content-Type: application/json" \
  -d '{"n": 200000, "chunks": 16}'

# Check status (use job_id from above)
curl http://localhost:8000/api/jobs/YOUR_JOB_ID
```

## Stop

```bash
docker compose down
```


