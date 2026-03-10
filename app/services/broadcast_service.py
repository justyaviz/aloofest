import aiosqlite
from app.database.db import DB


async def broadcast(bot, text):

    success = 0
    failed = 0

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute("SELECT telegram_id FROM users")

        users = await cursor.fetchall()

        for user in users:

            try:
                await bot.send_message(user[0], text)
                success += 1
            except:
                failed += 1

    return success, failed
