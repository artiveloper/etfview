# APScheduler 작업 구현

## 스케줄러 초기화

```python
# scheduler/setup.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from fastapi import FastAPI

def create_scheduler(engine_service) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

    scheduler.add_job(
        lambda: asyncio.create_task(start_trading_session(engine_service)),
        CronTrigger(hour=9, minute=0, day_of_week="mon-fri"),
        id="market_open",
    )
    scheduler.add_job(
        lambda: asyncio.create_task(stop_new_entries(engine_service)),
        CronTrigger(hour=15, minute=20, day_of_week="mon-fri"),
        id="stop_entries",
    )
    scheduler.add_job(
        lambda: asyncio.create_task(close_all_positions(engine_service)),
        CronTrigger(hour=15, minute=30, day_of_week="mon-fri"),
        id="market_close",
    )
    return scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler(app.state.engine_service)
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
```

## 09:00 장 시작 작업

```python
async def start_trading_session(engine_service) -> None:
    """손실 카운터 리셋, 진입 허용, WebSocket 구독 갱신."""
    for user_id, engine in engine_service.engines.items():
        if engine._settings.engine_status == "running":
            engine._risk.reset()
            engine.allow_new_entry = True

    await engine_service.scanner.run()
    await engine_service.shared_ws.start()
```

## 15:20 진입 중단 작업

```python
async def stop_new_entries(engine_service) -> None:
    """신규 진입만 중단. 보유 포지션은 유지."""
    for engine in engine_service.all_engines():
        engine.allow_new_entry = False
```

## 15:30 강제 청산 작업

```python
async def close_all_positions(engine_service, db_factory) -> None:
    """모든 포지션 시장가 청산 후 스캐너·WebSocket 중단."""
    async with db_factory() as db:
        for user_id, engine in engine_service.engines.items():
            for pos in engine._tracker.all():
                try:
                    await engine._client.sell_market(pos.code, pos.remaining)
                except Exception:
                    pass
            engine._tracker._positions.clear()
            await position_repo.close_all(db, user_id)

    await engine_service.scanner.stop()
    await engine_service.shared_ws.stop()
```

## lifespan 등록

```python
# main.py
from fastapi import FastAPI

app = FastAPI(lifespan=lifespan)
```

`@app.on_event("startup")` 는 deprecated. `lifespan` 컨텍스트 매니저를 사용한다.
