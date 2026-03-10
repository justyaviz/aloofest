from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    text = """
🎉 <b>Kutib oling aloo'dan MEGA KONKURS - aloofest</b>

🎯 Sizda 2 xil yutish imkoniyati bor:

1️⃣ TOP 3 ga kirish
2️⃣ Random o'yini

🥇 Tecno Spark GO 30C
🥈 Mini pech Artel
🥉 Ryugzak

🎲 Random sovg‘alar:
Airpods Max Copy (3 ta)

📅 G'oliblar JONLI EFIR orqali aniqlanadi.

1️⃣ Birinchi qadam: ISHTIROK ETAMAN
"""

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 ISHTIROK ETAMAN",
                    callback_data="join_contest"
                )
            ]
        ]
    )

    await message.answer(text, reply_markup=kb)

from aiogram.types import CallbackQuery
from app.keyboards.user import menu


@router.callback_query(lambda c: c.data == "join_contest")
async def join_contest(callback: CallbackQuery):

    text = """
🏆 <b>aloofest konkurs tizimi</b>

🎯 Ball tizimi

1 ta do‘st taklif qilish = <b>5 ball</b>

🎲 Random o‘yini

Kamida <b>3 ta do‘st</b> taklif qilish kerak.

3 referal = 15 ball

🥇 TOP konkurs

Eng ko‘p ball yig‘ganlar yutadi.

📋 Shartlar

1️⃣ @aloo_uzb kanaliga obuna bo‘lish

2️⃣ Instagram:
@aloo.uz_ sahifasiga obuna

🌐 Ro‘yxatdan o‘tish WEB orqali amalga oshiriladi.
"""

    await callback.message.answer(text, reply_markup=menu)

    await callback.answer()
