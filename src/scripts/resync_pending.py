# src/scripts/resync_pending.py
import asyncio
from utils.storage_db import user_storage_db
from database.session import AsyncSessionLocal
from utils.faceapi import send_to_faceid
from database.models import User
from sqlalchemy import select

async def resync_all():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.faceid_status != "ok"))
        users = res.scalars().all()
        for u in users:
            try:
                resp = await send_to_faceid(u.passport, u.photo_path)
                if resp.get("status") in ("success","ok",True):
                    u.synced = True
                    u.faceid_status = "ok"
                else:
                    u.faceid_status = "error"
                session.add(u)
                await session.commit()
            except Exception:
                # ignore for now
                pass

if __name__ == "__main__":
    asyncio.run(resync_all())
