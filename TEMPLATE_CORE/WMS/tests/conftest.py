import pytest
from wms_core.db import Base, engine_factory, get_session
import wms_core.models  # noqa: F401 — registers all models with Base.metadata


@pytest.fixture(scope="session")
def engine():
    eng = engine_factory("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def session(engine):
    with get_session(engine) as s:
        yield s
