from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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


@router.message(Text("📘 Qo‘llanma"))
async def help_menu(message: Message):

    text = """
📘 <b>Qo‘llanma</b>

1 do‘st = 5 ball

3 do‘st taklif qilsangiz
random o‘yinga tushasiz.

Eng ko‘p ball yig‘ganlar
TOP g‘olib bo‘lishi mumkin.
"""

    await message.answer(text)
