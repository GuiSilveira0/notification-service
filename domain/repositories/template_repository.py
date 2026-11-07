from abc import ABC, abstractmethod
from uuid import UUID
from domain.entities.template import Template

class TemplateRepository(ABC):
    @abstractmethod
    async def save(self, template: Template) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, template_id: UUID) -> Template | None:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Template | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Template]:
        pass

    @abstractmethod
    async def delete(self, template_id: UUID) -> None:
        pass