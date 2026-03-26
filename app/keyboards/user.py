from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ ISHTIROK ETAMAN", callback_data="join_now")]
        ]
    )


def rules_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 O‘yin qoidalari", callback_data="show_rules")]
        ]
    )


def subscribe_keyboard(channel_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url=f"https://t.me/{channel_username}")],
            [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription")],
        ]
    )


def after_registration_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 BOSHLASH", callback_data="open_main_menu")]
        ]
    )


def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Raqamni ulashish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Mening shaxsiy linkim")],
            [KeyboardButton(text="🎲 Random holati"), KeyboardButton(text="💎 Ballarim")],
            [KeyboardButton(text="🎁 Sovg‘alar"), KeyboardButton(text="ℹ️ O‘yin haqida")],
            [KeyboardButton(text="🆘 Yordam")],
        ],
        resize_keyboard=True
    )


def admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎲 Random start")],
            [KeyboardButton(text="📋 Mijozlar ro‘yxati"), KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="➕ Ball qo‘shish"), KeyboardButton(text="👥 Referal qo‘shish")],
            [KeyboardButton(text="⛔ Ban user"), KeyboardButton(text="✅ Unban user")],
            [KeyboardButton(text="🔎 User qidirish"), KeyboardButton(text="💬 Userga xabar yuborish")],
            [KeyboardButton(text="📣 Broadcast"), KeyboardButton(text="📤 Excel export")],
            [KeyboardButton(text="🌍 Hududiy statistika"), KeyboardButton(text="🎟 PROMO")],
        ],
        resize_keyboard=True
    )
