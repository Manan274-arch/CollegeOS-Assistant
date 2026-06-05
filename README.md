# CollegeOS Agent 🎓

CollegeOS Agent is a Telegram-based college assistant that helps students manage assignments, reminders, timetable entries, attendance, and daily planning through simple text messages.

## Features

- Add and track assignments
- Automatically create reminders for assignment deadlines
- Mark assignments as done
- Create normal reminders
- Mark reminders as done
- Add and view timetable entries
- Mark attendance
- View attendance summary
- Get a daily dashboard
- Ask normal chat questions using an LLM

## Main Commands

### Assignments

```text
Add DBMS assignment due tomorrow at 8 PM
Show pending assignments
Show all assignments
Mark assignment 2 as done
```

When an assignment has a deadline, the bot automatically creates a linked reminder.  
When the assignment is marked as done, the linked reminder is also marked as done.

### Reminders

```text
Remind me to drink water at 6 PM
Remind me to submit OS lab in 30 minutes
Show reminders
Mark reminder 3 as done
```

### Timetable

```text
Add DAA on Monday from 10:30 to 11:30
Show Monday timetable
Show timetable
```

### Attendance

```text
Mark DBMS attendance present
Mark OS attendance absent
Show attendance summary
```

### Dashboard

```text
Daily dashboard
What do I have today?
```

The dashboard shows:

- Today's timetable
- Pending assignments
- Upcoming reminders
- Attendance summary

## Tech Stack

- Python
- Telegram Bot API
- SQLite
- Groq LLM API
- llama-3.1-8b-instant
- APScheduler
- python-dotenv

## Project Structure

```text
CollegeOS-Assistant/
│
├── agent.py
├── telegram_bot.py
├── llm.py
├── tools.py
├── database.py
├── scheduler.py
├── config.py
├── reset_db.py
├── requirements.txt
├── .env
├── .gitignore
└── data/
    └── collegeos.db
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/CollegeOS-Assistant.git
cd CollegeOS-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

### 5. Create the database

```bash
python database.py
```

### 6. Run the bot

```bash
python telegram_bot.py
```

Then open the bot on Telegram and send:

```text
/start
```

## Important Notes

- This bot is currently designed for single-user/local use.
- The database is SQLite and stored locally.
- Do not push `.env` or `data/collegeos.db` to GitHub.
- Deadline times must be clear. If only a day/date is given without time, the bot asks for clarification instead of guessing.

## Current Status

MVP complete.

Implemented:

- Assignment management
- Automatic assignment reminders
- Reminder scheduler
- Timetable manager
- Attendance tracker
- Daily dashboard
- Normal chat mode
- Telegram `/start` and `/help` commands

## `.gitignore`

Make sure `.gitignore` contains:

```gitignore
.env
__pycache__/
*.pyc
data/collegeos.db
```