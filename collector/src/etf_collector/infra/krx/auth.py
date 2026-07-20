# KRX 데이터포털(data.krx.co.kr)에 로그인해 세션 쿠키를 확보하는 모듈
from __future__ import annotations

from typing import Any

import httpx

from etf_collector.config import Settings

_LOGIN_PAGE_URL = "https://data.krx.co.kr/contents/MDC/COMS/client/view/login.jsp?site=mdc"
_LOGIN_URL = "https://data.krx.co.kr/contents/MDC/COMS/client/MDCCOMS001D1.cmd"
_SUCCESS_CODE = "CD001"

# KRX WAF가 브라우저 User-Agent가 없는 요청을 403으로 차단한다.
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


async def login(client: httpx.AsyncClient, settings: Settings) -> None:
    """KRX 데이터포털에 로그인해 client의 쿠키 저장소에 세션을 채운다.

    이 계정으로 브라우저에 동시 로그인돼 있으면 중복 로그인(CD011)으로 실패한다.
    """
    await client.get(_LOGIN_PAGE_URL, headers={"User-Agent": _USER_AGENT})
    response = await client.post(
        _LOGIN_URL,
        data={
            "mbrNm": "",
            "telNo": "",
            "di": "",
            "certType": "",
            "mbrId": settings.krx_username,
            "pw": settings.krx_password,
        },
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": _LOGIN_PAGE_URL,
            "User-Agent": _USER_AGENT,
        },
    )
    response.raise_for_status()
    body: dict[str, Any] = response.json()
    if body.get("_error_code") != _SUCCESS_CODE:
        raise RuntimeError(f"KRX 로그인 실패: {body.get('_error_message')}")
