from aiogram import Bot


def generate_ref_link(username, user_id):
    return f"https://t.me/{username}?start={user_id}"
