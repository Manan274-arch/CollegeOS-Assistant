from telegram import Update
from telegram.request import HTTPXRequest
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from config import TELEGRAM_BOT_TOKEN
from agent import handle_message
from scheduler import start_scheduler


USER_CHAT_ID = None
scheduler_started = False
scheduler_instance = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global USER_CHAT_ID
    global scheduler_started
    global scheduler_instance

    USER_CHAT_ID = update.effective_chat.id

    if not scheduler_started:
        scheduler_instance = start_scheduler(context.bot, USER_CHAT_ID)
        scheduler_started = True

    await update.message.reply_text(
        "👋 Hi, I am CollegeOS Agent.\n\n"
        "I help you manage your college work from Telegram.\n\n"
        "📌 Assignments\n"
        "- Add DBMS assignment due tomorrow at 8 PM\n"
        "- Show pending assignments\n"
        "- Show all assignments\n"
        "- Mark assignment 2 as done\n\n"
        "⏰ Reminders\n"
        "- Remind me to drink water at 6 PM\n"
        "- Show reminders\n"
        "- Mark reminder 3 as done\n\n"
        "📅 Timetable\n"
        "- Add DAA on Monday from 10:30 to 11:30\n"
        "- Show Monday timetable\n\n"
        "✅ Attendance\n"
        "- Mark DBMS attendance present\n"
        "- Show attendance summary\n\n"
        "📊 Daily Dashboard\n"
        "- Daily dashboard\n"
        "- What do I have today?\n\n"
        "Note: Use the ID shown in lists when marking assignments or reminders as done.\n\n"
        "Reminder scheduler is active ✅"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await update.message.reply_text(
        "CollegeOS Agent Help\n\n"
        "Assignments:\n"
        "- Add DBMS assignment due tomorrow at 8 PM\n"
        "- Show pending assignments\n"
        "- Show all assignments\n"
        "- Mark assignment 2 as done\n\n"
        "Reminders:\n"
        "- Remind me to drink water at 6 PM\n"
        "- Remind me to submit OS lab in 30 minutes\n"
        "- Show reminders\n"
        "- Mark reminder 3 as done\n\n"
        "Timetable:\n"
        "- Add DAA on Monday from 10:30 to 11:30\n"
        "- Show Monday timetable\n"
        "- Show timetable\n\n"
        "Attendance:\n"
        "- Mark DBMS attendance present\n"
        "- Mark OS attendance absent\n"
        "- Show attendance summary\n\n"
        "Dashboard:\n"
        "- Daily dashboard\n"
        "- Today's dashboard\n"
        "- What do I have today?\n\n"
        "Tip: use the assignment/reminder ID when marking something as done."
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = handle_message(user_message)

    except Exception as error:
        response = f"Something went wrong while processing your message: {error}"

    await update.message.reply_text(response)


def main():
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .request(request)
        .build()
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    print("CollegeOS Telegram bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()