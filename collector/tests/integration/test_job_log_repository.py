from unittest.mock import MagicMock

from etf_collector.infra.supabase.job_log_repository import JobExecutionLogRepository


def test_start_returns_new_log_id() -> None:
    supabase = MagicMock()
    supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": 42}]
    repository = JobExecutionLogRepository(supabase)

    log_id = repository.start("sync_etf_info")

    assert log_id == 42
    supabase.table.assert_called_with("job_execution_log")
    insert_payload = supabase.table.return_value.insert.call_args.args[0]
    assert insert_payload["job_name"] == "sync_etf_info"
    assert insert_payload["execution_status"] == "RUNNING"


def test_succeed_updates_status_and_row_count() -> None:
    supabase = MagicMock()
    repository = JobExecutionLogRepository(supabase)

    repository.succeed(42, 10)

    table = supabase.table.return_value
    payload = table.update.call_args.args[0]
    assert payload["execution_status"] == "SUCCEEDED"
    assert payload["affected_row_count"] == 10
    table.update.return_value.eq.assert_called_once_with("id", 42)


def test_fail_updates_status_and_error_message() -> None:
    supabase = MagicMock()
    repository = JobExecutionLogRepository(supabase)

    repository.fail(42, "boom")

    table = supabase.table.return_value
    payload = table.update.call_args.args[0]
    assert payload["execution_status"] == "FAILED"
    assert payload["error_message"] == "boom"
