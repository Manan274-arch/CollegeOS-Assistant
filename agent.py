import json
import re
from datetime import datetime

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
    show_timetable
)


INTENT_SYSTEM_MESSAGE = """
You are the intent router for CollegeOS Agent.

Your job is to read the user's message and decide what the program should do.

Return ONLY valid JSON.
Do not add explanations.
Do not use markdown.

Available intents:

1. normal_chat
Use this when the user is asking a general question or having a normal conversation.
Examples:
- Explain recursion
- What is DBMS?
- Help me write a message
- Motivate me to study

2. add_assignment
Use this when the user wants to save a new assignment.
Required fields:
- title
Optional fields:
- subject
- deadline
- notes

3. show_assignments
Use this when the user wants to see assignments.
Optional fields:
- status

4. update_assignment_status
Use this when the user wants to update an assignment status.
Required fields:
- assignment_id
- status

5. mark_attendance
Use this when the user wants to mark attendance.
Required fields:
- subject
- status
Optional fields:
- date
- notes

6. show_attendance_summary
Use this when the user wants attendance summary.
Optional fields:
- subject

7. create_reminder
Use this when the user wants to create a reminder.

Required data:
- title
- reminder_time

Optional data:
- repeat_rule

Important:
reminder_time must be in this exact format:
YYYY-MM-DD HH:MM

If the user gives a relative time like "tomorrow at 8 PM", convert it to an exact date and time based on the current date given in the user message/context.
If the exact date cannot be determined, ask for clarification using normal_chat instead of creating a reminder.

Examples:
User: remind me to submit OS lab on 2026-06-04 at 20:00
Output:
{
  "intent": "create_reminder",
  "data": {
    "title": "submit OS lab",
    "reminder_time": "2026-06-04 20:00",
    "repeat_rule": null
  }
}

Important reminder time rule:
If the user gives a 12-hour clock time without AM or PM, do not guess.
For example, "at 6:30", "at 8", or "by 10:15" is ambiguous.
In such cases, still return create_reminder only if the backend can ask clarification, but do not invent AM or PM.
Clear times include:
- 6:30 PM
- 8 AM
- 18:30
- tomorrow at 7 PM

8. show_reminders
Use this when the user wants to see reminders.
Optional fields:
- status

9. save_project_discussion
Use this when the user wants to save a project idea, project discussion, rejected idea, decision, or tech stack note.
Required fields:
- project_name
- message
Optional fields:
- discussion_type

10. show_project_summary
Use this when the user asks what has been discussed or saved about a project.
Required fields:
- project_name

add_timetable_entry
Use this when the user wants to add a class/lab/session to their timetable.

Required data:
- day
- start_time
- subject

Optional data:
- end_time
- room
- teacher
- notes

Examples:
User: add DAA on Monday from 10:30 to 11:30
Output:
{
  "intent": "add_timetable_entry",
  "data": {
    "day": "Monday",
    "start_time": "10:30",
    "end_time": "11:30",
    "subject": "DAA",
    "room": null,
    "teacher": null,
    "notes": null
  }
}

User: add OS lab every Tuesday 2 to 4 in CL-11
Output:
{
  "intent": "add_timetable_entry",
  "data": {
    "day": "Tuesday",
    "start_time": "14:00",
    "end_time": "16:00",
    "subject": "OS lab",
    "room": "CL-11",
    "teacher": null,
    "notes": null
  }
}
11. show_timetable
Use this when the user asks for timetable.
Optional fields:
- day

JSON format:
{
  "intent": "intent_name",
  "data": {
    "field": "value"
  }
}

Important rules:
- If the user is just chatting, use normal_chat.
- If important college data should be stored or retrieved, choose the correct tool intent.
- If required information is missing, still choose the closest intent and put null for missing fields.
- Return only JSON.
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
        max_tokens=400
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
def handle_message(user_message):
    decision = decide_intent(user_message)

    intent = decision.get("intent", "normal_chat")
    data = decision.get("data", {})

    if intent == "normal_chat":
        return ask_llm(user_message)

    elif intent == "add_assignment":
        return add_assignment(
            title=data.get("title"),
            subject=data.get("subject"),
            deadline=data.get("deadline"),
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

        return create_reminder(
            title=data.get("title"),
            reminder_time=data.get("reminder_time"),
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

    else:
        return ask_llm(user_message)
