from __future__ import annotations
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime]


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    phone: Optional[str]
    timezone: Optional[str]
    locale: Optional[str]


class MembershipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tier: str
    started_at: datetime
    expires_at: Optional[datetime]

    @classmethod
    def from_orm_obj(cls, obj) -> "MembershipOut":
        return cls(
            tier=obj.tier.value if hasattr(obj.tier, "value") else str(obj.tier),
            started_at=obj.started_at,
            expires_at=obj.expires_at,
        )


class UserDetailOut(BaseModel):
    id: int
    email: str
    is_active: bool
    profile: Optional[ProfileOut]
    membership: Optional[MembershipOut]


class ActivityEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    occurred_at: datetime
    ip_address: Optional[str]


class UserOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    state: str
    total_amount: Optional[Decimal]
    created_at: datetime
