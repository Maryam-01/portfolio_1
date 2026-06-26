from db.connection import get_connection
from db.seeds.events_seed import drop_events, create_events, seed_events
from db.seeds.rsvp_seed import drop_rsvp, create_rsvp, seed_rsvp
from db.seeds.users_seed import drop_users, create_users, seed_users
from db.seeds.venues_seed import drop_venues, create_venues, seed_venues
import os
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
import bcrypt
from db.seeds.utils import hash_password, verify_password






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


if __name__ == "__main__":
    conn = get_connection()
    seed(conn)
    conn.close()


## returns all events list 











_cache = {}
CACHE_TTL_SECONDS = 60

def get_cached(key: str):
    entry = _cache.get(key)
    if entry is None:
        return None

    stored_at, value = entry

    if time.time() - stored_at > CACHE_TTL_SECONDS:
        del _cache[key]  # optional but recommended
        return None

    return value


def set_cached(key: str, value):
    _cache[key] = (time.time(), value)


app = FastAPI()












@app.on_event("startup")
async def startup():
    await connect_to_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db_connection()

router = APIRouter()
app.include_router(router)
@app.get("/events")
async def get_all_events(conn=Depends(get_async_conn)):
    cache_key = "all_events"
    cached_events = get_cached(cache_key)

    if cached_events is not None:
        
        return cached_events

    print("Cache miss")

    async with conn.transaction():
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, title, description, starts_at, ends_at, organiser_id, venue_id, created_at
                FROM events
                ORDER BY starts_at ASC;

                """,
                
            )
            rows = await cur.fetchall()
    events = [
    {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "starts_at": row["starts_at"],
        "ends_at": row["ends_at"],
        "organiser_id": row["organiser_id"],
        "venue_id": row["venue_id"],
        "created_at": row["created_at"],
    }
        for row in rows
    ]
    set_cached(cache_key, events)

    return events

@router.get("/events/{id}")
async def get_events_by_id(id: int, conn=Depends(get_async_conn)):
    # cache_key = "all_events"
    # cached_events = get_cached(cache_key)

    # if cached_events is not None:
        
    #     return cached_events

    # print("Cache miss")

    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur: # async psycopg does not return tuple, must add dictionary
            await cur.execute(
                """
                SELECT events.id, 
                       events.title, 
                       events.description, 
                       events.starts_at, 
                       events.ends_at, 
                       events.organiser_id,
                       events.venue_id,
                       events.created_at,
                       venues.name,
                       venues.address, 
                       venues.capacity
                       
                FROM events
                INNER JOIN venues
                ON events.organiser_id = venues.id
                WHERE events.id = %s;
                
                """, (id,))
                


            rows = await cur.fetchone()



    if rows is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Route not found"},
        )
    
    return rows
    

    
    #     "id": rows[0],
    #     "title": rows[1],
    #     "description": rows[2],
    #     "starts_at": rows[3],
    #     "ends_at": rows[4],
    #     "organiser_id": rows[5],
    #     "venue_id": rows[6],
    #     "created_at": rows[7],
    #     "name": rows[8],
    #     "address": rows[9],
    #     "capacity": rows[10]
    # }
        
    

    # set_cached(cache_key, events)


 ### auth login #####

load_dotenv()

JWT_EXPIRY_MINUTES = 30
JWT_ALGORITHM = "HS256"
JWT_SECRET= os.getenv("JWT_SECRET")

class CredentialsRequest(BaseModel):
    email: str
    password: str




# DATABASE_URL = os.getenv("DATABASE_URL")




# @app.post("/auth/register")
# async def register_user(payload: CredentialsRequest, conn=Depends(get_async_conn)):
#     async with conn.transaction():
#         async with conn.cursor() as cur:

#             # ✅ HASH THE PASSWORD HERE
#             hashed_password = hash_password(payload.password)

#             await cur.execute(
#                 """
#                 INSERT INTO users (email, password)
#                 VALUES (%s, %s)
#                 """,
#                 (payload.email, hashed_password)
#             )

#     return {"message": "User registered successfully"}




# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


def verify_password(plain_password: str, hashed:str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed.encode())



@app.post("/auth/login")
async def login_user(payload: CredentialsRequest, conn=Depends(get_async_conn)):
    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT id, password FROM users WHERE email = %s",
                (payload.email,),
            )
            user = await cur.fetchone()

            if user is None or not verify_password(payload.password, user["password"]):
                raise HTTPException(status_code=401, detail="invalid email or password")

            token = create_access_token(user["id"])

            return {
                "access_token": token,
                "token_type": "bearer"
            }

@app.post("/auth/register", status_code=201)
async def register_user(payload: RegisterRequest, conn=Depends(get_async_conn)):
    if not payload.email or not payload.password or not payload.name:
        raise HTTPException(
            status_code=400,
            detail={"code": "Bad Request", "message": "Missing required field"}
        )
    hashed_password = hash_password(payload.password)
    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                "SELECT id FROM users WHERE email = %s",
                (payload.email,)
            )
                existing_user = await cur.fetchone()

                if existing_user:
                    raise HTTPException(
                    status_code=409,
                    detail="Email already registered"
                )

                
                await cur.execute(
                    """
                
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            RETURNING id, name, email, created_at;
            """,
            (payload.name, payload.email, hashed_password)
            )
                


                new_user = await cur.fetchone()


                
                return new_user
    

        
    
                

                
                            


                              
                






def create_access_token(id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_MINUTES)
    payload = {"sub": str(id), 
               "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_event_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail= "Could not validate token")











if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port= 5431, reload=True)

