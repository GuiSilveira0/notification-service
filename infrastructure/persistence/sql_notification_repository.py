from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.repositories.notification_repository import NotificationRepository
from domain.entities.notification import Notification
from domain.entities.recipient import Recipient
from domain.value_objects.channel import Channel
from domain.value_objects.priority import Priority
from domain.value_objects.status import Status
from domain.value_objects.email_address import EmailAddress
from domain.value_objects.phone_number import PhoneNumber
from infrastructure.persistence.models import NotificationModel

class SqlNotificationRepository(NotificationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, notification: Notification) -> None:
        new_notification = NotificationModel(
            id = notification.id,
            recipient_name = notification.recipient.name,
            recipient_email = str(notification.recipient.email) if notification.recipient.email is not None else None,
            recipient_phone = str(notification.recipient.phone) if notification.recipient.phone is not None else None,
            recipient_webhook_url = notification.recipient.webhook_url,
            recipient_metadata = notification.recipient.metadata,
            channel = notification.channel.value,
            priority = notification.priority.value,
            status = notification.status.value,
            content = notification.content,
            subject = notification.subject,
            template_id = notification.template_id,
            meta_data = notification.metadata,
            attempts = notification.attempts,
            max_attempts = notification.max_attempts,
            scheduled_at = notification.scheduled_at,
            sent_at = notification.sent_at,
            failed_at = notification.failed_at,
            failure_reason = notification.failure_reason,
            created_at = notification.created_at,
            updated_at = notification.updated_at,
        )

        await self._session.merge(new_notification)

    async def get_by_id(self, notification_id: UUID) -> Notification | None:
        stmt = select(NotificationModel).where(NotificationModel.id == notification_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    def _to_entity(self, model: NotificationModel) -> Notification:
        recipient = Recipient(
            name=model.recipient_name,
            metadata=model.recipient_metadata or {},
            webhook_url=model.recipient_webhook_url,
            email=EmailAddress(model.recipient_email) if model.recipient_email is not None else None,
            phone=PhoneNumber(model.recipient_phone) if model.recipient_phone is not None else None,
        )

        notification = Notification(
            recipient=recipient,
            channel=Channel(model.channel),
            priority=Priority(model.priority),
            content=model.content,
            subject=model.subject,
            template_id=model.template_id,
            metadata=model.meta_data or {},
            max_attempts=model.max_attempts,
            scheduled_at=model.scheduled_at,
            id=model.id,
        )

        notification.status = Status(model.status)
        notification.attempts = model.attempts
        notification.sent_at = model.sent_at
        notification.failed_at = model.failed_at
        notification.failure_reason = model.failure_reason
        notification.created_at = model.created_at
        notification.updated_at = model.updated_at

        notification.clear_events()
        return notification