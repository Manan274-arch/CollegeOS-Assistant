from pathlib import Path
from datetime import datetime

from telegram import Update
from telegram.request import HTTPXRequest
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from config import TELEGRAM_BOT_TOKEN
from agent import handle_message
from image_parser import extract_text_from_image
from tools import save_uploaded_image


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi, I am CollegeOS Agent.\n\n"
        "You can send me text messages or images.\n\n"
        "Text examples:\n"
        "- Add DAA assignment due tomorrow\n"
        "- Show my assignments\n"
        "- Mark DBMS attendance present\n"
        "- Remind me to submit OS lab at 8 PM\n"
        "- Show Monday timetable\n\n"
        "Image examples:\n"
        "- Send a timetable image\n"
        "- Send an assignment/notice screenshot\n\n"
        "For now, I can extract and store OCR text from images."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "CollegeOS Agent currently supports:\n\n"
        "- Normal chat\n"
        "- Assignments\n"
        "- Attendance\n"
        "- Reminders\n"
        "- Project notes\n"
        "- Timetable queries\n"
        "- Image OCR text extraction\n\n"
        "Image flow right now:\n"
        "Telegram image → saved in data/uploads/ → OCR text extracted → saved in SQLite."
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = handle_message(user_message)

    except Exception as error:
        response = f"Something went wrong while processing your message: {error}"

    await update.message.reply_text(response)


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]

        telegram_file = await context.bot.get_file(photo.file_id)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"telegram_image_{timestamp}.jpg"
        file_path = UPLOAD_DIR / file_name

        await telegram_file.download_to_drive(custom_path=str(file_path))

        extracted_text = extract_text_from_image(file_path)

        image_id = save_uploaded_image(
            image_type="telegram_image",
            file_path=str(file_path),
            extracted_text=extracted_text,
            status="processed"
        )

        if len(extracted_text) > 3500:
            reply_text = (
                f"Image saved and OCR processed.\n\n"
                f"Image ID: {image_id}\n\n"
                f"The extracted text is too long to show fully here.\n\n"
                f"Preview:\n{extracted_text[:3500]}"
            )
        else:
            reply_text = (
                f"Image saved and OCR processed.\n\n"
                f"Image ID: {image_id}\n\n"
                f"Extracted text:\n{extracted_text}"
            )

        await update.message.reply_text(reply_text)

    except Exception as error:
        await update.message.reply_text(
            f"Something went wrong while processing the image: {error}"
        )


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
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))

    print("CollegeOS Telegram bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()