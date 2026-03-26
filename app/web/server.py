import html
import json
import hmac
import hashlib
import traceback
from aiohttp import web

from app.config import PORT, BOT_URL, WEBAPP_SECRET
from app.database.db import db
from app.database.models import DISTRICTS
from app.keyboards.user import after_registration_keyboard


def sign_uid(uid: int) -> str:
    return hmac.new(
        WEBAPP_SECRET.encode(),
        str(uid).encode(),
        hashlib.sha256
    ).hexdigest()


def verify_uid(uid: int, sig: str) -> bool:
    return sign_uid(uid) == sig


REGIONS = list(DISTRICTS.keys())


def build_html(user_id: int, sig: str) -> str:
    options = "".join(
        f'<option value="{html.escape(region)}">{html.escape(region)}</option>'
        for region in REGIONS
    )
    districts_json = json.dumps(DISTRICTS, ensure_ascii=False)
    back_url = BOT_URL or "#"

    return f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ALOOFEST 2-MAVSUM ro‘yxatdan o‘tish</title>
<style>
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  min-height: 100vh;
  font-family: Arial, sans-serif;
  background:
    radial-gradient(circle at top right, rgba(34,197,94,.22), transparent 25%),
    radial-gradient(circle at bottom left, rgba(59,130,246,.22), transparent 25%),
    linear-gradient(135deg, #0b1220 0%, #111827 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}}
.wrapper {{ width: 100%; max-width: 580px; }}
.card {{
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.10);
  backdrop-filter: blur(12px);
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 20px 60px rgba(0,0,0,.35);
}}
.badge {{
  display: inline-block;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(34,197,94,.15);
  border: 1px solid rgba(34,197,94,.35);
  color: #dcfce7;
  font-size: 13px;
  margin-bottom: 14px;
}}
h1 {{ margin: 0 0 8px; font-size: 28px; }}
p.subtitle {{ margin: 0 0 20px; color: #cbd5e1; line-height: 1.6; }}
label {{
  display: block;
  margin-top: 14px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #e2e8f0;
  font-weight: 600;
}}
input, select {{
  width: 100%;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.08);
  color: white;
  font-size: 15px;
  outline: none;
}}
input::placeholder {{ color: #94a3b8; }}
option {{ color: black; }}
button {{
  width: 100%;
  margin-top: 22px;
  padding: 15px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(90deg, #22c55e, #16a34a);
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}}
#msg {{
  margin-top: 16px;
  padding: 14px;
  border-radius: 14px;
  display: none;
  font-size: 14px;
  line-height: 1.5;
}}
.success {{
  display: block !important;
  background: rgba(34,197,94,.15);
  border: 1px solid rgba(34,197,94,.35);
  color: #dcfce7;
}}
.error {{
  display: block !important;
  background: rgba(239,68,68,.15);
  border: 1px solid rgba(239,68,68,.35);
  color: #fee2e2;
}}
.check-wrap {{
  margin-top: 18px;
  padding: 14px;
  border-radius: 14px;
  background: rgba(255,255,255,.05);
  border: 1px solid rgba(255,255,255,.08);
}}
.promo-box {{ display: none; }}
.back-wrap {{ display: none; margin-top: 14px; }}
.back-btn {{
  display: block;
  width: 100%;
  text-align: center;
  padding: 14px;
  border-radius: 14px;
  text-decoration: none;
  background: rgba(255,255,255,.08);
  color: white;
  border: 1px solid rgba(255,255,255,.12);
}}
</style>
</head>
<body>
<div class="wrapper">
  <div class="card">
    <div class="badge">🎉 ALOOFEST 2-MAVSUM</div>
    <h1>Ro‘yxatdan o‘tish</h1>
    <p class="subtitle">
      Ma’lumotlaringizni to‘ldiring va o‘yin ishtirokchisiga aylaning.
      Agar sizda promokod bo‘lsa, uni kiritsangiz <b>+15 ball</b> olasiz.
    </p>

    <form id="regForm">
      <label>Ism va familiya</label>
      <input id="full_name" placeholder="Masalan: Ali Valiyev" required>

      <label>Viloyatingizni tanlang</label>
      <select id="region" required>
        <option value="">Tanlang</option>
        {options}
      </select>

      <label>Tuman / shaharni tanlang</label>
      <select id="district" required>
        <option value="">Avval viloyat tanlang</option>
      </select>

      <div class="check-wrap">
        <label style="margin:0; display:flex; gap:10px; align-items:center;">
          <input type="checkbox" id="hasPromo" style="width:auto;">
          <span>Promokod bormi?</span>
        </label>
      </div>

      <div class="promo-box" id="promoBox">
        <label>Promokod yozing</label>
        <input id="promo_code" maxlength="4" placeholder="4 xonali kod">
      </div>

      <button type="submit">RO‘YXATDAN O‘TISH</button>
    </form>

    <div id="msg"></div>

    <div class="back-wrap" id="backWrap">
      <a class="back-btn" href="{back_url}">⬅️ ORQAGA QAYTISH</a>
    </div>
  </div>
</div>

<script>
const districts = {districts_json};
const uid = {user_id};
const sig = "{sig}";

const regionEl = document.getElementById("region");
const districtEl = document.getElementById("district");
const msgBox = document.getElementById("msg");
const backWrap = document.getElementById("backWrap");
const hasPromo = document.getElementById("hasPromo");
const promoBox = document.getElementById("promoBox");

regionEl.addEventListener("change", () => {{
  districtEl.innerHTML = '<option value="">Tanlang</option>';
  const arr = districts[regionEl.value] || [];
  arr.forEach(item => {{
    const opt = document.createElement("option");
    opt.value = item;
    opt.textContent = item;
    districtEl.appendChild(opt);
  }});
}});

hasPromo.addEventListener("change", () => {{
  promoBox.style.display = hasPromo.checked ? "block" : "none";
}});

document.getElementById("regForm").addEventListener("submit", async (e) => {{
  e.preventDefault();

  msgBox.className = "";
  msgBox.style.display = "none";
  backWrap.style.display = "none";

  const payload = {{
    uid: uid,
    sig: sig,
    full_name: document.getElementById("full_name").value.trim(),
    region: document.getElementById("region").value.trim(),
    district: document.getElementById("district").value.trim(),
    promo_code: hasPromo.checked ? document.getElementById("promo_code").value.trim() : ""
  }};

  try {{
    const res = await fetch("/api/register", {{
      method: "POST",
      headers: {{
        "Content-Type": "application/json"
      }},
      body: JSON.stringify(payload)
    }});

    const data = await res.json();

    if (data.ok) {{
      msgBox.classList.add("success");
      msgBox.innerText = data.message || "Muvaffaqiyatli ro‘yxatdan o‘tildi";
      document.getElementById("regForm").style.display = "none";
      backWrap.style.display = "block";
    }} else {{
      msgBox.classList.add("error");
      msgBox.innerText = data.error || "Xatolik yuz berdi";
    }}

    msgBox.style.display = "block";
  }} catch (err) {{
    msgBox.classList.add("error");
    msgBox.innerText = "Server bilan bog‘lanishda xatolik yuz berdi";
    msgBox.style.display = "block";
  }}
}});
</script>
</body>
</html>"""


async def register_page(request: web.Request):
    uid = request.query.get("uid", "").strip()
    sig = request.query.get("sig", "").strip()

    if not uid.isdigit() or not sig:
        return web.Response(text="Ruxsat yo‘q", status=403)

    if not verify_uid(int(uid), sig):
        return web.Response(text="Noto‘g‘ri imzo", status=403)

    return web.Response(text=build_html(int(uid), sig), content_type="text/html")


async def register_api(request: web.Request):
    try:
        bot = request.app["bot"]
        data = await request.json()

        uid = int(data.get("uid", 0))
        sig = data.get("sig", "").strip()
        full_name = str(data.get("full_name", "")).strip()
        region = str(data.get("region", "")).strip()
        district = str(data.get("district", "")).strip()
        promo_code = str(data.get("promo_code", "")).strip()

        if not verify_uid(uid, sig):
            return web.json_response({"ok": False, "error": "Ruxsat yo‘q"})

        if not full_name:
            return web.json_response({"ok": False, "error": "Ism-familiya kiritilishi shart"})

        if region not in DISTRICTS:
            return web.json_response({"ok": False, "error": "Viloyat noto‘g‘ri"})

        if district not in DISTRICTS[region]:
            return web.json_response({"ok": False, "error": "Tuman/shahar noto‘g‘ri"})

        if promo_code and (not promo_code.isdigit() or len(promo_code) != 4):
            return web.json_response({"ok": False, "error": "Promokod 4 xonali son bo‘lishi kerak"})

        ok, rid, promo_branch = await db.register_user(
            user_id=uid,
            full_name=full_name,
            region=region,
            district=district,
            promo_code=promo_code or None,
        )

        if not ok:
            return web.json_response({"ok": False, "error": rid})

        promo_text = ""
        web_text = ""
        if promo_branch:
            promo_text = (
                f"\n🎁 Promokod qabul qilindi va sizga <b>+15 ball</b> berildi."
                f"\n🏬 Filial: <b>{html.escape(promo_branch)}</b>"
            )
            web_text = " Promokod qabul qilindi va +15 ball berildi."

        await bot.send_message(
            chat_id=uid,
            text=(
                f"🎉 <b>Tabriklaymiz, {html.escape(full_name)}!</b>\n\n"
                f"Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz va <b>+5 ball</b> qo‘lga kiritdingiz."
                f"{promo_text}\n\n"
                f"💎 Agar ballaringizni ko‘paytirmoqchi bo‘lsangiz, eng yaqin <b>aloo</b> do‘koniga borib promokod olishingiz mumkin.\n\n"
                f"🆔 Sizning ID raqamingiz: <b>{rid}</b>"
            ),
            reply_markup=after_registration_keyboard().model_dump()
        )

        return web.json_response({
            "ok": True,
            "message": f"🎉 Tabriklaymiz! Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz. Sizning ID: {rid}.{web_text}"
        })

    except Exception as e:
        print("REGISTER_API_ERROR:", str(e))
        traceback.print_exc()
        return web.json_response({"ok": False, "error": f"Server xatoligi: {str(e)}"})


async def health(request: web.Request):
    return web.Response(text="OK")


async def setup_web_server(bot):
    app = web.Application()
    app["bot"] = bot

    app.router.add_get("/health", health)
    app.router.add_get("/register", register_page)
    app.router.add_post("/api/register", register_api)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    return runner
