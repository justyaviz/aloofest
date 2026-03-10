import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",")]

CHANNELS = os.getenv("CHANNELS", "").split(",")

PORT = int(os.getenv("PORT", 8080))
