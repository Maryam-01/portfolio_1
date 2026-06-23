import json
import psycopg2

def drop_venues(cur):
     cur.execute("DROP TABLE IF EXISTS venues CASCADE;")


def create_venues(cur):

    cur.execute("""CREATE TABLE venues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    capacity INT
);"""
                )
    


def seed_venues(cur):
    with open("db/data/venues.json") as f:
        venues = json.load(f)

    for venue in venues:
        cur.execute(
            """
            INSERT INTO venues (name, address, capacity)
            VALUES (%s, %s, %s);
            """,
            (venue["name"], venue["address"], venue["capacity"])
        )
