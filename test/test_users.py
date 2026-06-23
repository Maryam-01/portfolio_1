from main import seed
from db.connection import get_connection


def test_users_seeded():
    conn = get_connection()
    seed(conn)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users;")
    count = cur.fetchone()[0]

    assert count == 6

    cur.close()
    conn.close()


def test_users_table_resets_on_seed():
    conn = get_connection()
    seed(conn)

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (email, password, name)
        VALUES (%s, %s, %s);
    """, (
        "fake@user.com",
        "fakepassword",
        "FAKE_USER",
    ))
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM users;")
    count_with_fake = cur.fetchone()[0]

    seed(conn)

    cur.execute("SELECT COUNT(*) FROM users;")
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


def test_seed_is_idempotent_for_users():
    conn = get_connection()

    seed(conn)
    seed(conn)
    seed(conn)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users;")
    count = cur.fetchone()[0]

    assert count == 6

    cur.close()
    conn.close()


def test_specific_user_exists():
    conn = get_connection()
    seed(conn)

    cur = conn.cursor()
    cur.execute("""
        SELECT name FROM users
        WHERE name = %s;
    """, ("Bob Nguyen",))

    result = cur.fetchone()

    assert result is not None
    assert result[0] == "Bob Nguyen"

    cur.close()
    conn.close()