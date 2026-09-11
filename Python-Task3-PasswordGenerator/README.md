# Random Password Generator (Advanced) — Oasis Infobyte SIP

**Track:** Python Programming
**Task:** Task 3 — Random Password Generator (Advanced Tier)

## Objective
A GUI tool that generates strong, cryptographically secure passwords based
on user-defined length and character-type criteria.

## Tech Stack
- Python 3
- `tkinter` — GUI (slider, checkboxes, buttons)
- `secrets` — cryptographically secure random generation (not `random`)
- `string` — character pools

## Features
- GUI with a length slider (8–32) and checkboxes for uppercase, lowercase,
  digits, and symbols
- Uses the `secrets` module instead of `random` for cryptographic security
- **Guarantees** at least one character from each selected type
- Password **strength indicator** (Weak / Medium / Strong) based on length
  and character diversity
- **"Copy to Clipboard"** button (via tkinter's built-in clipboard)
- Option to **exclude ambiguous characters** (0, O, l, 1)
- **Session-only generation history** — last 5 passwords shown, never
  written to disk (for security)

## How to Run
```
python password_generator.py
```
1. Adjust the length slider and tick the character types you want.
2. Click **Generate Password**.
3. Click **Copy to Clipboard** to copy it.

## Project Structure (for GitHub)
```
OIBSIP/Python-Task3-PasswordGenerator/
├── password_generator.py
└── README.md
```

## Author
Lokesh Pareek — Python Programming Intern, Oasis Infobyte
