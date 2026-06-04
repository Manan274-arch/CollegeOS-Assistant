import json

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
Use this when the user wants to save a reminder.
Required fields:
- title
Optional fields:
- reminder_time
- notes

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
    llm_output = ask_llm(
        user_message=user_message,
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

    elif intent == "create_reminder":
        return create_reminder(
            title=data.get("title"),
            reminder_time=data.get("reminder_time"),
            notes=data.get("notes")
        )

    elif intent == "show_reminders":
        return show_reminders(
            status=data.get("status")
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

    elif intent == "show_timetable":
        return show_timetable(
            day=data.get("day")
        )

    else:
        return ask_llm(user_message)