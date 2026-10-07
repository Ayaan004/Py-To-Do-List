"""
TaskFlow - Professional To-Do List Application GUI
Built with CustomTkinter for a modern, sleek desktop experience.
"""

from __future__ import annotations
from datetime import date, timedelta
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk

from task_manager import (
    CATEGORIES,
    CATEGORY_PALETTE,
    PRIORITIES,
    PRIORITY_ACCENTS,
    PRIORITY_PALETTE,
    Task,
    TaskManager,
)

# Configure default appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class TaskDialog(ctk.CTkToplevel):
    """Modern modal dialog for Creating and Editing Tasks."""

    def __init__(self, parent: ctk.CTk, task: Optional[Task] = None, on_save_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.task = task
        self.on_save_callback = on_save_callback

        is_edit = task is not None
        self.title("Edit Task" if is_edit else "Create New Task")
        self.geometry("520x620")
        self.resizable(False, False)

        # Center dialog relative to parent
        self.transient(parent)
        self.grab_set()
        self.focus_force()

        self._center_window()
        self._build_ui(is_edit)

    def _center_window(self):
        self.update_idletasks()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        px = self.parent.winfo_x()
        py = self.parent.winfo_y()
        w = 520
        h = 620
        x = max(0, px + (pw - w) // 2)
        y = max(0, py + (ph - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self, is_edit: bool):
        # Header banner
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(20, 10))

        title_text = "✏️ Edit Task" if is_edit else "✨ Create New Task"
        header_lbl = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        header_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            header_frame,
            text="Organize your goals with priority, category and due dates.",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            anchor="w",
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Main scrollable or stacked form frame
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=10)

        # 1. Title Input
        ctk.CTkLabel(form, text="Task Title *", font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", pady=(5, 3)
        )
        self.title_entry = ctk.CTkEntry(
            form,
            placeholder_text="e.g., Deliver Quarterly Strategy Deck",
            height=38,
            font=ctk.CTkFont(size=13),
        )
        self.title_entry.pack(fill="x")
        if self.task:
            self.title_entry.insert(0, self.task.title)

        # 2. Description / Notes
        ctk.CTkLabel(form, text="Description & Notes", font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", pady=(12, 3)
        )
        self.desc_text = ctk.CTkTextbox(form, height=90, font=ctk.CTkFont(size=12))
        self.desc_text.pack(fill="x")
        if self.task and self.task.description:
            self.desc_text.insert("1.0", self.task.description)

        # 3. Category & Priority Row
        row_cat_pri = ctk.CTkFrame(form, fg_color="transparent")
        row_cat_pri.pack(fill="x", pady=(12, 0))

        # Category column
        cat_col = ctk.CTkFrame(row_cat_pri, fg_color="transparent")
        cat_col.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(cat_col, text="Category", font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", pady=(0, 4)
        )
        default_cat = self.task.category if self.task else "General"
        self.cat_var = ctk.StringVar(value=default_cat)
        self.cat_menu = ctk.CTkOptionMenu(
            cat_col,
            variable=self.cat_var,
            values=CATEGORIES,
            height=36,
        )
        self.cat_menu.pack(fill="x")

        # Priority column
        pri_col = ctk.CTkFrame(row_cat_pri, fg_color="transparent")
        pri_col.pack(side="right", fill="x", expand=True, padx=(8, 0))
        ctk.CTkLabel(pri_col, text="Priority", font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", pady=(0, 4)
        )
        default_pri = self.task.priority if self.task else "Medium"
        self.pri_var = ctk.StringVar(value=default_pri)
        self.pri_seg = ctk.CTkSegmentedButton(
            pri_col,
            variable=self.pri_var,
            values=["Low", "Medium", "High"],
            height=36,
        )
        self.pri_seg.pack(fill="x")

        # 4. Due Date with Quick Selectors
        ctk.CTkLabel(form, text="Due Date (YYYY-MM-DD)", font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", pady=(14, 3)
        )

        date_row = ctk.CTkFrame(form, fg_color="transparent")
        date_row.pack(fill="x")

        self.date_entry = ctk.CTkEntry(
            date_row,
            placeholder_text="YYYY-MM-DD",
            height=36,
            font=ctk.CTkFont(size=13),
        )
        self.date_entry.pack(side="left", fill="x", expand=True)
        if self.task and self.task.due_date:
            self.date_entry.insert(0, self.task.due_date)

        # Quick date buttons
        quick_dates_frame = ctk.CTkFrame(form, fg_color="transparent")
        quick_dates_frame.pack(fill="x", pady=(6, 0))

        btn_today = ctk.CTkButton(
            quick_dates_frame,
            text="Today",
            width=70,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self._set_due_date(0),
        )
        btn_today.pack(side="left", padx=(0, 6))

        btn_tmrw = ctk.CTkButton(
            quick_dates_frame,
            text="Tomorrow",
            width=75,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self._set_due_date(1),
        )
        btn_tmrw.pack(side="left", padx=(0, 6))

        btn_week = ctk.CTkButton(
            quick_dates_frame,
            text="+7 Days",
            width=70,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self._set_due_date(7),
        )
        btn_week.pack(side="left", padx=(0, 6))

        btn_clear = ctk.CTkButton(
            quick_dates_frame,
            text="Clear Date",
            width=75,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.date_entry.delete(0, "end"),
        )
        btn_clear.pack(side="left")

        # Bottom Actions Button Bar
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(15, 20), side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            height=40,
            fg_color="transparent",
            border_width=1,
            border_color=("gray60", "gray40"),
            text_color=("gray10", "gray90"),
            command=self.destroy,
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Changes" if is_edit else "Create Task",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_submit,
        )
        save_btn.pack(side="right", fill="x", expand=True, padx=(8, 0))

        # Keyboard shortcuts
        self.bind("<Escape>", lambda e: self.destroy())
        self.title_entry.bind("<Return>", lambda e: self._on_submit())
        self.title_entry.focus()

    def _set_due_date(self, days_offset: int):
        target = date.today() + timedelta(days=days_offset)
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, target.isoformat())

    def _on_submit(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Validation Error", "Please enter a task title.", parent=self)
            self.title_entry.focus()
            return

        due_date_str = self.date_entry.get().strip()
        if due_date_str:
            try:
                date.fromisoformat(due_date_str)
            except ValueError:
                messagebox.showerror(
                    "Invalid Date",
                    "Due date must follow YYYY-MM-DD format (e.g., 2026-10-15).",
                    parent=self,
                )
                self.date_entry.focus()
                return

        desc = self.desc_text.get("1.0", "end-1c").strip()
        category = self.cat_var.get()
        priority = self.pri_var.get()

        data = {
            "title": title,
            "description": desc,
            "category": category,
            "priority": priority,
            "due_date": due_date_str,
        }

        if self.on_save_callback:
            self.on_save_callback(data, self.task)

        self.destroy()


class TaskCard(ctk.CTkFrame):
    """Render a modern visual card for an individual task."""

    def __init__(
        self,
        parent,
        task: Task,
        on_toggle,
        on_edit,
        on_delete,
        **kwargs,
    ):
        super().__init__(
            parent,
            corner_radius=10,
            fg_color=("gray92", "#1E222B"),
            border_width=1,
            border_color=("gray80", "#2D333F"),
            **kwargs,
        )
        self.task = task
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete

        self._build_card()

    def _build_card(self):
        # Left-edge priority accent strip
        accent_color = PRIORITY_ACCENTS.get(self.task.priority, "#9CA3AF")
        if self.task.completed:
            accent_color = "#4B5563"  # Muted if completed

        strip = ctk.CTkFrame(
            self,
            width=5,
            corner_radius=3,
            fg_color=accent_color,
        )
        strip.pack(side="left", fill="y", padx=(6, 8), pady=8)

        # Checkbox for quick completion toggle
        self.chk_var = ctk.BooleanVar(value=self.task.completed)
        self.checkbox = ctk.CTkCheckBox(
            self,
            text="",
            variable=self.chk_var,
            width=24,
            height=24,
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=6,
            command=lambda: self.on_toggle(self.task.id),
        )
        self.checkbox.pack(side="left", padx=(2, 10), pady=12)

        # Center info container
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=10)

        # Title
        title_font = ctk.CTkFont(
            size=14,
            weight="bold" if not self.task.completed else "normal",
        )
        title_color = "gray50" if self.task.completed else ("gray15", "gray95")

        # Strikethrough unicode simulation if completed
        display_title = self._strikethrough(self.task.title) if self.task.completed else self.task.title

        title_lbl = ctk.CTkLabel(
            info_frame,
            text=display_title,
            font=title_font,
            text_color=title_color,
            anchor="w",
        )
        title_lbl.pack(anchor="w")

        # Description (if present)
        if self.task.description:
            snippet = self.task.description.split("\n")[0]
            if len(snippet) > 80:
                snippet = snippet[:80] + "..."
            desc_lbl = ctk.CTkLabel(
                info_frame,
                text=snippet,
                font=ctk.CTkFont(size=12),
                text_color="gray55",
                anchor="w",
            )
            desc_lbl.pack(anchor="w", pady=(2, 0))

        # Badges Row (Category, Priority, Due Date)
        badges_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        badges_row.pack(anchor="w", pady=(6, 0))

        # 1. Category Pill
        cat_bg, cat_fg = CATEGORY_PALETTE.get(
            self.task.category, (("#E5E7EB", "#1F2937"), ("#374151", "#9CA3AF"))
        )
        cat_badge = ctk.CTkLabel(
            badges_row,
            text=f"📁 {self.task.category}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=cat_bg,
            text_color=cat_fg,
            corner_radius=6,
            padx=7,
            pady=2,
        )
        cat_badge.pack(side="left", padx=(0, 6))

        # 2. Priority Pill
        pri_bg, pri_fg = PRIORITY_PALETTE.get(
            self.task.priority, (("#FEF3C7", "#451A03"), ("#B45309", "#FBBF24"))
        )
        pri_badge = ctk.CTkLabel(
            badges_row,
            text=f"⚡ {self.task.priority}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=pri_bg,
            text_color=pri_fg,
            corner_radius=6,
            padx=7,
            pady=2,
        )
        pri_badge.pack(side="left", padx=(0, 6))

        # 3. Due Date Pill
        if self.task.due_date:
            if self.task.is_overdue:
                date_text = f"⚠️ Overdue ({self.task.due_date})"
                date_bg = ("#FEE2E2", "#450A0A")
                date_fg = ("#B91C1C", "#F87171")
            elif self.task.is_due_today:
                date_text = "📅 Due Today"
                date_bg = ("#FEF3C7", "#451A03")
                date_fg = ("#B45309", "#FBBF24")
            else:
                date_text = f"📅 {self.task.due_date}"
                date_bg = ("#E0E7FF", "#1E1B4B")
                date_fg = ("#3730A3", "#818CF8") if not self.task.completed else ("#6B7280", "#9CA3AF")

            date_badge = ctk.CTkLabel(
                badges_row,
                text=date_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=date_bg,
                text_color=date_fg,
                corner_radius=6,
                padx=7,
                pady=2,
            )
            date_badge.pack(side="left", padx=(0, 6))

        # Right-side Action buttons
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(side="right", padx=12, pady=10)

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=32,
            height=32,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=("gray80", "#2D333F"),
            text_color=("gray20", "gray85"),
            command=lambda: self.on_edit(self.task),
        )
        edit_btn.pack(side="left", padx=2)

        del_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=32,
            height=32,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=("#FEE2E2", "#451A1A"),
            text_color=("#DC2626", "#F87171"),
            command=lambda: self.on_delete(self.task.id),
        )
        del_btn.pack(side="left", padx=2)

    def _strikethrough(self, text: str) -> str:
        return "".join(c + "\u0336" for c in text)


class TodoApp(ctk.CTk):
    """Main Application Window for TaskFlow."""

    def __init__(self):
        super().__init__()

        self.title("TaskFlow • Professional Task Manager")
        self.geometry("1120x740")
        self.minsize(980, 620)

        # Initialize Task Data Manager
        self.task_manager = TaskManager("tasks.json")

        # UI State variables
        self.active_filter = "all"  # 'all', 'today', 'upcoming', 'high_priority', 'overdue', 'completed'
        self.active_category = "All"
        self.sort_by = "created_desc"
        self.search_text = ""

        # Setup Layout
        self._setup_layout()
        self._refresh_ui()

    def _setup_layout(self):
        # Configure main grid weights (2 columns: Sidebar and Content)
        self.grid_columnconfigure(0, weight=0)  # fixed sidebar
        self.grid_columnconfigure(1, weight=1)  # expandable content
        self.grid_rowconfigure(0, weight=1)

        # ------------------ LEFT SIDEBAR ------------------
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=("gray95", "#16191F"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(3, weight=1)

        # Sidebar Header Branding
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=18, pady=(20, 16))

        logo_lbl = ctk.CTkLabel(
            brand_frame,
            text="⚡ TaskFlow",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#2563EB", "#60A5FA"),
        )
        logo_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            brand_frame,
            text="Productivity Workspace",
            font=ctk.CTkFont(size=12),
            text_color="gray55",
        )
        subtitle_lbl.pack(anchor="w")

        # CTA Add Task Button
        self.btn_new_task = ctk.CTkButton(
            self.sidebar,
            text="+ Add New Task",
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#2563EB", "#3B82F6"),
            hover_color=("#1D4ED8", "#2563EB"),
            command=self._open_add_dialog,
        )
        self.btn_new_task.pack(fill="x", padx=18, pady=(0, 16))

        # Filter Section Label
        ctk.CTkLabel(
            self.sidebar,
            text="VIEWS & FILTERS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray50",
            anchor="w",
        ).pack(fill="x", padx=18, pady=(8, 4))

        # Filter Buttons Container
        self.filter_buttons = {}
        filters_config = [
            ("all", "📋 All Tasks"),
            ("today", "📅 Due Today"),
            ("upcoming", "🚀 Upcoming"),
            ("high_priority", "⚡ High Priority"),
            ("overdue", "⚠️ Overdue"),
            ("completed", "✅ Completed"),
        ]

        for f_key, label_text in filters_config:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label_text,
                height=34,
                anchor="w",
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                hover_color=("gray85", "#242A36"),
                text_color=("gray20", "gray90"),
                command=lambda k=f_key: self._set_filter(k),
            )
            btn.pack(fill="x", padx=14, pady=2)
            self.filter_buttons[f_key] = btn

        # Category Section Label
        ctk.CTkLabel(
            self.sidebar,
            text="PROJECTS & CATEGORIES",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray50",
            anchor="w",
        ).pack(fill="x", padx=18, pady=(16, 4))

        category_options = ["All"] + CATEGORIES
        self.cat_select_var = ctk.StringVar(value="All")
        self.cat_selector = ctk.CTkOptionMenu(
            self.sidebar,
            values=category_options,
            variable=self.cat_select_var,
            height=34,
            command=self._on_category_changed,
        )
        self.cat_selector.pack(fill="x", padx=16, pady=4)

        # Bottom Sidebar Utilities (Import/Export, Theme Toggle)
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(fill="x", side="bottom", padx=18, pady=16)

        clear_completed_btn = ctk.CTkButton(
            bottom_frame,
            text="🧹 Clear Completed",
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=("gray85", "#262C38"),
            text_color=("gray30", "gray70"),
            command=self._clear_completed,
        )
        clear_completed_btn.pack(fill="x", pady=2)

        clear_all_btn = ctk.CTkButton(
            bottom_frame,
            text="🗑️ Clear All Tasks",
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=("#FEE2E2", "#451A1A"),
            text_color=("#DC2626", "#F87171"),
            command=self._clear_all,
        )
        clear_all_btn.pack(fill="x", pady=2)

        data_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        data_row.pack(fill="x", pady=4)

        btn_exp = ctk.CTkButton(
            data_row,
            text="Export CSV",
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("gray80", "#242A36"),
            hover_color=("gray70", "#303746"),
            text_color=("gray20", "gray90"),
            command=self._export_csv,
        )
        btn_exp.pack(side="left", fill="x", expand=True, padx=(0, 4))

        btn_imp = ctk.CTkButton(
            data_row,
            text="Import CSV",
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("gray80", "#242A36"),
            hover_color=("gray70", "#303746"),
            text_color=("gray20", "gray90"),
            command=self._import_csv,
        )
        btn_imp.pack(side="right", fill="x", expand=True, padx=(4, 0))

        # Appearance mode toggle
        self.mode_var = ctk.StringVar(value="Dark")
        mode_switch = ctk.CTkOptionMenu(
            bottom_frame,
            values=["Dark", "Light", "System"],
            variable=self.mode_var,
            height=30,
            command=lambda mode: ctk.set_appearance_mode(mode),
        )
        mode_switch.pack(fill="x", pady=(6, 0))

        # ------------------ RIGHT CONTENT AREA ------------------
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray98", "#0F1117"))
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # Top Control & Search Bar
        top_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=24, pady=(20, 12))

        # View Title
        self.view_title_lbl = ctk.CTkLabel(
            top_bar,
            text="All Tasks",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w",
        )
        self.view_title_lbl.pack(side="left")

        # Search Bar
        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="🔍 Search tasks by title or notes...",
            width=280,
            height=36,
        )
        self.search_entry.pack(side="right", padx=(12, 0))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

        # Sort Dropdown
        sort_options = ["Newest First", "Priority", "Due Date", "Title (A-Z)", "Oldest First"]
        self.sort_var = ctk.StringVar(value="Newest First")
        self.sort_menu = ctk.CTkOptionMenu(
            top_bar,
            values=sort_options,
            variable=self.sort_var,
            width=140,
            height=36,
            command=self._on_sort_changed,
        )
        self.sort_menu.pack(side="right")

        # ------------------ STATS DASHBOARD STRIP ------------------
        self.stats_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("gray92", "#181C24"),
            corner_radius=12,
        )
        self.stats_frame.pack(fill="x", padx=24, pady=(0, 14))

        self.stat_cards = {}
        stat_configs = [
            ("total", "Total Tasks", "0", "#3B82F6"),
            ("pending", "Pending", "0", "#F59E0B"),
            ("completed", "Completed", "0", "#10B981"),
            ("high_priority", "High Priority", "0", "#EF4444"),
        ]

        for s_key, label_str, initial_val, color_accent in stat_configs:
            card = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            card.pack(side="left", fill="both", expand=True, padx=12, pady=12)

            num_lbl = ctk.CTkLabel(
                card,
                text=initial_val,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=color_accent,
                anchor="w",
            )
            num_lbl.pack(anchor="w")

            desc_lbl = ctk.CTkLabel(
                card,
                text=label_str,
                font=ctk.CTkFont(size=12),
                text_color="gray55",
                anchor="w",
            )
            desc_lbl.pack(anchor="w")

            self.stat_cards[s_key] = num_lbl

        # Progress bar column in stats
        progress_card = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        progress_card.pack(side="right", fill="both", expand=True, padx=16, pady=12)

        self.progress_lbl = ctk.CTkLabel(
            progress_card,
            text="0% Complete",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        self.progress_lbl.pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(
            progress_card,
            height=10,
            corner_radius=5,
            progress_color="#10B981",
        )
        self.progress_bar.pack(fill="x", pady=(4, 0))
        self.progress_bar.set(0)

        # ------------------ TASKS SCROLLABLE CONTAINER ------------------
        self.tasks_container = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            corner_radius=8,
        )
        self.tasks_container.pack(fill="both", expand=True, padx=24, pady=(0, 10))

        # ------------------ BOTTOM STATUS BAR ------------------
        self.status_bar = ctk.CTkLabel(
            self.content_frame,
            text="Ready • Auto-saved",
            font=ctk.CTkFont(size=11),
            text_color="gray50",
            anchor="w",
        )
        self.status_bar.pack(fill="x", padx=26, pady=(0, 8))

    def _set_status(self, text: str):
        self.status_bar.configure(text=f"{text} • Auto-saved")

    def _open_add_dialog(self):
        TaskDialog(self, on_save_callback=self._handle_save_task)

    def _open_edit_dialog(self, task: Task):
        TaskDialog(self, task=task, on_save_callback=self._handle_save_task)

    def _handle_save_task(self, data: dict, existing_task: Optional[Task] = None):
        if existing_task:
            self.task_manager.update_task(
                existing_task.id,
                title=data["title"],
                description=data["description"],
                category=data["category"],
                priority=data["priority"],
                due_date=data["due_date"],
            )
            self._set_status("Task updated successfully")
        else:
            self.task_manager.add_task(
                title=data["title"],
                description=data["description"],
                category=data["category"],
                priority=data["priority"],
                due_date=data["due_date"],
            )
            self._set_status("New task added")

        self._refresh_ui()

    def _handle_toggle(self, task_id: str):
        task = self.task_manager.toggle_complete(task_id)
        if task:
            state_msg = "marked completed" if task.completed else "marked pending"
            self._set_status(f"Task '{task.title[:25]}' {state_msg}")
        self._refresh_ui()

    def _handle_delete(self, task_id: str):
        task = self.task_manager.get_task(task_id)
        task_name = task.title[:30] if task else "task"
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete:\n\"{task_name}\"?",
            parent=self,
        )
        if confirm:
            self.task_manager.delete_task(task_id)
            self._set_status("Task deleted")
            self._refresh_ui()

    def _clear_completed(self):
        stats = self.task_manager.get_statistics()
        if stats["completed"] == 0:
            messagebox.showinfo("Clear Completed", "There are no completed tasks to clear.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Clear Completed Tasks",
            f"Are you sure you want to delete all {stats['completed']} completed tasks?",
            parent=self,
        )
        if confirm:
            count = self.task_manager.clear_completed()
            self._set_status(f"Cleared {count} completed tasks")
            self._refresh_ui()

    def _clear_all(self):
        stats = self.task_manager.get_statistics()
        if stats["total"] == 0:
            messagebox.showinfo("Clear All Tasks", "There are no tasks to clear.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Clear All Tasks",
            f"Are you sure you want to delete ALL {stats['total']} tasks?\nThis will remove all pending and completed tasks.",
            parent=self,
        )
        if confirm:
            count = self.task_manager.clear_all()
            self._set_status(f"Cleared all {count} tasks")
            self._refresh_ui()

    def _set_filter(self, filter_name: str):
        self.active_filter = filter_name
        self._refresh_ui()

    def _on_category_changed(self, choice: str):
        self.active_category = choice
        self._refresh_ui()

    def _on_search_change(self, event=None):
        self.search_text = self.search_entry.get().strip()
        self._render_task_cards()

    def _on_sort_changed(self, choice: str):
        mapping = {
            "Newest First": "created_desc",
            "Oldest First": "created_asc",
            "Priority": "priority",
            "Due Date": "due_date",
            "Title (A-Z)": "title",
        }
        self.sort_by = mapping.get(choice, "created_desc")
        self._render_task_cards()

    def _export_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile="tasks_export.csv",
            title="Export Tasks to CSV",
            parent=self,
        )
        if file_path:
            try:
                self.task_manager.export_csv(file_path)
                messagebox.showinfo("Export Successful", f"Saved tasks to:\n{file_path}", parent=self)
                self._set_status("Tasks exported to CSV")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Could not export tasks:\n{e}", parent=self)

    def _import_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Import Tasks from CSV",
            parent=self,
        )
        if file_path:
            try:
                count = self.task_manager.import_csv(file_path)
                messagebox.showinfo("Import Successful", f"Successfully imported {count} tasks!", parent=self)
                self._set_status(f"Imported {count} tasks")
                self._refresh_ui()
            except Exception as e:
                messagebox.showerror("Import Failed", f"Could not import tasks:\n{e}", parent=self)

    def _refresh_ui(self):
        # 1. Update Sidebar Active Style
        view_titles = {
            "all": "All Tasks",
            "today": "Due Today",
            "upcoming": "Upcoming Tasks",
            "high_priority": "High Priority Tasks",
            "overdue": "Overdue Tasks",
            "completed": "Completed Tasks",
        }
        self.view_title_lbl.configure(text=view_titles.get(self.active_filter, "Tasks"))

        for f_key, btn in self.filter_buttons.items():
            if f_key == self.active_filter:
                btn.configure(
                    fg_color=("#DBEAFE", "#2563EB"),
                    text_color=("#1D4ED8", "#FFFFFF"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray20", "gray90"),
                )

        # 2. Update Stats cards
        stats = self.task_manager.get_statistics()
        self.stat_cards["total"].configure(text=str(stats["total"]))
        self.stat_cards["pending"].configure(text=str(stats["pending"]))
        self.stat_cards["completed"].configure(text=str(stats["completed"]))
        self.stat_cards["high_priority"].configure(text=str(stats["high_priority"]))

        rate = stats["completion_rate"]
        self.progress_lbl.configure(text=f"{rate}% Complete ({stats['completed']}/{stats['total']})")
        self.progress_bar.set(rate / 100.0)

        # 3. Render Cards
        self._render_task_cards()

    def _render_task_cards(self):
        # Clear existing cards
        for widget in self.tasks_container.winfo_children():
            widget.destroy()

        tasks = self.task_manager.get_filtered_tasks(
            filter_type=self.active_filter,
            category_filter=self.active_category,
            search_query=self.search_text,
            sort_by=self.sort_by,
        )

        if not tasks:
            empty_frame = ctk.CTkFrame(self.tasks_container, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, pady=60)

            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="🎉",
                font=ctk.CTkFont(size=48),
            )
            empty_icon.pack()

            empty_lbl = ctk.CTkLabel(
                empty_frame,
                text="No tasks match the current filter or search.",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="gray60",
            )
            empty_lbl.pack(pady=(10, 4))

            empty_sub = ctk.CTkLabel(
                empty_frame,
                text="Click '+ Add New Task' to capture ideas or plan your day.",
                font=ctk.CTkFont(size=12),
                text_color="gray45",
            )
            empty_sub.pack()
            return

        for task in tasks:
            card = TaskCard(
                self.tasks_container,
                task=task,
                on_toggle=self._handle_toggle,
                on_edit=self._open_edit_dialog,
                on_delete=self._handle_delete,
            )
            card.pack(fill="x", pady=5)


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
