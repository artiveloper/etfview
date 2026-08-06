import asyncio

from etf_collector.scheduler.registry import JobId, JobRegistry, RegisteredJob


def _make_registry(run: RegisteredJob) -> JobRegistry:
    return JobRegistry({"open": run})


async def test_run_locked_executes_job_and_reports_not_running_after() -> None:
    calls = []

    async def run() -> None:
        calls.append(1)

    registry = _make_registry(RegisteredJob(name="open", lock=asyncio.Lock(), run=run))

    assert registry.is_running("open") is False
    result = await registry.run_locked("open")

    assert result is True
    assert calls == [1]
    assert registry.is_running("open") is False


async def test_run_locked_skips_when_already_running() -> None:
    started = asyncio.Event()
    release = asyncio.Event()

    async def run() -> None:
        started.set()
        await release.wait()

    registry = _make_registry(RegisteredJob(name="open", lock=asyncio.Lock(), run=run))

    first = asyncio.ensure_future(registry.run_locked("open"))
    await started.wait()

    assert registry.is_running("open") is True
    second_result = await registry.run_locked("open")
    assert second_result is False

    release.set()
    first_result = await first
    assert first_result is True
    assert registry.is_running("open") is False


def test_job_id_covers_all_registered_jobs() -> None:
    job_ids: tuple[JobId, ...] = ("open", "intraday", "close", "close_nxt")
    assert set(job_ids) == {"open", "intraday", "close", "close_nxt"}
