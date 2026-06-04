from database import get_connection
from datetime import datetime

def add_assignment(title, subject=None, deadline=None, priority="normal", notes=None):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    INSERT INTO assignments(title, subject, deadline, priority, notes)
    VALUES (?, ?, ?, ?, ?)
    """, (title, subject, deadline, priority, notes))

    conn.commit()
    assignment_id=cursor.lastrowid
    conn.close()

    return f"Assignment added successfully with ID {assignment_id}."


def show_assignments(status=None):
    conn=get_connection()
    cursor=conn.cursor()

    if status:
        cursor.execute("""
        SELECT * FROM assignments
        WHERE status=?
        ORDER BY deadline ASC
        """, (status,))
    else:
        cursor.execute("""
        SELECT * FROM assignments
        ORDER BY deadline ASC
        """)

    rows=cursor.fetchall()
    conn.close()

    if not rows:
        return "No assignments found."

    result=[]

    for row in rows:
        assignment_text=(
            f"ID: {row['id']}\n"
            f"Title: {row['title']}\n"
            f"Subject: {row['subject'] or 'Not mentioned'}\n"
            f"Deadline: {row['deadline'] or 'Not mentioned'}\n"
            f"Status: {row['status']}\n"
            f"Priority: {row['priority']}\n"
            f"Notes: {row['notes'] or 'None'}"
        )

        result.append(assignment_text)

    return "\n\n".join(result)


def update_assignment_status(assignment_id, status):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    UPDATE assignments
    SET status=?, updated_at=CURRENT_TIMESTAMP
    WHERE id=?
    """, (status, assignment_id))

    conn.commit()
    rows_updated=cursor.rowcount
    conn.close()

    if rows_updated==0:
        return f"No assignment found with ID {assignment_id}."

    return f"Assignment {assignment_id} marked as {status}."

def find_assignment_by_text(text):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM assignments
    WHERE title LIKE ?
       OR subject LIKE ?
       OR notes LIKE ?
    ORDER BY deadline ASC
    """, (f"%{text}%", f"%{text}%", f"%{text}%"))

    rows = cursor.fetchall()
    conn.close()

    return rows


def mark_attendance(subject, date, status, reason=None):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    INSERT INTO attendance(subject, date, status, reason)
    VALUES (?, ?, ?, ?)
    """, (subject, date, status, reason))

    conn.commit()
    attendance_id=cursor.lastrowid
    conn.close()

    return f"Attendance marked successfully with ID {attendance_id}."


def show_attendance_summary():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    SELECT 
        subject,
        COUNT(*) AS total_classes,
        SUM(CASE WHEN status='attended' THEN 1 ELSE 0 END) AS attended_classes,
        SUM(CASE WHEN status='absent' THEN 1 ELSE 0 END) AS absent_classes,
        SUM(CASE WHEN status='leave' THEN 1 ELSE 0 END) AS leave_classes
    FROM attendance
    GROUP BY subject
    ORDER BY subject ASC
    """)

    rows=cursor.fetchall()
    conn.close()

    if not rows:
        return "No attendance records found."

    result=[]

    for row in rows:
        total=row["total_classes"]
        attended=row["attended_classes"] or 0
        absent=row["absent_classes"] or 0
        leave=row["leave_classes"] or 0

        percentage=(attended/total)*100 if total>0 else 0

        summary=(
            f"Subject: {row['subject']}\n"
            f"Total Classes: {total}\n"
            f"Attended: {attended}\n"
            f"Absent: {absent}\n"
            f"Leave: {leave}\n"
            f"Attendance Percentage: {percentage:.2f}%"
        )

        result.append(summary)

    return "\n\n".join(result)


def create_reminder(title, reminder_time, repeat_rule=None):
    if not title:
        return "Please mention what I should remind you about."

    if not reminder_time:
        return (
            "Please mention a clear reminder time.\n\n"
            "Examples:\n"
            "- remind me to drink water in 2 mins\n"
            "- remind me to submit OS lab at 8 PM\n"
            "- remind me to submit OS lab on 2026-06-04 at 20:00"
        )

    try:
        reminder_datetime = datetime.strptime(reminder_time, "%Y-%m-%d %H:%M")
    except ValueError:
        return (
            "I could not understand the reminder time clearly.\n\n"
            "Please use a clear time like:\n"
            "2026-06-04 20:00"
        )

    now = datetime.now()

    if reminder_datetime <= now:
        return (
            "That reminder time is already in the past.\n\n"
            "Please give a future time."
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO reminders(title, reminder_time, repeat_rule)
    VALUES (?, ?, ?)
    """, (title, reminder_time, repeat_rule))

    conn.commit()
    reminder_id = cursor.lastrowid
    conn.close()

    return f"Reminder created successfully with ID {reminder_id}."

def show_reminders(status="active"):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    SELECT * FROM reminders
    WHERE status=?
    ORDER BY reminder_time ASC
    """, (status,))

    rows=cursor.fetchall()
    conn.close()

    if not rows:
        return "No reminders found."

    result=[]

    for row in rows:
        reminder_text=(
            f"ID: {row['id']}\n"
            f"Title: {row['title']}\n"
            f"Reminder Time: {row['reminder_time']}\n"
            f"Repeat Rule: {row['repeat_rule'] or 'None'}\n"
            f"Status: {row['status']}"
        )

        result.append(reminder_text)

    return "\n\n".join(result)

def get_active_reminders():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM reminders
    WHERE status = ?
    ORDER BY reminder_time ASC
    """, ("active",))

    rows = cursor.fetchall()
    conn.close()

    return rows

def mark_reminder_notification_sent(reminder_id, notification_column):
    allowed_columns = [
        "notified_1d",
        "notified_12h",
        "notified_6h",
        "notified_3h",
        "notified_1h",
        "notified_final"
    ]

    if notification_column not in allowed_columns:
        return "Invalid notification column."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
    UPDATE reminders
    SET {notification_column} = ?
    WHERE id = ?
    """, ("yes", reminder_id))

    conn.commit()
    conn.close()

    return f"{notification_column} marked as sent for reminder {reminder_id}."

def mark_reminder_done(reminder_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE reminders
    SET status = ?
    WHERE id = ?
    AND status = ?
    """, ("done", reminder_id, "active"))

    conn.commit()

    rows_updated = cursor.rowcount

    conn.close()

    if rows_updated == 0:
        return f"No active reminder found with ID {reminder_id}."

    return f"Reminder {reminder_id} marked as done."

def save_project_discussion(project_name, message_type, content):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    INSERT INTO project_discussions(project_name, message_type, content)
    VALUES (?, ?, ?)
    """, (project_name, message_type, content))

    conn.commit()
    discussion_id=cursor.lastrowid
    conn.close()

    return f"Project discussion saved successfully with ID {discussion_id}."


def show_project_summary(project_name):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    SELECT * FROM project_discussions
    WHERE project_name=?
    ORDER BY created_at ASC
    """, (project_name,))

    rows=cursor.fetchall()
    conn.close()

    if not rows:
        return f"No project discussions found for {project_name}."

    result=[f"Project Summary: {project_name}"]

    for row in rows:
        discussion_text=(
            f"[{row['message_type']}]\n"
            f"{row['content']}"
        )

        result.append(discussion_text)

    return "\n\n".join(result)


def save_uploaded_image(image_type, file_path, extracted_text=None, status="uploaded"):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    INSERT INTO uploaded_images(image_type, file_path, extracted_text, status)
    VALUES (?, ?, ?, ?)
    """, (image_type, file_path, extracted_text, status))

    conn.commit()
    image_id=cursor.lastrowid
    conn.close()

    return image_id


def add_timetable_entry(day, start_time, end_time, subject, room=None, teacher=None, notes=None, source_image_id=None):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    INSERT INTO timetable_entries(day, start_time, end_time, subject, room, teacher, notes, source_image_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (day, start_time, end_time, subject, room, teacher, notes, source_image_id))

    conn.commit()
    entry_id=cursor.lastrowid
    conn.close()

    return f"Timetable entry added successfully with ID {entry_id}."


def show_timetable(day=None):
    conn=get_connection()
    cursor=conn.cursor()

    if day:
        cursor.execute("""
        SELECT * FROM timetable_entries
        WHERE day=?
        ORDER BY start_time ASC
        """, (day,))
    else:
        cursor.execute("""
        SELECT * FROM timetable_entries
        ORDER BY day ASC, start_time ASC
        """)

    rows=cursor.fetchall()
    conn.close()

    if not rows:
        return "No timetable entries found."

    result=[]

    for row in rows:
        timetable_text=(
            f"Day: {row['day']}\n"
            f"Time: {row['start_time']} - {row['end_time'] or 'Not mentioned'}\n"
            f"Subject: {row['subject']}\n"
            f"Room: {row['room'] or 'Not mentioned'}\n"
            f"Teacher: {row['teacher'] or 'Not mentioned'}\n"
            f"Notes: {row['notes'] or 'None'}"
        )

        result.append(timetable_text)

    return "\n\n".join(result)