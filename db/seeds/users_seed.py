import json
import psycopg2
from pydantic import BaseModel
from dotenv import load_dotenv
from psycopg.rows import dict_row
from fastapi import APIRouter, Depends, HTTPException, FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.events_app import AsyncConnectionPool, get_async_conn, connect_to_db, close_db_connection
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
import asyncio
import time
import psycopg
from db.seeds.utils import hash_password, verify_password

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
### DOES NOT HASH PASSWORDS !!! ####
# def seed_users(cur):
#     with open("db/data/users.json") as f:
#         users = json.load(f)

#     for user in users:
#         cur.execute(
#             """
#             INSERT INTO users (email, password, name)
#             VALUES (%s, %s, %s);
#             """,
#             (user["email"], user["password"], user["name"])
#         )





        



def seed_users(cur):
    with open("db/data/users.json") as f:
        users = json.load(f)

    for user in users:
        hashed_password = hash_password(user["password"])
        cur.execute(
            """
            INSERT INTO users (email, password, name)
            VALUES (%s, %s, %s);
            """,
            (user["email"], hashed_password, user["name"])
        )
