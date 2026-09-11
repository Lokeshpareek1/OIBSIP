# BMI Calculator (Advanced) — Oasis Infobyte SIP

**Track:** Python Programming
**Task:** Task 2 — BMI Calculator (Advanced Tier)

## Objective
A desktop application that calculates a user's Body Mass Index (BMI) from
their weight and height, classifies it into a standard health category, and
keeps a per-user history so trends can be viewed over time.

## Tech Stack
- Python 3
- `tkinter` — GUI window, input fields, and the "Calculate" button
- `sqlite3` — local database for storing historical BMI records
- `matplotlib` — line chart of a user's BMI trend over time

## Features
- GUI window with **Name**, **Weight (kg)**, and **Height (m)** input fields
  and a **Calculate BMI** button (no command line needed)
- Result shown directly in the GUI with **color-coded feedback**:
  - Blue = Underweight (BMI < 18.5)
  - Green = Normal (18.5 – 24.9)
  - Orange = Overweight (25 – 29.9)
  - Red = Obese (≥ 30)
- **Multi-user support** — records are saved per entered name, so multiple
  people can use the same app and keep separate histories
- **Historical records** stored in an SQLite database (`bmi_records.db`,
  created automatically on first run)
- **Graph view** — a "View BMI Trend Graph" button opens a line chart of a
  user's BMI over all their past entries, with colored bands showing the
  BMI category ranges
- **Input validation** — rejects empty names, non-numeric input, and
  negative/zero values with a clear popup message
- **Error handling** for database read/write failures (shown as a warning
  popup instead of crashing)

## How to Run
1. Make sure Python 3 is installed (tkinter ships with most standard
   installs; on Linux you may need `sudo apt install python3-tk`)
2. Install matplotlib if not already present:
   ```
   pip install matplotlib
   ```
3. Run the app:
   ```
   python bmi_calculator.py
   ```
4. Enter a name, weight, and height, then click **Calculate BMI**.
5. Use the same name across sessions to build up trend history, then click
   **View BMI Trend Graph** to see it plotted.

## How SQLite Is Used
SQLite is a lightweight, file-based database — no separate server process is
needed. On first run, `init_db()` creates a `bmi_records.db` file in the
project folder with one table:

| Column       | Type    | Description                          |
|--------------|---------|---------------------------------------|
| id           | INTEGER | Auto-incrementing primary key         |
| user_name    | TEXT    | Name entered in the GUI               |
| weight       | REAL    | Weight in kg                          |
| height       | REAL    | Height in m                           |
| bmi          | REAL    | Calculated BMI                        |
| category     | TEXT    | Underweight / Normal / Overweight / Obese |
| recorded_at  | TEXT    | Timestamp of the calculation          |

Every time **Calculate BMI** succeeds, a new row is inserted. The trend
graph reads all rows for the entered name, ordered by time, and plots BMI
against the record number.

## BMI Formula
```
BMI = weight (kg) / height (m)²
```

## Project Structure
```
OIBSIP/Python-Task2-BMICalculator/
├── bmi_calculator.py   # Main application (GUI + database + graph)
├── README.md           # This file
└── bmi_records.db      # Created automatically on first run (not committed)
```

## Author
Lokesh Pareek — Python Programming Intern, Oasis Infobyte
