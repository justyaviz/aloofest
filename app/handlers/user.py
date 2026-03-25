from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.database.db import db
from app.keyboards.user import phone_keyboard, main_menu

router = Router()

GUIDE_TEXT = """
🎉 <b>Tabriklaymiz!</b>

Siz <b>ALOOFEST 2-MAVSUM</b> random sovg‘ali o‘yinlarida muvaffaqiyatli ro‘yxatdan o‘tdingiz va boshlang‘ich ballarni qo‘lga kiritdingiz. ✅

📌 <b>Endi keyingi bosqich juda muhim:</b>  
quyidagi qisqa yo‘riqnoma orqali konkursda qanday qatnashish, qanday ball yig‘ish va random o‘yinlarida qanday ishtirok etishni bilib oling.

🎯 <b>Sizning asosiy imkoniyatingiz:</b>
• har hafta random o‘yinida qatnashish  
• do‘stlaringizni taklif qilish orqali ball yig‘ish  
• promokod orqali qo‘shimcha ustunlikka ega bo‘lish

📹 <b>Qisqa yo‘riqnoma:</b>
• do‘stlarni taklif qiling  
• har bir taklif uchun +5 ball oling  
• do‘kondan promokod olib +15 ball qo‘lga kiriting  
• shu hafta ichida 25 ball to‘plab random ishtirokchisiga aylaning  
• chorshanba kuni soat 14:00 dagi jonli efirni kuzating

🏬 <b>Muhim eslatma:</b>
Promokodlar har hafta yangilanadi.  
Demak, yangi haftada yana faol bo‘lish, yangi promokod olish va yangi ball yig‘ish sizning g‘oliblik imkoniyatingizni oshiradi.

👥 Endi do‘stlaringizni taklif qiling, ko‘proq ball yig‘ing va “aloo”dan qimmatbaho sovg‘alarni yutib oling!

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
        f"Telefon raqamingiz muvaffaqiyatli qabul qilindi va siz endi o‘yin menyularidan to‘liq foydalanishingiz mumkin.",
        reply_markup=main_menu()
    )

    await message.answer(GUIDE_TEXT, reply_markup=main_menu())
