from dataclasses import dataclass
from datetime import datetime
from domain.events.base_event import DomainEvent

@dataclass(frozen=True)
class NotificationSent(DomainEvent):
    sent_at: datetime