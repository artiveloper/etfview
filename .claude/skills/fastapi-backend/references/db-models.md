# DB 모델

## SQLAlchemy Async 설정

```python
# db/engine.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## User

```python
from sqlalchemy import Boolean, Column, DateTime, Integer, LargeBinary, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 키움 API 키 (AES-256-GCM 암호화, nonce||ciphertext)
    kiwoom_app_key_enc = Column(LargeBinary, nullable=True)
    kiwoom_app_secret_enc = Column(LargeBinary, nullable=True)

    settings = relationship("UserSettings", back_populates="user", uselist=False)
    positions = relationship("Position", back_populates="user")
    orders = relationship("Order", back_populates="user")
```

## UserSettings

```python
class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    operating_capital = Column(Integer, default=0)      # 운영자금 (원)
    max_positions = Column(Integer, default=3)          # 동시 보유 종목 수
    max_daily_loss = Column(Integer, default=100_000)   # 당일 최대 손실 (원)
    mode = Column(String(10), default="paper")           # "real" | "paper"
    engine_status = Column(String(20), default="stopped")

    user = relationship("User", back_populates="settings")
```

## Position

```python
class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_code = Column(String(10), nullable=False)
    stock_name = Column(String(50))
    quantity = Column(Integer, nullable=False)
    remaining = Column(Integer, nullable=False)
    avg_price = Column(Integer, nullable=False)
    partial_sold = Column(Boolean, default=False)
    entered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="positions")
```

## Order

```python
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_code = Column(String(10), nullable=False)
    stock_name = Column(String(50))
    side = Column(String(4), nullable=False)       # "buy" | "sell"
    order_type = Column(String(20))               # "market" | "limit"
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=True)
    executed_price = Column(Integer, nullable=True)
    status = Column(String(20), default="pending") # "pending" | "filled" | "cancelled"
    reason = Column(String(50), nullable=True)     # "pattern_a", "stop_loss", ...
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    executed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="orders")
```

## Alembic 초기 마이그레이션

```bash
alembic init alembic
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

`alembic.ini`의 `sqlalchemy.url`은 `.env`에서 로드.
