"""Reusable column mixins for all abstract models.

Import these into model files; do NOT import from model files here.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class PrimaryKeyMixin:
    """Adds an auto-incrementing integer primary key.

    Extension point: override ``id`` in your concrete subclass to use
    a UUID primary key::

        id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
    """

    id: Mapped[int] = mapped_column(primary_key=True)


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` columns managed by the DB."""

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class SoftDeleteMixin:
    """Opt-in soft-delete support via a nullable ``deleted_at`` timestamp.

    Use ``soft_delete()`` instead of ``session.delete(obj)`` to preserve the
    row. Filter active records with ``Model.deleted_at.is_(None)``.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, default=None)

    @property
    def is_deleted(self) -> bool:
        """Return True if the record has been soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark this record as deleted by setting ``deleted_at`` to now."""
        from datetime import timezone

        self.deleted_at = datetime.now(timezone.utc)
