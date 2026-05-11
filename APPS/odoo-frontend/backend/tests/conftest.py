import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from db import get_db


TEST_DATABASE_URL = "sqlite:///./test_odoo.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Import all models to register them
    from models.concrete import User  # noqa: F401
    import wms_core.models  # noqa: F401
    import ecommerce_core.models  # noqa: F401
    from user_core.db import Base as UserBase
    from wms_core.db import Base as WMSBase
    from ecommerce_core.db import Base as ECBase
    UserBase.metadata.create_all(bind=engine)
    WMSBase.metadata.create_all(bind=engine)
    ECBase.metadata.create_all(bind=engine)
    yield
    ECBase.metadata.drop_all(bind=engine)
    WMSBase.metadata.drop_all(bind=engine)
    UserBase.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_odoo.db"):
        os.remove("test_odoo.db")


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
