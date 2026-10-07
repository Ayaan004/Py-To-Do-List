# ⚡ TaskFlow — Professional Desktop To-Do List Application

A modern, responsive, and feature-complete productivity and task management desktop application built with Python and **CustomTkinter**.

---

## ✨ Features

- **🎨 Modern Dark & Light Theme UI**:
  - Sleek visual styling with rounded cards, border accents, and smooth hover effects.
  - Switch anytime between **Dark**, **Light**, or **System** theme.

- **📋 Complete Task Lifecycle**:
  - **Create & Edit**: Set title, multi-line notes/descriptions, category, priority, and due dates.
  - **Quick Due Date Pickers**: Fast-set shortcuts (`Today`, `Tomorrow`, `+7 Days`, or manual `YYYY-MM-DD`).
  - **Priority System**: ⚡ High (Crimson), Medium (Amber), and Low (Green) with colored badge indicators.
  - **Category / Project Tags**: Work, Personal, Study, Finance, Health, and General.
  - **Quick Completion**: Checkbox toggle with instant strikethrough styling and real-time counter updates.

- **🔍 Smart Search & Filtering**:
  - **Live Search**: Instant keyword search across task titles and notes as you type.
  - **Sidebar Views**:
    - 📋 All Tasks
    - 📅 Due Today
    - 🚀 Upcoming
    - ⚡ High Priority
    - ⚠️ Overdue (highlights past due dates in red)
    - ✅ Completed
  - **Category Filtering**: Filter tasks by project category directly from the sidebar.
  - **Multi-criteria Sorting**: Sort by Newest, Oldest, Priority, Due Date, or Alphabetical (A-Z).

- **📊 Productivity Analytics Dashboard**:
  - Live metric counters: Total Tasks, Pending, Completed, High Priority.
  - Visual completion percentage progress bar.

- **💾 Data Persistence & Portability**:
  - **Auto-save**: Real-time JSON persistence (`tasks.json`).
  - **CSV Export**: Export all tasks with full metadata to `.csv` for Excel or backup.
  - **CSV Import**: Import tasks seamlessly from any standard CSV file.
  - **Batch Actions**: One-click "Clear Completed" and "Clear All Tasks" with safety confirmation prompts.

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.8+
- Dependencies: `customtkinter` and `pillow`

```bash
pip install customtkinter pillow
```

### 2. Launch the Application
Run `main.py` directly from your terminal:

```bash
python main.py
```

---

## 📁 Project Structure

```
To-Do List/
├── main.py          # Application entry point with error handling
├── todo_app.py      # CustomTkinter GUI (Sidebar, Task Cards, Dialogs)
├── task_manager.py  # Data model (Task) and Manager (JSON storage, filters, stats, CSV)
├── tasks.json       # Local task database (auto-generated)
└── README.md        # Documentation
```
