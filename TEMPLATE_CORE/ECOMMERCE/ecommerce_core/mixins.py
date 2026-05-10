from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class ActiveMixin:
    active: Mapped[bool] = mapped_column(default=True)


class NameMixin:
    name: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str | None] = mapped_column(nullable=True)


class CurrencyMixin:
    currency: Mapped[str] = mapped_column(default='USD')
