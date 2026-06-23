from db.connection import get_connection
from db.seeds.events_seed import drop_events, create_events, seed_events
from db.seeds.rsvp_seed import drop_rsvp, create_rsvp, seed_rsvp
from db.seeds.users_seed import drop_users, create_users, seed_users
from db.seeds.venues_seed import drop_venues, create_venues, seed_venues


def seed(conn):
    cur = conn.cursor()

    drop_rsvp(cur)
    drop_events(cur)
    drop_venues(cur)
    drop_users(cur)

    create_users(cur)
    create_venues(cur)
    create_events(cur)
    create_rsvp(cur)

    seed_users(cur)
    seed_venues(cur)
    seed_events(cur)
    seed_rsvp(cur)

    conn.commit()
    cur.close()

    print("✅ Database seeded successfully")

    print("✅ Database seeded successfully")


if __name__ == "__main__":
    conn = get_connection()
    seed(conn)
    conn.close()