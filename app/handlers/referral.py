from aiogram import Router
from aiogram.types import Message
import aiosqlite
import random

router = Router()

DB = "aloofest.db"


def generate_fest():

    n = random.randint(1,999)

    return f"FEST-{n:03d}"


@router.message(lambda msg: msg.text == "💎 Mening ballarim")
async def my_points(message: Message):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT name,fest_id,referrals_count,points FROM users WHERE telegram_id=?",
            (message.from_user.id,)
        )

        row = await cursor.fetchone()

        if not row:
            await message.answer("Ro‘yxatdan o‘tmagansiz.")
            return

        name, fest, refs, pts = row

        text = f"""
👤 Ism: {name}
🆔 ID: {fest}

👥 Do‘stlar: {refs}
💎 Ballar: {pts}
"""

        await message.answer(text)
