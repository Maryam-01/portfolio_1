import json
import psycopg2

def drop_users(cur):
    cur.execute("DROP TABLE IF EXISTS users CASCADE;")



def create_users(cur):
    cur.execute("""
        CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
                
);
                """
                )

def seed_users(cur):
    with open("db/data/users.json") as f:
        users = json.load(f)

    for user in users:
        cur.execute(
            """
            INSERT INTO users (email, password, name)
            VALUES (%s, %s, %s);
            """,
            (user["email"], user["password"], user["name"])
        )
