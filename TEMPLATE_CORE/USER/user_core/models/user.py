"""AbstractUser — core user entity for authentication and identity.

Analogous to Django's AbstractBaseUser or Odoo's res.users (simplified).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from user_core.db import Base
from user_core.mixins import PrimaryKeyMixin, SoftDeleteMixin, TimestampMixin


class AbstractUser(PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Abstract base for the application's primary user entity.

    Covers email/password credentials and OAuth-only accounts (password_hash
    is nullable). Password hashing is intentionally **not** implemented here —
    override ``set_password`` and ``check_password`` with your chosen library
    (bcrypt, argon2-cffi, etc.).

    Extension example::

        class User(AbstractUser):
            __tablename__ = "user"
            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))

    Agents should add a FK on ``user_id`` columns in related models.
    """

    __abstract__ = True
    __table_args__ = (
        Index("ix_user_email", "email"),
    )

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)

    def set_password(self, raw: str) -> None:
        """Hash and store *raw* as the password.

        **Stub** — override in your concrete subclass::

            from passlib.hash import argon2
            def set_password(self, raw: str) -> None:
                self.password_hash = argon2.hash(raw)
        """

    def check_password(self, raw: str) -> bool:
        """Return True if *raw* matches the stored hash.

        **Stub** — always returns False until overridden.
        """
        return False
