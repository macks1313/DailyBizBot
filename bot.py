import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Fetch tokens from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check if the keys exist
if not TELEGRAM_TOKEN:
    logging.error("TELEGRAM_TOKEN is not set in environment variables!")
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY is not set in environment variables!")

# OpenAI API key setup
openai.api_key = OPENAI_API_KEY

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi, I'm your sarcastic bot!")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")

# Main function
def main() -> None:
    if not TELEGRAM_TOKEN:
        logging.error("TELEGRAM_TOKEN is missing! Exiting.")
        return

    try:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.run_polling()
    except Exception as e:
        logging.error(f"Failed to initialize the bot: {e}")

if __name__ == "__main__":
    main()