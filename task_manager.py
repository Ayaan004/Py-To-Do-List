"""
Task Model and Storage Manager for Professional To-Do List Application.
Handles task data structures, JSON persistence, filtering, statistics, and import/export.
"""

from __future__ import annotations
import csv
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple


PRIORITIES = ["High", "Medium", "Low"]
CATEGORIES = ["Work", "Personal", "Study", "Finance", "Health", "General"]

# (LightModeBg, DarkModeBg), (LightModeFg, DarkModeFg)
PRIORITY_PALETTE: Dict[str, Tuple[Tuple[str, str], Tuple[str, str]]] = {
    "High": (("#FEE2E2", "#450A0A"), ("#B91C1C", "#F87171")),
    "Medium": (("#FEF3C7", "#451A03"), ("#B45309", "#FBBF24")),
    "Low": (("#D1FAE5", "#064E3B"), ("#047857", "#34D399")),
}

CATEGORY_PALETTE: Dict[str, Tuple[Tuple[str, str], Tuple[str, str]]] = {
    "Work": (("#DBEAFE", "#1E3A8A"), ("#1D4ED8", "#93C5FD")),
    "Personal": (("#EDE9FE", "#371B58"), ("#6D28D9", "#C4B5FD")),
    "Study": (("#FCE7F3", "#500724"), ("#BE185D", "#F472B6")),
    "Finance": (("#CCFBF1", "#042F2E"), ("#0F766E", "#2DD4BF")),
    "Health": (("#CFFAFE", "#083344"), ("#0E7490", "#22D3EE")),
    "General": (("#E5E7EB", "#1F2937"), ("#374151", "#9CA3AF")),
}

PRIORITY_ACCENTS: Dict[str, str] = {
    "High": "#EF4444",
    "Medium": "#F59E0B",
    "Low": "#10B981",
}


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    category: str = "General"
    priority: str = "Medium"
    due_date: str = ""  # YYYY-MM-DD
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        # Filter unknown keys to prevent breakages
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

    @property
    def is_overdue(self) -> bool:
        if self.completed or not self.due_date:
            return False
        try:
            due = date.fromisoformat(self.due_date)
            return due < date.today()
        except ValueError:
            return False

    @property
    def is_due_today(self) -> bool:
        if not self.due_date:
            return False
        try:
            due = date.fromisoformat(self.due_date)
            return due == date.today()
        except ValueError:
            return False


class TaskManager:
    """Manages collection of tasks with auto-saving, filtering, and stats."""

    def __init__(self, storage_path: str = "tasks.json"):
        self.storage_path = storage_path
        self.tasks: List[Task] = []
        self.load()

    def add_task(
        self,
        title: str,
        description: str = "",
        category: str = "General",
        priority: str = "Medium",
        due_date: str = "",
    ) -> Task:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Task title cannot be empty.")

        task = Task(
            title=clean_title,
            description=description.strip(),
            category=category if category in CATEGORIES else "General",
            priority=priority if priority in PRIORITIES else "Medium",
            due_date=due_date.strip(),
        )
        self.tasks.insert(0, task)
        self.save()
        return task

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task:
            return None

        if title is not None:
            clean_title = title.strip()
            if clean_title:
                task.title = clean_title
        if description is not None:
            task.description = description.strip()
        if category is not None:
            task.category = category
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date.strip()
        if completed is not None:
            task.completed = completed
            task.completed_at = datetime.now().isoformat(timespec="seconds") if completed else None

        self.save()
        return task

    def toggle_complete(self, task_id: str) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task:
            return None
        task.completed = not task.completed
        task.completed_at = datetime.now().isoformat(timespec="seconds") if task.completed else None
        self.save()
        return task

    def delete_task(self, task_id: str) -> bool:
        initial_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        if len(self.tasks) != initial_len:
            self.save()
            return True
        return False

    def clear_completed(self) -> int:
        initial_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t.completed]
        removed = initial_len - len(self.tasks)
        if removed > 0:
            self.save()
        return removed

    def clear_all(self) -> int:
        initial_len = len(self.tasks)
        if initial_len > 0:
            self.tasks.clear()
            self.save()
        return initial_len

    def get_task(self, task_id: str) -> Optional[Task]:
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        pending = total - completed
        overdue = sum(1 for t in self.tasks if t.is_overdue)
        high_priority = sum(1 for t in self.tasks if not t.completed and t.priority == "High")
        completion_rate = (completed / total * 100.0) if total > 0 else 0.0

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": round(completion_rate, 1),
        }

    def get_filtered_tasks(
        self,
        filter_type: str = "all",
        category_filter: str = "All",
        search_query: str = "",
        sort_by: str = "created_desc",
    ) -> List[Task]:
        results = list(self.tasks)
        today = date.today()

        # 1. Filter by Status/View
        if filter_type == "today":
            results = [t for t in results if t.is_due_today]
        elif filter_type == "upcoming":
            def is_upcoming(t: Task) -> bool:
                if not t.due_date or t.completed:
                    return False
                try:
                    return date.fromisoformat(t.due_date) > today
                except ValueError:
                    return False
            results = [t for t in results if is_upcoming(t)]
        elif filter_type == "overdue":
            results = [t for t in results if t.is_overdue]
        elif filter_type == "high_priority":
            results = [t for t in results if t.priority == "High" and not t.completed]
        elif filter_type == "pending":
            results = [t for t in results if not t.completed]
        elif filter_type == "completed":
            results = [t for t in results if t.completed]

        # 2. Filter by Category
        if category_filter and category_filter != "All":
            results = [t for t in results if t.category == category_filter]

        # 3. Filter by Search Query
        if search_query:
            q = search_query.lower().strip()
            results = [
                t for t in results
                if q in t.title.lower() or q in t.description.lower() or q in t.category.lower()
            ]

        # 4. Sort
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        if sort_by == "priority":
            results.sort(key=lambda t: (t.completed, priority_order.get(t.priority, 1)))
        elif sort_by == "due_date":
            # Tasks without due dates go last
            results.sort(
                key=lambda t: (t.completed, t.due_date if t.due_date else "9999-99-99")
            )
        elif sort_by == "title":
            results.sort(key=lambda t: (t.completed, t.title.lower()))
        elif sort_by == "created_asc":
            results.sort(key=lambda t: (t.completed, t.created_at))
        else:  # created_desc default
            results.sort(key=lambda t: (t.completed, t.created_at), reverse=True)

        return results

    def save(self) -> None:
        try:
            data = [t.to_dict() for t in self.tasks]
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Error saving tasks]: {e}")

    def load(self) -> None:
        if not os.path.exists(self.storage_path):
            self._load_sample_data()
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.tasks = [Task.from_dict(item) for item in data]
                else:
                    self.tasks = []
        except Exception as e:
            print(f"[Error loading tasks]: {e}")
            self.tasks = []

    def _load_sample_data(self) -> None:
        """Seed initial helpful tasks if first time running."""
        today_str = date.today().isoformat()
        self.tasks = [
            Task(
                title="Welcome to your Modern To-Do Planner! 🎉",
                description="Explore categories, priorities, due dates, and search filters.",
                category="General",
                priority="High",
                due_date=today_str,
                completed=False,
            ),
            Task(
                title="Complete project proposal report",
                description="Finalize financial projections and executive summary.",
                category="Work",
                priority="High",
                due_date=today_str,
                completed=False,
            ),
            Task(
                title="Review weekly team milestones",
                description="Check GitHub issues and sprint roadmap.",
                category="Work",
                priority="Medium",
                due_date="",
                completed=False,
            ),
            Task(
                title="Weekly grocery shopping list",
                description="Almond milk, whole wheat bread, fruits, and greens.",
                category="Personal",
                priority="Low",
                due_date="",
                completed=True,
            ),
        ]
        self.save()

    def export_csv(self, file_path: str) -> None:
        fieldnames = [
            "id", "title", "description", "category",
            "priority", "due_date", "completed", "created_at", "completed_at"
        ]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in self.tasks:
                writer.writerow(t.to_dict())

    def import_csv(self, file_path: str) -> int:
        imported_count = 0
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "title" in row and row["title"].strip():
                    completed_val = str(row.get("completed", "false")).lower() in ("true", "1", "yes")
                    task = Task(
                        title=row["title"].strip(),
                        description=row.get("description", "").strip(),
                        category=row.get("category", "General"),
                        priority=row.get("priority", "Medium"),
                        due_date=row.get("due_date", "").strip(),
                        completed=completed_val,
                    )
                    self.tasks.append(task)
                    imported_count += 1
        if imported_count > 0:
            self.save()
        return imported_count
