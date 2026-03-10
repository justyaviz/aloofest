import aiosqlite
from app.database.db import DB


async def get_top_users():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute("""
        SELECT name, fest_id, points
        FROM users
        ORDER BY points DESC
        LIMIT 10
        """)

        return await cursor.fetchall()
