
import json
import psycopg2

def drop_events(cur):
    cur.execute("DROP TABLE IF EXISTS events CASCADE;")





def create_events(cur):
    cur.execute("""CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    organiser_id INT NOT NULL REFERENCES users(id),
    venue_id INT REFERENCES venues(id),
    created_at TIMESTAMPTZ DEFAULT NOW()


);"""
                )
    
def seed_events(cur):
    with open("db/data/events.json") as f:
        events = json.load(f)

    for event in events:
        cur.execute(
            """
            INSERT INTO events (title, description, starts_at, ends_at, organiser_id, venue_id)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (event["title"], event["description"], event["starts_at"], event["ends_at"], event["organiser_id"], event["venue_id"])
        )