from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.database.db import db
from app.keyboards.user import phone_keyboard, main_menu

router = Router()

GUIDE_TEXT = """
🎉 <b>Tabriklaymiz!</b>

Siz <b>ALOOFEST 2-MAVSUM RANDOM sovg‘ali o‘yinlari</b>da muvaffaqiyatli ro‘yxatdan o‘tdingiz va boshlang‘ich ballarni qo‘lga kiritdingiz. ✅

📌 Endi keyingi bosqich juda muhim:
quyidagi qisqa yo‘riqnoma orqali o‘yinda qanday qatnashish, ballarni qanday yig‘ish va randomga qanday kirishni bilib oling.

🎯 <b>Sizning imkoniyatingiz:</b>
• har hafta random o‘yinida qatnashish  
• do‘st taklif qilib ball yig‘ish  
• promokod orqali qo‘shimcha ustunlikka ega bo‘lish

💎 <b>Ball tizimi:</b>
• ro‘yxatdan o‘tish — +5 ball  
• har 1 do‘st taklif qilish — +5 ball  
• promokod — +15 ball

🏬 <b>Muhim:</b>
Agar ballaringizni tezroq oshirmoqchi bo‘lsangiz, eng yaqin <b>aloo</b> do‘koniga borib promokod oling.

📅 Random o‘yinlari har hafta <b>chorshanba kuni soat 14:00</b> da bo‘lib o‘tadi.

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
            f"📱 <b>{user['full_name']}</b>, ro‘yxatdan o‘tish jarayonini yakunlash uchun telefon raqamingizni ulashing.",
            reply_markup=phone_keyboard()
        )
        await call.answer("Raqamni ulashing")
        return

    await call.message.answer(GUIDE_TEXT, reply_markup=main_menu())
    await call.answer("Menyu ochildi")


@router.message(F.contact)
async def save_contact(message: Message):
    user = await db.get_user(message.from_user.id)

    if not user or not user["registered"]:
        await message.answer("Avval ro‘yxatdan o‘ting.")
        return

    await db.save_phone(message.from_user.id, message.contact.phone_number)

    await message.answer(
        f"🎉 <b>Tabriklaymiz, {user['full_name']}!</b>\n\n"
        f"Telefon raqamingiz muvaffaqiyatli qabul qilindi. Endi siz o‘yin menyularidan to‘liq foydalanishingiz mumkin.",
        reply_markup=main_menu()
    )

    await message.answer(GUIDE_TEXT, reply_markup=main_menu())
