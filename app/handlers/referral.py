from aiogram import Router
from aiogram.types import Message

from app.config import REFERRAL_IMAGE_FILE_ID
from app.database.db import db

router = Router()


@router.message(lambda m: m.text == "👥 Do‘stlarni taklif qilish")
async def referral_menu(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user["registered"]:
        await message.answer("Avval ro‘yxatdan o‘ting.")
        return

    me = await message.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{message.from_user.id}"

    caption = (
        "🔥 <b>ALOOFEST 2-MAVSUM RANDOM sovg‘ali o‘yinlari</b>\n\n"
        "Do‘stlaringizni taklif qiling va sovg‘alarga yaqinlashing.\n\n"
        "💎 Har 1 do‘st = +5 ball\n"
        "🏬 Do‘kondan promokod = +15 ball\n\n"
        "Promokod olsangiz, yana 2 ta do‘st taklif qilib randomga kirishingiz mumkin.\n\n"
        f"🔗 Sizning shaxsiy linkingiz:\n{link}"
    )

    if REFERRAL_IMAGE_FILE_ID:
        await message.answer_photo(REFERRAL_IMAGE_FILE_ID, caption=caption)
    else:
        await message.answer(caption)
