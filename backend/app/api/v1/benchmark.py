from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.core.exceptions import EntityNotFoundError
from app.models.benchmark import BenchmarkSuite
from app.schemas.benchmark import (
    BenchmarkRunRequest,
    BenchmarkRunResponse,
    BenchmarkSuiteRequest,
    BenchmarkSuiteResponse,
    SuiteResultItem,
)
from app.services.benchmark_service import BenchmarkService

router = APIRouter(tags=["Performance & Benchmarking"])


@router.post(
    "/compilations/{compilation_id}/benchmark",
    response_model=BenchmarkRunResponse,
    summary="Execute multi-run benchmark for a specific compilation",
)
async def benchmark_compilation(
    compilation_id: str,
    payload: BenchmarkRunRequest,
    db: AsyncSession = Depends(get_db),
):
    bench_service = BenchmarkService(db)
    return await bench_service.run_benchmark(
        compilation_id=compilation_id,
        num_runs=payload.num_runs,
        stdin_payload=payload.stdin_payload,
    )


@router.post(
    "/files/{file_id}/benchmark-suite",
    response_model=BenchmarkSuiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Orchestrate full multi-level benchmark suite (-O0 to -O3)",
)
async def run_benchmark_suite(
    file_id: str,
    payload: BenchmarkSuiteRequest,
    db: AsyncSession = Depends(get_db),
):
    bench_service = BenchmarkService(db)
    return await bench_service.run_suite(
        source_file_id=file_id,
        runs_per_level=payload.runs_per_level,
        stdin_payload=payload.stdin_payload,
    )


@router.get(
    "/benchmarks/suite/{suite_id}",
    response_model=BenchmarkSuiteResponse,
    summary="Get status and results of a benchmark suite",
)
async def get_suite_status(
    suite_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BenchmarkSuite).where(BenchmarkSuite.id == suite_id)
    result = await db.execute(stmt)
    suite = result.scalar_one_or_none()
    if not suite:
        raise EntityNotFoundError("BenchmarkSuite", suite_id)

    result_items = [
        SuiteResultItem(
            optimization_level=r.optimization_level,
            mean_time_ms=r.mean_time_ms,
            median_time_ms=r.median_time_ms,
            stddev_time_ms=r.stddev_time_ms,
            min_time_ms=r.min_time_ms,
            max_time_ms=r.max_time_ms,
            variance_cv_percent=r.variance_cv_percent,
            speedup_vs_o0=r.speedup_vs_o0,
            peak_memory_kb=r.peak_memory_kb,
            binary_size_bytes=r.binary_size_bytes,
            has_high_variance=r.has_high_variance,
        )
        for r in suite.results
    ]

    return BenchmarkSuiteResponse(
        suite_id=suite.id,
        source_file_id=suite.source_file_id,
        status=suite.status,
        started_at=suite.started_at,
        completed_at=suite.completed_at,
        results=result_items,
    )

