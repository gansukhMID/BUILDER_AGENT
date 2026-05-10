from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session


class Base(DeclarativeBase):
    pass


def engine_factory(dsn: str, echo: bool = False) -> Engine:
    return create_engine(dsn, echo=echo)


def SessionFactory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session(engine: Engine) -> Generator[Session, None, None]:
    factory = SessionFactory(engine)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Backward-compatible aliases
engine_from_url = engine_factory
session_factory = SessionFactory
