from dataclasses import dataclass
from domain.events.base_event import DomainEvent

@dataclass(frozen=True, kw_only=True)
class NotificationRetried(DomainEvent):
    retry_attempt: int