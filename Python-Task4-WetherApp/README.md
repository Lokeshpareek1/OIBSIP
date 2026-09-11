# Basic Weather App (Advanced) — Oasis Infobyte SIP

**Track:** Python Programming
**Task:** Task 4 — Basic Weather App (Advanced Tier)

## Objective
A GUI application that fetches and displays real-time weather data for a
user-specified city using the OpenWeatherMap API, with hourly/daily
forecasts and a unit toggle.

## Tech Stack
- Python 3
- `tkinter` — GUI
- `requests` — API calls
- OpenWeatherMap API (free tier)

## ⚠️ Setup Required — API Key
1. Create a free account at https://openweathermap.org/api and generate an
   API key.
2. Either:
   - Open `weather_app.py` and replace `YOUR_API_KEY_HERE` with your key, **or**
   - Set an environment variable before running (safer — keeps the key out
     of your code):
     ```
     # Windows PowerShell
     $env:OPENWEATHERMAP_API_KEY = "your_key_here"
     python weather_app.py
     ```

## Features
- City input field + **Get Weather** button
- Displays current temperature, humidity, weather condition, and wind speed
- **Hourly forecast panel** — next 6 time-steps
- **Daily forecast panel** — next 5 days (midday snapshot each day)
- **°C / °F toggle** checkbox — instantly re-renders all displayed values
- All errors (city not found, invalid API key, network issue) are shown
  **inside the GUI**, never as a crash or terminal-only message

## How to Run
```
pip install requests
python weather_app.py
```
Enter a city name (e.g. "Jodhpur") and click **Get Weather**.

## Project Structure (for GitHub)
```
OIBSIP/Python-Task4-WeatherApp/
├── weather_app.py
└── README.md
```

## Author
Lokesh Pareek — Python Programming Intern, Oasis Infobyte
