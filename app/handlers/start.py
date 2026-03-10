from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    text = """
🎉 <b>Kutib oling aloo'dan MEGA KONKURS - aloofest</b>

🎯 Sizda 2 xil yutish imkoniyati bor:

1️⃣ TOP 3 ga kirish
2️⃣ Random o'yini

📅 G'oliblar JONLI EFIR orqali aniqlanadi.

Hammaga omad!
"""

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 ISHTIROK ETAMAN",
                    callback_data="participate"
                )
            ]
        ]
    )

    await message.answer(text, reply_markup=kb)
