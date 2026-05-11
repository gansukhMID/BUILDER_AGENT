from __future__ import annotations
from datetime import datetime
from typing import Optional, Type, TypeVar

from sqlalchemy.orm import Session

from user_core.enums import MembershipTier

T = TypeVar("T")


# ── User ──────────────────────────────────────────────────────────────────────

def create_user(
    session: Session,
    model_cls: Type[T],
    *,
    email: str,
    password_hash: Optional[str] = None,
    is_active: bool = True,
    is_superuser: bool = False,
) -> T:
    user = model_cls(
        email=email,
        password_hash=password_hash,
        is_active=is_active,
        is_superuser=is_superuser,
    )
    session.add(user)
    session.flush()
    return user


def update_user(
    session: Session,
    model_cls: Type[T],
    user_id: int,
    *,
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    password_hash: Optional[str] = None,
) -> T:
    user = session.get(model_cls, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")
    if email is not None:
        user.email = email
    if is_active is not None:
        user.is_active = is_active
    if is_verified is not None:
        user.is_verified = is_verified
    if is_superuser is not None:
        user.is_superuser = is_superuser
    if password_hash is not None:
        user.password_hash = password_hash
    session.flush()
    return user


# ── UserProfile ───────────────────────────────────────────────────────────────

def create_user_profile(
    session: Session,
    model_cls: Type[T],
    *,
    user_id: int,
    display_name: Optional[str] = None,
    bio: Optional[str] = None,
    phone: Optional[str] = None,
    timezone: str = "UTC",
    locale: str = "en",
    avatar_url: Optional[str] = None,
) -> T:
    profile = model_cls(
        user_id=user_id,
        display_name=display_name,
        bio=bio,
        phone=phone,
        timezone=timezone,
        locale=locale,
        avatar_url=avatar_url,
    )
    session.add(profile)
    session.flush()
    return profile


def update_user_profile(
    session: Session,
    model_cls: Type[T],
    user_id: int,
    *,
    display_name: Optional[str] = None,
    bio: Optional[str] = None,
    phone: Optional[str] = None,
    timezone: Optional[str] = None,
    locale: Optional[str] = None,
    avatar_url: Optional[str] = None,
) -> T:
    profile = session.query(model_cls).filter_by(user_id=user_id).first()
    if profile is None:
        raise ValueError(f"UserProfile for user {user_id} not found")
    if display_name is not None:
        profile.display_name = display_name
    if bio is not None:
        profile.bio = bio
    if phone is not None:
        profile.phone = phone
    if timezone is not None:
        profile.timezone = timezone
    if locale is not None:
        profile.locale = locale
    if avatar_url is not None:
        profile.avatar_url = avatar_url
    session.flush()
    return profile


# ── Membership ────────────────────────────────────────────────────────────────

def create_membership(
    session: Session,
    model_cls: Type[T],
    *,
    user_id: int,
    tier: MembershipTier,
    started_at: datetime,
    expires_at: Optional[datetime] = None,
) -> T:
    membership = model_cls(
        user_id=user_id,
        tier=tier,
        started_at=started_at,
        expires_at=expires_at,
    )
    session.add(membership)
    session.flush()
    return membership


def update_membership(
    session: Session,
    model_cls: Type[T],
    membership_id: int,
    *,
    tier: Optional[MembershipTier] = None,
    expires_at: Optional[datetime] = None,
    cancelled_at: Optional[datetime] = None,
) -> T:
    membership = session.get(model_cls, membership_id)
    if membership is None:
        raise ValueError(f"Membership {membership_id} not found")
    if tier is not None:
        membership.tier = tier
    if expires_at is not None:
        membership.expires_at = expires_at
    if cancelled_at is not None:
        membership.cancelled_at = cancelled_at
    session.flush()
    return membership
