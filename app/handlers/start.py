import hmac
import hashlib

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.config import CHANNEL_USERNAME, BASE_URL, WEBAPP_SECRET
from app.database.db import db
from app.keyboards.user import start_keyboard, rules_keyboard, subscribe_keyboard

router = Router()

START_TEXT = """
🎉 <b>ALOOFEST 2-MAVSUM RANDOM sovg‘ali o‘yinlariga xush kelibsiz!</b>

“aloo” siz uchun navbatdagi qiziqarli va sovg‘alarga boy mavsumni boshlab berdi.  
Bu safar o‘yin yanada sodda, yanada faol va yanada foydali bo‘ladi. 🔥

🎁 <b>Asosiy sovg‘alar:</b>
📱 Telefon  
📟 Planshet  
🫖 Elektr choynak  
⌚ Smartwatch  
🎧 AirPods  
va boshqa qimmatbaho sovg‘alar

📅 <b>Random o‘yinlari har hafta chorshanba kuni soat 14:00 da</b> jonli efirda o‘tkaziladi.

💙 Ishtirok etish juda oson:
— kanalga obuna bo‘ling  
— ro‘yxatdan o‘ting  
— do‘stlaringizni taklif qiling  
— ball yig‘ing  
— random ishtirokchisiga aylaning

🚀 Tayyor bo‘lsangiz, boshlaymiz!
"""

RULES_TEXT = """
📋 <b>ALOOFEST 2-MAVSUM o‘yin qoidalari</b>

Bu mavsumda o‘yin <b>faqat RANDOM formatda</b> bo‘ladi.  
Demak, siz har hafta yangi imkoniyat bilan sovg‘a yutishingiz mumkin. 🎲

💎 <b>Ball tizimi:</b>
• Ro‘yxatdan o‘tish — <b>+5 ball</b>  
• Har 1 ta do‘st taklif qilish — <b>+5 ball</b>  
• Promokod kiritish — <b>+15 ball</b>

🏬 <b>Promokod haqida:</b>
Agar siz eng yaqin <b>aloo</b> do‘koniga borib promokod olsangiz, botga kiritganingizdan keyin sizga darhol <b>+15 ball</b> qo‘shiladi.

Shunda yana atigi <b>2 ta do‘st</b> taklif qilsangiz, random o‘yinida qatnashish imkoniyatiga juda yaqinlashasiz.

✅ <b>Randomda qatnashish uchun:</b>
Tanlangan haftada jami <b>25 ball yoki undan ko‘p</b> to‘plashingiz kerak.

📅 <b>Muhim:</b>
Random har hafta alohida hisoblanadi.  
Yangi haftada yana faol bo‘lish sizning g‘oliblik imkoniyatingizni oshiradi.

👇 Endi keyingi bosqichga o‘tish uchun kanalga obuna bo‘ling va tekshirish tugmasini bosing.
"""


def sign_uid(uid: int) -> str:
    return hmac.new(
        WEBAPP_SECRET.encode(),
        str(uid).encode(),
        hashlib.sha256
    ).hexdigest()


@router.message(CommandStart())
async def start_cmd(message: Message):
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        tg_name=message.from_user.first_name,
    )

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) > 1 and parts[1].startswith("ref_"):
        ref = parts[1].replace("ref_", "").strip()
        if ref.isdigit():
            await db.set_referrer_if_empty(message.from_user.id, int(ref))

    user = await db.get_user(message.from_user.id)
    if user and user["registered"]:
        await message.answer(
            "🎉 Siz allaqachon ro‘yxatdan o‘tgansiz.\n\n"
            "Endi menyu orqali o‘yindagi holatingizni kuzatishingiz mumkin."
        )
        return

    await message.answer(START_TEXT, reply_markup=start_keyboard())


@router.callback_query(F.data == "join_now")
async def join_now(call: CallbackQuery):
    await call.message.answer(
        "🔥 Ajoyib! Unda birinchi navbatda o‘yin qoidalari bilan tanishib chiqing:",
        reply_markup=rules_keyboard()
    )
    await call.answer()


@router.callback_query(F.data == "show_rules")
async def show_rules(call: CallbackQuery):
    await call.message.answer(
        RULES_TEXT,
        reply_markup=subscribe_keyboard(CHANNEL_USERNAME)
    )
    await call.answer()


@router.callback_query(F.data == "check_subscription")
async def check_subscription(call: CallbackQuery):
    uid = call.from_user.id
    sig = sign_uid(uid)
    url = f"{BASE_URL}/register?uid={uid}&sig={sig}"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 RO‘YXATDAN O‘TISH", url=url)]
        ]
    )

    await call.message.answer(
        "✅ Zo‘r! Endi ro‘yxatdan o‘tish bosqichiga o‘tamiz.\n\n"
        "Quyidagi tugma orqali ma’lumotlaringizni kiriting va o‘yin ishtirokchisiga aylaning 👇",
        reply_markup=kb,
    )
    await call.answer()
