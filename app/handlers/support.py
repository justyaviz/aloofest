from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import ADMIN_IDS
from app.database.db import db
from app.keyboards.user import admin_menu

router = Router()

IGNORE_TEXTS = {
    "👥 Mening shaxsiy linkim",
    "🎲 Random holati",
    "💎 Ballarim",
    "🎁 Sovg‘alar",
    "ℹ️ O‘yin haqida",
    "🆘 Yordam",
    "📋 Mijozlar ro‘yxati",
    "🎲 Random start",
    "📤 Excel export",
    "📊 Statistika",
    "🌍 Hududiy statistika",
    "🎟 PROMO",
    "⛔ Ban user",
    "✅ Unban user",
    "🔎 User qidirish",
    "💬 Userga xabar yuborish",
    "📣 Broadcast",
    "➕ Ball qo‘shish",
    "👥 Referal qo‘shish",
    "📱 Raqamni ulashish",
}


@router.message(lambda m: m.text == "🆘 Yordam")
async def help_menu(message: Message):
    await message.answer(
        "🆘 <b>Yordam bo‘limi</b>\n\n"
        "Savolingizni shu yerga yozib yuboring. Adminlar imkon qadar tez javob berishadi."
    )


@router.message(Command(commands=["reply"]))
async def reply_help(message: Message):
    await message.answer("To‘g‘ri format: /reply_123456789")


@router.message(lambda m: bool(m.text) and m.text.startswith("/reply_"))
async def reply_dynamic(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    raw = message.text.split("_", 1)[1].strip()
    if not raw.isdigit():
        await message.answer("Noto‘g‘ri format.")
        return

    target_id = int(raw)
    await db.set_pending_reply(message.from_user.id, target_id)
    await message.answer(f"Endi {target_id} foydalanuvchiga yuboriladigan javob matnini yozing.")


@router.message()
async def support_fallback(message: Message):
    if message.contact:
        return

    if message.photo or message.voice or message.video:
        return

    if not message.text:
        return

    if message.text in IGNORE_TEXTS:
        return

    if message.text.startswith("/"):
        return

    if message.from_user.id in ADMIN_IDS:
        pending = await db.get_pending_reply(message.from_user.id)
        if pending:
            await message.bot.send_message(
                pending,
                f"📩 <b>Admin javobi</b>\n\n{message.text}"
            )
            await db.clear_pending_reply(message.from_user.id)
            await message.answer("✅ Javob foydalanuvchiga yuborildi.", reply_markup=admin_menu())
        return

    user = await db.get_user(message.from_user.id)
    if not user or not user["registered"]:
        return

    await db.save_support_message(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=user["full_name"] or user["tg_name"],
        message_text=message.text
    )

    text = (
        f"🆘 <b>Yangi yordam xabari</b>\n\n"
        f"👤 {user['full_name'] or user['tg_name']}\n"
        f"🆔 {message.from_user.id}\n"
        f"🪪 {user['rid'] or '-'}\n\n"
        f"💬 {message.text}\n\n"
        f"Javob yozish uchun /reply_{message.from_user.id}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(admin_id, text)
        except Exception:
            pass

    await message.answer("✅ Xabaringiz adminlarga yuborildi. Tez orada javob berishadi.")
