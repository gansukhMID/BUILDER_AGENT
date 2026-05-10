"""Pytest fixtures: SQLite in-memory engine and session with rollback teardown."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from user_core.db import Base
import tests.concrete_models  # noqa: F401 — registers all concrete tables


@pytest.fixture(scope="session")
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def session(engine) -> Session:
    factory = sessionmaker(bind=engine)
    s = factory()
    yield s
    s.rollback()
    s.close()
