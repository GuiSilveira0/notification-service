from uuid import UUID
from sqlalchemy import select, delete
from domain.entities.template import Template
from domain.value_objects.channel import Channel
from infrastructure.persistence.models import TemplateModel
from domain.repositories.template_repository import TemplateRepository

from sqlalchemy.ext.asyncio import AsyncSession

class SqlTemplateRepository(TemplateRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, template: Template) -> None:
        new_template = TemplateModel(
            id = template.id,
            name = template.name,
            channel = template.channel.value,
            subject_template = template.subject_template,
            body_template = template.body_template,
            created_at = template.created_at,
            updated_at = template.updated_at
        )

        await self._session.merge(new_template)

    async def get_by_id(self, template_id: UUID) -> Template | None:
        stmt = select(TemplateModel).where(TemplateModel.id == template_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._to_entity(model)

    async def get_by_name(self, name: str) -> Template | None:
        stmt = select(TemplateModel).where(TemplateModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._to_entity(model)

    async def list_all(self) -> list[Template]:
        stmt = select(TemplateModel).order_by(TemplateModel.name)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(item) for item in models]

    async def delete(self, template_id: UUID) -> None:
        stmt = delete(TemplateModel).where(TemplateModel.id == template_id)
        await self._session.execute(stmt)

    def _to_entity(self, model: TemplateModel) -> Template:
        template = Template(
            id = model.id,
            name = model.name,
            channel = Channel(model.channel),
            subject_template = model.subject_template,
            body_template = model.body_template,
        )

        template.created_at = model.created_at
        template.updated_at = model.updated_at

        return template