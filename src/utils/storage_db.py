# src/utils/storage_db.py
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.exc import NoResultFound
from datetime import date, datetime

from database.session import AsyncSessionLocal
from database.models import User

class UserStorageDB:
    """Async DB-backed wrapper returning plain dicts for handlers."""

    async def _to_dict(self, user: User) -> Dict[str, Any]:
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "full_name": user.full_name,
            "passport": user.passport,
            "photo_id": user.photo_id,
            "photo_path": getattr(user, "photo_path", None),
            "faceid_status": getattr(user, "faceid_status", None),
            "synced": getattr(user, "synced", None),
            "role": getattr(user, "role", "user"),
            "is_active": getattr(user, "is_active", True),
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    async def get_total_users(self) -> int:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(func.count()).select_from(User))
            return int(result.scalar() or 0)

    async def get_today_users(self) -> int:
        today = date.today()
        async with AsyncSessionLocal() as session:
            # Use cast to date on created_at depending on DB; func.date works for postgres
            result = await session.execute(
                select(func.count()).select_from(User).where(func.date(User.created_at) == today)
            )
            return int(result.scalar() or 0)

    async def find_duplicate_passports(self) -> List[str]:
        async with AsyncSessionLocal() as session:
            q = (
                select(User.passport)
                .group_by(User.passport)
                .having(func.count(User.passport) > 1)
            )
            result = await session.execute(q)
            rows = result.scalars().all()
            return list(rows)

    async def get_all_users(self) -> List[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).order_by(User.created_at.desc()))
            users = result.scalars().all()
            return [await self._to_dict(u) for u in users]

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalars().first()
            if not user:
                return None
            return await self._to_dict(user)

    async def add_or_update_user(
        self,
        telegram_id: int,
        full_name: str,
        passport: str,
        photo_id: str,
        photo_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update user row, return dict."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalars().first()
            now = datetime.utcnow()

            if user:
                # update fields
                user.full_name = full_name
                user.passport = passport
                user.photo_id = photo_id
                if photo_path is not None:
                    setattr(user, "photo_path", photo_path)
                user.updated_at = now
                # ensure synced/faceid_status exist
            else:
                user = User(
                    telegram_id=telegram_id,
                    full_name=full_name,
                    passport=passport,
                    photo_id=photo_id,
                    created_at=now,
                    updated_at=now
                )
                if photo_path is not None:
                    setattr(user, "photo_path", photo_path)
                session.add(user)

            await session.commit()
            # refresh to get id
            await session.refresh(user)
            return await self._to_dict(user)

    async def update_status(self, user_id: int, *, synced: Optional[bool] = None, faceid_status: Optional[str] = None):
        """Update status fields for a given user id."""
        async with AsyncSessionLocal() as session:
            user = await session.get(User, user_id)
            if not user:
                return False
            if synced is not None:
                setattr(user, "synced", bool(synced))
            if faceid_status is not None:
                setattr(user, "faceid_status", faceid_status)
            user.updated_at = datetime.utcnow()
            await session.commit()
            return True

# create a singleton instance to import easily
user_storage_db = UserStorageDB()
