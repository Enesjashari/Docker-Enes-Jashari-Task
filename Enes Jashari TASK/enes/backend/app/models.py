from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class CountPrimesRequest(BaseModel):
    """Request model for counting primes."""
    n: int = Field(..., ge=10_000, description="Maximum number to check (must be >= 10,000)")
    chunks: int = Field(..., ge=1, le=128, description="Number of parallel chunks (1-128)")

    @field_validator('n')
    @classmethod
    def validate_n(cls, v):
        if v < 10_000:
            raise ValueError('n must be at least 10,000')
        return v

    @field_validator('chunks')
    @classmethod
    def validate_chunks(cls, v):
        if v < 1 or v > 128:
            raise ValueError('chunks must be between 1 and 128')
        return v


class CountPrimesResponse(BaseModel):
    job_id: str


class ProgressInfo(BaseModel):
    completed: int
    total: int


class ResultInfo(BaseModel):
    prime_count: int
    n: int
    duration_sec: float


class JobStatusResponse(BaseModel):
    state: Literal["PENDING", "STARTED", "PROGRESS", "SUCCESS", "FAILURE"]
    progress: Optional[ProgressInfo] = None
    result: Optional[ResultInfo] = None
    error: Optional[str] = None

