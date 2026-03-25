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
    await db.add_points(int(parts[1]), int(parts[2]))
    await message.answer("✅ Ball o‘zgartirildi.")


@router.message(Command("addref"))
async def add_ref(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("Format: /addref USER_ID SON")
        return
    await db.add_referrals(int(parts[1]), int(parts[2]))
    await message.answer("✅ Referal o‘zgartirildi.")


@router.message(Command("setready"))
async def set_ready(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = (message.text or "").split()
    if len(parts) != 4:
        await message.answer("Format: /setready USER_ID BALL REF")
        return
    await db.set_ready_user(int(parts[1]), int(parts[2]), int(parts[3]))
    await message.answer("✅ User random uchun tayyorlandi.")


@router.message(lambda m: m.text == "📋 Mijozlar ro‘yxati")
async def users_list(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = await db.get_recent_users(30)
    text = "📋 Mijozlar:\n\n"
    for u in users:
        text += f"{u['rid'] or '-'} | {u['full_name'] or '-'} | {u['diamonds']} ball\n"
    await message.answer(text)


@router.message(lambda m: m.text == "📊 Statistika")
async def stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    s = await db.get_stats()
    await message.answer(
        f"👥 Jami: {s['total_users']}\n"
        f"✅ Registered: {s['registered']}\n"
        f"💎 Ballar: {s['diamonds']}\n"
        f"🎲 Randomga tayyor: {s['random_ready']}"
    )


@router.message(lambda m: m.text == "🌍 Hududiy statistika")
async def region_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    rows = await db.get_region_stats()
    text = "🌍 Hududiy statistika\n\n"
    for row in rows:
        text += f"{row['region']}: {row['total']} ta | {row['diamonds']} ball\n"
    await message.answer(text)


@router.message(lambda m: m.text == "🎟 PROMO")
async def promo_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    rows = await db.get_promo_stats()
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
    ws.append(["user_id", "full_name", "phone", "rid", "region", "district", "diamonds", "refs"])

    for u in users:
        ws.append([
            u["user_id"],
            u["full_name"] or "",
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
    await message.answer_document(BufferedInputFile(bio.read(), filename="aloofest_users.xlsx"))


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
    masked = phone[:5] + "***" + phone[-2:] if len(phone) >= 7 else phone

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
        f"🏆 Random g‘olibi:\n\n"
        f"👤 {winner_name}\n"
        f"🆔 {winner['rid'] or '-'}\n"
        f"📱 {masked}\n"
        f"💎 {winner['diamonds'] or 0} ball"
    )
