# Voice Assistant (Advanced) — Oasis Infobyte SIP

**Track:** Python Programming
**Task:** Task 1 — Voice Assistant (Advanced Tier)

## Objective
A Python voice assistant that listens to spoken commands via microphone
and responds using text-to-speech, with simple natural-language
understanding, reminders, and live weather lookups.

## Tech Stack
- Python 3
- `speech_recognition` — captures and converts microphone audio to text
- `pyttsx3` — text-to-speech responses
- `requests` — OpenWeatherMap API calls
- `pyaudio` — required by `speech_recognition` for microphone access (optional — see fallback below)

## ⚠️ Important: Microphone Fallback Mode
`pyaudio` does not always have a pre-built installer available for the
newest Python versions on Windows, so `pip install pyaudio` can fail with
a "failed building wheel" error depending on your Python version.

**This app handles that automatically:** at startup it tries to initialise
a real microphone. If that fails (pyaudio missing, or no mic hardware), it
automatically falls back to **typed input** in the terminal — you type your
command instead of speaking it. Every other feature (understanding the
command, spoken responses via text-to-speech, reminders, weather, custom
commands) works identically in both modes.

To get real microphone input working:
```
pip install pipwin
pipwin install pyaudio
```
Or use a Python version (3.11/3.12) that has pre-built pyaudio wheels
available if your installed version is very new.

## Setup
```
pip install speechrecognition pyttsx3 requests
pip install pyaudio   # optional — falls back to typed input if this fails
```

### Weather feature (optional)
To use the weather command, get a free API key at
https://openweathermap.org/api and set it before running:
```
# Windows PowerShell
$env:OPENWEATHERMAP_API_KEY = "your_key_here"
```
Without a key, every other feature still works — only the weather command
will politely say it isn't configured.

## Features
**Beginner (all included):**
- Captures voice input via microphone (or typed input as an automatic fallback)
- Responds to greetings ("hello", "hi", "hey")
- Tells the current time and date
- Performs a web search on a spoken/typed topic (opens the default browser)
- Graceful error handling — asks the user to repeat if unclear
- Text-to-speech feedback for every response

**Advanced (added on top):**
- Simple intent parsing — recognizes phrases anywhere in a sentence
  (e.g. "hey can you tell me the time" still triggers the time intent)
- Timed reminders: say/type *"remind me in 5 minutes to drink water"*
- Live weather lookup via OpenWeatherMap: *"what's the weather in Jodhpur"*
- Custom commands loaded from `commands.json`

## How to Run
```
python voice_assistant.py
```
If a working microphone is detected, speak your commands. Otherwise, type
them when prompted. Say/type "exit", "quit", or "goodbye" to stop.

## Example Commands
| You say/type | Assistant does |
|---|---|
| "Hello" | Greets you back |
| "What's the time?" | Speaks the current time |
| "What's today's date?" | Speaks the current date |
| "Search for python tutorials" | Opens a Google search in your browser |
| "What's the weather in Jodhpur?" | Speaks the current temperature and condition |
| "Remind me in 2 minutes to call mom" | Speaks a reminder after 2 minutes |
| "Play music" (from commands.json) | Speaks the configured custom response |

## 🔒 Privacy Note
- Microphone audio (when available) is sent to Google's speech recognition
  service to be converted to text — this is the only third-party data
  transfer for voice input.
- If you use the weather command, only the **city name** is sent to the
  OpenWeatherMap API — no audio or personal data.
- No conversation audio or transcripts are stored to disk by this app.

## Project Structure (for GitHub)
```
OIBSIP/Python-Task1-VoiceAssistant/
├── voice_assistant.py
├── commands.json
└── README.md
```

## Author
Lokesh Pareek — Python Programming Intern, Oasis Infobyte
