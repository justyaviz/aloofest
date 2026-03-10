from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👥 Do‘stlarni taklif qilish"),
            KeyboardButton(text="🏆 Reyting")
        ],
        [
            KeyboardButton(text="🎲 Random o‘yin"),
            KeyboardButton(text="💎 Mening ballarim")
        ],
        [
            KeyboardButton(text="🎁 Sovg‘alar"),
            KeyboardButton(text="📘 Qo‘llanma")
        ],
        [
            KeyboardButton(text="📞 Bog‘lanish")
        ]
    ],
    resize_keyboard=True
)


@router.message()
async def menu_handler(message: Message):

    if message.text == "📘 Qo‘llanma":

        await message.answer("""
📘 Qo‘llanma

1 do‘st = 5 ball

3 do‘st taklif qilsangiz randomga tushasiz.

Eng ko‘p ball yig‘ganlar TOP g‘olib bo‘ladi.
""")
