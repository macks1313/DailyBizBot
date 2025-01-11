import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Увімкнення логів
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Токени
TELEGRAM_TOKEN = "ВАШ_TELEGRAM_ТОКЕН"
OPENAI_API_KEY = "ВАШ_OPENAI_КЛЮЧ"

# Ініціалізація OpenAI API
openai.api_key = OPENAI_API_KEY

# Системні повідомлення для ChatGPT
SYSTEM_MESSAGES = {
    "default": "You are a sarcastic friend with dark humor, witty remarks, and occasional 18+ jokes.",
    "uk": "Ти бот-друг із чорним гумором, сарказмом, підколками та 18+ жартами. Відповідай українською.",
    "fr": "Tu es un ami sarcastique avec un humour noir et des réponses pleines d'esprit. Parle en français.",
    "en": "You are a sarcastic friend with dark humor, witty remarks, and occasional 18+ jokes.",
}

# Генерація відповіді від ChatGPT
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
        return "Щось не так з моїм інтернетом. Спробуй ще раз!"

# Визначення мови (без обмеження довжини)
def detect_language(text: str) -> str:
    if any(word in text.lower() for word in ["bonjour", "salut", "merci"]):
        return "fr"
    elif any(word in text.lower() for word in ["привіт", "дякую", "будь ласка"]):
        return "uk"
    else:
        return "en"

# Обробка команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Salut, je suis ton bot sarcastique préféré ! Parle-moi.")

# Обробка текстових повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    language = detect_language(user_message)
    bot_response = await generate_response(user_message, language)
    await update.message.reply_text(bot_response)

# Запуск бота
def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Додавання команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск
    application.run_polling()

if __name__ == "__main__":
    main()