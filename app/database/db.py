import aiosqlite
import os

DB_DIR = "data"
DB = f"{DB_DIR}/aloofest.db"


async def init_db():

    os.makedirs(DB_DIR, exist_ok=True)

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
        telegram_id INTEGER PRIMARY KEY,
        name TEXT,
        instagram TEXT,
        region TEXT,
        district TEXT,
        fest_id TEXT,
        referrer_id INTEGER,
        referrals_count INTEGER DEFAULT 0,
        points INTEGER DEFAULT 0,
        registered INTEGER DEFAULT 0
        )
        """)

        await db.commit()
