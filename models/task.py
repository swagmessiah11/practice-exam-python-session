from datetime import datetime


class Task:
    VALID_STATUSES = ('pending', 'in_progress', 'completed')
    VALID_PRIORITIES = (1, 2, 3)

    def __init__(self, title, description, priority, due_date, project_id, assignee_id):
        if not title or not str(title).strip():
            raise ValueError("Название задачи не может быть пустым")
        if priority not in self.VALID_PRIORITIES:
            raise ValueError("Приоритет должен быть 1, 2 или 3")
        if not isinstance(due_date, datetime):
            raise ValueError("due_date должен быть объектом datetime")
        if project_id is not None and (not isinstance(project_id, int) or project_id <= 0):
            raise ValueError("project_id должен быть положительным целым числом")
        if assignee_id is not None and (not isinstance(assignee_id, int) or assignee_id <= 0):
            raise ValueError("assignee_id должен быть положительным целым числом")

        self.id = None
        self.title = str(title).strip()
        self.description = str(description).strip() if description else ""
        self.priority = priority
        self.status = 'pending'
        self.due_date = due_date
        self.project_id = project_id
        self.assignee_id = assignee_id

    def update_status(self, new_status):
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Недопустимый статус: {new_status}. Допустимые: {self.VALID_STATUSES}")
        self.status = new_status

    def is_overdue(self):
        if self.status == 'completed':
            return False
        return datetime.now() > self.due_date

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "project_id": self.project_id,
            "assignee_id": self.assignee_id,
        }
