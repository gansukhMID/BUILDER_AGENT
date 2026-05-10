"""AbstractMembership — user subscription / membership tier record."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from user_core.db import Base
from user_core.enums import MembershipTier
from user_core.mixins import PrimaryKeyMixin, TimestampMixin


class AbstractMembership(PrimaryKeyMixin, TimestampMixin, Base):
    """Abstract base for a user's membership tier record.

    A user may have multiple membership rows over time (tier history). The
    active membership is the row where ``cancelled_at`` is None and either
    ``expires_at`` is None or ``expires_at`` is in the future.

    Concrete subclass must set ``__tablename__`` and add a FK::

        class Membership(AbstractMembership):
            __tablename__ = "membership"
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    To gate features by tier, read ``membership.tier`` and compare to
    ``MembershipTier.pro`` or ``MembershipTier.vip``.
    """

    __abstract__ = True

    # Agents must add ForeignKey("user.id") in their concrete subclass
    user_id: Mapped[int] = mapped_column(nullable=False)
    tier: Mapped[MembershipTier] = mapped_column(
        Enum(MembershipTier, name="membership_tier"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(nullable=False)
    # None = non-expiring (typical for Free tier)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(nullable=True)

    @property
    def is_active(self) -> bool:
        """Return True if this membership record is currently active.

        A record is active when it has not been cancelled and has not expired.
        Override as a SQLAlchemy ``hybrid_property`` in your subclass for
        server-side filtering support.
        """
        from datetime import timezone

        if self.cancelled_at is not None:
            return False
        if self.expires_at is None:
            return True
        return datetime.now(timezone.utc) < self.expires_at.replace(
            tzinfo=timezone.utc
        )
