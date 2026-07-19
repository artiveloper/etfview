# KIS API가 HTTP 200과 함께 반환하는 비즈니스 레벨 에러(rt_cd/msg_cd) 예외 계층
from __future__ import annotations


class KisApiError(Exception):
    """KIS TR 응답이 rt_cd != '0'으로 실패를 나타낼 때 발생하는 베이스 예외.

    KIS는 초당 호출 제한 초과 등도 HTTP 200 + 응답 바디의 rt_cd/msg_cd로
    표현하므로, httpx.HTTPError(전송 계층 에러)와는 별도로 이 계층을 둔다.
    """

    def __init__(self, msg_cd: str, msg1: str) -> None:
        self.msg_cd = msg_cd
        self.msg1 = msg1
        super().__init__(f"[{msg_cd}] {msg1}")


class KisRateLimitError(KisApiError):
    """초당 거래건수 초과 등 재시도하면 성공할 수 있는 에러.

    정확한 msg_cd 목록(예: EGW00201)은 제공된 docs에는 없고 KIS 개발자포럼에
    공개된 값이다 — 실제 연동 전 최신 공지로 재확인이 필요하다.
    """


class KisAuthenticationError(KisApiError):
    """접근토큰이 만료·무효화되어 발생하는 에러. 캐시를 무효화하고 재발급해야 한다."""
