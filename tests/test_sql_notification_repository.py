import uuid
from datetime import datetime, timedelta, timezone

from domain.entities.notification import Notification
from domain.entities.recipient import Recipient
from domain.value_objects.channel import Channel
from domain.value_objects.email_address import EmailAddress
from domain.value_objects.phone_number import PhoneNumber
from domain.value_objects.priority import Priority
from domain.value_objects.status import Status
from infrastructure.persistence.sql_notification_repository import SqlNotificationRepository


def make_notification(**overrides) -> Notification:
    recipient = overrides.pop("recipient", None) or Recipient(
        name="Maria",
        metadata={"locale": "pt-BR"},
        email=EmailAddress("maria@example.com"),
        phone=PhoneNumber("+5511999998888"),
        webhook_url="https://example.com/hook",
    )
    params = dict(
        recipient=recipient,
        channel=Channel.EMAIL,
        priority=Priority.HIGH,
        content="Olá, Maria!",
        subject="Bem-vinda",
        template_id=uuid.uuid4(),
        metadata={"campaign": "welcome", "tags": ["a", "b"]},
        max_attempts=5,
    )
    params.update(overrides)
    return Notification(**params)


async def save_and_commit(session_factory, notification: Notification) -> None:
    async with session_factory() as session:
        await SqlNotificationRepository(session).save(notification)
        await session.commit()


async def load(session_factory, notification_id: uuid.UUID) -> Notification | None:
    async with session_factory() as session:
        return await SqlNotificationRepository(session).get_by_id(notification_id)


async def test_save_and_get_by_id_roundtrip(session_factory, created_ids):
    original = make_notification()
    created_ids.append(original.id)

    await save_and_commit(session_factory, original)
    loaded = await load(session_factory, original.id)

    assert loaded is not None
    assert loaded.id == original.id
    assert loaded.channel == Channel.EMAIL
    assert loaded.priority == Priority.HIGH
    assert loaded.status == Status.PENDING
    assert loaded.content == original.content
    assert loaded.subject == original.subject
    assert loaded.template_id == original.template_id
    assert loaded.metadata == original.metadata
    assert loaded.attempts == 0
    assert loaded.max_attempts == 5
    assert loaded.scheduled_at is None
    assert loaded.sent_at is None
    assert loaded.failed_at is None
    assert loaded.failure_reason is None


async def test_recipient_is_rehydrated(session_factory, created_ids):
    original = make_notification()
    created_ids.append(original.id)

    await save_and_commit(session_factory, original)
    loaded = await load(session_factory, original.id)

    assert loaded.recipient.name == "Maria"
    assert loaded.recipient.email == EmailAddress("maria@example.com")
    assert loaded.recipient.phone == PhoneNumber("+5511999998888")
    assert loaded.recipient.webhook_url == "https://example.com/hook"
    assert loaded.recipient.metadata == {"locale": "pt-BR"}


async def test_recipient_with_optional_fields_none(session_factory, created_ids):
    recipient = Recipient(name="Só Webhook", metadata={}, webhook_url="https://example.com/x")
    original = make_notification(
        recipient=recipient,
        channel=Channel.WEBHOOK,
        subject=None,
        template_id=None,
        metadata=None,
    )
    created_ids.append(original.id)

    await save_and_commit(session_factory, original)
    loaded = await load(session_factory, original.id)

    assert loaded.channel == Channel.WEBHOOK
    assert loaded.recipient.email is None
    assert loaded.recipient.phone is None
    assert loaded.recipient.webhook_url == "https://example.com/x"
    assert loaded.subject is None
    assert loaded.template_id is None
    assert loaded.metadata == {}


async def test_get_by_id_returns_none_when_not_found(session_factory):
    assert await load(session_factory, uuid.uuid4()) is None


async def test_save_without_commit_is_not_persisted(session_factory, created_ids):
    original = make_notification()
    created_ids.append(original.id)

    async with session_factory() as session:
        await SqlNotificationRepository(session).save(original)
        await session.rollback()

    assert await load(session_factory, original.id) is None


async def test_save_updates_existing_notification(session_factory, created_ids):
    original = make_notification()
    created_ids.append(original.id)
    await save_and_commit(session_factory, original)

    original.mark_as_queued()
    original.mark_as_processing()
    original.mark_as_sent()
    await save_and_commit(session_factory, original)

    loaded = await load(session_factory, original.id)
    assert loaded.status == Status.SENT
    assert loaded.attempts == 1
    assert loaded.sent_at == original.sent_at
    assert loaded.updated_at == original.updated_at


async def test_failed_notification_persists_reason(session_factory, created_ids):
    original = make_notification()
    created_ids.append(original.id)
    original.mark_as_queued()
    original.mark_as_processing()
    original.mark_as_failed("SMTP timeout")

    await save_and_commit(session_factory, original)
    loaded = await load(session_factory, original.id)

    assert loaded.status == Status.FAILED
    assert loaded.failure_reason == "SMTP timeout"
    assert loaded.failed_at == original.failed_at
    assert loaded.can_retry() is True


async def test_datetimes_are_stored_as_utc_aware(session_factory, created_ids):
    scheduled = datetime.now(timezone.utc) + timedelta(hours=1)
    original = make_notification(scheduled_at=scheduled)
    created_ids.append(original.id)

    await save_and_commit(session_factory, original)
    loaded = await load(session_factory, original.id)

    assert loaded.created_at.tzinfo is not None
    assert loaded.created_at.utcoffset() == timedelta(0)
    assert loaded.created_at == original.created_at
    assert loaded.scheduled_at == scheduled
    assert loaded.scheduled_at.utcoffset() == timedelta(0)


async def test_rehydrated_entity_has_no_pending_events(session_factory, created_ids):
    original = make_notification()
    created_ids.append(original.id)
    assert len(original.get_domain_events()) == 1

    await save_and_commit(session_factory, original)
    loaded = await load(session_factory, original.id)

    assert loaded.get_domain_events() == []
