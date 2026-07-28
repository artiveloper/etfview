"""Bearer 토큰 인증 의존성 — 새 시크릿 없이 KIS_APP_KEY 값을 API 토큰으로 재사용한다."""

from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from etf_collector.config import Settings

_bearer_scheme = HTTPBearer(auto_error=False)


def require_api_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> None:
    settings: Settings = request.app.state.settings
    if credentials is None or not secrets.compare_digest(
        credentials.credentials, settings.kis_app_key
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
