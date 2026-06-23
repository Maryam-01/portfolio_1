
from main import seed
from db.connection import get_connection

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

    assert count == 10  # same expected number

    cur.close()


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

