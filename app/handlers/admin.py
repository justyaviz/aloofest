import io
import random
import asyncio
import calendar
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    BufferedInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from openpyxl import Workbook

from app.config import ADMIN_IDS
from app.database.db import db
from app.keyboards.user import admin_menu

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class AdminBallState(StatesGroup):
    waiting_user = State()
    waiting_points = State()


class AdminRefState(StatesGroup):
    waiting_user = State()
    waiting_refs = State()


class BanState(StatesGroup):
    waiting_user = State()


class UnbanState(StatesGroup):
    waiting_user = State()


class SearchState(StatesGroup):
    waiting_query = State()


class DirectMessageState(StatesGroup):
    waiting_user = State()
    waiting_message = State()


class BroadcastState(StatesGroup):
    waiting_content = State()


def build_calendar(year: int, month: int, prefix: str) -> InlineKeyboardMarkup:
    kb = []
    month_name = f"{year}-{month:02d}"
    kb.append([
        InlineKeyboardButton(text="◀️", callback_data=f"{prefix}:nav:{year}:{month}:prev"),
        InlineKeyboardButton(text=month_name, callback_data="noop"),
        InlineKeyboardButton(text="▶️", callback_data=f"{prefix}:nav:{year}:{month}:next"),
    ])
    kb.append([
        InlineKeyboardButton(text="Du", callback_data="noop"),
        InlineKeyboardButton(text="Se", callback_data="noop"),
        InlineKeyboardButton(text="Ch", callback_data="noop"),
        InlineKeyboardButton(text="Pa", callback_data="noop"),
        InlineKeyboardButton(text="Ju", callback_data="noop"),
        InlineKeyboardButton(text="Sh", callback_data="noop"),
        InlineKeyboardButton(text="Ya", callback_data="noop"),
    ])

    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="noop"))
            else:
                row.append(
                    InlineKeyboardButton(text=str(day), callback_data=f"{prefix}:pick:{year}:{month}:{day}")
                )
        kb.append(row)

    return InlineKeyboardMarkup(inline_keyboard=kb)


@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return
    await message.answer("🛠 <b>Admin panel</b>", reply_markup=admin_menu())


@router.message(lambda m: m.text == "➕ Ball qo‘shish")
async def add_ball_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminBallState.waiting_user)
    await message.answer("Ball qo‘shiladigan ishtirokchi ID yoki R-ID ni yuboring.")


@router.message(AdminBallState.waiting_user)
async def add_ball_get_user(message: Message, state: FSMContext):
    query = message.text.strip()
    user = await db.get_user(int(query)) if query.isdigit() else await db.get_user_by_rid(query)
    if not user:
        await message.answer("Ishtirokchi topilmadi.")
        await state.clear()
        return

    await state.update_data(target_user_id=user["user_id"])
    await state.set_state(AdminBallState.waiting_points)
    await message.answer(
        f"👤 {user['full_name'] or user['tg_name']}\n"
        f"🆔 {user['rid'] or '-'}\n\n"
        f"Endi qo‘shiladigan yoki ayriladigan ball miqdorini yuboring.\n"
        f"Masalan: 15 yoki -10"
    )


@router.message(AdminBallState.waiting_points)
async def add_ball_finish(message: Message, state: FSMContext):
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("Ball raqam bo‘lishi kerak.")
        return

    points = int(message.text.strip())
    data = await state.get_data()
    user_id = data["target_user_id"]

    await db.add_points(user_id, points)
    user = await db.get_user(user_id)

    await message.answer(
        f"✅ Ball muvaffaqiyatli yangilandi.\n\n"
        f"👤 {user['full_name'] or user['tg_name']}\n"
        f"🆔 {user['rid'] or '-'}\n"
        f"💎 Joriy ball: {user['diamonds']}",
        reply_markup=admin_menu()
    )
    await state.clear()


@router.message(lambda m: m.text == "👥 Referal qo‘shish")
async def add_ref_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminRefState.waiting_user)
    await message.answer("Referal qo‘shiladigan ishtirokchi ID yoki R-ID ni yuboring.")


@router.message(AdminRefState.waiting_user)
async def add_ref_get_user(message: Message, state: FSMContext):
    query = message.text.strip()
    user = await db.get_user(int(query)) if query.isdigit() else await db.get_user_by_rid(query)
    if not user:
        await message.answer("Ishtirokchi topilmadi.")
        await state.clear()
        return

    await state.update_data(target_user_id=user["user_id"])
    await state.set_state(AdminRefState.waiting_refs)
    await message.answer(
        f"👤 {user['full_name'] or user['tg_name']}\n"
        f"🆔 {user['rid'] or '-'}\n\n"
        f"Endi qo‘shiladigan yoki ayriladigan referal sonini yuboring.\n"
        f"Masalan: 2 yoki -1"
    )


@router.message(AdminRefState.waiting_refs)
async def add_ref_finish(message: Message, state: FSMContext):
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("Referal soni raqam bo‘lishi kerak.")
        return

    refs = int(message.text.strip())
    data = await state.get_data()
    user_id = data["target_user_id"]

    await db.add_referrals(user_id, refs)
    user = await db.get_user(user_id)

    await message.answer(
        f"✅ Referal muvaffaqiyatli yangilandi.\n\n"
        f"👤 {user['full_name'] or user['tg_name']}\n"
        f"🆔 {user['rid'] or '-'}\n"
        f"👥 Joriy referal: {user['referral_count']}\n"
        f"💎 Joriy ball: {user['diamonds']}",
        reply_markup=admin_menu()
    )
    await state.clear()


@router.message(lambda m: m.text == "⛔ Ban user")
async def ban_user_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(BanState.waiting_user)
    await message.answer("Ban qilish uchun ishtirokchi ID yoki R-ID yuboring.")


@router.message(BanState.waiting_user)
async def ban_user_finish(message: Message, state: FSMContext):
    query = message.text.strip()
    user = await db.get_user(int(query)) if query.isdigit() else await db.get_user_by_rid(query)
    if not user:
        await message.answer("Ishtirokchi topilmadi.")
        await state.clear()
        return

    await db.ban_user(user["user_id"])
    await message.answer(
        f"⛔ Ishtirokchi ban qilindi.\n\n"
        f"👤 {user['full_name'] or user['tg_name']}\n"
        f"🆔 {user['rid'] or '-'}",
        reply_markup=admin_menu()
    )
    await state.clear()


@router.message(lambda m: m.text == "✅ Unban user")
async def unban_user_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(UnbanState.waiting_user)
    await message.answer("Unban qilish uchun ishtirokchi ID yoki R-ID yuboring.")


@router.message(UnbanState.waiting_user)
async def unban_user_finish(message: Message, state: FSMContext):
    query = message.text.strip()
    user = await db.get_user(int(query)) if query.isdigit() else await db.get_user_by_rid(query)
    if not user:
        await message.answer("Ishtirokchi topilmadi.")
        await state.clear()
        return

    await db.unban_user(user["user_id"])
    await message.answer(
        f"✅ Ishtirokchi unban qilindi.\n\n"
        f"👤 {user['full_name'] or user['tg_name']}\n"
        f"🆔 {user['rid'] or '-'}",
        reply_markup=admin_menu()
    )
    await state.clear()


@router.message(lambda m: m.text == "🔎 User qidirish")
async def search_user_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(SearchState.waiting_query)
    await message.answer("Qidirish uchun ID, R-ID yoki ism yuboring.")


@router.message(SearchState.waiting_query)
async def search_user_finish(message: Message, state: FSMContext):
    rows = await db.search_users(message.text.strip())
    if not rows:
        await message.answer("Ishtirokchi topilmadi.")
        await state.clear()
        return

    text = "🔎 <b>Qidiruv natijalari</b>\n\n"
    for user in rows:
        text += (
            f"👤 {user['full_name'] or user['tg_name'] or '-'}\n"
            f"🆔 {user['rid'] or '-'}\n"
            f"📱 {user['phone'] or '-'}\n"
            f"🌍 {user['region'] or '-'} / {user['district'] or '-'}\n"
            f"💎 {user['diamonds']} | 👥 {user['referral_count']}\n\n"
        )

    await message.answer(text, reply_markup=admin_menu())
    await state.clear()


@router.message(lambda m: m.text == "💬 Userga xabar yuborish")
async def direct_msg_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(DirectMessageState.waiting_user)
    await message.answer("Xabar yuboriladigan ishtirokchi ID yoki R-ID ni yuboring.")


@router.message(DirectMessageState.waiting_user)
async def direct_msg_pick_user(message: Message, state: FSMContext):
    query = message.text.strip()
    user = await db.get_user(int(query)) if query.isdigit() else await db.get_user_by_rid(query)
    if not user:
        await message.answer("Ishtirokchi topilmadi.")
        await state.clear()
        return

    await state.update_data(target_user_id=user["user_id"])
    await state.set_state(DirectMessageState.waiting_message)
    await message.answer(f"Endi {user['full_name'] or user['tg_name']} uchun yuboriladigan xabarni yozing.")


@router.message(DirectMessageState.waiting_message)
async def direct_msg_send(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["target_user_id"]

    try:
        await message.bot.send_message(user_id, f"📩 <b>Admin xabari</b>\n\n{message.text}")
        await message.answer("✅ Xabar yuborildi.", reply_markup=admin_menu())
    except Exception as e:
        await message.answer(f"Xabar yuborilmadi: {e}", reply_markup=admin_menu())

    await state.clear()


@router.message(lambda m: m.text == "📣 Broadcast")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(BroadcastState.waiting_content)
    await message.answer(
        "Broadcast uchun matn, rasmga caption bilan yoki voice yuborishingiz mumkin.\n\n"
        "✅ Oddiy matn yuborsangiz — hammaga text ketadi\n"
        "✅ Rasm yuborsangiz — hammaga rasm ketadi\n"
        "✅ Voice yuborsangiz — hammaga voice ketadi"
    )


@router.message(BroadcastState.waiting_content)
async def broadcast_send(message: Message, state: FSMContext):
    users = await db.all_users()
    sent = 0

    for user in users:
        try:
            if message.photo:
                await message.bot.send_photo(
                    user["user_id"],
                    photo=message.photo[-1].file_id,
                    caption=message.caption or ""
                )
            elif message.voice:
                await message.bot.send_voice(
                    user["user_id"],
                    voice=message.voice.file_id,
                    caption=message.caption or ""
                )
            else:
                await message.bot.send_message(
                    user["user_id"],
                    f"📢 <b>ALOOFEST yangiligi</b>\n\n{message.text or ''}"
                )
            sent += 1
            await asyncio.sleep(0.03)
        except Exception:
            pass

    await message.answer(f"✅ Broadcast yakunlandi. Yuborildi: {sent}", reply_markup=admin_menu())
    await state.clear()


@router.message(lambda m: m.text == "📋 Mijozlar ro‘yxati")
async def users_list(message: Message):
    if not is_admin(message.from_user.id):
        return

    users = await db.get_recent_users(30)
    if not users:
        await message.answer("Mijozlar topilmadi.")
        return

    text = "📋 <b>Mijozlar ro‘yxati</b>\n\n"
    for u in users:
        text += f"🆔 {u['rid'] or '-'} | 👤 {u['full_name'] or u['tg_name'] or '-'} | 💎 {u['diamonds']}\n"
    await message.answer(text)


@router.message(lambda m: m.text == "📊 Statistika")
async def stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    s = await db.get_stats()
    await message.answer(
        f"📊 <b>Umumiy statistika</b>\n\n"
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

    text = "🌍 <b>Hududiy statistika</b>\n\n"
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

    text = "🎟 <b>PROMO statistika</b>\n\n"
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


@router.message(lambda m: m.text == "🎲 Random start")
async def random_start(message: Message):
    if not is_admin(message.from_user.id):
        return

    now = datetime.now()
    await message.answer(
        "🎲 <b>RANDOM START</b>\n\n📅 Boshlanish sanasini tanlang:",
        reply_markup=build_calendar(now.year, now.month, "rnd_start")
    )


@router.callback_query(F.data == "noop")
async def noop_handler(call: CallbackQuery):
    await call.answer()


@router.callback_query(F.data.startswith("rnd_start:nav:"))
async def rnd_start_nav(call: CallbackQuery):
    _, _, y, m, direction = call.data.split(":")
    y = int(y)
    m = int(m)

    if direction == "prev":
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    else:
        m += 1
        if m == 13:
            m = 1
            y += 1

    await call.message.edit_reply_markup(reply_markup=build_calendar(y, m, "rnd_start"))
    await call.answer()


@router.callback_query(F.data.startswith("rnd_start:pick:"))
async def rnd_start_pick(call: CallbackQuery):
    _, _, y, m, d = call.data.split(":")
    start_date = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

    now = datetime.now()
    await call.message.edit_text(
        f"✅ Boshlanish sanasi: <b>{start_date}</b>\n\n📅 Endi tugash sanasini tanlang:",
        reply_markup=build_calendar(now.year, now.month, f"rnd_end:{start_date}")
    )
    await call.answer()


@router.callback_query(F.data.startswith("rnd_end:"))
async def rnd_end_router(call: CallbackQuery):
    parts = call.data.split(":")
    if len(parts) < 5:
        await call.answer()
        return

    _, start_date, action, y, m, *rest = parts
    y = int(y)
    m = int(m)

    if action == "nav":
        direction = rest[0]
        if direction == "prev":
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        else:
            m += 1
            if m == 13:
                m = 1
                y += 1

        await call.message.edit_reply_markup(reply_markup=build_calendar(y, m, f"rnd_end:{start_date}"))
        await call.answer()
        return

    if action == "pick":
        d = int(rest[0])
        end_date = f"{y:04d}-{m:02d}-{d:02d}"

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎯 RANDOMNI BOSHLASH", callback_data=f"rnd_confirm:{start_date}:{end_date}")]
            ]
        )

        await call.message.edit_text(
            f"✅ Boshlanish: <b>{start_date}</b>\n"
            f"✅ Tugash: <b>{end_date}</b>\n\n"
            f"Endi randomni boshlash tugmasini bosing.",
            reply_markup=kb
        )
        await call.answer()


@router.callback_query(F.data.startswith("rnd_confirm:"))
async def random_confirm(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    _, start_date, end_date = call.data.split(":", 2)

    users = await db.get_random_candidates()
    if not users:
        await call.message.edit_text("❌ Random uchun ishtirokchilar topilmadi.")
        await call.answer()
        return

    for p in range(1, 101):
        if p == 1:
            await call.message.edit_text(
                "🎲 <b>Random ishga tushdi</b>\n\n"
                "⏳ Ishtirokchilar tekshirilmoqda...\n"
                f"Loading: {p}%"
            )
        elif p % 5 == 0:
            await call.message.edit_text(
                "🎲 <b>Random ishga tushdi</b>\n\n"
                "🔍 Ishtirokchilar saralanmoqda...\n"
                "✨ G‘olib aniqlanmoqda...\n"
                f"Loading: {p}%"
            )
        await asyncio.sleep(0.6)

    winner = random.choice(users)
    winner_name = winner["full_name"] or winner["tg_name"] or "Ishtirokchi"

    await db.save_random_history(
        winner_user_id=winner["user_id"],
        winner_name=winner_name,
        rid=winner["rid"] or "-",
        phone=winner["phone"] or "",
        points=winner["diamonds"] or 0,
        start_date=start_date,
        end_date=end_date,
    )

    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_last_random")],
            [InlineKeyboardButton(text="📢 G‘olibni e’lon qilish", callback_data="announce_last_random")]
        ]
    )

    await call.message.edit_text(
        f"🏆 <b>Random g‘olibi aniqlandi!</b>\n\n"
        f"👤 Ism: {winner_name}\n"
        f"🌍 Hudud: {winner['region'] or '-'} / {winner['district'] or '-'}\n"
        f"📱 Telefon: {winner['phone'] or '-'}\n"
        f"🆔 ID: {winner['rid'] or '-'}\n"
        f"💎 Ball: {winner['diamonds'] or 0}\n\n"
        f"📅 Oralig‘: {start_date} → {end_date}",
        reply_markup=confirm_kb
    )
    await call.answer()


@router.callback_query(F.data == "confirm_last_random")
async def confirm_last_random(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    row = await db.get_last_random()
    if not row:
        await call.answer("Tasdiqlanadigan random topilmadi.", show_alert=True)
        return

    await db.confirm_last_random()

    try:
        await call.message.bot.send_message(
            row["winner_user_id"],
            "🎉 <b>Tabriklaymiz!</b>\n\n"
            "Siz bugungi random o‘yinining g‘olibi bo‘ldingiz.\n\n"
            "📞 Tez orada siz bilan <b>93 194 92 00</b> raqamidan bog‘lanishadi.\n"
            "Agar 5–6 soat ichida bog‘lanishmasa, o‘zingiz aloqaga chiqing."
        )
    except Exception:
        pass

    await call.answer("✅ G‘olibga xabar yuborildi.", show_alert=True)


@router.callback_query(F.data == "announce_last_random")
async def announce_last_random(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    row = await db.get_last_random()
    if not row:
        await call.answer("E’lon qilinadigan random topilmadi.", show_alert=True)
        return

    phone = row["phone"] or ""
    masked = phone[:5] + "***" + phone[-2:] if len(phone) >= 7 else phone
    users = await db.all_users()

    text = (
        "📢 <b>Bugungi random o‘yini g‘olibi aniqlandi!</b>\n\n"
        f"📅 Sana: {row['end_date']}\n"
        f"👥 Ishtirokchilar soni: {len(users)}\n"
        f"🏆 G‘olib: {row['winner_name']}\n"
        f"🆔 ID: {row['rid']}\n"
        f"📱 Telefon: {masked}\n\n"
        "Barcha ishtirokchilarga rahmat! Keyingi random o‘yinlarida faol bo‘ling va imkoniyatingizni oshiring."
    )

    sent = 0
    for user in users:
        try:
            await call.message.bot.send_message(user["user_id"], text)
            sent += 1
            await asyncio.sleep(0.03)
        except Exception:
            pass

    await call.answer(f"E’lon yuborildi: {sent} ta foydalanuvchiga", show_alert=True)
