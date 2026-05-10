"""Re-exports all abstract models and their related enums.

Importing this module registers nothing with ``Base.metadata`` — all classes
use ``__abstract__ = True``.
"""
from user_core.models.user import AbstractUser
from user_core.models.oauth_account import AbstractOAuthAccount
from user_core.models.user_profile import AbstractUserProfile
from user_core.models.membership import AbstractMembership
from user_core.models.order import AbstractOrder, AbstractOrderLine
from user_core.models.purchase import AbstractPurchase
from user_core.models.review import AbstractReview
from user_core.models.activity_event import AbstractActivityEvent

__all__ = [
    "AbstractUser",
    "AbstractOAuthAccount",
    "AbstractUserProfile",
    "AbstractMembership",
    "AbstractOrder",
    "AbstractOrderLine",
    "AbstractPurchase",
    "AbstractReview",
    "AbstractActivityEvent",
]
