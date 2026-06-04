import sqlite3
from pathlib import Path


BASE_DIR=Path(__file__).resolve().parent
DATA_DIR=BASE_DIR/"data"
UPLOADS_DIR=DATA_DIR/"uploads"
DB_PATH=DATA_DIR/"collegeos.db"


def get_connection():
    DATA_DIR.mkdir(exist_ok=True)
    UPLOADS_DIR.mkdir(exist_ok=True)

    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row

    return conn


def create_tables():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT,
        deadline TEXT,
        status TEXT DEFAULT 'pending',
        priority TEXT DEFAULT 'normal',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        reason TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        reminder_time TEXT NOT NULL,
        repeat_rule TEXT,
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drafts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        draft_type TEXT NOT NULL,
        recipient TEXT,
        tone TEXT,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_ideas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        idea TEXT NOT NULL,
        status TEXT DEFAULT 'proposed',
        reason TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_discussions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        message_type TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        final_report TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploaded_images(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_type TEXT,
        file_path TEXT NOT NULL,
        extracted_text TEXT,
        status TEXT DEFAULT 'uploaded',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timetable_entries(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT,
        subject TEXT NOT NULL,
        room TEXT,
        teacher TEXT,
        notes TEXT,
        source_image_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(source_image_id) REFERENCES uploaded_images(id)
    )
    """)

    conn.commit()
    conn.close()


def reset_database():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS assignments")
    cursor.execute("DROP TABLE IF EXISTS attendance")
    cursor.execute("DROP TABLE IF EXISTS reminders")
    cursor.execute("DROP TABLE IF EXISTS drafts")
    cursor.execute("DROP TABLE IF EXISTS project_ideas")
    cursor.execute("DROP TABLE IF EXISTS project_discussions")
    cursor.execute("DROP TABLE IF EXISTS project_reports")
    cursor.execute("DROP TABLE IF EXISTS uploaded_images")
    cursor.execute("DROP TABLE IF EXISTS timetable_entries")

    conn.commit()
    conn.close()

    create_tables()


if __name__=="__main__":
    create_tables()
    print("Database and tables created successfully.")