import aiosqlite
from app.database.db import DB


async def get_top():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
            SELECT name, fest_id, points
            FROM users
            WHERE registered = 1
            ORDER BY points DESC, referrals_count DESC, telegram_id ASC
            LIMIT 10
        """)
        return await cur.fetchall()
