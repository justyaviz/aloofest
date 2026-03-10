from aiohttp import web
import os

PORT = int(os.environ.get("PORT",8080))


async def health(request):
    return web.Response(text="OK")


async def start_web():

    app = web.Application()

    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner,"0.0.0.0",PORT)

    await site.start()
