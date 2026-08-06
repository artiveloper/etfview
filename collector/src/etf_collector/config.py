from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    kis_app_key: str
    kis_app_secret: str
    kis_env: str = "prod"

    krx_username: str
    krx_password: str

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

    # NXT 후장 마감 후 재동기화 (1일 1회) — NXT는 20:00까지 거래되어 15:40 마감 스케줄만으로는
    # NXT 반영분 최종가를 놓친다. run_daily_close를 한 번 더 돌려 최종가를 다시 확정한다.
    close_nxt_cron_day_of_week: str = "mon-fri"
    close_nxt_cron_hour: str = "20"
    close_nxt_cron_minute: str = "30"

    @property
    def kis_base_url(self) -> str:
        if self.kis_env == "paper":
            return "https://openapivts.koreainvestment.com:29443"
        return "https://openapi.koreainvestment.com:9443"


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
