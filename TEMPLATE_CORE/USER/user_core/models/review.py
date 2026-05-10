"""AbstractReview — user-written review with polymorphic target."""
from __future__ import annotations

from sqlalchemy import CheckConstraint, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column

from user_core.db import Base
from user_core.enums import ReviewStatus
from user_core.mixins import PrimaryKeyMixin, TimestampMixin


class AbstractReview(PrimaryKeyMixin, TimestampMixin, Base):
    """Abstract base for a user review targeting any entity type.

    Uses a polymorphic reference pattern: ``target_type`` names the entity
    (e.g., ``"product"``, ``"seller"``, ``"service"``) and ``target_id`` is
    its primary key. This avoids a separate review table per entity.

    ``rating`` is constrained to 1–5 by a DB-level ``CHECK`` constraint.

    ``status`` drives moderation: reviews start as ``draft``, move to
    ``published`` after moderation (or immediately, depending on policy),
    can be ``flagged`` by other users, and ``removed`` by moderators.

    Concrete subclass must:
    1. Set ``__tablename__``.
    2. Add FK: ``user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))``.

    Merge the inherited ``__table_args__`` if adding your own constraints::

        __table_args__ = AbstractReview.__table_args__ + (
            UniqueConstraint("user_id", "target_type", "target_id"),
        )
    """

    __abstract__ = True
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating_range"),
        Index("ix_review_target", "target_type", "target_id"),
    )

    # Agents must add ForeignKey("user.id") in their concrete subclass
    user_id: Mapped[int] = mapped_column(nullable=False)
    target_type: Mapped[str] = mapped_column(nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str | None] = mapped_column(nullable=True)
    body: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status"),
        default=ReviewStatus.draft,
        nullable=False,
    )
