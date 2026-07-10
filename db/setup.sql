-- Drop and recreate the database
DROP DATABASE IF EXISTS nc_plus_one;
CREATE DATABASE nc_plus_one;

-- Connect to the new database
\c nc_plus_one;

---- DROP TABLES IF EXISTS ---

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS RSVP;
DROP TABLE IF EXISTS venues;
DROP TABLE IF EXISTS events;


--- CREATE TABLES -----


---- USERS TABLE ----- 

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

----- CREATE VENUES TABLE ----

CREATE TABLE venues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    capacity INT
);
--- CREATE EVENTS TABLE -----

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    organiser_id INT NOT NULL REFERENCES users(id),
    venue_id INT REFERENCES venues(id),
    created_at TIMESTAMPTZ DEFAULT NOW()


);

----- RSVP TABLE ----- 

-- CREATE TABLE RSVP (
--     id SERIAL PRIMARY KEY,
--     attendee_id INT NOT NULL REFERENCES users(id),
--     event_id INT NOT NULL REFERENCES events(id),
--     created_at TIMESTAMPTZ DEFAULT NOW()
-- );

CREATE TABLE rsvp (
    id SERIAL PRIMARY KEY,
    attendee_id INT NOT NULL REFERENCES users(id),
    event_id INT NOT NULL REFERENCES events(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);








