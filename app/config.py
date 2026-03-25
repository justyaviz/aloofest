import os


def _parse_admin_ids(value: str) -> list[int]:
    result = []
    for item in value.split(","):
        item = item.strip()
        if item.isdigit():
            result.append(int(item))
    return result


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
BOT_USERNAME = os.getenv("BOT_USERNAME", "").replace("@", "").strip()
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "aloo_uzb").replace("@", "").strip()

ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))

DB_PATH = os.getenv("DB_PATH", "bot.db").strip()

REGISTRATION_BONUS = int(os.getenv("REGISTRATION_BONUS", "5"))
REFERRAL_BONUS = int(os.getenv("REFERRAL_BONUS", "5"))
PROMO_BONUS = int(os.getenv("PROMO_BONUS", "15"))

REFERRAL_IMAGE_FILE_ID = os.getenv("REFERRAL_IMAGE_FILE_ID", "").strip()

BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
WEBAPP_SECRET = os.getenv("WEBAPP_SECRET", "super-secret-key").strip()
BOT_URL = f"https://t.me/{BOT_USERNAME}" if BOT_USERNAME else ""

PORT = int(os.getenv("PORT", "8080"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

if not BOT_USERNAME:
    raise RuntimeError("BOT_USERNAME topilmadi")

if not BASE_URL:
    raise RuntimeError("BASE_URL topilmadi")
