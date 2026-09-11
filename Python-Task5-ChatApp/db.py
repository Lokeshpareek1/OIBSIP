"""
db.py — Shared database layer for the Chat Application.

Uses SQLite (chat_app.db) to store:
  1. Registered users (username + a hashed password)
  2. Message history per chat room

IMPORTANT SECURITY NOTE (documented again in README.md):
Passwords are hashed with PBKDF2-HMAC-SHA256 + a random per-user salt before
being stored, so plaintext passwords are never written to disk. However,
CHAT MESSAGES THEMSELVES ARE STORED IN PLAIN TEXT and are NOT encrypted in
transit (the socket connection is plain TCP, not TLS). This project is a
learning exercise, not a production-secure messenger — see README.md.
"""

import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_app.db")


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            sender TEXT NOT NULL,
            text TEXT NOT NULL,
            sent_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Password hashing (PBKDF2 - part of Python's stdlib `hashlib`, no external
# dependency needed, unlike bcrypt).
# ---------------------------------------------------------------------------

def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
    ).hex()


def register_user(username, password):
    """Returns (success: bool, message: str)."""
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        conn.close()
        return False, "That username is already taken."

    salt = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)
    cur.execute(
        "INSERT INTO users (username, salt, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (username, salt, pw_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()
    return True, "Registration successful."


def verify_login(username, password):
    """Returns (success: bool, message: str)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT salt, password_hash FROM users WHERE username = ?", (username.strip(),))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False, "Invalid username or password."

    computed = _hash_password(password, row["salt"])
    if computed == row["password_hash"]:
        return True, "Login successful."
    return False, "Invalid username or password."


# ---------------------------------------------------------------------------
# Message history
# ---------------------------------------------------------------------------

def save_message(room, sender, text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (room, sender, text, sent_at) VALUES (?, ?, ?, ?)",
        (room, sender, text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_room_history(room, limit=50):
    """Return the last `limit` messages for a room, oldest first."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT sender, text, sent_at FROM messages
        WHERE room = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (room, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return list(reversed(rows))  # oldest first


def get_known_rooms():
    """Rooms that already have at least one message, for convenience."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT room FROM messages ORDER BY room ASC")
    rooms = [r["room"] for r in cur.fetchall()]
    conn.close()
    return rooms
