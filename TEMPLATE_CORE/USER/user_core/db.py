"""Database foundation: shared Base, engine factory, session factory."""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session


class Base(DeclarativeBase):
    """Shared declarative base. Import this in every concrete model file.

    Because all template models use ``__abstract__ = True``, this Base
    registers zero tables. ``Base.metadata`` is empty until an agent
    imports and creates their concrete subclasses.
    """


def engine_from_url(dsn: str, echo: bool = False) -> Engine:
    """Create a synchronous engine from a database URL string."""
    return create_engine(dsn, echo=echo)


def session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a sessionmaker bound to the given engine."""
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session(engine: Engine) -> Generator[Session, None, None]:
    """Context manager that yields a session, commits on success, rolls back on error."""
    factory = session_factory(engine)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
