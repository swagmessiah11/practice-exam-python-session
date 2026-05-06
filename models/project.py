from datetime import datetime


class Project:
    VALID_STATUSES = ('active', 'completed', 'on_hold')

    def __init__(self, name, description, start_date, end_date):
        if not name or not str(name).strip():
            raise ValueError("Название проекта не может быть пустым")
        if not isinstance(start_date, datetime):
            raise ValueError("start_date должен быть объектом datetime")
        if not isinstance(end_date, datetime):
            raise ValueError("end_date должен быть объектом datetime")
        if end_date <= start_date:
            raise ValueError("Дата окончания должна быть позже даты начала")

        self.id = None
        self.name = str(name).strip()
        self.description = str(description).strip() if description else ""
        self.start_date = start_date
        self.end_date = end_date
        self.status = 'active'

    def update_status(self, new_status):
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Недопустимый статус: {new_status}. Допустимые: {self.VALID_STATUSES}")
        self.status = new_status

    def get_progress(self):
        if self.status == 'completed':
            return 100.0

        now = datetime.now()

        if now <= self.start_date:
            return 0.0
        if now >= self.end_date:
            return 100.0

        total_duration = (self.end_date - self.start_date).total_seconds()
        elapsed = (now - self.start_date).total_seconds()
        return round((elapsed / total_duration) * 100, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
        }
