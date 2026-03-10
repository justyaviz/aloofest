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
