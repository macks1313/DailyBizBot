import openai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
import logging
import os

# Configuration des logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Récupération des clés API depuis les variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("Le token Telegram (TELEGRAM_TOKEN) est manquant.")
if not OPENAI_API_KEY:
    raise ValueError("La clé API OpenAI (OPENAI_API_KEY) est manquante.")

openai.api_key = OPENAI_API_KEY

# Fonction pour interagir avec OpenAI
def openai_query(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.8,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Erreur lors de la requête OpenAI : {e}")
        return "❌ Une erreur est survenue. Réessaye plus tard."

# Commande /start
async def start(update: Update, context: CallbackContext):
    message = (
        "👋 *Bienvenue sur DailyBizBot* 🦾 !\n\n"
        "✨ Voici ce que je peux faire pour toi :\n\n"
        "📋 /plan - Crée un business plan simplifié étape par étape.\n"
        "💡 /news - Découvre des idées de business en choisissant un thème et une heure pour les recevoir.\n"
        "✅ /validation - Analyse et améliore une idée de business.\n"
        "📈 /marketing - Obtiens une stratégie marketing personnalisée pour ton projet.\n"
        "🛠️ /ressources - Accède à des outils et ressources pratiques pour entrepreneurs.\n"
        "⏰ /notifications - Planifie des notifications quotidiennes pour recevoir des idées ou conseils.\n\n"
        "📬 Tape une commande ou pose-moi une question directement. Je suis prêt à t’aider à réussir ! 🚀"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# Gestion des messages texte non commandés
async def handle_text(update: Update, context: CallbackContext):
    user_message = update.message.text
    logger.info(f"Message reçu : {user_message}")

    # Utiliser OpenAI pour générer une réponse
    prompt = f"Réponds à ce message avec un ton professionnel et utile : {user_message}"
    response = openai_query(prompt)

    # Envoyer la réponse générée au user
    await update.message.reply_text(response)

# Configuration principale du bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Ajout des commandes
    application.add_handler(CommandHandler("start", start))

    # Ajout du gestionnaire pour les messages texte
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("✅ Le bot est prêt et fonctionne...")
    application.run_polling()

if __name__ == "__main__":
    main()