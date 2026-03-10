from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
