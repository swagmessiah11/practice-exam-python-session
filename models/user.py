from datetime import datetime
import re


class User:
    VALID_ROLES = ('admin', 'manager', 'developer')

    def __init__(self, username, email, role):
        if not username or not str(username).strip():
            raise ValueError("Имя пользователя не может быть пустым")
        if not email or not self._is_valid_email(email):
            raise ValueError("Некорректный email адрес")
        if role not in self.VALID_ROLES:
            raise ValueError(f"Недопустимая роль: {role}. Допустимые: {self.VALID_ROLES}")

        self.id = None
        self.username = str(username).strip()
        self.email = str(email).strip().lower()
        self.role = role
        self.registration_date = datetime.now()

    @staticmethod
    def _is_valid_email(email):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(pattern, str(email).strip()))

    def update_info(self, username=None, email=None, role=None):
        if username is not None:
            if not str(username).strip():
                raise ValueError("Имя пользователя не может быть пустым")
            self.username = str(username).strip()

        if email is not None:
            if not self._is_valid_email(email):
                raise ValueError("Некорректный email адрес")
            self.email = str(email).strip().lower()

        if role is not None:
            if role not in self.VALID_ROLES:
                raise ValueError(f"Недопустимая роль: {role}. Допустимые: {self.VALID_ROLES}")
            self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
        }
