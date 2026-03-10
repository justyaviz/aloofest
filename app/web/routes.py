from aiohttp import web
import aiosqlite

from app.database.db import DB

routes = web.RouteTableDef()


@routes.get("/health")
async def health(request):
    return web.Response(text="OK")


@routes.get("/register")
async def register_page(request):

    return web.FileResponse(
        "app/web/templates/register.html"
    )


@routes.post("/register")
async def register_user(request):

    data = await request.post()

    telegram_id = data["telegram_id"]
    name = data["name"]
    instagram = data["instagram"]
    region = data["region"]
    district = data["district"]

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute(
        "SELECT COUNT(*) FROM users"
        )

        count = (await cur.fetchone())[0] + 1

        fest_id = f"FEST-{count:03d}"

        await db.execute("""

        INSERT INTO users(
        telegram_id,
        name,
        instagram,
        region,
        district,
        fest_id,
        registered
        )

        VALUES(?,?,?,?,?,?,1)

        """,

        (telegram_id,name,instagram,region,district,fest_id)

        )

        await db.commit()

    return web.Response(text="Registered successfully")


def setup_routes(app):

    app.add_routes(routes)
