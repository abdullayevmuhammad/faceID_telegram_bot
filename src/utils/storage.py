# src/utils/storage.py
"""
Temporary in-memory storage for users data.
This will be replaced with database later.
"""
from datetime import datetime
from typing import Dict, Optional, List


class UserStorage:
    """In-memory user storage"""

    def __init__(self):
        self.users: Dict[int, dict] = {}  # telegram_id -> user data
        self.passports: Dict[str, int] = {}  # passport -> telegram_id

    def add_user(self, telegram_id: int, full_name: str, passport: str, photo_id: str) -> dict:
        """Add or update user"""
        user_data = {
            "telegram_id": telegram_id,
            "full_name": full_name,
            "passport": passport.upper(),
            "photo_id": photo_id,
            "role": "user",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Remove old passport mapping if exists
        if telegram_id in self.users:
            old_passport = self.users[telegram_id].get("passport")
            if old_passport and old_passport in self.passports:
                del self.passports[old_passport]

        # Store user
        self.users[telegram_id] = user_data
        self.passports[passport.upper()] = telegram_id

        return user_data

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[dict]:
        """Get user by telegram ID"""
        return self.users.get(telegram_id)

    def get_user_by_passport(self, passport: str) -> Optional[dict]:
        """Get user by passport"""
        telegram_id = self.passports.get(passport.upper())
        if telegram_id:
            return self.users.get(telegram_id)
        return None

    def get_all_users(self) -> List[dict]:
        """Get all users"""
        return list(self.users.values())

    def get_total_users(self) -> int:
        """Get total number of users"""
        return len(self.users)

    def get_today_users(self) -> int:
        """Get users registered today"""
        today = datetime.utcnow().date()
        count = 0
        for user in self.users.values():
            if user["created_at"].date() == today:
                count += 1
        return count

    def find_duplicate_passports(self) -> List[str]:
        """Find duplicate passports (should be empty in this implementation)"""
        return []

    def user_exists(self, telegram_id: int) -> bool:
        """Check if user exists"""
        return telegram_id in self.users

    def passport_exists(self, passport: str) -> bool:
        """Check if passport already registered"""
        return passport.upper() in self.passports

    def delete_user(self, telegram_id: int) -> bool:
        """Delete user"""
        if telegram_id in self.users:
            passport = self.users[telegram_id].get("passport")
            if passport and passport in self.passports:
                del self.passports[passport]
            del self.users[telegram_id]
            return True
        return False


# Global storage instance
user_storage = UserStorage()