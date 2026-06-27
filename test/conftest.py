import pytest
from fastapi.testclient import TestClient
from main import app
from db.connection import get_connection
from app.events_app import connect_to_db, close_db_connection
from main import seed
import asyncio


@pytest.fixture
def client():
    # ✅ Seed DB using sync connection
    conn = get_connection()
    seed(conn)
    conn.close()

    # ✅ Manually open async pool
    asyncio.run(connect_to_db())

    with TestClient(app) as client:
        yield client

    # ✅ Close async pool after test
    asyncio.run(close_db_connection())