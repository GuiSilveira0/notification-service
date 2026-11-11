import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from infrastructure.config import get_environment_variable
from infrastructure.persistence.models import NotificationModel, TemplateModel


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine(get_environment_variable().DATABASE_URL, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture
async def created_ids(session_factory):
    ids: list = []
    yield ids
    if ids:
        async with session_factory() as session:
            await session.execute(delete(NotificationModel).where(NotificationModel.id.in_(ids)))
            await session.commit()


@pytest_asyncio.fixture
async def created_template_ids(session_factory):
    ids: list = []
    yield ids
    if ids:
        async with session_factory() as session:
            await session.execute(delete(TemplateModel).where(TemplateModel.id.in_(ids)))
            await session.commit()
