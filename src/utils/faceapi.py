# src/utils/faceapi.py
import asyncio

import aiohttp
import os
from typing import Dict
from bot.config import FACEID_API_URL, FACEID_USERNAME, FACEID_PASSWORD


# async def send_to_faceid(passport: str, image_path: str) -> Dict:
#     """
#     Foydalanuvchi fotosini va passport ID sini FaceID qurilmaga yuboradi.
#     Qurilma FaceGate API asosida ishlaydi.
#     """
#
#     # Masalan: FACEID_API_URL = "http://172.16.110.15"
#     endpoint = f"{FACEID_API_URL.rstrip('/')}/face/addPerson"
#
#     # Form-data tayyorlash
#     form = aiohttp.FormData()
#     form.add_field("username", FACEID_USERNAME)
#     form.add_field("password", FACEID_PASSWORD)
#     form.add_field("personId", passport)
#     form.add_field("personName", passport)  # ismi o‘rniga passportdan foydalandik
#     form.add_field(
#         "photo",
#         open(image_path, "rb"),
#         filename=os.path.basename(image_path),
#         content_type="image/jpeg"
#     )
#
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.post(endpoint, data=form, timeout=20) as resp:
#                 text = await resp.text()
#
#                 # Ba’zi hollarda server JSON emas, oddiy HTML qaytaradi
#                 try:
#                     data = await resp.json()
#                 except Exception:
#                     data = {"status": "raw", "text": text}
#
#                 # 200 bo‘lsa — muvaffaqiyatli deb qabul qilamiz
#                 return {
#                     "status": "success" if resp.status == 200 else "error",
#                     "http_status": resp.status,
#                     "data": data,
#                 }
#
#     except aiohttp.ClientConnectorError:
#         return {"status": "error", "exception": "Serverga ulanib bo‘lmadi (IP noto‘g‘ri yoki offline)."}
#     except aiohttp.ServerTimeoutError:
#         return {"status": "error", "exception": "So‘rov vaqti tugadi (server javob bermadi)."}
#     except Exception as e:
#         return {"status": "error", "exception": str(e)}

async def send_to_faceid(passport: str, image_path: str) -> dict:
    print(f"[MOCK] Simulating FaceID upload: {passport} -> {image_path}")
    await asyncio.sleep(1)  # biroz kutish effekti uchun
    return {"status": "success", "message": "Simulated FaceID upload"}