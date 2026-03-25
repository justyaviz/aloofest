from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.database.db import db
from app.keyboards.user import phone_keyboard, main_menu

router = Router()

GUIDE_TEXT = """
🎉 Tabriklaymiz!

Siz “aloofest” mega konkursida muvaffaqiyatli ro‘yxatdan o‘tdingiz va boshlang‘ich ball qo‘lga kiritdingiz. ✅

📌 Endi keyingi bosqich juda muhim:
quyidagi qisqa yo‘riqnoma orqali konkursda qanday qatnashish, ball yig‘ish va g‘olib bo‘lish tartibini ko‘rib chiqing.

🎯 Sizda 2 xil imkoniyat bor:
• TOP 3 mega konkursda g‘olib bo‘lish
• Haftalik random o‘yinlarida sovg‘a yutish

📹 Qisqa yo‘riqnoma:
• konkursda qanday ishtirok etish
• do‘st taklif qilib ball yig‘ish
• TOP 3 ga chiqish
• haftalik random o‘yinida qatnashish

👥 Endi do‘stlaringizni taklif qiling, ko‘proq ball yig‘ing va hayit oldidan “aloo”dan qimmatbaho sovg‘alarni yutib oling!

👇 Quyidagi menyular orqali davom eting
"""


@router.callback_query(F.data == "open_main_menu")
async def open_main_menu(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    if not user or not user["registered"]:
        await call.message.answer("Avval ro‘yxatdan o‘ting.")
        await call.answer()
        return

    if not user["phone_verified"]:
        await call.message.answer(
            "📱 Telefon raqamingizni ulashing.",
            reply_markup=phone_keyboard()
        )
        await call.answer()
        return

    await call.message.answer(GUIDE_TEXT, reply_markup=main_menu())
    await call.answer()


@router.message(F.contact)
async def save_contact(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user["registered"]:
        await message.answer("Avval ro‘yxatdan o‘ting.")
        return

    await db.save_phone(message.from_user.id, message.contact.phone_number)
    await message.answer(GUIDE_TEXT, reply_markup=main_menu())
