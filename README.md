# Essen Ausländerbehörde Appointment Monitor

A Python automation tool that monitors the City of Essen's public appointment portal for available appointments and sends Telegram notifications when a selectable date and time are detected.

Built as a personal automation and portfolio project using **Python, Playwright, Telegram, and Docker**.

**The application does not automatically book appointments.** All bookings must be completed manually.

## Features

- **Automated browser navigation:** Uses Playwright to navigate the Essen appointment portal.
- **Availability detection:** Identifies enabled calendar dates and checks for selectable appointment times.
- **Telegram notifications:** Sends alerts when new availability is detected.
- **Screenshot evidence:** Captures screenshots when appointments become available.
- **Duplicate prevention:** Avoids repeated notifications for unchanged availability.
- **Daily reports:** Provides a summary of monitoring activity.
- **Logging:** Records application activity for troubleshooting.
- **Docker support:** Runs in a container with automatic restart configuration.
- **Environment-based configuration:** Keeps Telegram credentials separate from the source code.

## How It Works

1. Playwright launches a Chromium browser and opens the Essen appointment portal.
2. The application navigates through the appointment workflow to the date-and-time selection page.
3. It inspects calendar buttons to identify selectable dates.
4. It checks whether actual appointment times are available.
5. When new availability is confirmed, it sends a Telegram notification.
6. The application waits before performing the next check.

The monitor uses a **minimum interval of 60 seconds between completed checks**.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main application |
| Playwright | Browser automation |
| AsyncIO | Asynchronous execution |
| python-telegram-bot | Telegram notifications |
| python-dotenv | Environment configuration |
| Docker | Containerized deployment |
| Docker Compose | Container management |

## Getting Started

### Prerequisites

For local execution:

- Python 3.11 or newer
- A Telegram bot token
- A Telegram chat ID
- Chromium installed through Playwright

Alternatively, use Docker with Docker Compose.

### 1. Clone the Repository

```bash
git clone https://github.com/M3tz43/essen-auslaenderbehoerde-appointment-monitor.git
cd essen-auslaenderbehoerde-appointment-monitor
```

### 2. Configure Telegram

Create a `.env` file using `.env.example` as a template.

```env
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
CHECK_INTERVAL_SECONDS=60
```

You can create a Telegram bot using [@BotFather](https://t.me/BotFather).

Never commit your real `.env` file to GitHub.

### 3. Run with Docker (Recommended)

Build and start the monitor:

```bash
docker compose up -d --build
```

View application logs:

```bash
docker compose logs -f
```

Check container status:

```bash
docker compose ps
```

Stop the monitor:

```bash
docker compose down
```

The container is configured to restart automatically unless explicitly stopped.

Logs and screenshots are stored in local directories using Docker volumes.

### 4. Run Locally Without Docker

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Install Chromium:

```bash
python -m playwright install chromium
```

Start the monitor:

```bash
python abh_monitor.py
```

Windows users can alternatively run `start_bot.bat` after completing the setup.

## Configuration

| Variable | Description | Default |
|---|---|---|
| `TELEGRAM_TOKEN` | Telegram bot authentication token | Required |
| `TELEGRAM_CHAT_ID` | Destination for notifications | Required |
| `CHECK_INTERVAL_SECONDS` | Delay between completed checks, in seconds | 60 |

The application enforces a minimum check interval of 60 seconds.

## Repository Structure

```text
essen-auslaenderbehoerde-appointment-monitor/
├── abh_monitor.py
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── start_bot.bat
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── .dockerignore
└── tools/
    ├── check_availability.py
    ├── check_page.py
    ├── inspect_calendar.py
    ├── inspect_dates.py
    └── test_bot.py
```

The `tools/` directory contains development and debugging utilities for inspecting the appointment website and testing Telegram functionality.

## Logging and Monitoring

The application records operational information, including:

- Appointment check execution
- Browser navigation progress
- Calendar inspection results
- Detected availability
- Notification activity
- Errors and troubleshooting information

Use Docker logs or local application logs to investigate problems.

## Responsible Use and Limitations

- Use reasonable polling intervals and respect the appointment website's terms and capacity.
- The application does not reserve or book appointments.
- Appointment availability can change at any time.
- Website updates may require changes to browser selectors or navigation logic.
- Telegram delivery depends on network connectivity and the Telegram service.
- This project is not affiliated with or endorsed by the City of Essen.

## License

Distributed under the MIT License. See `LICENSE` for details.
