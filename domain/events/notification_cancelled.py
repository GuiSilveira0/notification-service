import uuid
from dataclasses import dataclass
from domain.events.base_event import DomainEvent

@dataclass(frozen=True, kw_only=True)
class NotificationCancelled(DomainEvent):
    pass