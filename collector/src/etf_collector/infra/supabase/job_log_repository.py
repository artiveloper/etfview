# job_execution_log 테이블 접근 리포지토리 — 배치 파이프라인 단계별 실행 이력 기록
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from supabase import Client

_TABLE = "job_execution_log"


class JobExecutionLogRepository:
    def __init__(self, supabase: Client) -> None:
        self._supabase = supabase

    def start(self, job_name: str) -> int:
        """작업 시작을 기록하고 로그 행 id를 반환한다."""
        result = (
            self._supabase.table(_TABLE)
            .insert(
                {
                    "job_name": job_name,
                    "started_at": datetime.now(UTC).isoformat(),
                    "execution_status": "RUNNING",
                }
            )
            .execute()
        )
        row = cast(dict[str, Any], result.data[0])
        log_id: int = row["id"]
        return log_id

    def succeed(self, log_id: int, affected_row_count: int) -> None:
        self._supabase.table(_TABLE).update(
            {
                "finished_at": datetime.now(UTC).isoformat(),
                "execution_status": "SUCCEEDED",
                "affected_row_count": affected_row_count,
            }
        ).eq("id", log_id).execute()

    def fail(self, log_id: int, error_message: str) -> None:
        self._supabase.table(_TABLE).update(
            {
                "finished_at": datetime.now(UTC).isoformat(),
                "execution_status": "FAILED",
                "error_message": error_message,
            }
        ).eq("id", log_id).execute()
