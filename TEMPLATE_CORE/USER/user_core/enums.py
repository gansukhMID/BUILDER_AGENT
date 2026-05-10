"""All domain enums for user_core.

Centralised here to prevent circular imports: model files import enums,
never each other. Agents may extend these enums but should not modify
this file — define new enum classes in their application package instead.
"""
import enum


class MembershipTier(str, enum.Enum):
    """Subscription tier for a user's membership."""

    free = "free"
    pro = "pro"
    vip = "vip"


class OrderState(str, enum.Enum):
    """Lifecycle states for an order.

    Allowed transitions::

        draft → placed → confirmed → shipped → delivered
                       ↘                      ↗
                        → cancelled
    """

    draft = "draft"
    placed = "placed"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class PurchaseStatus(str, enum.Enum):
    """Payment / purchase outcome status."""

    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class ReviewStatus(str, enum.Enum):
    """Moderation status for a user review."""

    draft = "draft"
    published = "published"
    flagged = "flagged"
    removed = "removed"
