import openpyxl
import aiosqlite
from app.database.db import DB


async def export_users():

    wb = openpyxl.Workbook()
    ws = wb.active

    ws.append(["Name","FestID","Points","Referrals"])

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute("""
        SELECT name,fest_id,points,referrals_count FROM users
        """)

        rows = await cur.fetchall()

        for r in rows:
            ws.append(r)

    file = "users.xlsx"

    wb.save(file)

    return file
