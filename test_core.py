from database import reset_database
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
    save_uploaded_image,
    add_timetable_entry,
    show_timetable
)


def print_result(result):
    if result is None:
        print("No result returned.")
        return

    if isinstance(result, str):
        print(result)
        return

    if isinstance(result, list):
        if len(result) == 0:
            print("No records found.")
            return

        for item in result:
            try:
                print(dict(item))
            except (TypeError, ValueError):
                print(item)

        return

    try:
        print(dict(result))
    except (TypeError, ValueError):
        print(result)


def test_assignments():
    print("\n--- TESTING ASSIGNMENTS ---")

    result = add_assignment(
        title="Math Assignment",
        subject="Mathematics",
        deadline="2026-06-10 23:59",
        priority="high",
        notes="Complete questions 1 to 10"
    )

    print("\nAdd assignment result:")
    print_result(result)

    print("\nAssignments before update:")
    assignments = show_assignments()
    print_result(assignments)

    update_result = update_assignment_status(1, "completed")

    print("\nUpdate assignment status result:")
    print_result(update_result)

    print("\nAssignments after update:")
    assignments = show_assignments()
    print_result(assignments)


def test_attendance():
    print("\n--- TESTING ATTENDANCE ---")

    result_1 = mark_attendance(
        subject="Mathematics",
        date="2026-06-04",
        status="attended",
        reason=None
    )

    print("\nMark attendance result 1:")
    print_result(result_1)

    result_2 = mark_attendance(
        subject="Physics",
        date="2026-06-04",
        status="absent",
        reason="Sick"
    )

    print("\nMark attendance result 2:")
    print_result(result_2)

    print("\nAttendance summary:")
    summary = show_attendance_summary()
    print_result(summary)


def test_reminders():
    print("\n--- TESTING REMINDERS ---")

    result = create_reminder(
        title="Submit Math Assignment",
        reminder_time="2026-06-10 20:00",
        repeat_rule=None
    )

    print("\nCreate reminder result:")
    print_result(result)

    print("\nReminders:")
    reminders = show_reminders()
    print_result(reminders)


def test_project_memory():
    print("\n--- TESTING PROJECT MEMORY ---")

    result_1 = save_project_discussion(
        project_name="CollegeOS Agent",
        message_type="decision",
        content="Use Telegram as the main interface."
    )

    print("\nSave project discussion result 1:")
    print_result(result_1)

    result_2 = save_project_discussion(
        project_name="CollegeOS Agent",
        message_type="tech_stack",
        content="Use Python, SQLite, Groq Llama 8B, and APScheduler."
    )

    print("\nSave project discussion result 2:")
    print_result(result_2)

    print("\nProject summary:")
    summary = show_project_summary("CollegeOS Agent")
    print_result(summary)


def test_images_and_timetable():
    print("\n--- TESTING IMAGES AND TIMETABLE ---")

    result = save_uploaded_image(
        image_type="timetable",
        file_path="data/uploads/sample_timetable.jpg",
        extracted_text="Monday 09:00 to 10:00 Mathematics Room 101",
        status="processed"
    )

    print("\nSave uploaded image result:")
    print_result(result)

    timetable_result = add_timetable_entry(
        day="Monday",
        start_time="09:00",
        end_time="10:00",
        subject="Mathematics",
        room="Room 101",
        teacher="Not mentioned",
        notes="Added from OCR test",
        source_image_id=1
    )

    print("\nAdd timetable entry result:")
    print_result(timetable_result)

    print("\nTimetable:")
    timetable = show_timetable()
    print_result(timetable)


if __name__ == "__main__":
    print("Resetting database...")
    reset_database()

    test_assignments()
    test_attendance()
    test_reminders()
    test_project_memory()
    test_images_and_timetable()

    print("\nAll core tests completed.")

    reset_database()
    print("Database reset after testing.")