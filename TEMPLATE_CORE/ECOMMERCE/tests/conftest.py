import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ecommerce_core.db import Base
import ecommerce_core.models  # registers all models with Base.metadata


@pytest.fixture(scope="session")
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def session(engine):
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.rollback()
    s.close()
