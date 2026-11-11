import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class NotificationModel(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_status_scheduled_at", "status", "scheduled_at"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    recipient_name: Mapped[str] = mapped_column(String(255))
    recipient_email: Mapped[str | None] = mapped_column(String(255))
    recipient_phone: Mapped[str | None] = mapped_column(String(32))
    recipient_webhook_url: Mapped[str | None] = mapped_column(String(2048))
    recipient_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    channel: Mapped[str] = mapped_column(String(32))
    priority: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(String)
    subject: Mapped[str | None] = mapped_column(String(998))
    template_id: Mapped[uuid.UUID | None] = mapped_column()
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class TemplateModel(Base):
    __tablename__ = "templates"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    channel: Mapped[str] = mapped_column(String(32))
    subject_template: Mapped[str | None] = mapped_column(String(998))
    body_template: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
