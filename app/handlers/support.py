from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from app.config import ADMIN_IDS

router = Router()

support_users = {}

exit_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Yakunlash")]
    ],
    resize_keyboard=True
)


@router.message(F.text == "📞 Bog‘lanish")
async def support_start(message: Message):

    support_users[message.from_user.id] = True

    await message.answer(
        """📞 Bog‘lanish

Iltimos, savolingizni yuboring.
Xabaringiz adminlarga jo‘natiladi.

Chiqish uchun ❌ Yakunlash tugmasini bosing.""",
        reply_markup=exit_kb
    )


@router.message(F.text == "❌ Yakunlash")
async def support_stop(message: Message):

    support_users.pop(message.from_user.id, None)

    await message.answer("Muloqot yakunlandi.")


@router.message()
async def support_messages(message: Message):

    if message.from_user.id not in support_users:
        return

    for admin in ADMIN_IDS:

        await message.bot.send_message(
            admin,
            f"""
📩 Yangi murojaat

👤 {message.from_user.full_name}
🆔 {message.from_user.id}

📝 Savol:
{message.text}
"""
        )

    await message.answer(
        "✅ Xabaringiz yuborildi. Admin javobini kuting."
    )
