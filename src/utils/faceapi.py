import aiohttp
import asyncio
import random
import re
from io import BytesIO

FACEGATE_HOST = "http://172.16.110.15"
AUTH_HEADER_VALUE = "Basic YWRtaW46YWlmdTFxMnczZTRyQA=="
from datetime import datetime

async def get_users_stats():
    """
    FaceGate qurilmasidan foydalanuvchilar statistikasi olish:
    - jami foydalanuvchilar
    - bugun qo‘shilganlar
    - duplicate foydalanuvchilar
    """
    url = f"{FACEGATE_HOST}/webs/getWhitelist"
    headers = {"Authorization": AUTH_HEADER_VALUE}
    params = {
        "action": "list",
        "group": "LIST",
        "uflag": 0,
        "usex": 1,
        "uage": "0-100",
        "MjCardNo": 0,
        "begintime": "2023-01-01/00:00:00",
        "endtime": "2030-01-01/23:59:59",
        "utype": 3,
        "sequence": 0,
        "beginno": 0,
        "reqcount": 200,  # yetarlicha ko‘p foydalanuvchi
        "sessionid": 0,
        "RanId": random.randint(10000000, 99999999),
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            text = await resp.text()
            print("📊 getWhitelist RESPONSE:\n", text[:500])  # faqat boshi

            # Jami foydalanuvchilar
            total = re.search(r"root\.LIST\.totalcount=(\d+)", text)
            total_count = int(total.group(1)) if total else 0

            # Har bir foydalanuvchi
            names = re.findall(r"root\.LIST\.ITEM\d+\.uname=([^\n\r]*)", text)
            times = re.findall(r"root\.LIST\.ITEM\d+\.utime=([\d\-/:\s]*)", text)

            # Bugungi sana
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = sum(1 for t in times if today in t)

            # Duplicate foydalanuvchilar
            duplicates = len(names) - len(set(names))

            return {
                "status": "ok",
                "total": total_count,
                "today": today_count,
                "duplicates": duplicates,
            }


async def login_and_get_session() -> aiohttp.ClientSession:
    """Login qilib session qaytaradi"""
    login_url = f"{FACEGATE_HOST}/webs/login"
    headers = {"Authorization": AUTH_HEADER_VALUE}

    session = aiohttp.ClientSession()
    async with session.get(login_url, headers=headers) as resp:
        text = await resp.text()
        print("🔑 Login response:", text.strip())
        if "root.ERR.des=ok" not in text:
            print("❌ Login muvaffaqiyatsiz!")
    return session


async def upload_file(session: aiohttp.ClientSession, sessionid: int, photo_path: str) -> bool:
    """Rasmni yuborish"""
    url = f"{FACEGATE_HOST}/webs/uploadfile"

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = BytesIO()
    with open(photo_path, "rb") as f:
        data = f.read()

    # multipart/form-data
    body.write(f"--{boundary}\r\n".encode())
    body.write(f'Content-Disposition: form-data; name="file"; filename="{photo_path.split("/")[-1]}"\r\n'.encode())
    body.write(b"Content-Type: image/jpeg\r\n\r\n")
    body.write(data)
    body.write(f"\r\n--{boundary}--\r\n".encode())

    headers = {
        "Authorization": AUTH_HEADER_VALUE,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    params = {
        "action": "LISTADD",
        "group": "UPLOAD",
        "sessionid": sessionid,
        "IsCheckSim": 0,
    }

    async with session.post(url, params=params, data=body.getvalue(), headers=headers) as resp:
        text = await resp.text()
        print("📤 Upload STATUS:", resp.status)
        print("📤 Upload RESPONSE:", text.strip())
        return resp.status == 200


async def get_upload_position(session: aiohttp.ClientSession, sessionid: int):
    """Upload foizini tekshirish va dwfilepos olish"""
    url = f"{FACEGATE_HOST}/webs/getUploadPercent"
    headers = {"Authorization": AUTH_HEADER_VALUE}

    for i in range(15):
        params = {
            "action": "list",
            "group": "UPLOAD",
            "sessionid": sessionid,
            "nRanId": random.randint(10000000, 99999999),
        }

        async with session.get(url, headers=headers, params=params) as resp:
            text = await resp.text()
            print(f"🔁 getUploadPercent [{i+1}]:", text.strip())

            m_state = re.search(r"root\.UPLOAD\.state[=:\"]?(\d+)", text)
            m_pos = re.search(r"root\.UPLOAD\.dwfilepos[=:\"]?(\d+)", text)
            m_idx = re.search(r"root\.UPLOAD\.dwfileindex[=:\"]?(\d+)", text)
            m_type = re.search(r"root\.UPLOAD\.dwfiletype[=:\"]?(\d+)", text)

            state = int(m_state.group(1)) if m_state else 0
            dwfilepos = m_pos.group(1) if m_pos else None
            dwfileindex = m_idx.group(1) if m_idx else "0"
            dwfiletype = m_type.group(1) if m_type else "0"

            if state >= 100 and dwfilepos and int(dwfilepos) > 0:
                print(f"✅ Upload tugadi. dwfilepos={dwfilepos}")
                await asyncio.sleep(0.3)
                return dwfilepos, dwfileindex, dwfiletype

        await asyncio.sleep(1)

    print("❌ Upload position topilmadi.")
    return None, None, None


async def add_user(session: aiohttp.ClientSession, passport: str, dwfilepos: str, dwfileindex: str, dwfiletype: str):
    """FaceID qurilmaga yangi foydalanuvchi qo‘shish"""
    url = f"{FACEGATE_HOST}/webs/setWhitelist"
    headers = {
        "Authorization": AUTH_HEADER_VALUE,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    clean_name = passport.strip().replace(" ", "_")
    params = {
        "action": "add",
        "group": "LIST",
        "LIST.uid": -1,
        "LIST.dwfiletype": int(dwfiletype),
        "LIST.dwfileindex": int(dwfileindex),
        "LIST.dwfilepos": dwfilepos,
        "LIST.protocol": 1,
        "LIST.publicMjCardNo": random.randint(1000, 9999),
        "LIST.MjCardNo": random.randint(1000, 9999),
        "LIST.uname": clean_name,
        "LIST.ubirth": "2024-01-25",
        "LIST.uvalidbegintime": "2025-01-25 00:00:00",
        "LIST.uvalidendtime": "2030-01-30 23:59:59",
        "LIST.uIsCheckSim": 1,
        "LIST.uPermission": 0,
        "LIST.ucardtype": 0,
        "LIST.ulisttype": 3,
        "LIST.utype": 3,
        "LIST.uStatus": 4,
        "nRanId": random.randint(10000000, 99999999),
    }

    async with session.post(url, params=params, headers=headers) as resp:
        text = await resp.text()
        print("✅ AddUser RESPONSE:", text.strip())
        return text


async def send_to_faceid(passport: str, photo_path: str):
    """To‘liq FaceID jarayoni: login → upload → getpos → add"""
    session = await login_and_get_session()
    sessionid = random.randint(10000000, 99999999)
    print(f"🚀 SessionID: {sessionid}")

    ok = await upload_file(session, sessionid, photo_path)
    if not ok:
        await session.close()
        return {"status": "error", "msg": "upload_failed"}

    dwfilepos, dwfileindex, dwfiletype = await get_upload_position(session, sessionid)
    if not dwfilepos:
        await session.close()
        return {"status": "error", "msg": "no_dwfilepos"}

    add_resp = await add_user(session, passport, dwfilepos, dwfileindex, dwfiletype)
    await session.close()

    if "root.ERR.des=ok" in add_resp:
        return {"status": "success", "msg": "user_added", "dwfilepos": dwfilepos}
    else:
        return {"status": "error", "msg": "add_failed", "resp": add_resp}


if __name__ == "__main__":
    passport = "Dilnora_Xolmurodov"
    photo_path = "tmp_photos/Dilnora_Xolmurodov.jpg"
    result = asyncio.run(send_to_faceid(passport, photo_path))
    print("\n🧾 NATIJA:", result)
