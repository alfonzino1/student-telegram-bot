
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("subjects.id"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("subjects.id"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )
    timezone: Mapped[str] = mapped_column(
        String(50), default="UTC"
    )
    reminder_time: Mapped[str] = mapped_column(
        String(5), default="17:00"
    )
    reminders_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True
    )

    def __repr__(self) -> str:
        return f"UserSettings(user_id={self.user_id}, timezone={self.timezone})"