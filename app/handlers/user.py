from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import aiosqlite

from app.config import CHANNEL, BOT_USERNAME
from app.database.db import DB
from app.services.ranking import get_top
from app.services.referral import generate_ref_link

router = Router()

user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Do‘stlarni taklif qilish"), KeyboardButton(text="🏆 Reyting (TOP 10)")],
        [KeyboardButton(text="🎲 Random o‘yin"), KeyboardButton(text="💎 Mening ballarim")],
        [KeyboardButton(text="📊 Statistikam"), KeyboardButton(text="ℹ️ Konkurs haqida")],
        [KeyboardButton(text="🎁 Sovg‘alar"), KeyboardButton(text="📘 Qo‘llanma")],
        [KeyboardButton(text="📞 Bog‘lanish")],
    ],
    resize_keyboard=True
)


@router.callback_query(F.data == "join")
async def join_contest(callback):
    text = f"""
🏆 <b>aloofest konkurs tizimi (final model)</b>

🎯 <b>Ball tizimi</b>

1 ta do‘st taklif qilish = <b>5 ball</b>

Ball random o‘yinda ham, TOP reytingda ham ishlatiladi.

Misol:
• 1 referal = 5 ball
• 5 referal = 25 ball
• 10 referal = 50 ball

🎲 <b>1. Har hafta RANDOM o‘yini</b>

Kamida <b>3 ta do‘st</b> taklif qilish kerak.
3 referal = 15 ball

Shunda foydalanuvchi random o‘yin ishtirokchisi bo‘ladi.

🥇 <b>2. RAMAZON HAYITI SUPER KONKURSI (TOP)</b>

Eng ko‘p ball yig‘ganlar yutadi.

📋 <b>TOP konkurs shartlari</b>

1️⃣ Telegram:
Ishtirokchi {CHANNEL} kanaliga obuna bo‘lishi kerak.

2️⃣ Instagram:
@aloo.uz_ sahifasiga obuna bo‘lishi kerak.

🌐 Ro‘yxatdan o‘tish WEB orqali amalga oshiriladi.
"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL.replace('@','')}")],
            [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")]
        ]
    )
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "check_sub")
async def check_subscription(callback):
    user_id = callback.from_user.id
    try:
        member = await callback.bot.get_chat_member(CHANNEL, user_id)
        if member.status in ("member", "administrator", "creator"):
            async with aiosqlite.connect(DB) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO users (telegram_id)
                    VALUES (?)
                """, (user_id,))
                await db.commit()

            web_url = f"https://aloofest-production.up.railway.app/register?telegram_id={user_id}"
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🌐 Ro‘yxatdan o‘tish", url=web_url)]
                ]
            )
            await callback.message.answer(
                "✅ Obuna tasdiqlandi.\n\nEndi WEB sahifa orqali ro‘yxatdan o‘ting:",
                reply_markup=kb
            )
        else:
            await callback.message.answer("❌ Siz hali kanalga obuna bo‘lmagansiz.")
    except Exception:
        await callback.message.answer("❌ Obunani tekshirib bo‘lmadi. Kanal username va bot adminligini tekshiring.")
    await callback.answer()


@router.message(F.text == "👥 Do‘stlarni taklif qilish")
async def invite_friends(message: Message):
    link = generate_ref_link(BOT_USERNAME, message.from_user.id)
    await message.answer(
        f"""👥 <b>Do‘stlarni taklif qilish</b>

Sizning taklif havolangiz:

{link}

1 do‘st = 5 ball
Ko‘proq do‘st taklif qiling va TOP reytingga kiring!"""
    )


@router.message(F.text == "🏆 Reyting (TOP 10)")
async def ranking_top(message: Message):
    top = await get_top()
    if not top:
        await message.answer("Hozircha reyting bo‘sh.")
        return

    text = "<b>🏆 Aloofest TOP 10</b>\n\n"
    for i, row in enumerate(top, start=1):
        name = row[0] or "Ishtirokchi"
        fest_id = row[1] or "FEST-000"
        points = row[2] or 0
        text += f"{i}. {name} — {fest_id} — {points} ball\n"

    await message.answer(text)


@router.message(F.text == "🎲 Random o‘yin")
async def random_game_info(message: Message):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT referrals_count FROM users WHERE telegram_id=?",
            (message.from_user.id,)
        )
        row = await cur.fetchone()

    refs = row[0] if row else 0
    need = max(0, 3 - refs)

    if refs >= 3:
        text = f"""🎲 <b>Random o‘yin</b>

Siz random o‘yin uchun mos ekansiz ✅

👥 Taklif qilingan do‘stlar: {refs}
💎 Ballar random va TOP uchun hisoblanadi."""
    else:
        text = f"""🎲 <b>Random o‘yin</b>

Kamida 3 ta do‘st taklif qilish kerak.

👥 Siz taklif qilgan do‘stlar: {refs}
Yana {need} ta do‘st taklif qilsangiz random ishtirokchisiga aylanasiz."""
    await message.answer(text)


@router.message(F.text == "💎 Mening ballarim")
async def my_points(message: Message):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
            SELECT name, fest_id, referrals_count, points
            FROM users WHERE telegram_id=?
        """, (message.from_user.id,))
        row = await cur.fetchone()

    if not row:
        await message.answer("Siz hali ro‘yxatdan o‘tmagansiz.")
        return

    name, fest_id, refs, points = row
    remain = max(0, 3 - (refs or 0))

    extra = (
        "✅ Siz random o‘yinga kirdingiz."
        if (refs or 0) >= 3 else
        f"🎲 Random o‘yinga kirish uchun yana {remain} do‘st taklif qiling."
    )

    await message.answer(
        f"""💎 <b>Mening ballarim</b>

👤 Ism: {name or "—"}
🆔 ID: {fest_id or "—"}

👥 Taklif qilingan do‘stlar: {refs or 0}
💎 Ballar: {points or 0}

{extra}"""
    )


@router.message(F.text == "📊 Statistikam")
async def my_stats(message: Message):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
            SELECT name, fest_id, referrals_count, points, region, district
            FROM users WHERE telegram_id=?
        """, (message.from_user.id,))
        row = await cur.fetchone()

    if not row:
        await message.answer("Statistika uchun avval ro‘yxatdan o‘ting.")
        return

    name, fest_id, refs, points, region, district = row
    await message.answer(
        f"""📊 <b>Statistikam</b>

👤 Ism: {name or "—"}
🆔 FEST ID: {fest_id or "—"}
👥 Referallar: {refs or 0}
💎 Ballar: {points or 0}
📍 Hudud: {region or "—"}, {district or "—"}"""
    )


@router.message(F.text == "ℹ️ Konkurs haqida")
async def contest_info(message: Message):
    await message.answer(
        """ℹ️ <b>Konkurs haqida</b>

• 1 do‘st = 5 ball
• 3 ta do‘st = random imkoniyati
• Eng ko‘p ball yig‘ganlar TOP g‘olib bo‘ladi
• Har 5 referalda bonus +10 ball beriladi

📅 G‘oliblar sanasi bot va @aloo_uzb kanalida e’lon qilinadi."""
    )


@router.message(F.text == "🎁 Sovg‘alar")
async def gifts(message: Message):
    await message.answer(
        """🎁 <b>Joriy sovg‘alar</b>

<b>TOP 3:</b>
🥇 Tecno Spark GO 30C
🥈 Mini pech Artel
🥉 Ryugzak

<b>Random:</b>
1. Airpods Max Copy
2. Airpods Max Copy
3. Airpods Max Copy

Admin sovg‘alarni istalgan vaqtda yangilashi mumkin."""
    )


@router.message(F.text == "📘 Qo‘llanma")
async def guide(message: Message):
    await message.answer(
        """📘 <b>Qo‘llanma</b>

1. Kanalga obuna bo‘ling
2. WEB orqali ro‘yxatdan o‘ting
3. Do‘stlaringizni taklif qiling
4. 1 do‘st = 5 ball
5. 3 ta do‘st taklif qilsangiz randomga tushasiz
6. Eng ko‘p ball yig‘sangiz TOP g‘olib bo‘lasiz"""
    )
