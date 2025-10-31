# src/bot/handlers/profile.py
import asyncio
from io import BytesIO
from aiogram import Router
from aiogram.types import Message, InputFile
from utils.db import get_user_by_id
from utils.faceapi import (
    find_user_in_all_devices,
    get_user_data_from_device,
    download_facefile_from_device
)
from bot.keyboards.admin_keyboards import admin_main_keyboard

from bot.keyboards.main_menu import get_main_menu

router = Router()


@router.message(lambda msg: msg.text in ["👤 Profilim", "/profile"])
async def profile_cmd(message: Message):
    """Foydalanuvchi profilini ko‘rsatadi"""
    user = get_user_by_id(message.from_user.id)

    if not user:
        return await message.answer(
            "⚠️ Siz hali ro‘yxatdan o‘tmagansiz.\n"
            "Iltimos, /register orqali ro‘yxatdan o‘ting."
        )

    passport = user.get("passport")
    full_name = user.get("full_name", message.from_user.full_name)

    await message.answer("🔍 Ma'lumotlaringiz FaceID tizimida tekshirilmoqda...")

    # 🔍 Foydalanuvchini barcha qurilmalarda izlaymiz
    result = await find_user_in_all_devices(passport)
    if result["status"] != "found" or not result["devices"]:
        return await message.answer(
            f"⚠️ <b>{passport}</b> tizimda topilmadi.\n"
            "Ehtimol, ma'lumotlaringiz o‘chirilgan.\n"
            "Iltimos, /register orqali qayta ro‘yxatdan o‘ting.",
            parse_mode="HTML"
        )

    devices = [d["host"] for d in result["devices"]]
    text = (
        f"👤 <b>{full_name}</b>\n"
        f"🪪 Pasport: <code>{passport}</code>\n"
        # f"🌐 Topilgan qurilmalar soni: <b>{len(devices)}</b>\n"
        # + "\n".join([f"✅ {d}" for d in devices])
    )

    # 🖼️ Suratni olish uchun birinchi topilgan qurilmadan foydalanamiz
    source_host = result["devices"][0]["host"]
    user_data = await get_user_data_from_device(source_host, passport)

    photo_bytes = None
    if user_data and user_data.get("dwfilepos"):
        photo_bytes = await download_facefile_from_device(
            source_host,
            user_data["dwfilepos"],
            user_data["dwfileindex"],
            user_data["dwfiletype"],
        )

    print(f"[DEBUG] photo_bytes type={type(photo_bytes)}, size={len(photo_bytes) if photo_bytes else 0}")

    if photo_bytes:
        try:
            from aiogram.types import BufferedInputFile
            photo = BufferedInputFile(photo_bytes, filename="profile.jpg")
            await message.answer_photo(photo=photo, caption=text, parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))
        except Exception as e:
            print(f"[ERROR] Photo send failed: {e}")
            await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))
