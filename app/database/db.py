import aiosqlite

DB_PATH = "aloofest.db"


async def init_db():

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            instagram TEXT,
            region TEXT,
            district TEXT,
            fest_id TEXT,
            referrer_id INTEGER,
            referrals_count INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            is_registered INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.commit()
