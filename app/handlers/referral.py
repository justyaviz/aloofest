from aiogram import Router
from aiogram.types import Message

from app.config import REFERRAL_IMAGE_FILE_ID
from app.database.db import db

router = Router()


@router.message(lambda m: m.text == "👥 Mening shaxsiy linkim")
async def referral_menu(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user["registered"]:
        await message.answer("Avval ro‘yxatdan o‘ting.")
        return

    me = await message.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{message.from_user.id}"

    caption = (
        "🔥 <b>Diqqat! Haftalik random o‘yinlariga start berilgan!</b>\n\n"
        "Siz ham qimmatbaho sovg‘alarni yutib olishingiz mumkin! 🎁\n\n"
        "📌 Ishtirok etish juda oson:\n"
        "✅ botga kiring\n"
        "✅ ro‘yxatdan o‘ting\n"
        "✅ do‘stlaringizni taklif qiling\n"
        "✅ ball yig‘ing va randomga kiring\n\n"
        "💎 Har bir taklif qilingan do‘st uchun sizga <b>+5 ball</b> beriladi.\n"
        "🏬 Eng yaqin <b>aloo</b> do‘konidan promokod olsangiz esa yana <b>+15 ball</b> olasiz.\n\n"
        "🎯 Bu esa sizning randomga chiqish imkoniyatingizni yanada oshiradi.\n\n"
        "🚀 <b>Mana mening shaxsiy havolam:</b>\n"
        f"{link}\n\n"
        "Ushbu link orqali kirib ishtirok eting va birgalikda sovg‘alarga yaqinlashamiz!"
    )

    if REFERRAL_IMAGE_FILE_ID:
        await message.answer_photo(REFERRAL_IMAGE_FILE_ID, caption=caption)
    else:
        await message.answer(caption)
