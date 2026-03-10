import random
import aiosqlite
from app.database.db import DB


async def choose_random_winner():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute("""
        SELECT telegram_id FROM users
        WHERE referrals_count >= 3
        """)

        users = await cursor.fetchall()

        if not users:
            return None

        return random.choice(users)[0]
