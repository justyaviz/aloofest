from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    text = """
🎉 <b>Kutib oling aloo'dan MEGA KONKURS - aloofest</b>

🎯 Sizda 2 xil yutish imkoniyati bor:

1️⃣ TOP 3 ga kirish  
2️⃣ Random o'yini

🎁 <b>TOP sovg‘alar</b>

🥇 Tecno Spark GO 30C  
🥈 Mini pech Artel  
🥉 Ryugzak

🎲 <b>Random sovg‘alar</b>

Airpods Max Copy (3 ta)

📅 G'oliblar JONLI EFIR orqali aniqlanadi.

1️⃣ Birinchi qadam: <b>ISHTIROK ETAMAN</b>
"""

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 ISHTIROK ETAMAN", callback_data="join")]
        ]
    )

    await message.answer(text, reply_markup=kb)
