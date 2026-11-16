import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with Session() as session:
        yield session
    engine.dispose()