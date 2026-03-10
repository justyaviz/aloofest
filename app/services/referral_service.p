from aiogram import Bot


def generate_ref_link(bot_username, user_id):

    return f"https://t.me/{bot_username}?start={user_id}"
