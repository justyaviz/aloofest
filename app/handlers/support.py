from aiogram import Router
from aiogram.types import Message

from app.config import ADMIN_IDS
from app.database.db import db

router = Router()


@router.message(lambda m: m.text == "🆘 Yordam")
async def help_menu(message: Message):
    await message.answer("Savolingizni yozib yuboring. Adminlar javob beradi.")


@router.message()
async def support_fallback(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user["registered"]:
        return

    text = (
        f"🆘 Yangi murojaat\n\n"
        f"👤 {user['full_name'] or user['tg_name']}\n"
        f"🆔 {message.from_user.id}\n"
        f"📨 {message.text}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(admin_id, text)
        except Exception:
            pass

    await message.answer("✅ Xabaringiz yuborildi.")
