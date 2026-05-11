from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException
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
)

router = APIRouter()


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
