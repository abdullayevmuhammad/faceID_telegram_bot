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

from datetime import datetime



async def update_face_photo_all(passport: str, photo_path: str) -> dict:
    """
    Mavjud foydalanuvchini barcha qurilmalarda rasm bilan yangilash:
    1. Avval uid orqali o'chirish
    2. Keyin yangi user sifatida qo'shish (rassm bilan)
    """
    passport_clean = passport.strip().upper()
    results = []

    for host in FACEID_HOSTS:
        session = await login_and_get_session(host)
        sessionid = random.randint(10000000, 99999999)
        try:
            # 1️⃣ Qurilmadan uid olish
            user_data = await get_user_data_from_device(host, passport_clean)
            uid = user_data.get("uid") if user_data else None

            # Agar uid topilsa, o'chirish
            if uid:
                url_delete = f"{host}/webs/setWhitelist"
                headers = {"Authorization": AUTH_HEADER_VALUE, "Content-Type": "application/x-www-form-urlencoded"}
                params_delete = {
                    "action": "del",
                    "group": "LIST",
                    "LIST.uid": uid,
                    "nRanId": random.randint(10000000, 99999999)
                }
                async with session.post(url_delete, params=params_delete, headers=headers, timeout=20) as resp_del:
                    text_del = await resp_del.text()
                    ok_del = "root.ERR.des=ok" in text_del
                    if not ok_del:
                        results.append({"host": host, "status": "delete_failed", "resp": text_del[:150]})
                        continue  # Agar delete bo'lmasa, keyingi qadamga o‘tmaymiz

            # 2️⃣ Rasmni yuklash
            dwfile_data = await upload_file_safe(host, session, sessionid, photo_path)
            if not dwfile_data:
                results.append({"host": host, "status": "upload_failed"})
                continue

            # 3️⃣ Yangi user sifatida qo'shish
            url_add = f"{host}/webs/setWhitelist"
            params_add = {
                "action": "add",
                "group": "LIST",
                "LIST.uid": -1,
                "LIST.dwfilepos": dwfile_data["dwfilepos"],
                "LIST.dwfileindex": dwfile_data["dwfileindex"],
                "LIST.dwfiletype": dwfile_data["dwfiletype"],
                "LIST.protocol": 1,
                "LIST.uname": passport_clean,
                "LIST.utype": 3,
                "LIST.uStatus": 4,
                "nRanId": random.randint(10000000, 99999999)
            }
            async with session.post(url_add, params=params_add, headers=headers, timeout=20) as resp_add:
                text_add = await resp_add.text()
                ok_add = "root.ERR.des=ok" in text_add
                results.append({"host": host, "status": "success" if ok_add else "add_failed", "resp": text_add[:150]})

        except Exception as e:
            results.append({"host": host, "status": "exception", "error": str(e)})
        finally:
            await session.close()

    ok_hosts = [r["host"] for r in results if r["status"] == "success"]
    return {
        "status": "success" if ok_hosts else "error",
        "msg": f"{len(ok_hosts)}/{len(FACEID_HOSTS)} qurilmaga muvaffaqiyatli yangilandi",
        "details": results
    }




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


async def sync_user_to_all_devices(passport: str, found_devices: list) -> dict:
    """Mavjud foydalanuvchi ma'lumotlarini barcha qurilmalarga ko'chirish"""
    passport_clean = passport.strip().upper()
    results = []

    # Topilgan qurilmalardan birining ma'lumotlarini olamiz
    if not found_devices:
        return {"status": "error", "msg": "No source devices found"}

    source_device = found_devices[0]  # Birinchi topilgan qurilma ma'lumotlaridan foydalanamiz
    source_host = source_device["host"]

    # Manba qurilmadan foydalanuvchi ma'lumotlarini olamiz
    source_user_data = await get_user_data_from_device(source_host, passport_clean)
    if not source_user_data:
        return {"status": "error", "msg": "Could not get user data from source device"}

    # Barcha qurilmalarga ko'chiramiz
    for host in FACEID_HOSTS:
        # Agar bu qurilma allaqachon ma'lumotga ega bo'lsa, o'tkazib yuboramiz
        if any(device["host"] == host for device in found_devices):
            results.append({"host": host, "status": "already_exists", "action": "skip"})
            continue

        session = await login_and_get_session(host)
        try:
            # Foydalanuvchini qo'shamiz
            url_add = f"{host}/webs/setWhitelist"
            headers = {"Authorization": AUTH_HEADER_VALUE, "Content-Type": "application/x-www-form-urlencoded"}
            params = {
                "action": "add",
                "group": "LIST",
                "LIST.uid": -1,
                "LIST.dwfilepos": source_user_data["dwfilepos"],
                "LIST.dwfileindex": source_user_data["dwfileindex"],
                "LIST.dwfiletype": source_user_data["dwfiletype"],
                "LIST.protocol": 1,
                "LIST.uname": passport_clean,
                "LIST.utype": 3,
                "LIST.uStatus": 4,
                "nRanId": random.randint(10000000, 99999999)
            }

            async with session.post(url_add, params=params, headers=headers, timeout=20) as resp:
                text = await resp.text()
                ok = "root.ERR.des=ok" in text
                results.append({
                    "host": host,
                    "status": "success" if ok else "add_failed",
                    "action": "copy"
                })

        except Exception as e:
            results.append({"host": host, "status": "exception", "error": str(e), "action": "copy"})
        finally:
            await session.close()

    success_count = len([r for r in results if r["status"] == "success"])
    return {
        "status": "success" if success_count > 0 else "error",
        "success_count": success_count,
        "total_devices": len(FACEID_HOSTS),
        "details": results
    }


async def get_user_data_from_device(host: str, passport: str) -> dict:
    """Qurilmadan foydalanuvchi ma'lumotlarini olish"""
    try:
        url = f"{host}/webs/getWhitelist"
        headers = {"Authorization": AUTH_HEADER_VALUE}
        params = {
            "action": "list",
            "group": "LIST",
            "Searchname": passport,
            "sequence": 1,
            "beginno": 0,
            "reqcount": 10,
            "sessionid": 0,
            "RanId": random.randint(10000000, 99999999)
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=10) as resp:
                text = await resp.text()

                # Foydalanuvchi ma'lumotlarini pars qilish
                uids = re.findall(r"root\.LIST\.ITEM\d+\.uid=(\d+)", text)
                unames = re.findall(r"root\.LIST\.ITEM\d+\.uname=([^\r\n]*)", text)
                filepos_list = re.findall(r"root\.LIST\.ITEM\d+\.dwfilepos=(\d+)", text)
                fileindex_list = re.findall(r"root\.LIST\.ITEM\d+\.dwfileindex=(\d+)", text)
                filetype_list = re.findall(r"root\.LIST\.ITEM\d+\.dwfiletype=(\d+)", text)

                for i, uname in enumerate(unames):
                    if uname.strip().upper() == passport:
                        return {
                            "uid": uids[i] if i < len(uids) else None,
                            "dwfilepos": filepos_list[i] if i < len(filepos_list) else "0",
                            "dwfileindex": fileindex_list[i] if i < len(fileindex_list) else "0",
                            "dwfiletype": filetype_list[i] if i < len(filetype_list) else "0"
                        }
    except Exception as e:
        print(f"[{host}] ❌ Foydalanuvchi ma'lumotlarini olishda xato: {e}")

    return None
async def download_facefile_from_device(host: str, dwfilepos: str, dwfileindex: str, dwfiletype: str) -> bytes | None:
    """
    Source device'dan rasmni oladi va bytes qaytaradi
    """
    try:
        import random
        url = f"{host}/webs/getImage"
        params = {
            "action": "list",
            "group": "IMAGE",
            "dwfiletype": dwfiletype,
            "dwfileindex": dwfileindex,
            "dwfilepos": dwfilepos,
            "RanId": random.randint(10000000, 99999999)
        }
        headers = {"Authorization": AUTH_HEADER_VALUE}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=20) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception as e:
        print(f"[{host}] download_facefile error: {e}")
    return None


async def copy_user_to_missing_devices(passport: str) -> dict:
    """
    Mavjud foydalanuvchi profilini barcha qurilmalarga nusxalash (rassm bilan birga)
    """
    passport = passport.strip().upper()
    found = await find_user_in_all_devices(passport)
    if found["status"] != "found":
        return {"status": "error", "msg": "user_not_found_on_any_device", "details": []}

    existing_hosts = [d["host"] for d in found["devices"]]
    missing_hosts = [h for h in FACEID_HOSTS if h not in existing_hosts]

    if not missing_hosts:
        return {"status": "ok", "msg": "All devices already have user", "details": []}

    # Source device sifatida birinchi topilgan device
    source_device = found["devices"][0]
    source_host = source_device["host"]

    # Source device'dan foydalanuvchi metadata ni olish
    fileinfo = await get_user_data_from_device(source_host, passport)

    if not fileinfo:
        return {"status": "error", "msg": "Could not get user data from source device", "details": []}

    # Rasmni olish
    file_bytes = None
    if fileinfo and fileinfo.get("dwfilepos"):
        file_bytes = await download_facefile_from_device(
            source_host,
            fileinfo["dwfilepos"],
            fileinfo.get("dwfileindex", "0"),
            fileinfo.get("dwfiletype", "0")
        )

    results = []
    for host in missing_hosts:
        session = await login_and_get_session(host)
        sessionid = random.randint(10000000, 99999999)
        try:
            if file_bytes:
                # Vaqtinchalik fayl yaratib upload
                import tempfile, os
                tmpf = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                try:
                    tmpf.write(file_bytes)
                    tmpf.flush()
                    tmp_path = tmpf.name
                finally:
                    tmpf.close()

                # Rasmni yangi qurilmaga yuklash
                dw = await upload_file_safe(host, session, sessionid, tmp_path)
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

                if not dw:
                    results.append({"host": host, "status": "upload_failed"})
                    await session.close()
                    continue

                # Add user bilan rasm metadata
                url_add = f"{host}/webs/setWhitelist"
                headers = {"Authorization": AUTH_HEADER_VALUE, "Content-Type": "application/x-www-form-urlencoded"}
                params = {
                    "action": "add",
                    "group": "LIST",
                    "LIST.uid": -1,
                    "LIST.dwfilepos": dw["dwfilepos"],
                    "LIST.dwfileindex": dw["dwfileindex"],
                    "LIST.dwfiletype": dw["dwfiletype"],
                    "LIST.protocol": 1,
                    "LIST.uname": passport,
                    "LIST.utype": 3,
                    "LIST.uStatus": 4,
                    "nRanId": random.randint(10000000, 99999999)
                }
                async with session.post(url_add, params=params, headers=headers, timeout=20) as resp:
                    text = await resp.text()
                    ok = "root.ERR.des=ok" in text
                    results.append({"host": host, "status": "success" if ok else "add_failed"})
            else:
                # Rasm yo'q fallback: minimal add (rassmsiz)
                url_add = f"{host}/webs/setWhitelist"
                headers = {"Authorization": AUTH_HEADER_VALUE, "Content-Type": "application/x-www-form-urlencoded"}
                params = {
                    "action": "add",
                    "group": "LIST",
                    "LIST.uid": -1,
                    "LIST.uname": passport,
                    "LIST.utype": 3,
                    "LIST.uStatus": 4,
                    "nRanId": random.randint(10000000, 99999999)
                }
                async with session.post(url_add, params=params, headers=headers, timeout=20) as resp:
                    text = await resp.text()
                    ok = "root.ERR.des=ok" in text
                    results.append({"host": host, "status": "success" if ok else "add_failed_nofile"})

        except Exception as e:
            results.append({"host": host, "status": "exception", "error": str(e)})
        finally:
            await session.close()

    ok_hosts = [r["host"] for r in results if r["status"] == "success"]
    return {
        "status": "success" if ok_hosts else "error",
        "msg": f"{len(ok_hosts)}/{len(missing_hosts)} qurilmaga nusxalandi",
        "details": results
    }

import aiohttp
import asyncio
from datetime import datetime
from typing import List

FACEID_HOSTS = [
    "http://172.16.110.14",
    "http://172.16.110.15",
    "http://172.16.110.18",
    "http://172.16.110.19",
    "http://172.16.110.20",
    "http://172.16.110.21",
    "http://172.16.110.23",
    "http://172.16.110.24"
]

AUTH_HEADER = {"Authorization": "Basic YWRtaW46YWlmdTFxMnczZTRyQA=="}  # seni Postmandan olgan headering

async def get_device_stats(session: aiohttp.ClientSession, host: str):
    """Bitta qurilmadan statistikani olish"""
    try:
        url = f"{host}/webs/getWhitelist?action=list&group=LIST&nRanId=123456"
        async with session.get(url, headers=AUTH_HEADER, timeout=5) as resp:
            text = await resp.text()

            # Ma’lumotni parse qilamiz (HTML-style javob)
            users = []
            for line in text.splitlines():
                if "LIST[" in line and ".uid=" in line:
                    users.append(line.strip())

            total = len(users)

            # bugungi sana bo‘yicha hisob
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = sum(today in line for line in text.splitlines())

            return {"host": host, "total": total, "today": today_count, "status": "ok"}

    except Exception as e:
        return {"host": host, "total": 0, "today": 0, "status": "error", "error": str(e)}


async def get_users_stats():
    """Barcha qurilmalardan foydalanuvchilar statistikasi"""
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(get_device_stats(session, h) for h in FACEID_HOSTS))

    total_all = sum(r["total"] for r in results)
    today_all = sum(r["today"] for r in results)

    return {
        "status": "ok",
        "devices": results,
        "summary": {
            "total_all": total_all,
            "today_all": today_all
        }
    }
