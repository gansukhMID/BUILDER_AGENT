from __future__ import annotations
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from user_core.models.user import AbstractUser
from user_core.models.oauth_account import AbstractOAuthAccount
from user_core.models.user_profile import AbstractUserProfile
from user_core.models.membership import AbstractMembership
from user_core.models.order import AbstractOrder, AbstractOrderLine
from user_core.models.purchase import AbstractPurchase
from user_core.models.review import AbstractReview
from user_core.models.activity_event import AbstractActivityEvent

# WMS and ECOMMERCE models are already concrete — just import to register them
import wms_core.models  # noqa: F401
import ecommerce_core.models  # noqa: F401


class User(AbstractUser):
    __tablename__ = "user"


class OAuthAccount(AbstractOAuthAccount):
    __tablename__ = "oauth_account"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)


class UserProfile(AbstractUserProfile):
    __tablename__ = "user_profile"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_profile_user"),)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)


class Membership(AbstractMembership):
    __tablename__ = "membership"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)


class Order(AbstractOrder):
    __tablename__ = "order"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)


class OrderLine(AbstractOrderLine):
    __tablename__ = "order_line"
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), nullable=False)


class Purchase(AbstractPurchase):
    __tablename__ = "purchase"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("order.id"), nullable=True)


class Review(AbstractReview):
    __tablename__ = "review"
    __table_args__ = AbstractReview.__table_args__ + (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_review_once"),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)


class ActivityEvent(AbstractActivityEvent):
    __tablename__ = "activity_event"
    __table_args__ = AbstractActivityEvent.__table_args__
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)
