from celery import group, chord
from celery.result import AsyncResult
from app.celery_app import celery_app
from app.utils import count_primes_in_range, split_into_chunks
import time
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.count_primes_chunk")
def count_primes_chunk(self, start: int, end: int, chunk_index: int, total_chunks: int):
    """
    Count primes in a specific range (single chunk).
    """
    logger.info(
        f"Worker {self.request.id}: Processing chunk {chunk_index + 1}/{total_chunks} - range [{start}, {end}]"
    )

    count = count_primes_in_range(start, end)

    logger.info(
        f"Worker {self.request.id}: Chunk {chunk_index + 1}/{total_chunks} found {count} primes"
    )
    return count


@celery_app.task(name="app.tasks.aggregate_results")
def aggregate_results(results, n: int, start_time: float):

    total_primes = sum(results)
    duration = time.time() - start_time

    logger.info(f"Aggregation complete: {total_primes} primes found up to {n} in {duration:.2f}s")

    return {
        "prime_count": total_primes,
        "n": n,
        "duration_sec": round(duration, 2),
    }


@celery_app.task(bind=True, name="app.tasks.count_primes_distributed")
def count_primes_distributed(self, n: int, chunks: int):

    start_time = time.time()
    logger.info(f"Starting distributed prime counting: n={n}, chunks={chunks}")

    ranges = split_into_chunks(n, chunks)

    header = group(
        count_primes_chunk.s(start, end, idx, chunks)
        for idx, (start, end) in enumerate(ranges)
    )

    job = chord(header)(aggregate_results.s(n, start_time))

    self.update_state(
        state="STARTED",
        meta={
            "chord_id": job.id,
            "total": chunks,
            "completed": 0,
            "n": n,
        },
    )

    logger.info(f"Job {self.request.id} started with {chunks} chunks (chord ID: {job.id})")

    return job.id


def get_job_status(job_id: str) -> dict:

    result = AsyncResult(job_id, app=celery_app)

    response = {
        "state": result.state,
        "progress": None,
        "result": None,
        "error": None,
    }

    if result.state == "SUCCESS" and isinstance(result.result, str):
        chord_id = result.result
        logger.debug(f"Switching to chord {chord_id} for job {job_id}")
        result = AsyncResult(chord_id, app=celery_app)

    total = result.info.get("total", 0) if isinstance(result.info, dict) else 0

    children = list(result.children or [])
    completed = sum(1 for child in children if child.ready())

    if len(children) > 0:
        response["progress"] = {"completed": completed, "total": len(children)}
        total = len(children)
    elif total > 0:
        response["progress"] = {"completed": 0, "total": total}

    if result.state == "SUCCESS":
        response["state"] = "SUCCESS"
        response["result"] = result.result
        if response["progress"]:
            response["progress"]["completed"] = response["progress"]["total"]
    elif result.state == "FAILURE":
        response["state"] = "FAILURE"
        response["error"] = str(result.info) if result.info else "Unknown error"
    elif completed > 0 and completed < total:
        response["state"] = "PROGRESS"
    elif completed == total and result.state != "SUCCESS":
        response["state"] = "STARTED"
    elif result.state == "PENDING":
        response["state"] = "PENDING"
    else:
        response["state"] = "STARTED"

    return response
