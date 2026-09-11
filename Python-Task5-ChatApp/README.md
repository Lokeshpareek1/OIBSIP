# Chat Application (Advanced) — Oasis Infobyte SIP

**Track:** Python Programming
**Task:** Task 5 — Chat Application (Advanced Tier)

## Objective
A real-time messaging application with a GUI chat window, user
registration/login, multiple named chat rooms, and message history.

## Tech Stack
- Python 3
- `socket` + `threading` — client/server networking
- `tkinter` — GUI login screen, room screen, and chat window
- `sqlite3` — stores users and message history
- `hashlib` (PBKDF2) — password hashing

## Files
| File          | Purpose                                                        |
|---------------|------------------------------------------------------------------|
| `db.py`       | Shared database layer (users + message history)                |
| `server.py`   | TCP server — accepts connections, manages rooms, broadcasts     |
| `client.py`   | tkinter GUI client — login, room selection, chat window          |

## Features
- **User registration & login** — usernames + passwords stored in SQLite,
  passwords hashed with PBKDF2-HMAC-SHA256 + a random per-user salt (never
  stored in plain text)
- **Multiple chat rooms** — users can create or join any named room
- **Message history** — the last 50 messages in a room are loaded
  automatically when a user joins
- **In-app notification** — the window title changes to `* New message *`
  and the system bell rings when a message arrives while the window isn't
  focused
- **Emoji shortcode support** — typing `:smile:`, `:heart:`, `:fire:`, etc.
  renders the matching Unicode emoji
- **Multi-client support** — the server handles many simultaneous clients
  using a thread per connection

## How to Run
1. Make sure Python 3 is installed (tkinter ships with most standard
   installs; on Linux you may need `sudo apt install python3-tk`)
2. Start the server first (keep this terminal open):
   ```
   python server.py
   ```
3. In a **new terminal**, start a client:
   ```
   python client.py
   ```
4. Repeat step 3 in another terminal to simulate a second user.
5. In each client window: **Register** a username/password, then **Login**,
   then enter a room name (e.g. `general`) and click **Join Room**.
6. Type messages and press Enter or click **Send** — they appear instantly
   in every client that has joined the same room.

## ⚠️ Security Transparency (End-to-End Awareness)
This project is a **learning exercise**, not a production-secure messenger.
Please note:
- **Passwords** are hashed (PBKDF2-HMAC-SHA256, 100,000 iterations, unique
  salt per user) before being stored — plaintext passwords are never written
  to disk.
- **Chat messages are stored as plain text** in the SQLite database
  (`chat_app.db`). They are **not encrypted at rest**.
- **The network connection is plain TCP, not TLS/SSL.** Messages are sent
  as readable JSON over the socket and could be intercepted by anyone who
  can observe the network traffic (e.g. on the same Wi-Fi).
- This app is intended to run on `localhost` / a trusted local network for
  learning purposes — it should **not** be used to send sensitive
  information or exposed directly to the public internet.

## Protocol (for reference)
Client and server exchange newline-delimited JSON objects over the socket.

```
Client -> Server:
  {"action": "register", "username": "...", "password": "..."}
  {"action": "login",    "username": "...", "password": "..."}
  {"action": "join",     "room": "general"}
  {"action": "message",  "text": "Hello!"}

Server -> Client:
  {"type": "auth_result", "success": true, "message": "..."}
  {"type": "history", "messages": [...]}
  {"type": "message", "sender": "...", "text": "...", "sent_at": "..."}
  {"type": "system",  "text": "alice joined the room."}
  {"type": "error",   "text": "..."}
```

## Project Structure (for GitHub submission)
```
OIBSIP/Python-Task5-ChatApp/
├── db.py
├── server.py
├── client.py
├── README.md
└── chat_app.db     # created automatically on first run (not committed)
```

## Author
Lokesh Pareek — Python Programming Intern, Oasis Infobyte
