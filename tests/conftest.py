
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from database.scripts.seed_database import seed_database, clear_existing_data
from sqlalchemy_utils import database_exists, create_database, drop_database

TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/test_ecommerce_db")

# SQLAlchemy engine for the test database
engine = create_engine(TEST_DATABASE_URL)

# sessionmaker for the test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    """
    Fixture to create and drop the test database.
    """
    if not database_exists(engine.url):
        create_database(engine.url)
    
    # Run the schema migration and seeding
    seed_database(clear_data=True)
    
    yield
    
    drop_database(engine.url)

@pytest.fixture(scope="function")
def db_session(test_db):
    """
    Fixture to provide a transactional session for each test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture to provide a test client with an overridden database dependency.
    """
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c