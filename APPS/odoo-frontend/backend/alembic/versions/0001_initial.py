"""Initial schema — all tables from USER, WMS, and ECOMMERCE templates.

Revision ID: 0001
Revises:
Create Date: 2026-05-11
"""
from __future__ import annotations
from typing import Union, Sequence

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Import all models to register them with their Base metadata
    from models.concrete import (  # noqa: F401
        User, OAuthAccount, UserProfile, Membership,
        Order, OrderLine, Purchase, Review, ActivityEvent,
    )
    import wms_core.models  # noqa: F401
    import ecommerce_core.models  # noqa: F401

    from user_core.db import Base as UserBase
    from wms_core.db import Base as WMSBase
    from ecommerce_core.db import Base as ECBase

    bind = op.get_bind()
    UserBase.metadata.create_all(bind=bind)
    WMSBase.metadata.create_all(bind=bind)
    ECBase.metadata.create_all(bind=bind)


def downgrade() -> None:
    from models.concrete import User  # noqa: F401 — triggers registration
    import wms_core.models  # noqa: F401
    import ecommerce_core.models  # noqa: F401

    from user_core.db import Base as UserBase
    from wms_core.db import Base as WMSBase
    from ecommerce_core.db import Base as ECBase

    bind = op.get_bind()
    ECBase.metadata.drop_all(bind=bind)
    WMSBase.metadata.drop_all(bind=bind)
    UserBase.metadata.drop_all(bind=bind)
