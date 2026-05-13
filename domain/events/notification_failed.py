import uuid
from dataclasses import dataclass
from datetime import datetime
from domain.events.base_event import DomainEvent

@dataclass(frozen=True)
class NotificationFailed(DomainEvent):
    failed_at: datetime
    failure_reason: str
    attempt: int