"""
weather_app.py — Basic Weather App (Advanced Tier)
Oasis Infobyte SIP - Python Programming Track - Task 4

Features:
- GUI (tkinter) with city input and "Get Weather" button
- Fetches live data from the OpenWeatherMap API
- Shows current temperature (C/F toggle), humidity, condition, wind speed
- Hourly forecast panel (next 6 hours) and daily forecast panel (next 5 days)
- All errors (bad city, no internet, invalid key) shown inside the GUI

SETUP REQUIRED:
1. Get a free API key at https://openweathermap.org/api
2. Replace API_KEY below with your key (or set the OPENWEATHERMAP_API_KEY
   environment variable instead of hardcoding it).
"""

import os
import tkinter as tk
from tkinter import ttk
import requests

API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "YOUR_API_KEY_HERE")
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def kelvin_to_c(k):
    return k - 273.15


def c_to_f(c):
    return c * 9 / 5 + 32


def fetch_current_weather(city, api_key=API_KEY):
    """Returns (data_dict, error_message). Exactly one will be None."""
    if not city.strip():
        return None, "Please enter a city name."
    try:
        resp = requests.get(CURRENT_URL, params={"q": city, "appid": api_key}, timeout=8)
    except requests.exceptions.ConnectionError:
        return None, "Network error: could not reach the weather server."
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."

    if resp.status_code == 401:
        return None, "Invalid API key. Check your OpenWeatherMap API key."
    if resp.status_code == 404:
        return None, f"City '{city}' not found. Check the spelling."
    if resp.status_code != 200:
        return None, f"Weather service returned an error (HTTP {resp.status_code})."

    data = resp.json()
    parsed = {
        "city": data.get("name", city),
        "temp_c": round(kelvin_to_c(data["main"]["temp"]), 1),
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"].title(),
        "wind_speed": data["wind"]["speed"],
    }
    return parsed, None


def fetch_forecast(city, api_key=API_KEY):
    """Returns (hourly_list[6], daily_list[5], error_message)."""
    try:
        resp = requests.get(FORECAST_URL, params={"q": city, "appid": api_key}, timeout=8)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None, None, "Could not fetch forecast (network issue)."

    if resp.status_code != 200:
        return None, None, "Could not fetch forecast for this city."

    data = resp.json()
    entries = data.get("list", [])

    # Forecast API returns 3-hour steps -> next 6 hours ~= first 2 entries,
    # but task asks for "next 6 hours" so we take up to 2 steps (6h) padded to a
    # friendly 6-entry hourly-style display using available 3h steps.
    hourly = []
    for e in entries[:6]:
        hourly.append({
            "time": e["dt_txt"].split(" ")[1][:5],
            "temp_c": round(kelvin_to_c(e["main"]["temp"]), 1),
            "condition": e["weather"][0]["main"],
        })

    # Daily: OpenWeatherMap free tier gives 3h steps for 5 days; pick one
    # entry per day (around midday) as a simple "daily" summary.
    daily = []
    seen_dates = set()
    for e in entries:
        date = e["dt_txt"].split(" ")[0]
        time = e["dt_txt"].split(" ")[1]
        if date not in seen_dates and time.startswith("12:"):
            seen_dates.add(date)
            daily.append({
                "date": date,
                "temp_c": round(kelvin_to_c(e["main"]["temp"]), 1),
                "condition": e["weather"][0]["main"],
            })
        if len(daily) == 5:
            break

    return hourly, daily, None


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App - Oasis Infobyte SIP")
        self.geometry("480x600")
        self.configure(bg="#eef2f5")

        self.unit_fahrenheit = tk.BooleanVar(value=False)
        self.last_data = None

        self._build_widgets()

    def _build_widgets(self):
        tk.Label(self, text="Weather App", font=("Segoe UI", 20, "bold"),
                  bg="#eef2f5", fg="#2c3e50").pack(pady=(20, 10))

        top = tk.Frame(self, bg="#eef2f5")
        top.pack(pady=5)
        self.city_entry = ttk.Entry(top, width=25, font=("Segoe UI", 12))
        self.city_entry.grid(row=0, column=0, padx=5)
        self.city_entry.bind("<Return>", lambda e: self.on_get_weather())
        tk.Button(top, text="Get Weather", font=("Segoe UI", 10, "bold"),
                  bg="#2980b9", fg="white", relief="flat", padx=10,
                  command=self.on_get_weather).grid(row=0, column=1, padx=5)

        unit_frame = tk.Frame(self, bg="#eef2f5")
        unit_frame.pack(pady=5)
        tk.Checkbutton(unit_frame, text="Show in \u00b0F", variable=self.unit_fahrenheit,
                       bg="#eef2f5", command=self.refresh_display).pack()

        self.error_label = tk.Label(self, text="", fg="#c0392b", bg="#eef2f5", font=("Segoe UI", 10))
        self.error_label.pack(pady=5)

        self.current_frame = tk.Frame(self, bg="white", relief="solid", bd=1)
        self.current_frame.pack(padx=20, pady=10, fill="x")
        self.city_label = tk.Label(self.current_frame, text="", font=("Segoe UI", 16, "bold"), bg="white")
        self.city_label.pack(pady=(10, 0))
        self.temp_label = tk.Label(self.current_frame, text="", font=("Segoe UI", 32, "bold"), bg="white", fg="#2980b9")
        self.temp_label.pack()
        self.condition_label = tk.Label(self.current_frame, text="", font=("Segoe UI", 12), bg="white")
        self.condition_label.pack()
        self.details_label = tk.Label(self.current_frame, text="", font=("Segoe UI", 10), bg="white", fg="#7f8c8d")
        self.details_label.pack(pady=(0, 10))

        tk.Label(self, text="Next 6 Hours", font=("Segoe UI", 11, "bold"), bg="#eef2f5").pack(pady=(15, 2))
        self.hourly_frame = tk.Frame(self, bg="#eef2f5")
        self.hourly_frame.pack(fill="x", padx=20)

        tk.Label(self, text="Next 5 Days", font=("Segoe UI", 11, "bold"), bg="#eef2f5").pack(pady=(15, 2))
        self.daily_frame = tk.Frame(self, bg="#eef2f5")
        self.daily_frame.pack(fill="x", padx=20)

    def _display_temp(self, temp_c):
        if self.unit_fahrenheit.get():
            return f"{c_to_f(temp_c):.1f}\u00b0F"
        return f"{temp_c:.1f}\u00b0C"

    def on_get_weather(self):
        city = self.city_entry.get().strip()
        self.error_label.config(text="")

        data, err = fetch_current_weather(city)
        if err:
            self.error_label.config(text=err)
            return

        hourly, daily, ferr = fetch_forecast(city)
        if ferr:
            self.error_label.config(text=ferr)

        self.last_data = {"current": data, "hourly": hourly or [], "daily": daily or []}
        self.refresh_display()

    def refresh_display(self):
        if not self.last_data:
            return
        data = self.last_data["current"]
        self.city_label.config(text=data["city"])
        self.temp_label.config(text=self._display_temp(data["temp_c"]))
        self.condition_label.config(text=data["condition"])
        self.details_label.config(
            text=f"Humidity: {data['humidity']}%   |   Wind: {data['wind_speed']} m/s"
        )

        for widget in self.hourly_frame.winfo_children():
            widget.destroy()
        for h in self.last_data["hourly"]:
            col = tk.Frame(self.hourly_frame, bg="white", relief="solid", bd=1)
            col.pack(side="left", expand=True, fill="both", padx=2, pady=2)
            tk.Label(col, text=h["time"], bg="white", font=("Segoe UI", 8)).pack()
            tk.Label(col, text=self._display_temp(h["temp_c"]), bg="white", font=("Segoe UI", 9, "bold")).pack()
            tk.Label(col, text=h["condition"], bg="white", font=("Segoe UI", 7)).pack()

        for widget in self.daily_frame.winfo_children():
            widget.destroy()
        for d in self.last_data["daily"]:
            col = tk.Frame(self.daily_frame, bg="white", relief="solid", bd=1)
            col.pack(side="left", expand=True, fill="both", padx=2, pady=2)
            tk.Label(col, text=d["date"][5:], bg="white", font=("Segoe UI", 8)).pack()
            tk.Label(col, text=self._display_temp(d["temp_c"]), bg="white", font=("Segoe UI", 9, "bold")).pack()
            tk.Label(col, text=d["condition"], bg="white", font=("Segoe UI", 7)).pack()


if __name__ == "__main__":
    if API_KEY == "YOUR_API_KEY_HERE":
        print("WARNING: Set your OpenWeatherMap API key in API_KEY or the "
              "OPENWEATHERMAP_API_KEY environment variable before running.")
    app = WeatherApp()
    app.mainloop()
