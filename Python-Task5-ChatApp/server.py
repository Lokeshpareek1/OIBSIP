"""
server.py — Chat Application Server (Advanced Tier)

Handles multiple simultaneous clients using Python's socket + threading
modules. Each connected client is served on its own thread.

Simple line-delimited JSON protocol is used over TCP:
  Each message is one JSON object followed by a newline ("\\n").

Client -> Server actions:
  {"action": "register", "username": ..., "password": ...}
  {"action": "login",    "username": ..., "password": ...}
  {"action": "join",     "room": ...}
  {"action": "message",  "text": ...}

Server -> Client responses:
  {"type": "auth_result", "success": bool, "message": ...}
  {"type": "history", "messages": [ {sender, text, sent_at}, ... ]}
  {"type": "message", "sender": ..., "text": ..., "sent_at": ...}
  {"type": "system",  "text": ...}
  {"type": "error",   "text": ...}

Run with:  python server.py
"""

import socket
import threading
import json
import sys

import db

HOST = "0.0.0.0"
PORT = 5050

# room_name -> list of (conn, username)
rooms_lock = threading.Lock()
rooms = {}


def send_json(conn, payload):
    try:
        conn.sendall((json.dumps(payload) + "\n").encode("utf-8"))
    except OSError:
        pass  # client already disconnected


def broadcast(room, payload, exclude_conn=None):
    with rooms_lock:
        members = rooms.get(room, [])
        for conn, _uname in members:
            if conn is not exclude_conn:
                send_json(conn, payload)


def remove_client(conn):
    with rooms_lock:
        for room, members in rooms.items():
            rooms[room] = [(c, u) for (c, u) in members if c is not conn]


def handle_client(conn, addr):
    username = None
    current_room = None
    buffer = ""

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buffer += data.decode("utf-8")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    send_json(conn, {"type": "error", "text": "Malformed message."})
                    continue

                action = msg.get("action")

                # ---- REGISTER ----
                if action == "register":
                    success, text = db.register_user(msg.get("username", ""), msg.get("password", ""))
                    send_json(conn, {"type": "auth_result", "success": success, "message": text})

                # ---- LOGIN ----
                elif action == "login":
                    success, text = db.verify_login(msg.get("username", ""), msg.get("password", ""))
                    if success:
                        username = msg.get("username", "").strip()
                    send_json(conn, {"type": "auth_result", "success": success, "message": text})

                # ---- JOIN ROOM ----
                elif action == "join":
                    if not username:
                        send_json(conn, {"type": "error", "text": "You must log in first."})
                        continue

                    room = msg.get("room", "").strip()
                    if not room:
                        send_json(conn, {"type": "error", "text": "Room name cannot be empty."})
                        continue

                    # leave old room, join new one
                    with rooms_lock:
                        if current_room and current_room in rooms:
                            rooms[current_room] = [
                                (c, u) for (c, u) in rooms[current_room] if c is not conn
                            ]
                        rooms.setdefault(room, []).append((conn, username))
                    current_room = room

                    # send history for this room
                    history_rows = db.get_room_history(room, limit=50)
                    history_payload = [
                        {"sender": r["sender"], "text": r["text"], "sent_at": r["sent_at"]}
                        for r in history_rows
                    ]
                    send_json(conn, {"type": "history", "messages": history_payload})

                    broadcast(
                        room,
                        {"type": "system", "text": f"{username} joined the room."},
                        exclude_conn=conn,
                    )

                # ---- SEND MESSAGE ----
                elif action == "message":
                    if not username or not current_room:
                        send_json(conn, {"type": "error", "text": "Join a room before sending messages."})
                        continue

                    text = msg.get("text", "").strip()
                    if not text:
                        continue

                    db.save_message(current_room, username, text)
                    from datetime import datetime
                    payload = {
                        "type": "message",
                        "sender": username,
                        "text": text,
                        "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    broadcast(current_room, payload)

                else:
                    send_json(conn, {"type": "error", "text": f"Unknown action: {action}"})

    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        remove_client(conn)
        if username and current_room:
            broadcast(current_room, {"type": "system", "text": f"{username} disconnected."})
        conn.close()
        print(f"[DISCONNECTED] {addr}")


def main():
    db.init_db()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((HOST, PORT))
    except OSError as e:
        print(f"Could not bind to {HOST}:{PORT} -> {e}")
        sys.exit(1)

    server_socket.listen()
    print(f"[LISTENING] Chat server running on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"[CONNECTED] {addr}")
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\n[SHUTTING DOWN] Server stopped.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
