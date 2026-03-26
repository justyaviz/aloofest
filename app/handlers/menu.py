from datetime import datetime, timedelta

from aiogram import Router
from aiogram.types import Message

from app.database.db import db

router = Router()


def next_wednesday_14():
    now = datetime.now()
    days_ahead = (2 - now.weekday()) % 7
    if days_ahead == 0 and now.hour >= 14:
        days_ahead = 7
    next_dt = now + timedelta(days=days_ahead)
    return next_dt.replace(hour=14, minute=0, second=0, microsecond=0)


@router.message(lambda m: m.text == "🎲 Random holati")
async def random_status(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user["registered"]:
        await message.answer("Avval ro‘yxatdan o‘ting.")
        return

    upcoming = next_wednesday_14()
    status = "✅ Siz hozirgi random haftasida qatnashish uchun tayyorsiz." if (user["diamonds"] or 0) >= 25 else "❌ Hozircha siz random ro‘yxatiga kirmagansiz. 25 ball yig‘ing."

    remaining = max(0, 25 - (user["diamonds"] or 0))

    last = await db.get_last_random()
    last_text = ""
    if last:
        phone = last["phone"] or ""
        masked = phone[:5] + "***" + phone[-2:] if len(phone) >= 7 else phone
        last_text = (
            f"\n\n🏆 <b>Oxirgi g‘olib</b>\n"
            f"👤 {last['winner_name']}\n"
            f"🆔 {last['rid']}\n"
            f"📱 {masked}"
        )

    await message.answer(
        f"🎲 <b>Random holati</b>\n\n"
        f"📅 Keyingi efir: <b>{upcoming.strftime('%d-%m-%Y %H:%M')}</b>\n"
        f"📌 Holatingiz: {status}\n"
        f"💎 Ballaringiz: <b>{user['diamonds']}</b>\n"
        f"👥 Takliflaringiz: <b>{user['referral_count']}</b>\n"
        f"➕ Randomga chiqish uchun yana kerak: <b>{remaining}</b> ball"
        f"{last_text}"
    )


@router.message(lambda m: m.text == "💎 Ballarim")
async def my_points(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        return
    await message.answer(
        f"💎 <b>Sizning ballaringiz</b>\n\n"
        f"🆔 ID: <b>{user['rid'] or '-'}</b>\n"
        f"💎 Ballar: <b>{user['diamonds']}</b>\n"
        f"👥 Takliflar: <b>{user['referral_count']}</b>\n\n"
        f"Agar ballaringizni tezroq oshirmoqchi bo‘lsangiz, do‘stlaringizni taklif qiling yoki eng yaqin <b>aloo</b> do‘konidan promokod oling."
    )


@router.message(lambda m: m.text == "🎁 Sovg‘alar")
async def prizes(message: Message):
    await message.answer(
        "🎁 <b>ALOOFEST 2-MAVSUM sovg‘alari</b>\n\n"
        "📱 Telefon\n"
        "📟 Planshet\n"
        "🫖 Elektr choynak\n"
        "⌚ Smartwatch\n"
        "🎧 AirPods\n"
        "🎁 va boshqa qimmatbaho sovg‘alar\n\n"
        "Har hafta yangi random, yangi imkoniyat va yangi g‘oliblar!"
    )


@router.message(lambda m: m.text == "ℹ️ O‘yin haqida")
async def about(message: Message):
    await message.answer(
        "ℹ️ <b>ALOOFEST 2-MAVSUM haqida</b>\n\n"
        "Bu mavsum faqat <b>random sovg‘ali o‘yinlar</b> formatida o‘tkaziladi.\n\n"
        "📅 Random efirlari har hafta chorshanba kuni soat 14:00 da bo‘ladi.\n"
        "💎 Ishtirok etish uchun shu hafta ichida 25 ball yig‘ishingiz kerak.\n"
        "🏬 Promokod esa sizga +15 ball beradi.\n\n"
        "Shuning uchun do‘stlaringizni taklif qiling va imkoniyatingizni oshiring."
    )
