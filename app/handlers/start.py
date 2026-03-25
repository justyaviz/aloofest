from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.config import CHANNEL_USERNAME
from app.database.db import db
from app.keyboards.user import start_keyboard, rules_keyboard, subscribe_keyboard, register_keyboard

router = Router()

START_TEXT = """
🎉 <b>ALOOFEST 2-MAVSUM RANDOM sovg‘ali o‘yinlariga start berildi!</b>

Asosiy sovg‘alar:
📱 Telefon
📟 Planshet
🫖 Elektr choynak
⌚ Smartwatch
🎧 AirPods
va boshqalar

O‘yin har hafta <b>chorshanba kuni soat 14:00</b> jonli efirda bo‘ladi.
"""

RULES_TEXT = """
🎲 <b>Bu galgi o‘yin faqat RANDOM formatda bo‘ladi</b>

Ishtirok tartibi:
• Kanalga obuna bo‘lish
• Ro‘yxatdan o‘tish
• Do‘stlarni taklif qilish
• 25+ ball yig‘ish

💎 Ball tizimi:
• Ro‘yxatdan o‘tish: +5
• 1 do‘st taklif qilish: +5
• Promokod: +15

Agar do‘kondan promokod olsangiz, sizga +15 ball tushadi.
Shunda yana 2 ta do‘st taklif qilsangiz, randomga kirishingiz osonlashadi.
"""


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
        await message.answer("Siz allaqachon ro‘yxatdan o‘tgansiz.")
        return

    await message.answer(START_TEXT, reply_markup=start_keyboard())


@router.callback_query(F.data == "join_now")
async def join_now(call: CallbackQuery):
    await call.message.answer("Qoidalar bilan tanishing 👇", reply_markup=rules_keyboard())
    await call.answer()


@router.callback_query(F.data == "show_rules")
async def show_rules(call: CallbackQuery):
    await call.message.answer(RULES_TEXT, reply_markup=subscribe_keyboard(CHANNEL_USERNAME))
    await call.answer()


@router.callback_query(F.data == "check_subscription")
async def check_subscription(call: CallbackQuery):
    await call.message.answer(
        "✅ Obuna tekshirildi deb hisoblaymiz.\n\nEndi ro‘yxatdan o‘ting.",
        reply_markup=register_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "fake_register_info")
async def fake_register_info(call: CallbackQuery):
    await call.message.answer(
        "Web registration qismi uchun `app/web/` ichidagi eski sahifangizni ulaysiz.\n"
        "Hozircha backend tayyor, keyin ulab qo‘yasiz."
    )
    await call.answer()
