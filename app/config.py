import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS","").split(",") if x]

CHANNEL = "@aloo_uzb"

BOT_USERNAME = "aloofest_bot"
