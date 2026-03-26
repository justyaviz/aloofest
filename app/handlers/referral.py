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
        "Do‘stlaringizni taklif qiling va har bir muvaffaqiyatli taklif uchun <b>+5 ball</b> oling.\n\n"
        "🏬 Agar eng yaqin <b>aloo</b> do‘koniga borib promokod olsangiz, yana <b>+15 ball</b> qo‘lga kiritasiz.\n\n"
        "Bu degani, promokod + 2 ta do‘st = randomga juda yaqin imkoniyat.\n\n"
        "🔗 <b>Sizning shaxsiy linkingiz:</b>\n"
        f"{link}"
    )

    if REFERRAL_IMAGE_FILE_ID:
        await message.answer_photo(REFERRAL_IMAGE_FILE_ID, caption=caption)
    else:
        await message.answer(caption)
