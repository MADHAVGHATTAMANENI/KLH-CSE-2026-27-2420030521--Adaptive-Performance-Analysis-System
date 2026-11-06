from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.services.analytics_service import AnalyticsService
from app.models.benchmark import BenchmarkSuite, BenchmarkSuiteResult
from app.schemas.analytics import SuiteAnalyticsResponse, FileAnalyticsOverview
from app.core.exceptions import EntityNotFoundError

router = APIRouter(tags=["Analytics"])


@router.get(
    "/files/{file_id}/analytics",
    response_model=FileAnalyticsOverview,
    summary="Get longitudinal benchmark analytics for a source file",
)
async def get_file_analytics(
    file_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns historical overview across all completed benchmark suites for the file,
    including best speedup, optimal flag, and recent regressions.
    """
    return await AnalyticsService.get_file_analytics(db, file_id)


@router.get(
    "/benchmarks/suite/{suite_id}/analytics",
    response_model=SuiteAnalyticsResponse,
    summary="Get deep analytics for a specific benchmark suite",
)
async def get_suite_analytics(
    suite_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Computes speedups, binary size savings, Pareto frontier trade-offs,
    and regression diagnostics for a specific benchmark suite run.
    """
    suite = await db.get(BenchmarkSuite, suite_id)
    if not suite:
        raise EntityNotFoundError("Benchmark suite", suite_id)

    results_query = select(BenchmarkSuiteResult).where(
        BenchmarkSuiteResult.suite_id == suite_id
    )
    res = await db.execute(results_query)
    results = list(res.scalars().all())

    if not results:
        raise EntityNotFoundError("Benchmark suite results", suite_id)

    return AnalyticsService.analyze_suite_results(
        suite_id=suite.id,
        source_file_id=suite.source_file_id,
        results=results,
    )
