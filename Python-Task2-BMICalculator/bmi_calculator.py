"""
Advanced BMI Calculator
------------------------
Oasis Infobyte SIP - Python Programming Track - Task 2

Features:
- GUI built with tkinter (no command line)
- Input fields for weight (kg) and height (m) with a Calculate button
- Color-coded result feedback (green = normal, red = obese, etc.)
- Multi-user support: BMI records saved per named user
- Historical records stored in an SQLite database
- Graph view: line chart of a user's BMI trend over time (matplotlib)
- Input validation and error handling for bad input / database failures
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------------------------------
# SQLite stores everything in a single local file (bmi_records.db). No
# separate server needed -- Python's built-in `sqlite3` module talks to it
# directly. Every record row = one BMI calculation for one user.

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bmi_records.db")


def get_connection():
    """Open (and if needed create) the database file, return a connection."""
    conn = sqlite3.connect(DB_FILE)
    return conn


def init_db():
    """Create the records table the first time the app runs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            bmi REAL NOT NULL,
            category TEXT NOT NULL,
            recorded_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_record(user_name, weight, height, bmi, category):
    """Insert one BMI calculation into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO bmi_records (user_name, weight, height, bmi, category, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_name, weight, height, bmi, category, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_user_history(user_name):
    """Fetch all past records for one user, ordered oldest -> newest."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT bmi, recorded_at FROM bmi_records
        WHERE user_name = ?
        ORDER BY recorded_at ASC
        """,
        (user_name,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_users():
    """Return a distinct list of every user who has a saved record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_name FROM bmi_records ORDER BY user_name ASC")
    rows = [r[0] for r in cursor.fetchall()]
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# BMI LOGIC
# ---------------------------------------------------------------------------

def calculate_bmi(weight_kg, height_m):
    return weight_kg / (height_m ** 2)


def classify_bmi(bmi):
    """Return (category, color) for a given BMI value."""
    if bmi < 18.5:
        return "Underweight", "#3498db"      # blue
    elif bmi < 25:
        return "Normal", "#27ae60"           # green
    elif bmi < 30:
        return "Overweight", "#e67e22"       # orange
    else:
        return "Obese", "#e74c3c"            # red


# ---------------------------------------------------------------------------
# GUI APPLICATION
# ---------------------------------------------------------------------------

class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced BMI Calculator - Oasis Infobyte SIP")
        self.geometry("460x520")
        self.resizable(False, False)
        self.configure(bg="#f4f6f7")

        self._build_widgets()

    # -- UI construction ---------------------------------------------------
    def _build_widgets(self):
        title = tk.Label(
            self, text="BMI Calculator", font=("Segoe UI", 20, "bold"),
            bg="#f4f6f7", fg="#2c3e50"
        )
        title.pack(pady=(20, 10))

        form = tk.Frame(self, bg="#f4f6f7")
        form.pack(pady=5)

        # Name
        tk.Label(form, text="Name:", font=("Segoe UI", 11), bg="#f4f6f7").grid(
            row=0, column=0, sticky="w", padx=8, pady=8
        )
        self.name_entry = ttk.Entry(form, width=25)
        self.name_entry.grid(row=0, column=1, padx=8, pady=8)

        # Weight
        tk.Label(form, text="Weight (kg):", font=("Segoe UI", 11), bg="#f4f6f7").grid(
            row=1, column=0, sticky="w", padx=8, pady=8
        )
        self.weight_entry = ttk.Entry(form, width=25)
        self.weight_entry.grid(row=1, column=1, padx=8, pady=8)

        # Height
        tk.Label(form, text="Height (m):", font=("Segoe UI", 11), bg="#f4f6f7").grid(
            row=2, column=0, sticky="w", padx=8, pady=8
        )
        self.height_entry = ttk.Entry(form, width=25)
        self.height_entry.grid(row=2, column=1, padx=8, pady=8)
        tk.Label(
            form, text="(e.g. 1.70 for 170cm)", font=("Segoe UI", 8, "italic"),
            bg="#f4f6f7", fg="#7f8c8d"
        ).grid(row=3, column=1, sticky="w", padx=8)

        # Calculate button
        calc_btn = tk.Button(
            self, text="Calculate BMI", font=("Segoe UI", 12, "bold"),
            bg="#2980b9", fg="white", activebackground="#1f618d",
            relief="flat", padx=10, pady=8, command=self.on_calculate
        )
        calc_btn.pack(pady=15)

        # Result display
        self.result_frame = tk.Frame(self, bg="#f4f6f7")
        self.result_frame.pack(pady=5)

        self.result_label = tk.Label(
            self.result_frame, text="", font=("Segoe UI", 16, "bold"),
            bg="#f4f6f7"
        )
        self.result_label.pack()

        self.category_label = tk.Label(
            self.result_frame, text="", font=("Segoe UI", 13),
            bg="#f4f6f7"
        )
        self.category_label.pack()

        # Graph button
        graph_btn = tk.Button(
            self, text="View BMI Trend Graph", font=("Segoe UI", 11),
            bg="#8e44ad", fg="white", activebackground="#6c3483",
            relief="flat", padx=10, pady=6, command=self.on_view_graph
        )
        graph_btn.pack(pady=(25, 5))

        hint = tk.Label(
            self, text="Tip: use the same name each time to build your trend history.",
            font=("Segoe UI", 8, "italic"), bg="#f4f6f7", fg="#7f8c8d"
        )
        hint.pack(pady=(0, 10))

    # -- Event handlers ------------------------------------------------------
    def on_calculate(self):
        name = self.name_entry.get().strip()
        weight_raw = self.weight_entry.get().strip()
        height_raw = self.height_entry.get().strip()

        # ---- Validation ----
        if not name:
            messagebox.showerror("Missing Name", "Please enter a name before calculating.")
            return

        try:
            weight = float(weight_raw)
            height = float(height_raw)
        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Weight and height must be numeric values.\n"
                "Example: weight = 65, height = 1.70"
            )
            return

        if weight <= 0 or height <= 0:
            messagebox.showerror(
                "Invalid Input", "Weight and height must be positive numbers."
            )
            return

        # ---- Calculation ----
        bmi = calculate_bmi(weight, height)
        category, color = classify_bmi(bmi)

        self.result_label.config(text=f"BMI: {bmi:.2f}", fg=color)
        self.category_label.config(text=f"Category: {category}", fg=color)

        # ---- Save to database (with error handling) ----
        try:
            save_record(name, weight, height, round(bmi, 2), category)
        except sqlite3.Error as e:
            messagebox.showwarning(
                "Database Warning",
                f"Result calculated, but could not be saved to history.\n\nDetails: {e}"
            )

    def on_view_graph(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Missing Name", "Enter a name first, then view its trend graph.")
            return

        try:
            history = get_user_history(name)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not read history.\n\nDetails: {e}")
            return

        if len(history) == 0:
            messagebox.showinfo(
                "No History", f"No saved BMI records found for '{name}' yet.\n"
                "Calculate at least one BMI for this name first."
            )
            return

        GraphWindow(self, name, history)


class GraphWindow(tk.Toplevel):
    """A separate window that shows the BMI trend line chart for a user."""

    def __init__(self, parent, user_name, history):
        super().__init__(parent)
        self.title(f"BMI Trend - {user_name}")
        self.geometry("560x420")

        bmis = [row[0] for row in history]
        dates = [row[1].split(" ")[0] for row in history]  # just the date part
        x_vals = list(range(1, len(bmis) + 1))

        fig = Figure(figsize=(5.5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(x_vals, bmis, marker="o", color="#2980b9", linewidth=2)
        ax.set_title(f"BMI Trend for {user_name}")
        ax.set_xlabel("Record #")
        ax.set_ylabel("BMI")
        ax.set_xticks(x_vals)
        ax.grid(True, linestyle="--", alpha=0.5)

        # Reference bands for BMI categories
        ax.axhspan(0, 18.5, color="#3498db", alpha=0.08)
        ax.axhspan(18.5, 25, color="#27ae60", alpha=0.08)
        ax.axhspan(25, 30, color="#e67e22", alpha=0.08)
        ax.axhspan(30, max(40, max(bmis) + 5), color="#e74c3c", alpha=0.08)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        init_db()
    except sqlite3.Error as e:
        print(f"Fatal: could not initialise database: {e}")
        raise SystemExit(1)

    app = BMIApp()
    app.mainloop()
