from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from app.config import ADMIN_IDS

router = Router()

support_users = {}

exit_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Yakunlash")]],
    resize_keyboard=True
)


@router.message(F.text == "📞 Bog‘lanish")
async def support_start(message: Message):

    support_users[message.from_user.id] = True

    await message.answer(
        """📞 Bog‘lanish

Savolingizni yozing.
Adminlarga yuboriladi.""",
        reply_markup=exit_kb
    )


@router.message()
async def support_forward(message: Message):

    if message.from_user.id not in support_users:
        return

    for admin in ADMIN_IDS:

        await message.bot.send_message(
            admin,
            f"""
📩 Yangi murojaat

👤 {message.from_user.full_name}
🆔 {message.from_user.id}

{message.text}
"""
        )

    await message.answer("✅ Xabar yuborildi")
