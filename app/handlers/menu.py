from datetime import datetime, timedelta

from aiogram import Router
from aiogram.types import Message

from app.database.db import db
from app.keyboards.user import main_menu

router = Router()


def next_wednesday_14():
    now = datetime.now()
    days_ahead = (2 - now.weekday()) % 7
    next_dt = now + timedelta(days=days_ahead)
    return next_dt.replace(hour=14, minute=0, second=0, microsecond=0)


@router.message(lambda m: m.text == "🎲 Random holati")
async def random_status(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user["registered"]:
        await message.answer("Avval ro‘yxatdan o‘ting.")
        return

    upcoming = next_wednesday_14()
    status = "✅ Qatnashmoqdasiz" if (user["diamonds"] or 0) >= 25 else "❌ Siz o‘yinda emassiz. 25 ball yig‘ing."

    last = await db.get_last_random()
    last_text = ""
    if last:
        phone = last["phone"] or ""
        masked = phone[:5] + "***" + phone[-2:] if len(phone) >= 7 else phone
        last_text = (
            f"\n\n🏆 Oxirgi g‘olib:\n"
            f"👤 {last['winner_name']}\n"
            f"🆔 {last['rid']}\n"
            f"📱 {masked}"
        )

    await message.answer(
        f"🎲 <b>Random holati</b>\n\n"
        f"⏰ Keyingi o‘yin: {upcoming.strftime('%d-%m-%Y %H:%M')}\n"
        f"📌 Sizning holatingiz: {status}\n"
        f"💎 Ballaringiz: {user['diamonds']}\n"
        f"👥 Takliflar: {user['referral_count']}{last_text}"
    )


@router.message(lambda m: m.text == "💎 Ballarim")
async def my_points(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        return
    await message.answer(
        f"💎 Ballar: {user['diamonds']}\n"
        f"👥 Takliflar: {user['referral_count']}\n"
        f"🆔 {user['rid'] or '-'}"
    )


@router.message(lambda m: m.text == "🎁 Sovg‘alar")
async def prizes(message: Message):
    await message.answer(
        "🎁 Asosiy sovg‘alar:\n"
        "📱 Telefon\n"
        "📟 Planshet\n"
        "🫖 Elektr choynak\n"
        "⌚ Smartwatch\n"
        "🎧 AirPods\n"
        "va boshqalar"
    )


@router.message(lambda m: m.text == "ℹ️ O‘yin haqida")
async def about(message: Message):
    await message.answer(
        "ALOOFEST 2-MAVSUM RANDOM sovg‘ali o‘yinlari.\n"
        "Har hafta chorshanba kuni 14:00 da random efir."
    )
