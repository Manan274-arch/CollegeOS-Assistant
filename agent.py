import json
import re
from datetime import datetime,timedelta

from llm import ask_llm
from tools import (
    add_assignment,
    show_assignments,
    update_assignment_status,
    mark_attendance,
    show_attendance_summary,
    create_reminder,
    show_reminders,
    save_project_discussion,
    show_project_summary,
    add_timetable_entry,
    show_timetable,
    show_daily_dashboard
)


INTENT_SYSTEM_MESSAGE = """
You are the intent router for CollegeOS Agent.

Return ONLY valid JSON. No markdown. No explanation.

Current possible intents:

normal_chat
add_assignment
show_assignments
update_assignment_status
mark_attendance
show_attendance_summary
create_reminder
show_reminders
save_project_discussion
show_project_summary
add_timetable_entry
show_timetable
show_daily_dashboard

Return this format:
{
  "intent": "intent_name",
  "data": {}
}

Rules:

Use normal_chat for general questions, explanations, writing help, motivation, or casual conversation.

Use add_assignment when the user wants to save a new assignment.
Data fields:
title, subject, deadline, notes

deadline must be in this exact format if mentioned:
YYYY-MM-DD HH:MM

Use the current local datetime given in the user message to convert relative deadlines like "tomorrow at 8 PM" or "Tuesday at 6 PM".

Important:
If the user gives only a day/date without a time, set deadline to null.
Do not use 00:00 unless the user clearly says midnight or 12 AM.

Use show_assignments when the user asks to view assignments.
Data fields:
status

For show_assignments:
- - If user says "show assignments", "show pending assignments", or "my assignments", set status to "pending".
- If user says "show all assignments", set status to null.
- If user asks for completed/done/submitted assignments, set status to "done".

Use update_assignment_status when the user wants to mark/update an assignment.
Data fields:
assignment_id, status

Use mark_attendance when the user wants to mark attendance.
Data fields:
subject, status, date, notes

Use show_attendance_summary when the user asks for attendance summary.
Data fields:
subject

Use create_reminder when the user wants a reminder.
Data fields:
title, reminder_time, repeat_rule

reminder_time must be:
YYYY-MM-DD HH:MM

Use the current local datetime given in the user message to convert relative times.

If date/time is missing or impossible to determine, use normal_chat and ask for clarification.

If the user gives time without AM/PM like "at 6", "at 8:30", or "by 10", keep the intent as create_reminder but do not invent AM/PM.

Use show_reminders when the user asks to see reminders.
Data fields:
status

Use save_project_discussion when the user wants to save project ideas, decisions, rejected ideas, or tech stack notes.
Data fields:
project_name, message, discussion_type

Use show_project_summary when the user asks what was discussed/saved about a project.
Data fields:
project_name

Use add_timetable_entry when the user wants to add a class/lab/session to timetable.
Data fields:
day, start_time, end_time, subject, room, teacher, notes

Use show_timetable when the user asks for timetable.
Data fields:
day

Use show_daily_dashboard when the user asks for today's dashboard, daily dashboard, today's plan, what they have today, or today's college summary.
Data fields:
none

If required data is missing, put null.
"""

def decide_intent(user_message):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")

    routing_message = (
        f"Current local datetime: {current_datetime}\n\n"
        f"User message: {user_message}"
    )

    llm_output = ask_llm(
        user_message=routing_message,
        system_message=INTENT_SYSTEM_MESSAGE,
        temperature=0,
        max_tokens=150
    )

    try:
        decision = json.loads(llm_output)
        return decision

    except json.JSONDecodeError:
        return {
            "intent": "normal_chat",
            "data": {
                "fallback_reason": "LLM did not return valid JSON."
            }
        }

def has_ambiguous_time(user_message):
    text = user_message.lower()

    # Relative times are clear.
    # Examples: "in 2 mins", "in 1 hour", "after 30 minutes"
    if re.search(r"\b(in|after)\s+\d+\s*(min|mins|minute|minutes|hour|hours)\b", text):
        return False

    # If AM/PM is clearly mentioned, it is not ambiguous.
    # Supports: am, pm, a.m., p.m.
    if re.search(r"\b(am|pm)\b", text) or re.search(r"\b(a\.m\.|p\.m\.)", text):
        return False

    # Detect time like 6:37, 10:30, 12:05
    time_matches = re.findall(r"\b(\d{1,2}):(\d{2})\b", text)

    for hour_text, minute_text in time_matches:
        hour = int(hour_text)

        # 13:00 to 23:59 is clearly 24-hour format.
        if 13 <= hour <= 23:
            continue

        # 00:00 is also clearly 24-hour format.
        if hour == 0:
            continue

        # 1:00 to 12:59 without AM/PM is ambiguous.
        if 1 <= hour <= 12:
            return True

    # Detect plain hour times like:
    # "at 6", "by 8", "before 10", "around 7"
    plain_hour_match = re.search(
        r"\b(at|by|before|around)\s+([1-9]|1[0-2])\b",
        text
    )

    if plain_hour_match:
        return True

    return False

def mentions_deadline_without_time(user_message):
    text = user_message.lower()

    deadline_words = ["due", "deadline", "submit", "submission"]

    has_deadline_word = any(word in text for word in deadline_words)

    if not has_deadline_word:
        return False

    # Clear relative time examples:
    # in 2 hours, after 30 minutes
    if re.search(r"\b(in|after)\s+\d+\s*(min|mins|minute|minutes|hour|hours)\b", text):
        return False

    # Clear AM/PM
    if re.search(r"\b(am|pm)\b", text) or re.search(r"\b(a\.m\.|p\.m\.)", text):
        return False

    # Clear 24-hour or clock time
    if re.search(r"\b\d{1,2}:\d{2}\b", text):
        return False

    return True

def fix_weekday_deadline(user_message, deadline):
    if not deadline:
        return deadline

    text = user_message.lower()

    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    mentioned_day = None

    for day_name, day_number in weekdays.items():
        if day_name in text:
            mentioned_day = day_number
            break

    if mentioned_day is None:
        return deadline

    try:
        deadline_datetime = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
    except ValueError:
        return deadline

    today = datetime.now()
    days_ahead = mentioned_day - today.weekday()

    # If the mentioned day has already passed this week, use next week.
    # If today is Tuesday and user says Tuesday, keep today only if the time is still future.
    if days_ahead < 0:
        days_ahead += 7

    corrected_date = today + timedelta(days=days_ahead)

    corrected_datetime = deadline_datetime.replace(
        year=corrected_date.year,
        month=corrected_date.month,
        day=corrected_date.day
    )

    # If corrected datetime is still in the past, move to next week.
    if corrected_datetime <= today:
        corrected_datetime += timedelta(days=7)

    return corrected_datetime.strftime("%Y-%m-%d %H:%M")

def handle_message(user_message):
    decision = decide_intent(user_message)

    intent = decision.get("intent", "normal_chat")
    data = decision.get("data", {})

    if intent == "normal_chat":
        return ask_llm(user_message)

    elif intent == "add_assignment":
        if mentions_deadline_without_time(user_message):
            return (
                "Please mention the time for the assignment deadline.\n\n"
                "Example:\n"
                "Add Internship assignment due on Tuesday at 8 PM\n\n"
                "You can also use 24-hour format, like 20:00."
            )

        corrected_deadline = fix_weekday_deadline(
            user_message=user_message,
            deadline=data.get("deadline")
        )

        return add_assignment(
            title=data.get("title"),
            subject=data.get("subject"),
            deadline=corrected_deadline,
            notes=data.get("notes")
        )

    elif intent == "show_assignments":
        return show_assignments(
            status=data.get("status")
        )

    elif intent == "update_assignment_status":
        return update_assignment_status(
            assignment_id=data.get("assignment_id"),
            status=data.get("status")
        )

    elif intent == "mark_attendance":
        return mark_attendance(
            subject=data.get("subject"),
            status=data.get("status"),
            date=data.get("date"),
            notes=data.get("notes")
        )

    elif intent == "show_attendance_summary":
        return show_attendance_summary(
            subject=data.get("subject")
        )

    if intent == "create_reminder":
        if has_ambiguous_time(user_message):
            return (
                "Please mention AM or PM for the reminder time.\n\n"
                "Example:\n"
                "remind me to drink water at 6:37 PM\n\n"
                "You can also use 24-hour format, like 18:37."
            )

        corrected_reminder_time = fix_weekday_deadline(
            user_message=user_message,
            deadline=data.get("reminder_time")
        )
        
        return create_reminder(
            title=data.get("title"),
            reminder_time=corrected_reminder_time,
            repeat_rule=data.get("repeat_rule")
        )

    elif intent == "show_reminders":
        return show_reminders(
            status=data.get("status") or "active"
        )

    elif intent == "save_project_discussion":
        return save_project_discussion(
            project_name=data.get("project_name"),
            message=data.get("message"),
            discussion_type=data.get("discussion_type")
        )

    elif intent == "show_project_summary":
        return show_project_summary(
            project_name=data.get("project_name")
        )

    elif intent == "add_timetable_entry":
        return add_timetable_entry(
            day=data.get("day"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            subject=data.get("subject"),
            room=data.get("room"),
            teacher=data.get("teacher"),
            notes=data.get("notes")
        )
    
    elif intent == "show_timetable":
        return show_timetable(
            day=data.get("day")
        )

    elif intent == "show_daily_dashboard":
        return show_daily_dashboard()
    
    else:
        return ask_llm(user_message)
