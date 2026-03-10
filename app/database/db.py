import aiosqlite
from .models import USERS_TABLE, WINNERS_TABLE, BROADCAST_TABLE

DB = "data/aloofest.db"


async def init_db():

    async with aiosqlite.connect(DB) as db:

        await db.execute(USERS_TABLE)
        await db.execute(WINNERS_TABLE)
        await db.execute(BROADCAST_TABLE)

        await db.commit()
