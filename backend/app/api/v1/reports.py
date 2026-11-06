from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.report_service import ReportService

router = APIRouter(tags=["Reports"])


@router.get(
    "/benchmarks/suite/{suite_id}/report",
    summary="Export performance audit report in Markdown or JSON format",
)
async def export_suite_report(
    suite_id: str,
    format: str = Query("json", enum=["json", "markdown"]),
    download: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """
    Exports a comprehensive performance audit report including hardware details,
    Clang version, execution time matrix, speedup curves, Pareto analysis,
    and ML recommendation rationale.
    """
    if format == "markdown":
        md_text = await ReportService.generate_markdown_report(db, suite_id)
        headers = {}
        if download:
            headers["Content-Disposition"] = f'attachment; filename="compilerx_report_{suite_id[:8]}.md"'
        return PlainTextResponse(content=md_text, media_type="text/markdown", headers=headers)

    json_data = await ReportService.generate_json_report(db, suite_id)
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="compilerx_report_{suite_id[:8]}.json"'
    return JSONResponse(content=json_data, headers=headers)
