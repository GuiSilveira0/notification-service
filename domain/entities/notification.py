import uuid
from datetime import datetime, timezone
from domain.events.base_event import DomainEvent
from domain.events.notification_cancelled import NotificationCancelled
from domain.events.notification_created import NotificationCreated
from domain.events.notification_failed import NotificationFailed
from domain.events.notification_processing import NotificationProcessing
from domain.events.notification_queued import NotificationQueued
from domain.events.notification_retried import NotificationRetried
from domain.events.notification_sent import NotificationSent
from domain.value_objects.channel import Channel
from domain.value_objects.priority import Priority
from domain.value_objects.status import Status
from domain.entities.recipient import Recipient

class Notification:
    def __init__(
        self,
        recipient: Recipient,
        channel: Channel,
        priority: Priority,
        content: str,
        subject: str | None = None,
        template_id: uuid.UUID | None = None,
        metadata: dict | None = None,
        max_attempts: int = 3,
        scheduled_at: datetime | None = None,
        id: uuid.UUID | None = None,
    ):
        self.id = id or uuid.uuid4()
        self.recipient = recipient
        self.channel = channel
        self.priority = priority
        self.status = Status.PENDING
        self.content = content
        self.subject = subject
        self.template_id = template_id
        self.metadata = metadata or {}
        self.attempts = 0
        self.max_attempts = max_attempts
        self.scheduled_at = scheduled_at
        self.sent_at = None
        self.failed_at = None
        self.failure_reason = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self._domain_events = []

        self._add_event(NotificationCreated(
            notification_id=self.id,
            recipient_id=self.recipient.id,
            channel=self.channel,
            priority=self.priority,
            content=self.content,
            subject=self.subject,
            template_id=self.template_id,
            scheduled_at=self.scheduled_at,
        ))

    def _add_event(self, event: DomainEvent):
        self._domain_events.append(event)
    
    def get_domain_events(self) -> list[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_events(self):
        self._domain_events.clear()

    def mark_as_queued(self):
        self._transition_to(Status.QUEUED)
        self._add_event(NotificationQueued(
            notification_id=self.id
        ))

    def mark_as_processing(self):
        self._transition_to(Status.PROCESSING)
        self.attempts += 1
        self._add_event(NotificationProcessing(
            notification_id=self.id,
            attempt=self.attempts
        ))

    def mark_as_sent(self):
        self._transition_to(Status.SENT)
        self.sent_at = datetime.now(timezone.utc)
        self._add_event(NotificationSent(
            sent_at=self.sent_at,
            notification_id=self.id,
        ))

    def mark_as_failed(self, reason: str):
        self._transition_to(Status.FAILED)
        self.failed_at = datetime.now(timezone.utc)
        self.failure_reason = reason
        self._add_event(NotificationFailed(
            notification_id=self.id,
            failed_at=self.failed_at,
            failure_reason=self.failure_reason,
            attempt=self.attempts,
        ))

    def cancel(self):
        self._transition_to(Status.CANCELLED)
        self._add_event(NotificationCancelled(
            notification_id=self.id
        ))

    def can_retry(self) -> bool:
        return self.status == Status.FAILED and self.attempts < self.max_attempts

    def retry(self):
        if not self.can_retry():
            raise ValueError("Notificação não pode ser reenviada")
        self._transition_to(Status.QUEUED)
        self.failed_at = None
        self.failure_reason = None
        self._add_event(NotificationRetried(
            notification_id=self.id,
            retry_attempt=self.attempts
        ))

    def _transition_to(self, new_status: Status):
        if not self.status.can_transition_to(new_status):
            raise ValueError(
                f"Transição inválida: {self.status.value} → {new_status.value}"
            )
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Notification):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
