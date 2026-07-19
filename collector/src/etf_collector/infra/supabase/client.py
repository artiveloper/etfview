from etf_collector.config import Settings
from supabase import Client, create_client


def get_supabase_client(settings: Settings) -> Client:
    """secret key로 생성하는 서버 전용 클라이언트 — RLS를 우회한다."""
    return create_client(settings.supabase_url, settings.supabase_secret_key)
