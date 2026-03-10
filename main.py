import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.config import BOT_TOKEN
from app.database.db import init_db
from app.web.server import start_web

from app.handlers.start import router as start_router
from app.handlers.user import router as user_router
from app.handlers.admin import router as admin_router
from app.handlers.support import router as support_router


async def main():

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(support_router)

    await init_db()

    asyncio.create_task(start_web())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
