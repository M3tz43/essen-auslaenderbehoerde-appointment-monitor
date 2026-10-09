# Essen Appointment Availability Monitor

Python automation tool that monitors the City of Essen's public appointment portal for available registration appointments and sends a Telegram notification when a real date and time becomes selectable.

The application is a personal automation and portfolio project. It **does not book appointments automatically**.

## Features

- Navigates the appointment workflow with Playwright.
- Distinguishes enabled calendar dates from disabled placeholders.
- Verifies that an actual appointment time is available.
- Sends Telegram alerts with the available date and time.
- Attaches a screenshot when availability is detected.
- Prevents duplicate notifications for unchanged availability.
- Writes operational logs for troubleshooting.
- Sends a daily summary of checks and detected appointments.
- Keeps Telegram credentials outside the source code with environment variables.

## How it works

1. A headless Chromium browser opens the Essen appointment portal.
2. Playwright navigates to the date-and-time selection step.
3. The monitor inspects enabled calendar buttons.
4. Each enabled date is checked for selectable time options.
5. New availability triggers a Telegram alert; booking remains manual.

## Technologies

- Python 3.11+
- Playwright
- python-telegram-bot
- python-dotenv
- AsyncIO

## Setup

Clone the repository and create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies and Chromium:

```bash
pip install -r requirements.txt
playwright install chromium
```

Copy `.env.example` to `.env` and add your Telegram bot token and chat ID:

```env
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
CHECK_INTERVAL_SECONDS=60
```

Run the monitor:

```bash
python abh_monitor.py
```

## Repository structure

- `abh_monitor.py` — monitoring, availability detection, logging and notifications
- `.env.example` — required configuration variables without secrets
- `requirements.txt` — direct Python dependencies
- `.gitignore` — excludes secrets, logs, screenshots and local environments

## Responsible use and limitations

- Use a reasonable check interval and respect the website's terms and capacity.
- The monitor is designed for notification only and intentionally leaves booking to the user.
- Website text, HTML structure or selectors may change and require maintenance.
- Availability can disappear before the user completes a booking.
- The project is not affiliated with or endorsed by the City of Essen.

## License

This project is available under the MIT License.

