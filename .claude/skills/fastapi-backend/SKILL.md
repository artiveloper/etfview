---
name: fastapi-backend
description: FastAPI 백엔드 스킬. MySQL+SQLAlchemy async, APScheduler(09:00 장시작/15:20 진입중단/15:30 정리), asyncio.Queue pub/sub 시세 브로드캐스트, JWT HS256 인증, AES-256-GCM API키 암호화, 관리자/사용자 권한 분리, SSE 실시간 스트리밍. DB 모델, 스케줄러, 인증, 암호화, 라우터, 서비스 구현 시 반드시 이 스킬을 사용할 것.
---

## 프로젝트 구조 (도메인 드리븐)

```
backend/
├── main.py                        # FastAPI app + lifespan + 라우터 등록
├── core/
│   ├── config.py                  # pydantic-settings (Settings 싱글턴)
│   ├── database.py                # AsyncEngine + AsyncSession + get_db
│   ├── security.py                # JWT 발급·검증, AES-256, bcrypt
│   └── dependencies.py            # get_current_user, require_admin
├── domains/
│   ├── auth/
│   │   ├── router.py              # POST /auth/login, POST /auth/refresh
│   │   ├── service.py             # 자격증명 검증 + JWT 발급
│   │   └── schema.py              # LoginRequest, TokenResponse, RefreshRequest
│   ├── user/
│   │   ├── router.py              # 사용자 설정 CRUD, 관리자 계정 관리
│   │   ├── service.py
│   │   ├── repository.py
│   │   ├── schema.py              # UserSettingsRead/Write, UserResponse
│   │   └── model.py               # User, UserSettings ORM
│   ├── trading/
│   │   ├── router.py              # POST /engine/start|stop, GET /engine/status
│   │   ├── service.py             # TradingEngine 인스턴스 풀 관리
│   │   └── schema.py
│   ├── position/
│   │   ├── router.py              # GET /positions, SSE /stream/positions|pnl
│   │   ├── service.py             # asyncio.Queue 브로드캐스트
│   │   ├── repository.py
│   │   ├── schema.py
│   │   └── model.py               # Position ORM
│   ├── order/
│   │   ├── router.py              # GET /orders (당일/이력)
│   │   ├── repository.py
│   │   ├── schema.py
│   │   └── model.py               # Order ORM
│   └── scanner/
│       ├── router.py              # SSE /stream/scanner
│       └── service.py             # StockScanner 참조
├── broker/
│   └── kiwoom/                    # kiwoom-api-engineer 담당
│       ├── rate_limiter.py
│       ├── token_manager.py
│       ├── ws_manager.py
│       ├── rest_client.py
│       ├── shared_ws.py
│       └── user_client.py
├── engine/                        # trading-engine-engineer 담당
└── scheduler/
    └── jobs.py                    # APScheduler 작업 정의
```

**도메인 격리 원칙**: 도메인 변경은 해당 `domains/{name}/` 내부에서 완결. 도메인 간 직접 import 금지 — 공통 의존성은 `core/`를 통해서만 주입.

## 핵심 의존성

```toml
[tool.poetry.dependencies]
fastapi = "^0.115"
uvicorn = {extras = ["standard"], version = "^0.34"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0"}
aiomysql = "^0.2"
alembic = "^1.14"
apscheduler = "^3.10"
pydantic-settings = "^2.7"
python-jose = {extras = ["cryptography"], version = "^3.3"}
passlib = {extras = ["bcrypt"], version = "^1.7"}
cryptography = "^44"
aiohttp = "^3.11"
msgspec = "^0.19"
orjson = "^3.10"
sse-starlette = "^2.2"
```

## APScheduler 통합

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

scheduler.add_job(
    start_trading_session, CronTrigger(hour=9, minute=0, day_of_week="mon-fri"),
    id="market_open",
)
scheduler.add_job(
    stop_new_entries, CronTrigger(hour=15, minute=20, day_of_week="mon-fri"),
    id="stop_entries",
)
scheduler.add_job(
    close_all_positions, CronTrigger(hour=15, minute=30, day_of_week="mon-fri"),
    id="market_close",
)
```

> 각 작업 상세 구현: `references/scheduler.md`

## asyncio.Queue Pub/Sub

```python
class MarketDataService:
    """SharedWSClient → 구독 엔진들에 브로드캐스트."""

    def __init__(self) -> None:
        self._queues: dict[int, asyncio.Queue] = {}  # user_id → queue

    def register(self, user_id: int, q: asyncio.Queue) -> None:
        self._queues[user_id] = q

    def unregister(self, user_id: int) -> None:
        self._queues.pop(user_id, None)

    async def broadcast(self, msg: dict) -> None:
        for q in self._queues.values():
            try:
                q.put_nowait(msg)
            except asyncio.QueueFull:
                pass  # 처리 느린 엔진 드롭
```

## Auth.js 연동 인증

### 흐름

```
Next.js 로그인 폼
  → Auth.js Credentials authorize()
  → POST /auth/login (FastAPI)   ← 자격증명 검증 + access/refresh 토큰 발급
  → Auth.js 세션에 accessToken + refreshToken + accessTokenExpires 저장
  → 이후 API 호출: Authorization: Bearer {accessToken}
  → FastAPI: python-jose로 JWT 검증

Silent Refresh (만료 5분 전):
  → Auth.js JWT callback → POST /auth/refresh
  → 새 access/refresh 토큰으로 세션 쿠키 갱신
```

### 토큰 설정

| 항목 | 값 |
|------|-----|
| Access Token 만료 | 30분 (`ACCESS_TOKEN_EXPIRE_MINUTES = 30`) |
| Refresh Token 만료 | 7일 (`REFRESH_TOKEN_EXPIRE_DAYS = 7`) |
| 갱신 트리거 | 만료 5분 전 (`accessTokenExpires - 5 * 60_000`) |

### security.py

```python
from datetime import UTC, datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
```

### /auth/login + /auth/refresh 엔드포인트

```python
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int        # seconds (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    user_id: str
    email: str
    role: str

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

@router.post("/login")
async def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    # 사용자 검증 후
    claims = {"sub": str(user.id), "email": user.email, "role": user.role}
    return TokenResponse(
        access_token=create_access_token(claims),
        refresh_token=create_refresh_token(claims),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        email=user.email,
        role=user.role,
    )

@router.post("/refresh")
async def refresh(payload: RefreshRequest, db: DbSession) -> RefreshResponse:
    return service.refresh(db, payload.refresh_token)

# service.refresh (DB 조회 추가 전까지 동기)
def refresh(_db: AsyncSession, refresh_token: str) -> RefreshResponse:
    payload = verify_refresh_token(refresh_token)
    claims = {"sub": payload["sub"], "email": payload["email"], "role": payload["role"]}
    return RefreshResponse(
        access_token=create_access_token(claims),
        refresh_token=create_refresh_token(claims),   # rotation
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
```

### Bearer 토큰 검증 (공통 Depends)

```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise ValueError("wrong token type")
        user_id = payload["sub"]
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await user_repo.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401)
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user
```

## AES-256-GCM 암호화

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_key = bytes.fromhex(settings.aes_key_hex)  # 64 hex chars = 32 bytes

def encrypt_api_key(plaintext: str) -> bytes:
    nonce = os.urandom(12)
    ct = AESGCM(_key).encrypt(nonce, plaintext.encode(), None)
    return nonce + ct  # 12 + len(ct) bytes

def decrypt_api_key(blob: bytes) -> str:
    return AESGCM(_key).decrypt(blob[:12], blob[12:], None).decode()
```

## SSE 엔드포인트

```python
from sse_starlette.sse import EventSourceResponse
import orjson, asyncio

@router.get("/stream/positions")
async def stream_positions(
    request: Request,
    user: User = Depends(get_current_user),
    svc: EngineService = Depends(get_engine_service),
):
    q: asyncio.Queue = svc.get_position_queue(user.id)

    async def gen():
        while not await request.is_disconnected():
            try:
                data = await asyncio.wait_for(q.get(), timeout=30.0)
                yield {"data": orjson.dumps(data).decode()}
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": ""}

    return EventSourceResponse(gen())
```

## 라우터 등록 (main.py)

```python
from domains.auth.router    import router as auth_router
from domains.user.router    import router as user_router
from domains.trading.router import router as trading_router
from domains.position.router import router as position_router
from domains.order.router   import router as order_router
from domains.scanner.router import router as scanner_router

app.include_router(auth_router,     prefix="/auth",     tags=["auth"])
app.include_router(user_router,     prefix="/users",    tags=["users"])
app.include_router(trading_router,  prefix="/engine",   tags=["trading"])
app.include_router(position_router, prefix="/positions",tags=["positions"])
app.include_router(order_router,    prefix="/orders",   tags=["orders"])
app.include_router(scanner_router,  prefix="/scanner",  tags=["scanner"])
```

## 라우터 목록

| 도메인 | 경로 | 권한 | 설명 |
|--------|------|------|------|
| auth | `POST /auth/login` | 공개 | access+refresh 토큰 발급 |
| auth | `POST /auth/refresh` | 공개 | silent refresh (refresh token → 새 토큰 쌍) |
| user | `POST /users/admin` | 관리자 | 사용자 생성 |
| user | `DELETE /users/admin/{id}` | 관리자 | 사용자 삭제 |
| user | `GET/PUT /users/settings` | 사용자 | 운영설정 조회/수정 |
| trading | `POST /engine/start` | 사용자 | 엔진 시작 |
| trading | `POST /engine/stop` | 사용자 | 엔진 중지 |
| trading | `GET /engine/status` | 사용자 | 엔진 상태 |
| position | `GET /positions/` | 사용자 | 현재 포지션 |
| position | `GET /positions/stream` | 사용자 | 포지션 SSE |
| position | `GET /positions/pnl/stream` | 사용자 | 손익 SSE |
| order | `GET /orders/` | 사용자 | 주문 내역 |
| scanner | `GET /scanner/stream` | 사용자 | 스캐너 SSE |

> DB 모델 전문(User, UserSettings, Position, Order): `references/db-models.md`
> APScheduler 작업 구현: `references/scheduler.md`
