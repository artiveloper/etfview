import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from zoneinfo import ZoneInfo

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s - %(message)s"
_LOG_TIMEZONE = ZoneInfo("Asia/Seoul")


class _KstFormatter(logging.Formatter):
    """컨테이너 OS 시간대(대개 UTC)와 무관하게 로그 시각을 항상 KST로 남긴다.

    스케줄러도 ZoneInfo("Asia/Seoul")로 cron을 해석하므로, 로그 시각을 그와
    다른 시간대로 남기면 실행 시각을 눈으로 확인할 때 혼란을 준다.
    """

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=_LOG_TIMEZONE)
        return dt.strftime(datefmt) if datefmt else dt.isoformat(sep=" ", timespec="milliseconds")


def configure_logging(level: int = logging.INFO) -> None:
    formatter = _KstFormatter(_LOG_FORMAT)
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    log_dir = os.environ.get("LOG_DIR")
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                Path(log_dir) / "etf-collector.log",
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
        )

    for handler in handlers:
        handler.setFormatter(formatter)

    logging.basicConfig(level=level, handlers=handlers)
