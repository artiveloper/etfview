"""등록된 스케줄 잡(open/intraday/close)을 수동으로 트리거하는 라우터."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from etf_collector.api.dependencies import require_api_token
from etf_collector.scheduler.registry import JobId, JobRegistry

router = APIRouter()


def _get_job_registry(request: Request) -> JobRegistry:
    registry: JobRegistry = request.app.state.job_registry
    return registry


@router.post(
    "/jobs/{job_id}/trigger",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_api_token)],
)
async def trigger_job(
    job_id: JobId,
    background_tasks: BackgroundTasks,
    registry: JobRegistry = Depends(_get_job_registry),
) -> dict[str, str]:
    if registry.is_running(job_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="job already running")
    background_tasks.add_task(registry.run_locked, job_id)
    return {"status": "accepted", "job_id": job_id}
