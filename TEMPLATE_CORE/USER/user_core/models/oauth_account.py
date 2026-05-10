"""AbstractOAuthAccount — linked third-party OAuth provider account."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from user_core.db import Base
from user_core.mixins import PrimaryKeyMixin, TimestampMixin


class AbstractOAuthAccount(PrimaryKeyMixin, TimestampMixin, Base):
    """Abstract base for OAuth provider accounts linked to a user.

    Supports linking multiple providers per user (Google, GitHub, Facebook,
    etc.). One user may have many ``OAuthAccount`` rows — one per provider.

    Concrete subclass must:
    1. Set ``__tablename__``.
    2. Override ``user_id`` with a proper ``ForeignKey`` pointing to the
       user table::

           user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    The token fields are stored as plain strings. Agents are responsible for
    field-level encryption if required.
    """

    __abstract__ = True
    __table_args__ = (
        UniqueConstraint("provider", "provider_uid", name="uq_oauth_provider_uid"),
    )

    # Agents must add ForeignKey("user.id") in their concrete subclass
    user_id: Mapped[int] = mapped_column(nullable=False)
    provider: Mapped[str] = mapped_column(nullable=False)
    provider_uid: Mapped[str] = mapped_column(nullable=False)
    access_token: Mapped[str | None] = mapped_column(nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
