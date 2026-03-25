import io
import random
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from openpyxl import Workbook

from app.config import ADMIN_IDS
from app.database.db import db
from app.keyboards.user import admin_menu

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return
    await message.answer("🛠 Admin panel", reply_markup=admin_menu())


@router.message(Command("addball"))
async def add_ball(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("Format: /addball USER_ID BALL")
        return

    user_id_raw = parts[1].strip()
    points_raw = parts[2].strip()

    if not user_id_raw.isdigit() or not points_raw.lstrip("-").isdigit():
        await message.answer("USER_ID va BALL raqam bo‘lishi kerak.")
        return

    user_id = int(user_id_raw)
    points = int(points_raw)

    user = await db.get_user(user_id)
    if not user:
        await message.answer("User topilmadi.")
        return

    await db.add_points(user_id, points)
    updated_user = await db.get_user(user_id)

    await message.answer(
        f"✅ Ball o‘zgartirildi.\n\n"
        f"🆔 User: {user_id}\n"
        f"👤 {updated_user['full_name'] or updated_user['tg_name'] or updated_user['username'] or '-'}\n"
        f"💎 Joriy ball: {updated_user['diamonds']}"
    )


@router.message(Command("addref"))
async def add_ref(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("Format: /addref USER_ID SON")
        return

    user_id_raw = parts[1].strip()
    refs_raw = parts[2].strip()

    if not user_id_raw.isdigit() or not refs_raw.lstrip("-").isdigit():
        await message.answer("USER_ID va SON raqam bo‘lishi kerak.")
        return

    user_id = int(user_id_raw)
    refs = int(refs_raw)

    user = await db.get_user(user_id)
    if not user:
        await message.answer("User topilmadi.")
        return

    await db.add_referrals(user_id, refs)
    updated_user = await db.get_user(user_id)

    await message.answer(
        f"✅ Referal o‘zgartirildi.\n\n"
        f"🆔 User: {user_id}\n"
        f"👤 {updated_user['full_name'] or updated_user['tg_name'] or updated_user['username'] or '-'}\n"
        f"👥 Joriy referal: {updated_user['referral_count']}\n"
        f"💎 Joriy ball: {updated_user['diamonds']}"
    )


@router.message(Command("setready"))
async def set_ready(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = (message.text or "").split()
    if len(parts) != 4:
        await message.answer("Format: /setready USER_ID BALL REF")
        return

    user_id_raw = parts[1].strip()
    diamonds_raw = parts[2].strip()
    refs_raw = parts[3].strip()

    if not user_id_raw.isdigit() or not diamonds_raw.isdigit() or not refs_raw.isdigit():
        await message.answer("USER_ID, BALL va REF raqam bo‘lishi kerak.")
        return

    user_id = int(user_id_raw)
    diamonds = int(diamonds_raw)
    refs = int(refs_raw)

    user = await db.get_user(user_id)
    if not user:
        await message.answer("User topilmadi.")
        return

    await db.set_ready_user(user_id, diamonds, refs)
    updated_user = await db.get_user(user_id)

    await message.answer(
        f"✅ User random uchun tayyorlandi.\n\n"
        f"🆔 User: {user_id}\n"
        f"👤 {updated_user['full_name'] or updated_user['tg_name'] or updated_user['username'] or '-'}\n"
        f"💎 Ball: {updated_user['diamonds']}\n"
        f"👥 Referral: {updated_user['referral_count']}\n"
        f"🪪 ID: {updated_user['rid'] or '-'}"
    )


@router.message(lambda m: m.text == "📋 Mijozlar ro‘yxati")
async def users_list(message: Message):
    if not is_admin(message.from_user.id):
        return

    users = await db.get_recent_users(30)
    if not users:
        await message.answer("Mijozlar topilmadi.")
        return

    text = "📋 Mijozlar ro‘yxati:\n\n"
    for u in users:
        text += (
            f"🪪 {u['rid'] or '-'} | "
            f"👤 {u['full_name'] or u['tg_name'] or '-'} | "
            f"💎 {u['diamonds']}\n"
        )
    await message.answer(text)


@router.message(lambda m: m.text == "📊 Statistika")
async def stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    s = await db.get_stats()
    await message.answer(
        f"📊 Umumiy statistika\n\n"
        f"👥 Jami foydalanuvchi: {s['total_users']}\n"
        f"✅ Registered: {s['registered']}\n"
        f"⛔ Ban: {s['banned']}\n"
        f"💎 Jami ball: {s['diamonds']}\n"
        f"🎲 Randomga tayyor: {s['random_ready']}"
    )


@router.message(lambda m: m.text == "🌍 Hududiy statistika")
async def region_stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    rows = await db.get_region_stats()
    if not rows:
        await message.answer("Hududiy statistika topilmadi.")
        return

    text = "🌍 Hududiy statistika\n\n"
    for row in rows:
        text += f"{row['region']}: {row['total']} ta | {row['diamonds']} ball\n"
    await message.answer(text)


@router.message(lambda m: m.text == "🎟 PROMO")
async def promo_stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    rows = await db.get_promo_stats()
    if not rows:
        await message.answer("PROMO statistika bo‘sh.")
        return

    text = "🎟 PROMO statistika\n\n"
    for row in rows:
        text += f"{row['promo_branch']} — {row['promo_code']} — {row['total']} ta\n"
    await message.answer(text)


@router.message(lambda m: m.text == "📤 Excel export")
async def excel_export(message: Message):
    if not is_admin(message.from_user.id):
        return

    users = await db.all_users()

    wb = Workbook()
    ws = wb.active
    ws.title = "Users"
    ws.append([
        "user_id", "full_name", "phone", "rid",
        "region", "district", "diamonds", "referral_count"
    ])

    for u in users:
        ws.append([
            u["user_id"],
            u["full_name"] or u["tg_name"] or "",
            u["phone"] or "",
            u["rid"] or "",
            u["region"] or "",
            u["district"] or "",
            u["diamonds"] or 0,
            u["referral_count"] or 0,
        ])

    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)

    await message.answer_document(
        BufferedInputFile(bio.read(), filename="aloofest_users.xlsx")
    )


@router.message(lambda m: m.text == "🎲 Random admin")
async def random_admin(message: Message):
    if not is_admin(message.from_user.id):
        return

    users = await db.get_random_candidates()
    if not users:
        await message.answer("Random uchun ishtirokchi topilmadi.")
        return

    winner = random.choice(users)
    winner_name = winner["full_name"] or winner["tg_name"] or "Ishtirokchi"
    phone = winner["phone"] or ""
    masked_phone = phone[:5] + "***" + phone[-2:] if len(phone) >= 7 else phone

    start_date = datetime.now().strftime("%d-%m-%Y")
    end_date = datetime.now().strftime("%d-%m-%Y")

    await db.save_random_history(
        winner_user_id=winner["user_id"],
        winner_name=winner_name,
        rid=winner["rid"] or "-",
        phone=phone,
        points=winner["diamonds"] or 0,
        start_date=start_date,
        end_date=end_date,
    )

    await message.answer(
        f"🏆 Haftalik random g‘olibi\n\n"
        f"👤 Ism: {winner_name}\n"
        f"🪪 ID: {winner['rid'] or '-'}\n"
        f"📱 Tel: {masked_phone}\n"
        f"💎 Ball: {winner['diamonds'] or 0}"
    )
