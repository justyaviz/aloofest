import aiosqlite
from app.database.db import DB


async def get_top():

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute("""
        SELECT name, fest_id, points
        FROM users
        ORDER BY points DESC
        LIMIT 10
        """)

        return await cur.fetchall()
