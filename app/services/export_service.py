import aiosqlite
import openpyxl
from app.database.db import DB


async def export_users():

    wb = openpyxl.Workbook()
    ws = wb.active

    ws.append(["Name","FestID","Points","Referrals"])

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute("""
        SELECT name, fest_id, points, referrals_count
        FROM users
        """)

        rows = await cursor.fetchall()

        for r in rows:
            ws.append(r)

    path = "exports/users.xlsx"

    wb.save(path)

    return path
