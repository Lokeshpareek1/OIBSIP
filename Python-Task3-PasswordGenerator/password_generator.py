"""
password_generator.py — Random Password Generator (Advanced Tier)
Oasis Infobyte SIP - Python Programming Track - Task 3

Features:
- GUI (tkinter) with length slider and character-type checkboxes
- Uses `secrets` (cryptographically secure) instead of `random`
- Password strength indicator (Weak / Medium / Strong)
- Guarantees at least one character from each selected type
- "Copy to Clipboard" button
- Option to exclude ambiguous characters (0, O, l, 1)
- Session-only generation history (last 5), never written to disk
"""

import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string


AMBIGUOUS = set("0Ol1I")


def generate_password(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous):
    pools = []
    guaranteed = []

    def clean(pool):
        return "".join(c for c in pool if c not in AMBIGUOUS) if exclude_ambiguous else pool

    if use_upper:
        pool = clean(string.ascii_uppercase)
        pools.append(pool)
        guaranteed.append(secrets.choice(pool))
    if use_lower:
        pool = clean(string.ascii_lowercase)
        pools.append(pool)
        guaranteed.append(secrets.choice(pool))
    if use_digits:
        pool = clean(string.digits)
        pools.append(pool)
        guaranteed.append(secrets.choice(pool))
    if use_symbols:
        pool = "!@#$%^&*()-_=+[]{}"
        pools.append(pool)
        guaranteed.append(secrets.choice(pool))

    if not pools:
        raise ValueError("Select at least one character type.")
    if length < len(guaranteed):
        raise ValueError(f"Length must be at least {len(guaranteed)} for the selected types.")

    all_chars = "".join(pools)
    remaining = length - len(guaranteed)
    body = [secrets.choice(all_chars) for _ in range(remaining)]

    password_chars = guaranteed + body
    # shuffle securely so guaranteed chars aren't always at the start
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    return "".join(password_chars)


def rate_strength(password, type_count):
    length = len(password)
    score = 0
    score += 1 if length >= 8 else 0
    score += 1 if length >= 12 else 0
    score += 1 if type_count >= 3 else 0
    score += 1 if type_count == 4 else 0

    if score <= 1:
        return "Weak", "#e74c3c"
    elif score <= 2:
        return "Medium", "#e67e22"
    else:
        return "Strong", "#27ae60"


class PasswordGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator - Oasis Infobyte SIP")
        self.geometry("460x560")
        self.configure(bg="#f4f6f7")
        self.history = []  # session-only, last 5

        self._build_widgets()

    def _build_widgets(self):
        tk.Label(
            self, text="Random Password Generator", font=("Segoe UI", 18, "bold"),
            bg="#f4f6f7", fg="#2c3e50"
        ).pack(pady=(20, 15))

        # Length
        length_frame = tk.Frame(self, bg="#f4f6f7")
        length_frame.pack(pady=5, fill="x", padx=30)
        tk.Label(length_frame, text="Length:", bg="#f4f6f7", font=("Segoe UI", 11)).pack(side="left")
        self.length_var = tk.IntVar(value=12)
        self.length_label = tk.Label(length_frame, text="12", bg="#f4f6f7", font=("Segoe UI", 11, "bold"))
        self.length_label.pack(side="right")
        self.length_slider = tk.Scale(
            self, from_=8, to=32, orient="horizontal", variable=self.length_var,
            bg="#f4f6f7", highlightthickness=0, command=self._update_length_label
        )
        self.length_slider.pack(fill="x", padx=30)

        # Checkboxes
        opts_frame = tk.Frame(self, bg="#f4f6f7")
        opts_frame.pack(pady=15)

        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)

        tk.Checkbutton(opts_frame, text="Uppercase (A-Z)", variable=self.use_upper,
                       bg="#f4f6f7", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        tk.Checkbutton(opts_frame, text="Lowercase (a-z)", variable=self.use_lower,
                       bg="#f4f6f7", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        tk.Checkbutton(opts_frame, text="Digits (0-9)", variable=self.use_digits,
                       bg="#f4f6f7", font=("Segoe UI", 10)).grid(row=0, column=1, sticky="w", padx=10, pady=4)
        tk.Checkbutton(opts_frame, text="Symbols (!@#$)", variable=self.use_symbols,
                       bg="#f4f6f7", font=("Segoe UI", 10)).grid(row=1, column=1, sticky="w", padx=10, pady=4)
        tk.Checkbutton(opts_frame, text="Exclude ambiguous characters (0, O, l, 1)",
                       variable=self.exclude_ambiguous, bg="#f4f6f7", font=("Segoe UI", 9)
                       ).grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 4))

        # Generate button
        tk.Button(
            self, text="Generate Password", font=("Segoe UI", 12, "bold"),
            bg="#2980b9", fg="white", relief="flat", padx=10, pady=8,
            command=self.on_generate
        ).pack(pady=15)

        # Result
        result_frame = tk.Frame(self, bg="#ffffff", relief="solid", bd=1)
        result_frame.pack(padx=30, fill="x")
        self.result_var = tk.StringVar(value="Click Generate to create a password")
        tk.Entry(
            result_frame, textvariable=self.result_var, font=("Consolas", 14),
            justify="center", state="readonly", relief="flat", bd=8
        ).pack(fill="x")

        self.strength_label = tk.Label(self, text="", font=("Segoe UI", 11, "bold"), bg="#f4f6f7")
        self.strength_label.pack(pady=8)

        tk.Button(
            self, text="Copy to Clipboard", font=("Segoe UI", 10, "bold"),
            bg="#27ae60", fg="white", relief="flat", padx=10, pady=6,
            command=self.on_copy
        ).pack(pady=5)

        # History
        tk.Label(self, text="Recent Passwords (this session only):", bg="#f4f6f7",
                 font=("Segoe UI", 9, "italic"), fg="#7f8c8d").pack(pady=(20, 2))
        self.history_box = tk.Listbox(self, height=5, font=("Consolas", 10))
        self.history_box.pack(padx=30, fill="x")

    def _update_length_label(self, value):
        self.length_label.config(text=str(value))

    def on_generate(self):
        type_count = sum([
            self.use_upper.get(), self.use_lower.get(),
            self.use_digits.get(), self.use_symbols.get()
        ])
        try:
            password = generate_password(
                self.length_var.get(),
                self.use_upper.get(), self.use_lower.get(),
                self.use_digits.get(), self.use_symbols.get(),
                self.exclude_ambiguous.get(),
            )
        except ValueError as e:
            messagebox.showerror("Invalid Selection", str(e))
            return

        self.result_var.set(password)
        strength, color = rate_strength(password, type_count)
        self.strength_label.config(text=f"Strength: {strength}", fg=color)

        self.history.insert(0, password)
        self.history = self.history[:5]
        self.history_box.delete(0, tk.END)
        for pw in self.history:
            self.history_box.insert(tk.END, pw)

    def on_copy(self):
        password = self.result_var.get()
        if not password or password == "Click Generate to create a password":
            messagebox.showwarning("Nothing to Copy", "Generate a password first.")
            return
        self.clipboard_clear()
        self.clipboard_append(password)
        messagebox.showinfo("Copied", "Password copied to clipboard!")


if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()
