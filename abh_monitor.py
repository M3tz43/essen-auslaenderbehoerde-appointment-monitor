import asyncio
import os
import logging
import re
from datetime import datetime, date

from dotenv import load_dotenv
from telegram import Bot
from playwright.async_api import async_playwright

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://termine.essen.de/?link=4ce9"

CHECK_INTERVAL = max(
    60,
    int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
)  # Minimum delay after each completed check

TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")

last_notification = None

# -------------------------------------------------
# Daily statistics
# -------------------------------------------------

daily_checks = 0
daily_appointment_found = False
daily_dates = []

# The date whose statistics are currently being collected
current_report_date = date.today()

# Prevent duplicate reports
last_report_sent_date = None

os.makedirs("logs", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/abh_monitor.log"),
        logging.StreamHandler()
    ]
)


# -------------------------------------------------
# Telegram
# -------------------------------------------------

async def send_telegram(message, screenshot=None):
    bot = Bot(token=TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )

    if screenshot:
        with open(screenshot, "rb") as photo:
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=photo
            )


# -------------------------------------------------
# Daily report
# -------------------------------------------------

async def send_daily_report(report_date):
    global daily_checks
    global daily_appointment_found
    global daily_dates
    global last_report_sent_date

    # Do not send the same day's report twice
    if last_report_sent_date == report_date:
        return True

    report = (
        "📊 Essen ABH Daily Report\n\n"
        f"Date: {report_date}\n"
        f"Checks performed: {daily_checks}\n\n"
    )

    if daily_appointment_found:
        report += (
            "Appointments found: ✅ Yes\n\n"
            "Available appointments:\n"
        )

        for appointment in daily_dates:
            report += (
                f"• {appointment['date']} — "
                f"{', '.join(appointment['times'])}\n"
            )

        report += (
            "\nAppointments were detected during the day."
        )

    else:
        report += (
            "Appointments found: ❌ No\n\n"
            "No available appointments were detected."
        )

    try:
        await send_telegram(report)

        last_report_sent_date = report_date

        logging.info(
            f"Daily report sent for {report_date} "
            f"({daily_checks} checks)"
        )

        return True

    except Exception as e:
        # Do not mark the report as sent.
        # The bot will try again next loop.
        logging.error(
            f"Could not send daily report: {e}"
        )

        return False


# -------------------------------------------------
# Reset statistics for a new day
# -------------------------------------------------

def reset_daily_statistics(new_date):
    global daily_checks
    global daily_appointment_found
    global daily_dates
    global current_report_date

    daily_checks = 0
    daily_appointment_found = False
    daily_dates = []
    current_report_date = new_date


# -------------------------------------------------
# Detect a new day and send yesterday's report
# -------------------------------------------------

async def handle_daily_report():
    global current_report_date

    today = date.today()

    # Still the same day
    if today == current_report_date:
        return

    previous_day = current_report_date

    logging.info(
        f"New day detected: {today}"
    )

    # Send the report BEFORE resetting the counters
    report_sent = await send_daily_report(
        previous_day
    )

    # Only reset if Telegram received the report
    if report_sent:
        reset_daily_statistics(today)

        logging.info(
            f"Daily statistics reset for {today}"
        )


# -------------------------------------------------
# Find available appointment times
# -------------------------------------------------

async def get_available_times(page):
    """
    Check the actual 'Zeit wählen' selector after selecting a date.

    Only enabled options containing a real HH:MM time are returned.
    """

    time_select = page.locator(
        "#time-select"
    )

    try:
        await time_select.wait_for(
            state="visible",
            timeout=5000
        )

    except Exception:
        logging.info(
            "Time selector not visible"
        )

        return []

    # Selecting a date updates the time selector asynchronously.
    # Wait for the selector to become enabled.
    for _ in range(15):

        try:
            if not await time_select.is_disabled():
                break

        except Exception:
            pass

        await page.wait_for_timeout(300)

    else:
        logging.info(
            "Time selector is disabled"
        )

        return []

    available_times = []

    time_options = time_select.locator(
        "option"
    )

    for i in range(
        await time_options.count()
    ):
        option = time_options.nth(i)

        try:
            if await option.is_disabled():
                continue

            value = await option.get_attribute(
                "value"
            )

            time_text = (
                await option.inner_text()
            ).strip()

            # Ignore "Zeit wählen" and other non-time options.
            if (
                value
                and TIME_PATTERN.fullmatch(time_text)
            ):
                if time_text not in available_times:
                    available_times.append(
                        time_text
                    )

        except Exception as e:
            logging.warning(
                f"Could not inspect time option: {e}"
            )

    return available_times


# -------------------------------------------------
# Store appointments found during the entire day
# -------------------------------------------------

def save_daily_appointments(real_appointments):
    global daily_appointment_found
    global daily_dates

    if not real_appointments:
        return

    daily_appointment_found = True

    # Do not overwrite appointments found earlier in the day.
    # Add new date/time combinations to the daily history.
    for new_appointment in real_appointments:

        existing = next(
            (
                appointment
                for appointment in daily_dates
                if appointment["date"]
                == new_appointment["date"]
            ),
            None
        )

        if existing:
            for time_value in new_appointment["times"]:
                if time_value not in existing["times"]:
                    existing["times"].append(
                        time_value
                    )

        else:
            daily_dates.append({
                "date": new_appointment["date"],
                "times": list(
                    new_appointment["times"]
                )
            })


# -------------------------------------------------
# Check appointments
# -------------------------------------------------

async def check_appointments():
    global last_notification
    global daily_checks

    daily_checks += 1

    check_number = daily_checks

    logging.info(
        f"Starting appointment check #{check_number}"
    )

    start_time = datetime.now()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        try:
            # -------------------------------------------------
            # Open Essen appointment page
            # -------------------------------------------------

            logging.info(
                "Opening Essen appointment page"
            )

            await page.goto(
                URL,
                wait_until="networkidle",
                timeout=60000
            )

            # -------------------------------------------------
            # Step 1: Anmeldung
            # -------------------------------------------------

            logging.info(
                "Clicking Anmeldung"
            )

            await page.get_by_text(
                "Anmeldung",
                exact=True
            ).click()

            await page.wait_for_load_state(
                "networkidle"
            )

            # -------------------------------------------------
            # Step 2
            # -------------------------------------------------

            logging.info(
                "Clicking Weiter zu Schritt 2"
            )

            await page.get_by_text(
                "Weiter zu Schritt 2",
                exact=True
            ).click()

            await page.wait_for_load_state(
                "networkidle"
            )

            # -------------------------------------------------
            # Step 3: Date and time
            # -------------------------------------------------

            logging.info(
                "Clicking Weiter zu Schritt 3"
            )

            await page.get_by_text(
                "Weiter zu Schritt 3",
                exact=True
            ).click()

            await page.wait_for_load_state(
                "networkidle"
            )

            # Give the calendar JavaScript time to load
            await page.wait_for_timeout(3000)

            logging.info(
                "Reached Step 3 - Date and Time"
            )

            # -------------------------------------------------
            # Find calendar buttons
            # -------------------------------------------------

            dates = page.locator(
                "button.duet-date__day"
            )

            count = await dates.count()

            logging.info(
                f"Calendar buttons: {count}"
            )

            selectable_dates = []

            # -------------------------------------------------
            # Find dates that are actually selectable
            # -------------------------------------------------

            for i in range(count):
                button = dates.nth(i)

                try:
                    aria_disabled = (
                        await button.get_attribute(
                            "aria-disabled"
                        )
                    )

                    disabled = (
                        await button.is_disabled()
                    )

                    # Ignore disabled calendar dates
                    if (
                        disabled
                        or aria_disabled == "true"
                    ):
                        continue

                    date_locator = button.locator(
                        ".duet-date__vhidden"
                    )

                    if await date_locator.count() > 0:
                        date_text = (
                            await date_locator.inner_text()
                        ).strip()

                    else:
                        date_text = (
                            await button.inner_text()
                        ).strip()

                    if not date_text:
                        continue

                    selectable_dates.append({
                        "index": i,
                        "date": date_text
                    })

                except Exception as e:
                    logging.warning(
                        f"Could not inspect calendar "
                        f"button #{i + 1}: {e}"
                    )

            # -------------------------------------------------
            # No selectable dates
            # -------------------------------------------------

            if not selectable_dates:
                logging.info(
                    "Selectable dates: none"
                )

                logging.info(
                    "No appointments available"
                )

                # Appointments disappeared.
                # Allow future availability to notify again.
                last_notification = None

                return

            # -------------------------------------------------
            # Selectable dates found
            # -------------------------------------------------

            logging.info(
                "Selectable dates: "
                + ", ".join(
                    item["date"]
                    for item in selectable_dates
                )
            )

            real_appointments = []

            # -------------------------------------------------
            # Click each date and check "Zeit wählen"
            # -------------------------------------------------

            for item in selectable_dates:
                date_text = item["date"]

                logging.info(
                    f"Checking times for {date_text}"
                )

                try:
                    # Re-locate the buttons because selecting
                    # a date can update the calendar DOM.
                    current_dates = page.locator(
                        "button.duet-date__day"
                    )

                    button = current_dates.nth(
                        item["index"]
                    )

                    # Make sure it is still selectable
                    if await button.is_disabled():
                        continue

                    aria_disabled = (
                        await button.get_attribute(
                            "aria-disabled"
                        )
                    )

                    if aria_disabled == "true":
                        continue

                    # Select date
                    await button.click()

                    # Check the actual time selector
                    available_times = (
                        await get_available_times(page)
                    )

                    if available_times:
                        logging.info(
                            f"Available times for "
                            f"{date_text}: "
                            f"{', '.join(available_times)}"
                        )

                        real_appointments.append({
                            "date": date_text,
                            "times": available_times
                        })

                    else:
                        logging.info(
                            f"No times available for "
                            f"{date_text}"
                        )

                except Exception as e:
                    logging.warning(
                        f"Could not check "
                        f"{date_text}: {e}"
                    )

            # -------------------------------------------------
            # Real appointments found
            # -------------------------------------------------

            if real_appointments:
                logging.info(
                    "REAL APPOINTMENTS FOUND"
                )

                # Save appointment history for daily report
                save_daily_appointments(
                    real_appointments
                )

                current_status = str(
                    real_appointments
                )

                # -------------------------------------------------
                # Send Telegram notification only when availability
                # changes
                # -------------------------------------------------

                if (
                    current_status
                    != last_notification
                ):
                    screenshot_name = (
                        "screenshots/appointment_"
                        f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
                    )

                    try:
                        await page.screenshot(
                            path=screenshot_name,
                            full_page=True
                        )

                    except Exception as e:
                        logging.warning(
                            f"Could not save screenshot: {e}"
                        )

                        screenshot_name = None

                    message = (
                        "🚨 Essen Ausländerbehörde "
                        "appointment available!\n\n"
                    )

                    for appointment in real_appointments:
                        message += (
                            f"📅 {appointment['date']}\n"
                            f"🕐 "
                            f"{', '.join(appointment['times'])}\n\n"
                        )

                    message += (
                        "Book it manually now!\n\n"
                        f"🔗 {URL}"
                    )

                    await send_telegram(
                        message,
                        screenshot_name
                    )

                    last_notification = (
                        current_status
                    )

                    logging.info(
                        "Telegram notification sent"
                    )

                else:
                    logging.info(
                        "Already notified about "
                        "these appointments"
                    )

            # -------------------------------------------------
            # No real appointment times
            # -------------------------------------------------

            else:
                logging.info(
                    "No real appointments detected"
                )

                last_notification = None

        except Exception as e:
            logging.error(
                f"Error during appointment check: {e}"
            )

        finally:
            await browser.close()

    elapsed = (
        datetime.now() - start_time
    ).total_seconds()

    logging.info(
        f"Check #{check_number} completed "
        f"in {elapsed:.1f} seconds"
    )


# -------------------------------------------------
# Main loop
# -------------------------------------------------

async def main():
    logging.info(
        "Essen ABH Monitor started"
    )

    logging.info(
        f"Check interval: {CHECK_INTERVAL} seconds"
    )

    logging.info(
        "Daily report: after midnight"
    )

    while True:
        try:
            # -------------------------------------------------
            # Send the previous day's report when midnight passes
            # -------------------------------------------------

            await handle_daily_report()

            # -------------------------------------------------
            # Check appointments
            # -------------------------------------------------

            await check_appointments()

        except Exception as e:
            logging.error(
                f"Main loop error: {e}"
            )

        # -------------------------------------------------
        # Wait a full 60 seconds AFTER the scan completes
        # -------------------------------------------------

        logging.info(
            f"Waiting {CHECK_INTERVAL} seconds"
        )

        await asyncio.sleep(
            CHECK_INTERVAL
        )


# -------------------------------------------------
# Start bot
# -------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
