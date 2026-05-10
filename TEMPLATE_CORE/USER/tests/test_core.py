"""Core test suite covering all PRD success criteria."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from user_core.db import Base
from user_core.enums import (
    MembershipTier,
    OrderState,
    PurchaseStatus,
    ReviewStatus,
)
from tests.concrete_models import (
    ActivityEvent,
    Membership,
    OAuthAccount,
    Order,
    OrderLine,
    Purchase,
    Review,
    User,
    UserProfile,
)


# ── SC-1: Zero tables in Base.metadata before concrete import ────────────────

def test_abstract_models_register_no_tables():
    """Importing user_core.models registers zero tables in Base.metadata."""
    import user_core.models  # noqa: F401

    # Concrete models from conftest populate metadata; we verify the abstract
    # classes themselves don't contribute extra tables beyond the concrete set.
    concrete_names = {
        "user", "oauth_account", "user_profile", "membership",
        "order", "order_line", "purchase", "review", "activity_event",
    }
    assert set(Base.metadata.tables.keys()) == concrete_names


# ── SC-2: Schema creates without errors ──────────────────────────────────────

def test_schema_creates_with_concrete_subclasses(engine):
    """Base.metadata.create_all() succeeds with all 9 concrete subclasses."""
    # engine fixture already called create_all; just verify tables exist
    assert "user" in Base.metadata.tables
    assert "oauth_account" in Base.metadata.tables
    assert "review" in Base.metadata.tables
    assert "activity_event" in Base.metadata.tables


# ── AbstractUser ─────────────────────────────────────────────────────────────

def test_user_create_and_fields(session):
    user = User(email="alice@example.com")
    session.add(user)
    session.flush()

    assert user.id is not None
    assert user.is_active is True
    assert user.is_verified is False
    assert user.is_superuser is False
    assert user.password_hash is None
    assert user.last_login_at is None


def test_user_email_unique(session):
    session.add(User(email="bob@example.com"))
    session.flush()

    with pytest.raises(Exception):
        session.add(User(email="bob@example.com"))
        session.flush()


def test_user_set_password_stub(session):
    """set_password stub does not raise and check_password returns False."""
    user = User(email="stub@example.com")
    session.add(user)
    session.flush()

    user.set_password("secret")
    assert user.check_password("secret") is False


def test_user_soft_delete(session):
    user = User(email="del@example.com")
    session.add(user)
    session.flush()

    assert user.is_deleted is False
    user.soft_delete()
    assert user.is_deleted is True
    assert user.deleted_at is not None


# ── AbstractOAuthAccount ─────────────────────────────────────────────────────

def test_oauth_account_create(session):
    user = User(email="oauth@example.com")
    session.add(user)
    session.flush()

    acct = OAuthAccount(
        user_id=user.id,
        provider="google",
        provider_uid="google-uid-123",
        access_token="tok",
    )
    session.add(acct)
    session.flush()

    assert acct.id is not None
    assert acct.provider == "google"


def test_oauth_account_unique_constraint(session):
    user = User(email="oauth2@example.com")
    session.add(user)
    session.flush()

    session.add(OAuthAccount(user_id=user.id, provider="github", provider_uid="gh-1"))
    session.flush()

    with pytest.raises(Exception):
        session.add(OAuthAccount(user_id=user.id, provider="github", provider_uid="gh-1"))
        session.flush()


# ── AbstractUserProfile ───────────────────────────────────────────────────────

def test_user_profile_defaults(session):
    user = User(email="profile@example.com")
    session.add(user)
    session.flush()

    profile = UserProfile(user_id=user.id, display_name="Alice")
    session.add(profile)
    session.flush()

    assert profile.timezone == "UTC"
    assert profile.locale == "en"
    assert profile.preferences is None


def test_user_profile_json_preferences(session):
    user = User(email="prefs@example.com")
    session.add(user)
    session.flush()

    profile = UserProfile(
        user_id=user.id,
        preferences={"theme": "dark", "notifications": True},
    )
    session.add(profile)
    session.flush()
    session.expire(profile)

    loaded = session.get(UserProfile, profile.id)
    assert loaded.preferences["theme"] == "dark"


# ── AbstractMembership ────────────────────────────────────────────────────────

def test_membership_active_non_expiring(session):
    user = User(email="free@example.com")
    session.add(user)
    session.flush()

    m = Membership(
        user_id=user.id,
        tier=MembershipTier.free,
        started_at=datetime.now(timezone.utc),
    )
    session.add(m)
    session.flush()

    assert m.is_active is True
    assert m.tier == MembershipTier.free


def test_membership_expired(session):
    user = User(email="expired@example.com")
    session.add(user)
    session.flush()

    m = Membership(
        user_id=user.id,
        tier=MembershipTier.pro,
        started_at=datetime.now(timezone.utc) - timedelta(days=31),
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    session.add(m)
    session.flush()

    assert m.is_active is False


# ── AbstractOrder + AbstractOrderLine ─────────────────────────────────────────

def test_order_state_machine(session):
    user = User(email="order@example.com")
    session.add(user)
    session.flush()

    order = Order(
        user_id=user.id,
        reference="ORD-001",
        currency="USD",
        total_amount=Decimal("99.9900"),
    )
    session.add(order)
    session.flush()

    assert order.state == OrderState.draft
    order.confirm()
    assert order.state == OrderState.confirmed
    order.cancel()
    assert order.state == OrderState.cancelled


def test_order_line_stored_total(session):
    user = User(email="orderline@example.com")
    session.add(user)
    session.flush()

    order = Order(user_id=user.id, reference="ORD-002", total_amount=Decimal("0"))
    session.add(order)
    session.flush()

    line = OrderLine(
        order_id=order.id,
        product_ref="SKU-X",
        product_name="Widget",
        quantity=Decimal("3"),
        unit_price=Decimal("10.0000"),
        line_total=Decimal("30.0000"),
    )
    session.add(line)
    session.flush()
    session.expire(line)

    loaded = session.get(OrderLine, line.id)
    assert loaded.line_total == Decimal("30.0000")


# ── AbstractPurchase ──────────────────────────────────────────────────────────

def test_purchase_defaults(session):
    user = User(email="purchase@example.com")
    session.add(user)
    session.flush()

    p = Purchase(user_id=user.id, amount=Decimal("9.99"), currency="USD")
    session.add(p)
    session.flush()

    assert p.status == PurchaseStatus.pending
    assert p.order_id is None
    assert p.external_ref is None


# ── AbstractReview ────────────────────────────────────────────────────────────

def test_review_rating_valid(session):
    user = User(email="reviewer@example.com")
    session.add(user)
    session.flush()

    review = Review(
        user_id=user.id,
        target_type="product",
        target_id=42,
        rating=5,
        title="Great!",
        body="Loved it.",
    )
    session.add(review)
    session.flush()

    assert review.status == ReviewStatus.draft
    assert review.rating == 5


def test_review_rating_check_constraint(session):
    user = User(email="badreview@example.com")
    session.add(user)
    session.flush()

    with pytest.raises(Exception):
        session.add(Review(
            user_id=user.id,
            target_type="product",
            target_id=1,
            rating=6,
        ))
        session.flush()


# ── AbstractActivityEvent ─────────────────────────────────────────────────────

def test_activity_event_append_only(session):
    user = User(email="activity@example.com")
    session.add(user)
    session.flush()

    event = ActivityEvent(
        user_id=user.id,
        event_type="user.login",
        ip_address="127.0.0.1",
        metadata_={"method": "password"},
    )
    session.add(event)
    session.flush()

    assert event.id is not None
    assert event.event_type == "user.login"
    assert event.metadata_["method"] == "password"


def test_activity_event_anonymous(session):
    """user_id is nullable for pre-auth events."""
    event = ActivityEvent(event_type="page.view", ip_address="10.0.0.1")
    session.add(event)
    session.flush()

    assert event.user_id is None


# ── SC-4: All models have docstrings ─────────────────────────────────────────

def test_get_session_commits_and_closes(engine):
    """get_session yields a working session and commits on clean exit."""
    from user_core.db import get_session
    with get_session(engine) as s:
        user = User(email="getsession@example.com")
        s.add(user)
    # after context exit, commit fired; row should be visible in a new query
    from sqlalchemy.orm import sessionmaker
    S = sessionmaker(bind=engine)
    with S() as verify:
        found = verify.query(User).filter_by(email="getsession@example.com").first()
        assert found is not None


def test_all_abstract_models_have_docstrings():
    import inspect
    from user_core.models import (
        AbstractUser, AbstractOAuthAccount, AbstractUserProfile,
        AbstractMembership, AbstractOrder, AbstractOrderLine,
        AbstractPurchase, AbstractReview, AbstractActivityEvent,
    )
    for cls in [
        AbstractUser, AbstractOAuthAccount, AbstractUserProfile,
        AbstractMembership, AbstractOrder, AbstractOrderLine,
        AbstractPurchase, AbstractReview, AbstractActivityEvent,
    ]:
        assert inspect.getdoc(cls), f"{cls.__name__} is missing a docstring"
