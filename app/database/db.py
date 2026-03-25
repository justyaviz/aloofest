from __future__ import annotations

import time
import aiosqlite

from app.config import DB_PATH, REGISTRATION_BONUS, REFERRAL_BONUS, PROMO_BONUS
from app.database.models import PROMO_CODES


class Database:
    async def init(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                tg_name TEXT,
                full_name TEXT,
                phone TEXT,
                region TEXT,
                district TEXT,
                rid TEXT UNIQUE,
                referrer_id INTEGER,
                promo_code TEXT,
                promo_branch TEXT,
                registered INTEGER DEFAULT 0,
                phone_verified INTEGER DEFAULT 0,
                banned INTEGER DEFAULT 0,
                diamonds INTEGER DEFAULT 0,
                referral_count INTEGER DEFAULT 0,
                created_at INTEGER,
                registered_at INTEGER
            )
            """)

            await db.execute("""
            CREATE TABLE IF NOT EXISTS random_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                winner_user_id INTEGER,
                winner_name TEXT,
                rid TEXT,
                phone TEXT,
                points INTEGER,
                start_date TEXT,
                end_date TEXT,
                created_at INTEGER,
                confirmed INTEGER DEFAULT 0
            )
            """)

            await db.commit()

    async def add_user(self, user_id: int, username: str | None, tg_name: str | None):
        now = int(time.time())
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            row = await cur.fetchone()
            if not row:
                await db.execute("""
                    INSERT INTO users (user_id, username, tg_name, created_at)
                    VALUES (?, ?, ?, ?)
                """, (user_id, username, tg_name, now))
            else:
                await db.execute("""
                    UPDATE users SET username = ?, tg_name = ?
                    WHERE user_id = ?
                """, (username, tg_name, user_id))
            await db.commit()

    async def get_user(self, user_id: int):
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return await cur.fetchone()

    async def get_user_by_rid(self, rid: str):
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM users WHERE rid = ?", (rid,))
            return await cur.fetchone()

    async def search_users(self, query: str, limit: int = 10):
        like = f"%{query}%"
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            if query.isdigit():
                cur = await db.execute("SELECT * FROM users WHERE user_id = ? LIMIT ?", (int(query), limit))
            else:
                cur = await db.execute("""
                    SELECT * FROM users
                    WHERE full_name LIKE ? OR rid LIKE ? OR username LIKE ?
                    LIMIT ?
                """, (like, like, like, limit))
            return await cur.fetchall()

    async def next_rid(self) -> str:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT COUNT(*) FROM users WHERE registered = 1")
            count = (await cur.fetchone())[0] + 1
            return f"R-{count}"

    async def set_referrer_if_empty(self, user_id: int, referrer_id: int):
        if user_id == referrer_id:
            return
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT referrer_id, registered FROM users WHERE user_id = ?", (user_id,))
            row = await cur.fetchone()
            if row and row[0] is None and row[1] == 0:
                await db.execute("UPDATE users SET referrer_id = ? WHERE user_id = ?", (referrer_id, user_id))
                await db.commit()

    async def register_user(self, user_id: int, full_name: str, region: str, district: str, promo_code: str | None = None):
        now = int(time.time())
        rid = await self.next_rid()

        promo_branch = None
        promo_bonus = 0
        if promo_code:
            promo_branch = PROMO_CODES.get(promo_code)
            if not promo_branch:
                return False, "Promokod noto‘g‘ri", None
            promo_bonus = PROMO_BONUS

        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = await cur.fetchone()
            if not user:
                return False, "Foydalanuvchi topilmadi", None

            first_registration = user["registered"] == 0

            await db.execute("""
                UPDATE users
                SET full_name = ?, region = ?, district = ?,
                    rid = COALESCE(rid, ?),
                    promo_code = COALESCE(promo_code, ?),
                    promo_branch = COALESCE(promo_branch, ?),
                    registered = 1,
                    registered_at = COALESCE(registered_at, ?)
                WHERE user_id = ?
            """, (full_name, region, district, rid, promo_code, promo_branch, now, user_id))

            if first_registration:
                total_bonus = REGISTRATION_BONUS + promo_bonus
                await db.execute("""
                    UPDATE users
                    SET diamonds = diamonds + ?
                    WHERE user_id = ?
                """, (total_bonus, user_id))

                if user["referrer_id"]:
                    await db.execute("""
                        UPDATE users
                        SET diamonds = diamonds + ?, referral_count = referral_count + 1
                        WHERE user_id = ?
                    """, (REFERRAL_BONUS, user["referrer_id"]))

            await db.commit()
            return True, rid, promo_branch

    async def save_phone(self, user_id: int, phone: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                UPDATE users
                SET phone = ?, phone_verified = 1
                WHERE user_id = ?
            """, (phone, user_id))
            await db.commit()

    async def add_points(self, user_id: int, points: int):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE users SET diamonds = diamonds + ? WHERE user_id = ?", (points, user_id))
            await db.commit()

    async def add_referrals(self, user_id: int, refs: int):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                UPDATE users
                SET referral_count = referral_count + ?, diamonds = diamonds + ?
                WHERE user_id = ?
            """, (refs, refs * REFERRAL_BONUS, user_id))
            await db.commit()

    async def set_ready_user(self, user_id: int, diamonds: int, refs: int):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                UPDATE users
                SET diamonds = ?, referral_count = ?, registered = 1
                WHERE user_id = ?
            """, (diamonds, refs, user_id))
            await db.commit()

    async def all_users(self):
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM users ORDER BY created_at ASC")
            return await cur.fetchall()

    async def get_recent_users(self, limit: int = 50):
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT ?", (limit,))
            return await cur.fetchall()

    async def get_stats(self):
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT COUNT(*) FROM users")
            total_users = (await cur.fetchone())[0]

            cur = await db.execute("SELECT COUNT(*) FROM users WHERE registered = 1")
            registered = (await cur.fetchone())[0]

            cur = await db.execute("SELECT COUNT(*) FROM users WHERE banned = 1")
            banned = (await cur.fetchone())[0]

            cur = await db.execute("SELECT COALESCE(SUM(diamonds),0) FROM users")
            diamonds = (await cur.fetchone())[0]

            cur = await db.execute("SELECT COUNT(*) FROM users WHERE diamonds >= 25 AND banned = 0 AND registered = 1")
            random_ready = (await cur.fetchone())[0]

            return {
                "total_users": total_users,
                "registered": registered,
                "banned": banned,
                "diamonds": diamonds,
                "random_ready": random_ready,
            }

    async def get_region_stats(self):
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("""
                SELECT region, COUNT(*) as total, COALESCE(SUM(diamonds),0) as diamonds
                FROM users
                WHERE registered = 1
                GROUP BY region
                ORDER BY total DESC
            """)
            return await cur.fetchall()

    async def get_promo_stats(self):
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("""
                SELECT promo_branch, promo_code, COUNT(*) as total
                FROM users
                WHERE promo_code IS NOT NULL AND promo_branch IS NOT NULL
                GROUP BY promo_branch, promo_code
                ORDER BY total DESC
            """)
            return await cur.fetchall()

    async def ban_user(self, user_id: int):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (user_id,))
            await db.commit()

    async def unban_user(self, user_id: int):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE users SET banned = 0 WHERE user_id = ?", (user_id,))
            await db.commit()

    async def get_random_candidates(self):
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("""
                SELECT * FROM users
                WHERE registered = 1 AND banned = 0 AND diamonds >= 25
            """)
            return await cur.fetchall()

    async def save_random_history(self, winner_user_id: int, winner_name: str, rid: str, phone: str, points: int, start_date: str, end_date: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO random_history (
                    winner_user_id, winner_name, rid, phone, points,
                    start_date, end_date, created_at, confirmed
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (winner_user_id, winner_name, rid, phone, points, start_date, end_date, int(time.time())))
            await db.commit()

    async def get_last_random(self):
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM random_history ORDER BY id DESC LIMIT 1")
            return await cur.fetchone()

    async def confirm_last_random(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                UPDATE random_history
                SET confirmed = 1
                WHERE id = (SELECT id FROM random_history ORDER BY id DESC LIMIT 1)
            """)
            await db.commit()


db = Database()
