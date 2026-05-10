"""AbstractUserProfile — extended personal profile data for a user."""
from __future__ import annotations

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from user_core.db import Base
from user_core.mixins import PrimaryKeyMixin, TimestampMixin


class AbstractUserProfile(PrimaryKeyMixin, TimestampMixin, Base):
    """Abstract base for extended user profile information.

    Maintains a 1-to-1 relationship with the user entity. The FK and unique
    constraint must be defined in the concrete subclass::

        class UserProfile(AbstractUserProfile):
            __tablename__ = "user_profile"
            user_id: Mapped[int] = mapped_column(
                ForeignKey("user.id"), unique=True
            )

    ``preferences`` is a free-form JSON dict for agent-defined settings
    (UI theme, notification flags, etc.).
    """

    __abstract__ = True

    # Agents must add ForeignKey("user.id") and unique=True in their subclass
    user_id: Mapped[int] = mapped_column(nullable=False)
    display_name: Mapped[str | None] = mapped_column(nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)
    bio: Mapped[str | None] = mapped_column(nullable=True)
    phone: Mapped[str | None] = mapped_column(nullable=True)
    timezone: Mapped[str] = mapped_column(default="UTC", nullable=False)
    locale: Mapped[str] = mapped_column(default="en", nullable=False)
    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
