@router.message(lambda m: m.text == "🎲 Random admin")
async def random_admin(message: Message):
    if not is_admin(message.from_user.id):
        return

    users = await db.get_random_candidates()
    if not users:
        await message.answer("Random uchun ishtirokchi topilmadi.")
        return

    winner = random.choice(users)
    winner_name = winner["full_name"] or winner["tg_name"] or "Ishtirokchi"
    phone = winner["phone"] or ""
    masked = phone[:5] + "***" + phone[-2:] if len(phone) >= 7 else phone

    start_date = datetime.now().strftime("%d-%m-%Y")
    end_date = datetime.now().strftime("%d-%m-%Y")

    await db.save_random_history(
        winner_user_id=winner["user_id"],
        winner_name=winner_name,
        rid=winner["rid"] or "-",
        phone=phone,
        points=winner["diamonds"] or 0,
        start_date=start_date,
        end_date=end_date,
    )

    await message.answer(
        f"🏆 <b>Haftalik random g‘olibi aniqlandi!</b>\n\n"
        f"👤 Ism: {winner_name}\n"
        f"🆔 {winner['rid'] or '-'}\n"
        f"📱 {masked}\n"
        f"💎 Ball: {winner['diamonds'] or 0}\n\n"
        f"✅ Endi g‘olib bilan bog‘lanishingiz mumkin."
    )
