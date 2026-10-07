"""
TaskFlow - Modern & Professional Desktop To-Do List Application
Entry Point
"""

import sys
import tkinter as tk
from tkinter import messagebox


def main():
    try:
        from todo_app import TodoApp
        app = TodoApp()
        app.mainloop()
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Missing Dependencies",
            f"Required package not found: {e}\n\nPlease install dependencies via:\npip install customtkinter pillow",
        )
        sys.exit(1)
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Application Error", f"An unexpected error occurred:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
