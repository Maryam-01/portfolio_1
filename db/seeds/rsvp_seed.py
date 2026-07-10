import json 
import psycopg2

def drop_rsvp(cur):
    cur.execute("DROP TABLE IF EXISTS rsvp CASCADE;")

def create_rsvp(cur):
    cur.execute("""CREATE TABLE rsvp (
    id SERIAL PRIMARY KEY,
    attendee_id INT NOT NULL REFERENCES users(id),
    event_id INT NOT NULL REFERENCES events(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);"""
                )


def seed_rsvp(cur):
    with open("db/data/rsvps.json") as f:
        rsvps = json.load(f)

    for rsvp in rsvps:
        cur.execute(
            """
            INSERT INTO rsvp (attendee_id, event_id)
            VALUES (%s, %s);
            """,
            (rsvp["attendee_id"], rsvp["event_id"])
        )