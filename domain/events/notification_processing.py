from dataclasses import dataclass
from domain.events.base_event import DomainEvent

@dataclass(frozen=True)
class NotificationProcessing(DomainEvent):
    attempt: int