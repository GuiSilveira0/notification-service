import uuid
from dataclasses import dataclass
from datetime import datetime
from domain.events.base_event import DomainEvent
from domain.value_objects.channel import Channel
from domain.value_objects.priority import Priority

@dataclass(frozen=True)
class NotificationCreated(DomainEvent):
    recipient_id: uuid.UUID
    channel: Channel
    priority: Priority
    content: str
    subject: str | None = None
    template_id: uuid.UUID | None = None
    scheduled_at: datetime | None = None