from db.connection import get_connection
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
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
load_dotenv()


router = APIRouter()


















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


# app = FastAPI()












# @app.on_event("startup")
# async def startup():
#     await connect_to_db()

# @app.on_event("shutdown")
# async def shutdown():
#     await close_db_connection()

# router = APIRouter()
# app.include_router(router)
# @app.get("/events")
# async def get_all_events(conn=Depends(get_async_conn)):
#     cache_key = "all_events"
#     cached_events = get_cached(cache_key)

#     if cached_events is not None:
        
#         return cached_events

#     print("Cache miss")

#     async with conn.transaction():
#         async with conn.cursor() as cur:
#             await cur.execute(
#                 """
#                 SELECT id, title, description, starts_at, ends_at, organiser_id, venue_id, created_at
#                 FROM events
#                 ORDER BY starts_at ASC;

#                 """,
                
#             )
#             rows = await cur.fetchall()
#     events = [
#     {
#         "id": row["id"],
#         "title": row["title"],
#         "description": row["description"],
#         "starts_at": row["starts_at"],
#         "ends_at": row["ends_at"],
#         "organiser_id": row["organiser_id"],
#         "venue_id": row["venue_id"],
#         "created_at": row["created_at"],
#     }
#         for row in rows
#     ]
#     set_cached(cache_key, events)

#     return events


@router.get("/events")
async def get_all_events(conn=Depends(get_async_conn)):
    cache_key = "all_events"
    cached_events = get_cached(cache_key)

    if cached_events is not None:
        return cached_events

    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT id, title, description, starts_at, ends_at,
                   organiser_id, venue_id, created_at
            FROM events
            ORDER BY starts_at ASC;
            """
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




load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


def verify_password(plain_password: str, hashed:str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed.encode())



@router.post("/auth/login")
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

@router.post("/auth/register", status_code=201)
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
    

        
JWT_EXPIRY_MINUTES = 30
JWT_ALGORITHM = "HS256"
JWT_SECRET= os.getenv("JWT_SECRET")


def create_access_token(id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_MINUTES)
    payload = {"sub": str(id), 
               "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail= "Could not validate token")


@router.post("/api/events/{event_id}/rsvp", status_code=201)
async def create_rsvp_by_authentication(event_id: int, user_id: int = Depends(get_current_user_id),conn=Depends(get_async_conn)):

    
    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT id FROM events WHERE id = %s",
                (event_id,)
            )
            event = await cur.fetchone()

            if not event:
                raise HTTPException(
                    status_code= 404,
                    detail= "Event not found"
                )
            
            await cur.execute("""
                              SELECT id FROM rsvp
                              WHERE attendee_id = %s AND event_id = %s
                              """,
                              (user_id, event_id)
                              )
            existing_rsvp = await cur.fetchone()
            if existing_rsvp:
                raise HTTPException(
                    status_code=409,
                    detail="ALready RSVPed"
                )
            
            await cur.execute(
                """ 
                INSERT INTO rsvp (attendee_id, event_id)
                VALUES (%s, %s)
                RETURNING id, attendee_id, event_id, created_at
                """,
                (user_id, event_id)

            )

            new_rsvp = await cur.fetchone()
            return {"rsvp": new_rsvp}
        

@router.delete("/api/events/events/{event_id}/rsvp/me", status_code=204)
async def delete_rsvp_by_authentication(event_id: int, user_id: int = Depends(get_current_user_id),conn=Depends(get_async_conn)):

    
    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """SELECT id FROM rsvp
                   WHERE attendee_id = %s AND event_id = %s
                   """,
                   (user_id, event_id)
            )
            existing = await cur.fetchone()

            if not existing:
                raise HTTPException(
                    status_code=404,
                    detail="RSVP not found"
                )
            await cur.execute(
                """ DELETE FROM rsvp
                    WHERE attendee_id = %s AND event_id = %s
                    """,
                    (user_id, event_id)
            )

class EventCreate(BaseModel):
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime
    venue_id: int



@router.post("/api/events", status_code=201)
async def create_a_new_event_by_authenticated_user(event: EventCreate, organiser_id: int = Depends(get_current_user_id),conn=Depends(get_async_conn)):

    
    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("""
                INSERT INTO events (
                            title, 
                            description, 
                            starts_at, 
                            ends_at, 
                            venue_id,
                            organiser_id
                            )
                   VALUES (%s, %s, %s, %s, %s, %s)
                   RETURNING id, 
                              title,
                              description,
                              starts_at,
                              ends_at,
                              venue_id,
                              organiser_id,
                              created_at
                              """,
                        (event.title,
                         event.description,
                         event.starts_at,
                         event.ends_at,
                         event.venue_id,
                         organiser_id)
            )
        
        


            new_event = await cur.fetchone()
            return {"event": new_event}
        
class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    venue_id: datetime | None = None

@router.patch("/api/events/{event_id}", status_code=200)
async def update_event(
    event_id: int,
    event: EventUpdate,
    organiser_id: int = Depends(get_current_user_id),
    conn = Depends(get_async_conn)
):

    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur:

            
            await cur.execute(
                "SELECT * FROM events WHERE id = %s",
                (event_id,)
            )
            existing_event = await cur.fetchone()

            if not existing_event:
                raise HTTPException(status_code=404, detail="Event not found")

           
            if existing_event["organiser_id"] != organiser_id:
                raise HTTPException(status_code=403, detail="Not authorised")

            
            update_data = event.model_dump(exclude_unset=True)

            if not update_data:
                raise HTTPException(status_code=400, detail="No fields provided")

            
            new_starts = update_data.get("starts_at", existing_event["starts_at"])
            new_ends = update_data.get("ends_at", existing_event["ends_at"])

            if new_ends <= new_starts:
                raise HTTPException(status_code=400, detail="Invalid date range")

            
            fields = []
            values = []

            for key, value in update_data.items():
                fields.append(f"{key} = %s")
                values.append(value)

            set_clause = ", ".join(fields)

            
            await cur.execute(
                f"""
                UPDATE events
                SET {set_clause}
                WHERE id = %s
                RETURNING id,
                          title,
                          description,
                          starts_at,
                          ends_at,
                          venue_id,
                          organiser_id,
                          created_at
                """,
                values + [event_id]
            )

            updated_event = await cur.fetchone()

    return {"event": updated_event}

@router.get("/api/events/{event_id}/attendees", status_code=200)
async def get_attendees_for_authenticated_user(
    event_id: int,
    organiser_id: int = Depends(get_current_user_id),
    conn = Depends(get_async_conn)
):
            

            async with conn.transaction():
                async with conn.cursor(row_factory=dict_row) as cur:

                        await cur.execute(
                            "SELECT organiser_id FROM events WHERE id = %s",
                            (event_id,)
                    )
                        organiser = await cur.fetchone()

                        if organiser is None:
                            raise HTTPException(status_code=404)


                
                        if organiser["organiser_id"] != organiser_id:
                            raise HTTPException(status_code=403, detail="Not authorised")
                        await cur.execute(
                                """
                                SELECT users.id,
                                users.name,
                                users.email
                                

                                    
                                FROM users
                                JOIN rsvp
                                ON users.id = rsvp.attendee_id
                                WHERE rsvp.event_id = %s
                                
                                """,
                                (event_id,)
                            )
                                    


                        rows = await cur.fetchall()




                        return {"attendees": rows}



@router.get("/api/user/me/events", status_code=200)
async def get_all_events_where_authorised_user_rsvped(
    organiser_id: int = Depends(get_current_user_id),
    conn = Depends(get_async_conn)

):



    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
                                 """
                                    SELECT
                                        e.id,
                                        e.title,
                                        e.starts_at,
                                        r_user.created_at AS rsvp_date,
                                        COUNT(r_all.id) AS total_rsvps,
                                        ROW_NUMBER() OVER (ORDER BY e.starts_at ASC) AS event_rank
                                    FROM events e
                                    JOIN rsvp r_user
                                        ON e.id = r_user.event_id
                                    JOIN rsvp r_all
                                        ON e.id = r_all.event_id
                                    WHERE r_user.attendee_id = %s
                                    GROUP BY
                                        e.id,
                                        e.title,
                                        e.starts_at,
                                        r_user.created_at
                                    ORDER BY e.starts_at ASC;
                                
                                """, (organiser_id,)
        )
        rows = await cur.fetchall()

        return {"attendees": rows}


@router.get("/api/organisers/{id}/stats", status_code= 200)
async def aggregate_statistics_for_organisers(
    id: int,
    conn = Depends(get_async_conn)
):


    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """WITH event_attendance AS (
                        
                        SELECT
                            e.id,
                            e.organiser_id,
                            COUNT(r.id) AS attendance
                        FROM events e
                        LEFT JOIN rsvp r ON r.event_id = e.id
                        GROUP BY e.id
                    ),

                    organiser_stats AS (
                       
                        SELECT
                            u.id AS organiser_id,
                            u.name,
                            COUNT(ea.id) AS total_events,
                            AVG(ea.attendance)::numeric(10,1) AS avg_attendance,
                            MAX(ea.attendance) AS best_attended_count
                        FROM users u
                        LEFT JOIN event_attendance ea ON ea.organiser_id = u.id
                        GROUP BY u.id, u.name
                    ),

                    ranked_organisers AS (
                        
                        SELECT
                            *,
                            ROW_NUMBER() OVER (ORDER BY total_events DESC) AS organiser_rank
                        FROM organiser_stats
                    )

                    
                    SELECT
                        organiser_id,
                        name,
                        total_events,
                        avg_attendance,
                        best_attended_count,
                        organiser_rank
                    FROM ranked_organisers
                    WHERE organiser_id = %s;

                          

            
                            """, (id,)
        )
        
        rows = await cur.fetchone()
        if rows is None:
            raise HTTPException(status_code=404, detail="organiser not found")
        return {"stats": rows}

@router.get("/api/health", status_code=200)
async def health_check():
    return {"status": "ok"}

def create_app():
    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        await connect_to_db()

    @app.on_event("shutdown")
    async def shutdown():
        await close_db_connection()

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid request data"},
        )



    app.include_router(router)
    return app


app = create_app()




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port= 5431, reload=True)

