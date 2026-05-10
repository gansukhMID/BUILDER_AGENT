"""AbstractActivityEvent — append-only audit / activity log."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Index, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from user_core.db import Base
from user_core.mixins import PrimaryKeyMixin


class AbstractActivityEvent(PrimaryKeyMixin, Base):
    """Abstract base for an append-only user activity / audit event.

    Intentionally excludes ``updated_at`` — events are immutable after
    insert. ``occurred_at`` is set by the database server on insert.

    ``event_type`` is a free-form string. Agents define their own taxonomy
    (e.g., ``"user.login"``, ``"order.placed"``, ``"profile.updated"``).

    ``metadata_`` (trailing underscore avoids shadowing Python's built-in
    ``metadata``) stores arbitrary structured payload as a JSON dict.

    ``user_id`` is nullable to support pre-authentication events
    (anonymous page views, failed login attempts).

    Concrete subclass must:
    1. Set ``__tablename__``.
    2. Add FK (optional but recommended)::

           user_id: Mapped[int | None] = mapped_column(
               ForeignKey("user.id"), nullable=True
           )

    Merge the inherited ``__table_args__`` if adding your own indexes::

        __table_args__ = AbstractActivityEvent.__table_args__ + (
            Index("ix_activity_event_type", "event_type"),
        )
    """

    __abstract__ = True
    __table_args__ = (
        Index("ix_activity_event_user_occurred", "user_id", "occurred_at"),
    )

    # Agents should add ForeignKey("user.id") nullable=True in their subclass
    user_id: Mapped[int | None] = mapped_column(nullable=True)
    event_type: Mapped[str] = mapped_column(nullable=False)
    ip_address: Mapped[str | None] = mapped_column(nullable=True)
    user_agent: Mapped[str | None] = mapped_column(nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    # Server-side default — not writable after insert
    occurred_at: Mapped[datetime] = mapped_column(server_default=func.now())
