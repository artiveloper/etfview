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

    sync_cron_day_of_week: str = "mon-fri"
    sync_cron_hour: int = 16
    sync_cron_minute: int = 10

    @property
    def kis_base_url(self) -> str:
        if self.kis_env == "paper":
            return "https://openapivts.koreainvestment.com:29443"
        return "https://openapi.koreainvestment.com:9443"


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
