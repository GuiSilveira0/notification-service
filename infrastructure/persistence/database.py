from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from infrastructure.config import get_environment_variable

settings = get_environment_variable()
engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)