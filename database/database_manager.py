import sqlite3
from datetime import datetime
from models.task import Task
from models.project import Project
from models.user import User


class DatabaseManager:
    def __init__(self, db_path="database/tasks.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._initialize_tables()

    def _initialize_tables(self):
        self.create_user_table()
        self.create_project_table()
        self.create_task_table()

    def close(self):
        if self.connection:
            self.connection.close()

    @staticmethod
    def _parse_datetime(value):
        if value is None:
            return None
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None

    # --- Tasks ---

    def create_task_table(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT    DEFAULT '',
                priority    INTEGER NOT NULL CHECK(priority IN (1, 2, 3)),
                status      TEXT    NOT NULL DEFAULT 'pending',
                due_date    TEXT    NOT NULL,
                project_id  INTEGER,
                assignee_id INTEGER,
                FOREIGN KEY (project_id)  REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (assignee_id) REFERENCES users(id)    ON DELETE SET NULL
            )
        """)
        self.connection.commit()

    def add_task(self, task):
        cursor = self.connection.execute(
            "INSERT INTO tasks (title, description, priority, status, due_date, project_id, assignee_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (task.title, task.description, task.priority, task.status, task.due_date.isoformat(), task.project_id, task.assignee_id),
        )
        self.connection.commit()
        task.id = cursor.lastrowid
        return task.id

    def get_task_by_id(self, task_id):
        row = self.connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._row_to_task(row) if row else None

    def get_all_tasks(self):
        rows = self.connection.execute("SELECT * FROM tasks").fetchall()
        return [self._row_to_task(r) for r in rows]

    def update_task(self, task_id, **kwargs):
        allowed = {"title", "description", "priority", "status", "due_date", "project_id", "assignee_id"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return False
        if "due_date" in fields and isinstance(fields["due_date"], datetime):
            fields["due_date"] = fields["due_date"].isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [task_id]
        cursor = self.connection.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_task(self, task_id):
        cursor = self.connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def search_tasks(self, query):
        pattern = f"%{query}%"
        rows = self.connection.execute(
            "SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ?", (pattern, pattern)
        ).fetchall()
        return [self._row_to_task(r) for r in rows]

    def get_tasks_by_project(self, project_id):
        rows = self.connection.execute("SELECT * FROM tasks WHERE project_id = ?", (project_id,)).fetchall()
        return [self._row_to_task(r) for r in rows]

    def get_tasks_by_user(self, user_id):
        rows = self.connection.execute("SELECT * FROM tasks WHERE assignee_id = ?", (user_id,)).fetchall()
        return [self._row_to_task(r) for r in rows]

    def _row_to_task(self, row):
        task = Task(
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            due_date=self._parse_datetime(row["due_date"]),
            project_id=row["project_id"],
            assignee_id=row["assignee_id"],
        )
        task.id = row["id"]
        task.status = row["status"]
        return task

    # --- Projects ---

    def create_project_table(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                description TEXT    DEFAULT '',
                start_date  TEXT    NOT NULL,
                end_date    TEXT    NOT NULL,
                status      TEXT    NOT NULL DEFAULT 'active'
            )
        """)
        self.connection.commit()

    def add_project(self, project):
        cursor = self.connection.execute(
            "INSERT INTO projects (name, description, start_date, end_date, status) VALUES (?, ?, ?, ?, ?)",
            (project.name, project.description, project.start_date.isoformat(), project.end_date.isoformat(), project.status),
        )
        self.connection.commit()
        project.id = cursor.lastrowid
        return project.id

    def get_project_by_id(self, project_id):
        row = self.connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return self._row_to_project(row) if row else None

    def get_all_projects(self):
        rows = self.connection.execute("SELECT * FROM projects").fetchall()
        return [self._row_to_project(r) for r in rows]

    def update_project(self, project_id, **kwargs):
        allowed = {"name", "description", "start_date", "end_date", "status"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return False
        for date_field in ("start_date", "end_date"):
            if date_field in fields and isinstance(fields[date_field], datetime):
                fields[date_field] = fields[date_field].isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [project_id]
        cursor = self.connection.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_project(self, project_id):
        cursor = self.connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def _row_to_project(self, row):
        project = Project(
            name=row["name"],
            description=row["description"],
            start_date=self._parse_datetime(row["start_date"]),
            end_date=self._parse_datetime(row["end_date"]),
        )
        project.id = row["id"]
        project.status = row["status"]
        return project

    # --- Users ---

    def create_user_table(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                username          TEXT    NOT NULL UNIQUE,
                email             TEXT    NOT NULL UNIQUE,
                role              TEXT    NOT NULL,
                registration_date TEXT    NOT NULL
            )
        """)
        self.connection.commit()

    def add_user(self, user):
        cursor = self.connection.execute(
            "INSERT INTO users (username, email, role, registration_date) VALUES (?, ?, ?, ?)",
            (user.username, user.email, user.role, user.registration_date.isoformat()),
        )
        self.connection.commit()
        user.id = cursor.lastrowid
        return user.id

    def get_user_by_id(self, user_id):
        row = self.connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._row_to_user(row) if row else None

    def get_all_users(self):
        rows = self.connection.execute("SELECT * FROM users").fetchall()
        return [self._row_to_user(r) for r in rows]

    def update_user(self, user_id, **kwargs):
        allowed = {"username", "email", "role"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [user_id]
        cursor = self.connection.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_user(self, user_id):
        cursor = self.connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def _row_to_user(self, row):
        user = User(username=row["username"], email=row["email"], role=row["role"])
        user.id = row["id"]
        user.registration_date = self._parse_datetime(row["registration_date"])
        return user
