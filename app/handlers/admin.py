from aiogram import Router
from aiogram.types import Message
from app.config import ADMIN_IDS
import aiosqlite

router = Router()

DB = "aloofest.db"


@router.message(lambda msg: msg.from_user.id in ADMIN_IDS)
async def admin_panel(message: Message):

    if message.text == "/admin":

        async with aiosqlite.connect(DB) as db:

            cursor = await db.execute("SELECT COUNT(*) FROM users")

            users = await cursor.fetchone()

        await message.answer(
            f"""
⚙️ Admin Panel

👥 Foydalanuvchilar: {users[0]}

Buyruqlar:
/users
"""
        )
