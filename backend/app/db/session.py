from sqlalchemy.orm import declarative_base
from app.config import settings

Base = declarative_base()

class DummyScalar:
    def all(self):
        return []

class DummyResult:
    def scalars(self):
        return DummyScalar()

class DummySession:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    def add(self, obj):
        pass
    async def get(self, entity, ident):
        return None
    async def execute(self, statement):
        return DummyResult()
    async def commit(self):
        pass
    async def close(self):
        pass

def DummySessionLocal():
    return DummySession()

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    except Exception:
        engine = None
        AsyncSessionLocal = DummySessionLocal
except Exception:
    engine = None
    AsyncSessionLocal = DummySessionLocal

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
