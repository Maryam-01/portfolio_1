import os
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.environ["DATABASE_URL"]

pool: AsyncConnectionPool | None = None


async def connect_to_db():
    global pool
    pool = AsyncConnectionPool(
        conninfo=DATABASE_URL,
        min_size=1,
        max_size=10,
        kwargs={"row_factory": dict_row},
    )
    await pool.open()


async def close_db_connection():
    global pool
    if pool:
        await pool.close()


async def get_async_conn():
    async with pool.connection() as conn:
        yield conn


