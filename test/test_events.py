
from main import seed, app
from db.connection import get_connection
from main import create_app
from fastapi.testclient import TestClient




def test_events_table_resets_on_seed():
    conn = get_connection()
    seed(conn)

    cur = conn.cursor()

   
    cur.execute("""
        INSERT INTO events (title, description, starts_at, ends_at, organiser_id, venue_id)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (
        "FAKE EVENT",
        "Should disappear",
        "2026-01-01 10:00:00",
        "2026-01-01 12:00:00",
        1,
        1
    ))
    conn.commit()



    cur.execute("SELECT COUNT(*) FROM events;")
    count_with_fake = cur.fetchone()[0]


    seed(conn)

    cur.execute("SELECT COUNT(*) FROM events;")
    count_after_seed = cur.fetchone()[0]


    assert count_after_seed < count_with_fake

    cur.close()
    conn.close()


def test_all_data_is_inserted_into_table():
    conn = get_connection()
    seed(conn)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM events;")
    count_rows = cur.fetchone()[0]

    assert count_rows == 10

    cur.close()
    conn.close()
    

def test_seed_is_idempotent_for_events():
    conn = get_connection()
    seed(conn)
    seed(conn)
    seed(conn)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM events;")
    count = cur.fetchone()[0]

    assert count == 10

    cur.close()
    conn.close()


def test_specific_record_in_table_exists():
    

    conn = get_connection()
    seed(conn)
    cur = conn.cursor()
    cur.execute("""
        SELECT title FROM events
        WHERE title = %s;
        """, ("Leeds Tech Meetup – June Edition",))

    result = cur.fetchone()

    assert result is not None
    cur.close()
    conn.close()

#### test endpoints ##




# def test_events_returns_all():
#     conn = get_connection()
#     seed(conn)
#     conn.cursor()
#     with TestClient(app) as client:
#         response = client.get("/events")
#     assert response.status_code == 200

#     body = response.json()

#     assert isinstance(body, list)
#     assert len(body) == 10

#     for event in body:
#         assert isinstance(event["id"], int)
#         assert isinstance(event["title"], str)
#         assert event["description"] is None or isinstance(event["description"], str)
#         assert isinstance(event["starts_at"], str)
#         assert isinstance(event["ends_at"], str)
#         assert isinstance(event["organiser_id"], int)
#         assert isinstance(event["venue_id"], int)
#         assert isinstance(event["created_at"], str)




def test_events_returns_all():
    conn = get_connection()
    seed(conn)
    conn.close()

    app = create_app()

    with TestClient(app) as client:
        response = client.get("/events")
        assert response.status_code == 200

def test_events_returns_by_id():
    conn = get_connection()
    seed(conn)
    conn.close()
    with TestClient(app) as client:
        response = client.get("/events/1")
        assert response.status_code == 200
        response = client.get("/events/999999")
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "NOT_FOUND"
        assert response.json()["detail"]["message"] == "Route not found" 
        body = response.json()

        assert isinstance(body, dict)
        assert len(body) == 1

