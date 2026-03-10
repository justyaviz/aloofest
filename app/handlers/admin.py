from aiogram import Router
from aiogram.types import Message
from app.config import ADMIN_IDS
from app.services.export_service import export_users

router = Router()


@router.message(lambda m: m.from_user.id in ADMIN_IDS)
async def admin_panel(message: Message):

    if message.text == "/admin":

        await message.answer("""
⚙ ADMIN PANEL

/users
/broadcast
/export
/random
""")


@router.message(lambda m: m.text == "/export")
async def export(message: Message):

    file = await export_users()

    await message.answer_document(open(file,"rb"))

@router.message(lambda m: m.text == "/random")
async def random(message: Message):

    user = await choose_random_winner()

    await message.answer(f"Random winner ID: {user}")
