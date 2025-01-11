import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Replace these with your actual tokens
TELEGRAM_TOKEN = "TELEGRAM_TOKEN"  # Replace with your Telegram Bot Token
OPENAI_API_KEY = "OPENAI_API_KEY"  # Replace with your OpenAI API Key

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# System messages for ChatGPT
SYSTEM_MESSAGES = {
    "default": "You are a sarcastic friend with dark humor, witty remarks, and occasional 18+ jokes.",
    "uk": "Ти бот-друг із чорним гумором, сарказмом, підколками та 18+ жартами. Відповідай українською.",
    "fr": "Tu es un ami sarcastique avec un humour noir et des réponses pleines d'esprit. Parle en français.",
    "en": "You are a sarcastic friend with dark humor, witty remarks, and occasional 18+ jokes.",
}

# Generate a response from ChatGPT
async def generate_response(user_input: str, language: str = "default") -> str:
    try:
        system_message = SYSTEM_MESSAGES.get(language, SYSTEM_MESSAGES["default"])
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input},
            ],
        )
        return response["choices"][0]["message"]["content"].strip()
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API Error: {e}")
        return "Something went wrong with my internet. Please try again later!"

# Detect the language of the message
def detect_language(text: str) -> str:
    if any(word in text.lower() for word in ["bonjour", "salut", "merci"]):
        return "fr"
    elif any(word in text.lower() for word in ["привіт", "дякую", "будь ласка"]):
        return "uk"
    else:
        return "en"

# Handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi, I'm your sarcastic bot! Let's chat.")

# Handle text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    language = detect_language(user_message)
    bot_response = await generate_response(user_message, language)
    await update.message.reply_text(bot_response)

# Run the bot
def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()