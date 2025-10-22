import aiohttp
import asyncio
import random
import re
from io import BytesIO
from typing import List, Dict
import aiofiles

FACEID_HOSTS: List[str] = [
    "http://172.16.110.15",
    "http://172.16.110.18",
    "http://172.16.110.21",
    "http://172.16.110.23",
    "http://172.16.110.14",
    "http://172.16.110.19",
    "http://172.16.110.20",
    "http://172.16.110.24",
]

AUTH_HEADER_VALUE = "Basic YWRtaW46YWlmdTFxMnczZTRyQA=="


# =========================
# Session login
# =========================
async def login_and_get_session(host: str) -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()
    try:
        url = f"{host}/webs/login"
        headers = {"Authorization": AUTH_HEADER_VALUE}
        async with session.get(url, headers=headers, timeout=10) as resp:
            text = await resp.text()
            print(f"[{host}] 🔑 Login javob: {text.strip()[:150]}")
    except Exception as e:
        print(f"[{host}] ❌ Login xatosi: {e}")
    return session



# =========================
# Faylni upload qilish va dwfilepos olish
# =========================
async def upload_file_safe(host: str, session: aiohttp.ClientSession, sessionid: int, photo_path: str) -> Dict[str, str] | None:
    """Rasmni serverga upload qiladi va dwfilepos, dwfileindex, dwfiletype qaytaradi"""
    url = f"{host}/webs/uploadfile"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

    try:
        async with aiofiles.open(photo_path, "rb") as f:
            data = await f.read()
    except Exception as e:
        print(f"[{host}] ❌ Rasm o‘qilmadi: {e}")
        return None

    body = BytesIO()
    body.write(f"--{boundary}\r\n".encode())
    body.write(f'Content-Disposition: form-data; name="file"; filename="{photo_path.split("/")[-1]}"\r\n'.encode())
    body.write(b"Content-Type: image/jpeg\r\n\r\n")
    body.write(data)
    body.write(f"\r\n--{boundary}--\r\n".encode())

    headers = {"Authorization": AUTH_HEADER_VALUE,
               "Content-Type": f"multipart/form-data; boundary={boundary}"}
    params = {"action": "LISTADD", "group": "UPLOAD", "sessionid": sessionid}

    try:
        async with session.post(url, params=params, data=body.getvalue(), headers=headers, timeout=30) as resp:
            text = await resp.text()
            if resp.status != 200:
                print(f"[{host}] ❌ Upload failed, status={resp.status}")
                return None
    except Exception as e:
        print(f"[{host}] ❌ Upload error: {e}")
        return None

    # dwfilepos, dwfileindex, dwfiletype kutish
    for _ in range(20):
        try:
            url_check = f"{host}/webs/getUploadPercent"
            params_check = {"action": "list", "group": "UPLOAD", "sessionid": sessionid,
                            "nRanId": random.randint(10000000, 99999999)}
            async with session.get(url_check, headers={"Authorization": AUTH_HEADER_VALUE}, params=params_check, timeout=10) as resp:
                text = await resp.text()
                m_pos = re.search(r"root\.UPLOAD\.dwfilepos\s*=\s*(\d+)", text)
                m_index = re.search(r"root\.UPLOAD\.dwfileindex\s*=\s*(\d+)", text)
                m_type = re.search(r"root\.UPLOAD\.dwfiletype\s*=\s*(\d+)", text)
                m_state = re.search(r"root\.UPLOAD\.state\s*=\s*(\d+)", text)

                dwfilepos = m_pos.group(1) if m_pos else None
                dwfileindex = m_index.group(1) if m_index else None
                dwfiletype = m_type.group(1) if m_type else None
                state = int(m_state.group(1)) if m_state else 0

                if dwfilepos and dwfileindex and dwfiletype and state >= 100:
                    return {"dwfilepos": dwfilepos, "dwfileindex": dwfileindex, "dwfiletype": dwfiletype}
        except Exception:
            pass
        await asyncio.sleep(1)

    print(f"[{host}] ❌ dwfilepos topilmadi")
    return None

# =========================
# Foydalanuvchini barcha qurilmalarda qidirish
# =========================
async def find_user_in_all_devices(passport: str) -> Dict:
    passport = passport.strip().upper()
    found = []
    for host in FACEID_HOSTS:
        try:
            url = f"{host}/webs/getWhitelist"
            params = {"action": "list", "group": "LIST", "uflag": 0, "Searchname": passport,
                      "sequence": 1, "beginno": 0, "reqcount": 2, "sessionid": 0,
                      "RanId": random.randint(10000000, 99999999)}
            headers = {"Authorization": AUTH_HEADER_VALUE}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers, timeout=15) as resp:
                    text = await resp.text()

            uids = re.findall(r"root\.LIST\.ITEM\d+\.uid=(\d+)", text)
            unames = re.findall(r"root\.LIST\.ITEM\d+\.uname=([^\r\n]*)", text)

            for uid, uname in zip(uids, unames):
                if uname.strip().upper() == passport:
                    found.append({"host": host, "uid": uid})
                    break

            if not any(d["host"] == host for d in found) and f"uname={passport}" in text:
                found.append({"host": host, "uid": None})

        except Exception as e:
            print(f"[{host}] ⚠️ Qidiruv xatolik: {e}")

    return {"status": "found", "devices": found} if found else {"status": "not_found", "devices": []}



# =========================
# Yangi foydalanuvchini qo‘shish
# =========================

async def send_to_faceid(passport: str, photo_path: str) -> dict:
    passport_clean = passport.strip()
    results = []

    for host in FACEID_HOSTS:
        session = await login_and_get_session(host)
        sessionid = random.randint(10000000, 99999999)
        try:
            dwfile_data = await upload_file_safe(host, session, sessionid, photo_path)
            if not dwfile_data:
                results.append({"host": host, "status": "upload_failed"})
                await session.close()
                continue

            url_add = f"{host}/webs/setWhitelist"
            headers = {"Authorization": AUTH_HEADER_VALUE, "Content-Type": "application/x-www-form-urlencoded"}
            params = {"action": "add", "group": "LIST", "LIST.uid": -1,
                      "LIST.dwfilepos": dwfile_data["dwfilepos"],
                      "LIST.dwfileindex": dwfile_data["dwfileindex"],
                      "LIST.dwfiletype": dwfile_data["dwfiletype"],
                      "LIST.protocol": 1, "LIST.uname": passport_clean, "LIST.utype": 3, "LIST.uStatus": 4,
                      "nRanId": random.randint(10000000, 99999999)}

            async with session.post(url_add, params=params, headers=headers, timeout=20) as resp:
                text = await resp.text()
                ok = "root.ERR.des=ok" in text
                results.append({"host": host, "status": "success" if ok else "add_failed", "resp": text[:150]})
        except Exception as e:
            results.append({"host": host, "status": "exception", "error": str(e)})
        finally:
            await session.close()

    ok_hosts = [r["host"] for r in results if r["status"] == "success"]
    return {"status": "success" if ok_hosts else "error",
            "msg": f"{len(ok_hosts)}/{len(FACEID_HOSTS)} qurilmaga yuborildi",
            "details": results}


# =========================
# Mavjud foydalanuvchi rasmini yangilash
# =========================

async def update_face_photo_all(passport: str, photo_path: str) -> dict:
    found = await find_user_in_all_devices(passport)
    if found["status"] != "found":
        return {"status": "error", "msg": "user_not_found_on_any_device", "details": []}

    results = []
    for device in found["devices"]:
        host = device["host"]
        uid = device.get("uid")
        session = await login_and_get_session(host)
        sessionid = random.randint(10000000, 99999999)
        try:
            dwfile_data = await upload_file_safe(host, session, sessionid, photo_path)
            if not dwfile_data:
                results.append({"host": host, "status": "upload_failed"})
                await session.close()
                continue

            if not uid:
                url = f"{host}/webs/getWhitelist"
                headers = {"Authorization": AUTH_HEADER_VALUE}
                params = {"action": "list", "group": "LIST", "nPage": 1, "nPageSize": 1000}
                async with session.get(url, params=params, headers=headers, timeout=10) as resp:
                    text = await resp.text()
                uids = re.findall(r"root\.LIST\.ITEM\d+\.uid=(\d+)", text)
                unames = re.findall(r"root\.LIST\.ITEM\d+\.uname=([^\r\n]*)", text)
                for _uid, uname in zip(uids, unames):
                    if uname.strip().upper() == passport.upper():
                        uid = _uid
                        break

            if not uid:
                results.append({"host": host, "status": "uid_not_found"})
                await session.close()
                continue

            url_update = f"{host}/webs/setWhitelist"
            headers = {"Authorization": AUTH_HEADER_VALUE, "Content-Type": "application/x-www-form-urlencoded"}
            params = {"action": "update", "group": "LIST", "LIST.uid": uid, "LIST.uname": passport,
                      "LIST.dwfilepos": dwfile_data["dwfilepos"],
                      "LIST.dwfileindex": dwfile_data["dwfileindex"],
                      "LIST.dwfiletype": dwfile_data["dwfiletype"],
                      "LIST.uStatus": 4, "LIST.utype": 3,
                      "nRanId": random.randint(10000000, 99999999)}

            async with session.post(url_update, params=params, headers=headers, timeout=20) as resp:
                text = await resp.text()
                ok = "root.ERR.des=ok" in text
                results.append({"host": host, "status": "success" if ok else "update_failed", "resp": text[:150]})
        except Exception as e:
            results.append({"host": host, "status": "exception", "error": str(e)})
        finally:
            await session.close()

    ok_hosts = [r["host"] for r in results if r["status"] == "success"]
    return {"status": "success" if ok_hosts else "error",
            "msg": f"{len(ok_hosts)}/{len(found['devices'])} qurilmaga rasm yangilandi",
            "details": results}


from datetime import datetime
async def get_users_stats():
    total = 0
    today_count = 0
    names = []

    today = datetime.now().strftime("%Y-%m-%d")

    for host in FACEID_HOSTS:
        try:
            url = f"{host}/webs/getWhitelist"
            headers = {"Authorization": AUTH_HEADER_VALUE}
            params = {"action": "list", "group": "LIST", "nPage": 1, "nPageSize": 1000,
                      "nRanId": random.randint(10000000, 99999999)}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=15) as resp:
                    text = await resp.text()

            total_match = re.search(r"root\.LIST\.totalcount=(\d+)", text)
            count = int(total_match.group(1)) if total_match else 0
            total += count

            user_names = re.findall(r"root\.LIST\.ITEM\d+\.uname=([^\r\n]*)", text)
            user_times = re.findall(r"root\.LIST\.ITEM\d+\.utime=([^\r\n]*)", text)

            names.extend(user_names)
            today_count += sum(1 for t in user_times if today in t)

        except Exception as e:
            print(f"[{host}] ⚠️ Statistika olishda xato: {e}")

    duplicates = len(names) - len(set(names))

    return {"status": "ok", "total": total, "today": today_count, "duplicates": duplicates}