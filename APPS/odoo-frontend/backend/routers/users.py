from __future__ import annotations
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from models.concrete import User, UserProfile, Membership, ActivityEvent, Order
from schemas.users import (
    UserOut,
    UserDetailOut,
    ProfileOut,
    MembershipOut,
    ActivityEventOut,
    UserOrderOut,
    UserIn,
    UserUpdate,
    ProfileUpdate,
    MembershipIn,
    MembershipUpdate,
)
from auth_utils import hash_password
from user_core.crud import (
    create_user,
    update_user,
    create_user_profile,
    update_user_profile,
    create_membership,
    update_membership,
)
from user_core.enums import MembershipTier

router = APIRouter()


@router.get("/health")
def users_health():
    return {"router": "users", "status": "ok"}


@router.get("", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()


@router.get("/{user_id}", response_model=UserDetailOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    )
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user_id)
        .order_by(Membership.started_at.desc())
        .first()
    )

    profile_out = ProfileOut.model_validate(profile) if profile else None
    membership_out = (
        MembershipOut.from_orm_obj(membership) if membership else None
    )

    return UserDetailOut(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        profile=profile_out,
        membership=membership_out,
    )


@router.get("/{user_id}/activity", response_model=List[ActivityEventOut])
def get_activity(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return (
        db.query(ActivityEvent)
        .filter(ActivityEvent.user_id == user_id)
        .order_by(ActivityEvent.occurred_at.desc())
        .limit(50)
        .all()
    )


@router.get("/{user_id}/orders", response_model=List[UserOrderOut])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(Order).filter(Order.user_id == user_id).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(body: UserIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(
        db,
        User,
        email=body.email,
        password_hash=hash_password(body.password),
        is_superuser=body.is_superuser,
    )
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserDetailOut)
def update_user_endpoint(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = update_user(db, User, user_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user_id)
        .order_by(Membership.started_at.desc())
        .first()
    )
    return UserDetailOut(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        profile=ProfileOut.model_validate(profile) if profile else None,
        membership=MembershipOut.from_orm_obj(membership) if membership else None,
    )


@router.post("/{user_id}/profile", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def create_profile_endpoint(user_id: int, body: ProfileUpdate, db: Session = Depends(get_db)):
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    existing = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    profile = create_user_profile(db, UserProfile, user_id=user_id, **body.model_dump(exclude_none=True))
    db.commit()
    db.refresh(profile)
    return ProfileOut.model_validate(profile)


@router.put("/{user_id}/profile", response_model=ProfileOut)
def update_profile_endpoint(user_id: int, body: ProfileUpdate, db: Session = Depends(get_db)):
    try:
        profile = update_user_profile(db, UserProfile, user_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(profile)
    return ProfileOut.model_validate(profile)


@router.post("/{user_id}/memberships", response_model=MembershipOut, status_code=status.HTTP_201_CREATED)
def create_membership_endpoint(user_id: int, body: MembershipIn, db: Session = Depends(get_db)):
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    try:
        tier = MembershipTier(body.tier)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {body.tier}")
    membership = create_membership(
        db,
        Membership,
        user_id=user_id,
        tier=tier,
        started_at=datetime.now(timezone.utc),
        expires_at=body.expires_at,
    )
    db.commit()
    db.refresh(membership)
    return MembershipOut.from_orm_obj(membership)


@router.put("/{user_id}/memberships/{membership_id}", response_model=MembershipOut)
def update_membership_endpoint(
    user_id: int, membership_id: int, body: MembershipUpdate, db: Session = Depends(get_db)
):
    membership = db.get(Membership, membership_id)
    if not membership or membership.user_id != user_id:
        raise HTTPException(status_code=404, detail="Membership not found")
    kwargs = body.model_dump(exclude_none=True)
    if "tier" in kwargs:
        try:
            kwargs["tier"] = MembershipTier(kwargs["tier"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tier: {kwargs['tier']}")
    try:
        membership = update_membership(db, Membership, membership_id, **kwargs)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(membership)
    return MembershipOut.from_orm_obj(membership)
