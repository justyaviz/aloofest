from aiohttp import web
import aiosqlite
from app.database.db import DB
from app.utils.helpers import generate_fest_id


async def register(request):

    data = await request.post()

    name = data["name"]
    instagram = data["instagram"]
    region = data["region"]
    district = data["district"]
    user_id = int(data["user_id"])

    fest = generate_fest_id()

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        UPDATE users
        SET name=?,instagram=?,region=?,district=?,fest_id=?,is_registered=1,points=5
        WHERE telegram_id=?
        """,(name,instagram,region,district,fest,user_id))

        await db.commit()

    return web.Response(text="OK")
