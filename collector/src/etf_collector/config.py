from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    kis_app_key: str
    kis_app_secret: str
    kis_env: str = "prod"

    supabase_url: str
    supabase_secret_key: str

    # 장 시작 전 유니버스 동기화 (1일 1회) — 이후 장중/마감 단계가 etf 테이블 존재를 전제한다.
    open_cron_day_of_week: str = "mon-fri"
    open_cron_hour: str = "8"
    open_cron_minute: str = "30"

    # 장중 일별 시세 갱신 (평일 09:00~15:30, 30분 간격) — 오늘 캔들을 실시간으로 채운다.
    intraday_cron_day_of_week: str = "mon-fri"
    intraday_cron_hour: str = "9-15"
    intraday_cron_minute: str = "0,30"

    # 장 마감 후 확정 동기화 (1일 1회) — 오늘 봉 확정 + EOD 시세 스냅샷 + 구성종목.
    close_cron_day_of_week: str = "mon-fri"
    close_cron_hour: str = "15"
    close_cron_minute: str = "40"

    @property
    def kis_base_url(self) -> str:
        if self.kis_env == "paper":
            return "https://openapivts.koreainvestment.com:29443"
        return "https://openapi.koreainvestment.com:9443"


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
