from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.models import CountPrimesRequest, CountPrimesResponse, JobStatusResponse
from app.tasks import count_primes_distributed, get_job_status
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Prime Counter API",
    description="Distributed prime counting service using Celery",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Prime Counter API is running",
        "docs": "/docs"
    }


@app.post(
    "/api/count-primes",
    response_model=CountPrimesResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Prime Counting"]
)
async def count_primes(request: CountPrimesRequest):

    try:
        logger.info(f"Received request: n={request.n}, chunks={request.chunks}")
        
        # Dispatch task to Celery
        task = count_primes_distributed.apply_async(
            args=[request.n, request.chunks]
        )
        
        logger.info(f"Job submitted with ID: {task.id}")
        
        return CountPrimesResponse(job_id=task.id)
    
    except Exception as e:
        logger.error(f"Error submitting job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit job: {str(e)}"
        )


@app.get(
    "/api/jobs/{job_id}",
    response_model=JobStatusResponse,
    tags=["Prime Counting"]
)
async def get_job(job_id: str):

    try:
        logger.info(f"Status request for job: {job_id}")
        
        job_status = get_job_status(job_id)
        
        logger.debug(f"Job {job_id} status: {job_status['state']}")
        
        return JobStatusResponse(**job_status)
    
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

