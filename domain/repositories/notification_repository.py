from uuid import UUID
from abc import ABC, abstractmethod
from domain.entities.notification import Notification

class NotificationRepository(ABC):
    @abstractmethod
    async def save(self, notification: Notification) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> Notification | None:
        pass