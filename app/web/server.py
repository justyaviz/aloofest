from aiohttp import web
import os

from app.web.routes import setup_routes

PORT = int(os.getenv("PORT",8080))


async def start_web():

    app = web.Application()

    setup_routes(app)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner,"0.0.0.0",PORT)

    await site.start()
