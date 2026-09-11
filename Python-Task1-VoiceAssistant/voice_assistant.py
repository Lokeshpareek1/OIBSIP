"""
voice_assistant.py — Voice Assistant (Advanced Tier)
Oasis Infobyte SIP - Python Programming Track - Task 1

Features (Beginner, all included):
- Captures voice input via microphone (speech_recognition), with an
  automatic fallback to typed text input if the microphone/pyaudio isn't
  available on this machine (see note below) — the rest of the assistant
  (understanding the command, speaking the response) works identically
  either way.
- Responds to greetings
- Tells the current time and date
- Performs a web search on a spoken/typed topic
- Graceful error handling (asks user to repeat if unclear)
- Text-to-speech feedback for every response (pyttsx3)

Features (Advanced, added on top):
- Simple natural-language intent parsing (looks for key phrases anywhere
  in the sentence, not just exact keyword matching)
- Timed reminder: "remind me in 5 minutes to drink water"
- Live weather lookup via OpenWeatherMap API: "what's the weather in Jodhpur"
- Custom commands loadable from a JSON config file (commands.json)

NOTE ON THE MICROPHONE FALLBACK:
`pyaudio` (required for live microphone capture) does not yet ship
pre-built installers for very new Python releases on Windows, so its
installation can fail with a "failed building wheel" error depending on
your Python version. This assistant detects that automatically at
startup: if the microphone can't be initialised, it falls back to typed
input in the terminal so you can still fully demo every feature. Text-to
-speech output (the assistant talking back to you) does NOT depend on
pyaudio and works either way.

To get real microphone input working, install pyaudio successfully, e.g.:
  pip install pipwin
  pipwin install pyaudio
or use a Python version (3.11/3.12) that has pyaudio wheels available.

SETUP:
  pip install speechrecognition pyttsx3 pyaudio requests
  (pyaudio is optional — the app still runs in text-fallback mode without it)

Run with:  python voice_assistant.py
"""

import datetime
import json
import os
import re
import threading
import webbrowser

import requests

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_LIBRARY_AVAILABLE = True
except ImportError:
    SR_LIBRARY_AVAILABLE = False

API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "YOUR_API_KEY_HERE")
COMMANDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commands.json")


# ---------------------------------------------------------------------------
# TEXT-TO-SPEECH
# ---------------------------------------------------------------------------

class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init() if TTS_AVAILABLE else None

    def say(self, text):
        print(f"Assistant: {text}")
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()


# ---------------------------------------------------------------------------
# INPUT LAYER — tries real microphone first, falls back to typed text
# ---------------------------------------------------------------------------

def try_init_microphone():
    """Attempt to set up a real microphone. Returns (recognizer, mic) or
    (None, None) if unavailable (missing pyaudio, no mic hardware, etc.)."""
    if not SR_LIBRARY_AVAILABLE:
        return None, None
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()  # raises if pyaudio/mic isn't available
        return recognizer, microphone
    except (OSError, AttributeError, NameError, ModuleNotFoundError):
        return None, None


def listen_from_microphone(recognizer, microphone, timeout=6):
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return None
    try:
        return recognizer.recognize_google(audio).lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return "__NETWORK_ERROR__"


def listen_from_keyboard():
    try:
        text = input("You (type your command): ").strip().lower()
    except EOFError:
        return "exit"
    return text if text else None


# ---------------------------------------------------------------------------
# INTENT PARSING (simple NLU — looks for key phrases anywhere in the
# sentence, not just as the very first word).
# ---------------------------------------------------------------------------

def load_custom_commands():
    if os.path.exists(COMMANDS_FILE):
        try:
            with open(COMMANDS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def parse_intent(text, custom_commands=None):
    """Return (intent_name, extracted_data_dict)."""
    custom_commands = custom_commands or {}
    text = text.lower().strip()

    if any(greet in text for greet in ["hello", "hi ", "hey"]) or text in ("hi", "hey"):
        return "greeting", {}

    if "time" in text and "reminder" not in text:
        return "time", {}

    if "date" in text and "reminder" not in text:
        return "date", {}

    search_match = re.search(r"search (?:for )?(.+)", text)
    if search_match:
        return "search", {"query": search_match.group(1).strip()}

    weather_match = re.search(r"weather (?:in|for)?\s*(.+)", text)
    if weather_match:
        return "weather", {"city": weather_match.group(1).strip()}

    reminder_match = re.search(
        r"remind me in (\d+)\s*(second|minute|hour)s? to (.+)", text
    )
    if reminder_match:
        amount, unit, task = reminder_match.groups()
        return "reminder", {"amount": int(amount), "unit": unit, "task": task.strip()}

    for phrase, response in custom_commands.items():
        if phrase.lower() in text:
            return "custom", {"response": response}

    if any(bye in text for bye in ["exit", "quit", "stop", "goodbye"]):
        return "exit", {}

    return "unknown", {}


# ---------------------------------------------------------------------------
# INTENT HANDLERS
# ---------------------------------------------------------------------------

def get_weather_report(city):
    if API_KEY == "YOUR_API_KEY_HERE":
        return "Weather lookup needs an OpenWeatherMap API key. Please set one up first."
    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": API_KEY}, timeout=8
        )
    except requests.exceptions.RequestException:
        return "I couldn't reach the weather service. Check your internet connection."

    if resp.status_code == 404:
        return f"I couldn't find weather data for {city}."
    if resp.status_code != 200:
        return "The weather service returned an error."

    data = resp.json()
    temp_c = data["main"]["temp"] - 273.15
    condition = data["weather"][0]["description"]
    return f"It's currently {temp_c:.1f} degrees Celsius in {city}, with {condition}."


def schedule_reminder(amount, unit, task, speaker):
    seconds = {"second": 1, "minute": 60, "hour": 3600}[unit] * amount

    def fire():
        speaker.say(f"Reminder: {task}")

    timer = threading.Timer(seconds, fire)
    timer.daemon = True
    timer.start()
    return f"Okay, I will remind you to {task} in {amount} {unit}{'s' if amount != 1 else ''}."


def handle_intent(intent, data, speaker):
    if intent == "greeting":
        speaker.say("Hello! How can I help you today?")
    elif intent == "time":
        now = datetime.datetime.now().strftime("%I:%M %p")
        speaker.say(f"The current time is {now}.")
    elif intent == "date":
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speaker.say(f"Today's date is {today}.")
    elif intent == "search":
        query = data["query"]
        speaker.say(f"Searching the web for {query}.")
        webbrowser.open(f"https://www.google.com/search?q={query}")
    elif intent == "weather":
        speaker.say(get_weather_report(data["city"]))
    elif intent == "reminder":
        speaker.say(schedule_reminder(data["amount"], data["unit"], data["task"], speaker))
    elif intent == "custom":
        speaker.say(data["response"])
    elif intent == "exit":
        speaker.say("Goodbye!")
        return False
    else:
        speaker.say("Sorry, I didn't understand that. Could you please repeat?")
    return True


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def main():
    speaker = Speaker()
    custom_commands = load_custom_commands()

    recognizer, microphone = try_init_microphone()
    voice_mode = recognizer is not None

    if voice_mode:
        speaker.say("Voice assistant ready. Say 'hello' to begin, or 'exit' to quit.")
    else:
        print(
            "\n[NOTICE] Microphone input is not available on this system "
            "(pyaudio missing or no mic hardware detected).\n"
            "Falling back to TYPED input — type your commands below.\n"
            "The assistant will still SPEAK its responses out loud.\n"
        )
        speaker.say("Voice assistant ready in typing mode. Type 'hello' to begin, or 'exit' to quit.")

    running = True
    while running:
        if voice_mode:
            text = listen_from_microphone(recognizer, microphone)
            if text is None:
                speaker.say("I didn't catch that. Could you please repeat?")
                continue
            if text == "__NETWORK_ERROR__":
                speaker.say("I'm having trouble reaching the speech recognition service.")
                continue
        else:
            text = listen_from_keyboard()
            if text is None:
                continue

        print(f"You said: {text}")
        intent, data = parse_intent(text, custom_commands)
        running = handle_intent(intent, data, speaker)


if __name__ == "__main__":
    main()
