import aiosqlite
from app.database.db import DB


async def broadcast(bot, text):

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute("SELECT telegram_id FROM users")

        users = await cur.fetchall()

        for u in users:

            try:
                await bot.send_message(u[0], text)
            except:
                pass
