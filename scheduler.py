from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tools import (
    get_active_reminders,
    mark_reminder_notification_sent,
    mark_reminder_done
)


REMINDER_FORMAT = "%Y-%m-%d %H:%M"

# Scheduler checks every 30 seconds.
# This is more reliable for short reminders like "in 2 mins".
SCHEDULER_INTERVAL_SECONDS = 30

# Staged reminders only fire inside this window.
# This prevents old missed stages from spamming.
STAGE_GRACE_MINUTES = 2


def parse_reminder_time(reminder_time):
    return datetime.strptime(reminder_time, REMINDER_FORMAT)


def is_stage_due_now(now, notify_at, already_notified):
    if already_notified == "yes":
        return False

    grace_end = notify_at + timedelta(minutes=STAGE_GRACE_MINUTES)

    return notify_at <= now <= grace_end


def is_final_due(now, reminder_time, already_notified):
    if already_notified == "yes":
        return False

    return now >= reminder_time


async def send_reminder_message(bot, chat_id, message):
    await bot.send_message(
        chat_id=chat_id,
        text=message,
        disable_notification=False
    )


async def check_reminders(bot, chat_id):
    print("Checking reminders...")

    try:
        active_reminders = get_active_reminders()
        now = datetime.now()

        print(f"Current time: {now.strftime(REMINDER_FORMAT)}")
        print(f"Active reminders found: {len(active_reminders)}")

        for reminder in active_reminders:
            reminder_id = reminder["id"]
            title = reminder["title"]
            reminder_time_text = reminder["reminder_time"]

            print(f"Checking reminder {reminder_id}: {title} at {reminder_time_text}")

            try:
                reminder_time = parse_reminder_time(reminder_time_text)
            except ValueError:
                print(f"Skipping reminder {reminder_id}: invalid time format")
                continue

            # 1. Final reminder comes first.
            # If final time has arrived, send final reminder and mark done.
            if is_final_due(now, reminder_time, reminder["notified_final"]):
                message = (
                    "⏰ Final Reminder\n\n"
                    f"{title}\n\n"
                    f"Scheduled time: {reminder_time_text}"
                )

                await send_reminder_message(bot, chat_id, message)

                mark_reminder_notification_sent(reminder_id, "notified_final")
                mark_reminder_done(reminder_id)

                print(f"Final reminder sent and marked done: {reminder_id}")

                continue

            # 2. Staged reminders only fire near their exact stage time.
            notification_stages = [
                {
                    "label": "1 day before",
                    "column": "notified_1d",
                    "notify_at": reminder_time - timedelta(days=1)
                },
                {
                    "label": "12 hours before",
                    "column": "notified_12h",
                    "notify_at": reminder_time - timedelta(hours=12)
                },
                {
                    "label": "6 hours before",
                    "column": "notified_6h",
                    "notify_at": reminder_time - timedelta(hours=6)
                },
                {
                    "label": "3 hours before",
                    "column": "notified_3h",
                    "notify_at": reminder_time - timedelta(hours=3)
                },
                {
                    "label": "1 hour before",
                    "column": "notified_1h",
                    "notify_at": reminder_time - timedelta(hours=1)
                }
            ]

            for stage in notification_stages:
                column = stage["column"]
                label = stage["label"]
                notify_at = stage["notify_at"]
                already_notified = reminder[column]

                if is_stage_due_now(now, notify_at, already_notified):
                    message = (
                        "⏰ Upcoming Reminder\n\n"
                        f"{title}\n\n"
                        f"Time left: {label}\n"
                        f"Scheduled time: {reminder_time_text}"
                    )

                    await send_reminder_message(bot, chat_id, message)

                    mark_reminder_notification_sent(reminder_id, column)

                    print(f"Stage reminder sent: {reminder_id}, stage: {label}")

                    break

    except Exception as error:
        print(f"Scheduler error: {error}")


def start_scheduler(bot, chat_id):
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        check_reminders,
        trigger="interval",
        seconds=SCHEDULER_INTERVAL_SECONDS,
        args=[bot, chat_id],
        id="collegeos_reminder_checker",
        replace_existing=True
    )

    scheduler.start()

    print("Reminder scheduler started.")

    return scheduler