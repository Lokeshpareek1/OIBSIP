import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox

HOST = "127.0.0.1"
PORT = 5050

# A small emoji shortcode dictionary -- typed as :code: and rendered as the
# matching Unicode character before the message is sent/displayed.
EMOJI_MAP = {
    ":smile:": "😄",
    ":laugh:": "😂",
    ":sad:": "😢",
    ":heart:": "❤️",
    ":thumbsup:": "👍",
    ":thumbsdown:": "👎",
    ":fire:": "🔥",
    ":clap:": "👏",
    ":wave:": "👋",
    ":thinking:": "🤔",
    ":party:": "🎉",
    ":ok:": "👌",
}


def render_emojis(text):
    for code, emoji in EMOJI_MAP.items():
        text = text.replace(code, emoji)
    return text


class ChatClient:
    """Thin networking wrapper around a TCP socket to the chat server."""

    def __init__(self, on_message):
        self.sock = None
        self.buffer = ""
        self.on_message = on_message  # callback(payload_dict)
        self.connected = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.connected = True
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        while self.connected:
            try:
                data = self.sock.recv(4096)
            except OSError:
                break
            if not data:
                break
            self.buffer += data.decode("utf-8")
            while "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self.on_message(payload)

    def send(self, payload):
        if self.sock:
            try:
                self.sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            except OSError:
                pass

    def close(self):
        self.connected = False
        if self.sock:
            self.sock.close()


class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat Application - Login")
        self.geometry("420x360")
        self.configure(bg="#f4f6f7")

        self.username = None
        self.current_room = None
        self.window_focused = True

        self.client = ChatClient(self.handle_server_message)

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

        self._build_login_screen()

    # -----------------------------------------------------------------
    # LOGIN / REGISTER SCREEN
    # -----------------------------------------------------------------
    def _build_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(
            self, text="Chat Application", font=("Segoe UI", 18, "bold"),
            bg="#f4f6f7", fg="#2c3e50"
        ).pack(pady=(30, 15))

        form = tk.Frame(self, bg="#f4f6f7")
        form.pack(pady=5)

        tk.Label(form, text="Username:", bg="#f4f6f7", font=("Segoe UI", 11)).grid(
            row=0, column=0, sticky="w", padx=8, pady=8
        )
        self.username_entry = ttk.Entry(form, width=25)
        self.username_entry.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(form, text="Password:", bg="#f4f6f7", font=("Segoe UI", 11)).grid(
            row=1, column=0, sticky="w", padx=8, pady=8
        )
        self.password_entry = ttk.Entry(form, width=25, show="*")
        self.password_entry.grid(row=1, column=1, padx=8, pady=8)

        btn_frame = tk.Frame(self, bg="#f4f6f7")
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame, text="Login", font=("Segoe UI", 11, "bold"),
            bg="#2980b9", fg="white", relief="flat", padx=20, pady=6,
            command=self.on_login
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            btn_frame, text="Register", font=("Segoe UI", 11, "bold"),
            bg="#27ae60", fg="white", relief="flat", padx=15, pady=6,
            command=self.on_register
        ).grid(row=0, column=1, padx=8)

        self.status_label = tk.Label(self, text="", bg="#f4f6f7", fg="#c0392b", font=("Segoe UI", 9))
        self.status_label.pack(pady=5)

        note = tk.Label(
            self, text="Note: messages are stored as plain text (not encrypted).\n"
                       "See README.md for details.",
            bg="#f4f6f7", fg="#7f8c8d", font=("Segoe UI", 8, "italic"), justify="center"
        )
        note.pack(side="bottom", pady=10)

        if not self.client.connected:
            try:
                self.client.connect()
            except OSError as e:
                self.status_label.config(text=f"Cannot reach server: {e}")

    def on_register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            self.status_label.config(text="Enter a username and password first.")
            return
        self._pending_action = "register"
        self.client.send({"action": "register", "username": username, "password": password})

    def on_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            self.status_label.config(text="Enter a username and password first.")
            return
        self._pending_action = "login"
        self._pending_username = username
        self.client.send({"action": "login", "username": username, "password": password})

    # -----------------------------------------------------------------
    # ROOM SELECTION SCREEN
    # -----------------------------------------------------------------
    def _build_room_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.title(f"Chat Application - {self.username}")
        self.geometry("420x260")

        tk.Label(
            self, text=f"Welcome, {self.username}!", font=("Segoe UI", 16, "bold"),
            bg="#f4f6f7", fg="#2c3e50"
        ).pack(pady=(30, 10))

        tk.Label(self, text="Enter a room name to join or create:", bg="#f4f6f7").pack(pady=5)

        self.room_entry = ttk.Entry(self, width=25)
        self.room_entry.pack(pady=5)
        self.room_entry.insert(0, "general")

        tk.Button(
            self, text="Join Room", font=("Segoe UI", 11, "bold"),
            bg="#2980b9", fg="white", relief="flat", padx=20, pady=6,
            command=self.on_join_room
        ).pack(pady=15)

    def on_join_room(self):
        room = self.room_entry.get().strip()
        if not room:
            messagebox.showerror("Missing Room", "Please enter a room name.")
            return
        self.current_room = room
        self.client.send({"action": "join", "room": room})
        self._build_chat_screen()

    # -----------------------------------------------------------------
    # CHAT SCREEN
    # -----------------------------------------------------------------
    def _build_chat_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.title(f"Chat - #{self.current_room} - {self.username}")
        self.geometry("520x520")

        header = tk.Label(
            self, text=f"#{self.current_room}", font=("Segoe UI", 14, "bold"),
            bg="#2c3e50", fg="white", pady=8
        )
        header.pack(fill="x")

        self.messages_box = tk.Text(
            self, state="disabled", wrap="word", bg="white", font=("Segoe UI", 10)
        )
        self.messages_box.pack(fill="both", expand=True, padx=8, pady=8)
        self.messages_box.tag_config("self_msg", foreground="#2980b9")
        self.messages_box.tag_config("other_msg", foreground="#2c3e50")
        self.messages_box.tag_config("system_msg", foreground="#7f8c8d", font=("Segoe UI", 9, "italic"))

        bottom = tk.Frame(self, bg="#f4f6f7")
        bottom.pack(fill="x", padx=8, pady=(0, 8))

        self.message_entry = ttk.Entry(bottom, font=("Segoe UI", 11))
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.message_entry.bind("<Return>", lambda e: self.on_send_message())

        tk.Button(
            bottom, text="Send", font=("Segoe UI", 10, "bold"),
            bg="#2980b9", fg="white", relief="flat", padx=15,
            command=self.on_send_message
        ).pack(side="right")

        hint = tk.Label(
            self, text="Emoji shortcuts: :smile: :laugh: :sad: :heart: :thumbsup: :fire: :clap: :wave:",
            bg="#f4f6f7", fg="#7f8c8d", font=("Segoe UI", 8)
        )
        hint.pack(pady=(0, 6))

    def on_send_message(self):
        text = self.message_entry.get().strip()
        if not text:
            return
        text = render_emojis(text)
        self.client.send({"action": "message", "text": text})
        self.message_entry.delete(0, tk.END)

    def _append_message(self, sender, text, sent_at, tag):
        self.messages_box.config(state="normal")
        time_part = sent_at.split(" ")[1] if " " in sent_at else sent_at
        if tag == "system_msg":
            self.messages_box.insert("end", f"[{time_part}] {text}\n", tag)
        else:
            self.messages_box.insert("end", f"[{time_part}] {sender}: {render_emojis(text)}\n", tag)
        self.messages_box.see("end")
        self.messages_box.config(state="disabled")

    # -----------------------------------------------------------------
    # WINDOW FOCUS TRACKING (for notifications)
    # -----------------------------------------------------------------
    def _on_focus_in(self, event):
        self.window_focused = True
        if self.username and self.current_room:
            self.title(f"Chat - #{self.current_room} - {self.username}")

    def _on_focus_out(self, event):
        self.window_focused = False

    def _notify_new_message(self):
        if not self.window_focused and self.current_room:
            self.title(f"* New message * - #{self.current_room}")
            self.bell()

    # -----------------------------------------------------------------
    # SERVER MESSAGE HANDLER (runs on the network thread -> must marshal
    # back onto the tkinter main thread using `after`)
    # -----------------------------------------------------------------
    def handle_server_message(self, payload):
        self.after(0, self._process_server_message, payload)

    def _process_server_message(self, payload):
        msg_type = payload.get("type")

        if msg_type == "auth_result":
            success = payload.get("success")
            text = payload.get("message", "")
            if success and getattr(self, "_pending_action", None) == "login":
                self.username = self._pending_username
                self._build_room_screen()
            elif success and getattr(self, "_pending_action", None) == "register":
                self.status_label.config(fg="#27ae60", text=text + " You can now log in.")
            else:
                self.status_label.config(fg="#c0392b", text=text)

        elif msg_type == "history":
            for m in payload.get("messages", []):
                tag = "self_msg" if m["sender"] == self.username else "other_msg"
                self._append_message(m["sender"], m["text"], m["sent_at"], tag)

        elif msg_type == "message":
            tag = "self_msg" if payload.get("sender") == self.username else "other_msg"
            self._append_message(payload.get("sender"), payload.get("text"), payload.get("sent_at"), tag)
            if payload.get("sender") != self.username:
                self._notify_new_message()

        elif msg_type == "system":
            self._append_message(None, payload.get("text", ""), "", "system_msg")

        elif msg_type == "error":
            messagebox.showerror("Server Error", payload.get("text", "Unknown error"))

    def on_close(self):
        self.client.close()
        self.destroy()


if __name__ == "__main__":
    app = ChatApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
