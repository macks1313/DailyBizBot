import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import os

# Configuration des logs
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Récupération des clés API depuis les variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API")

# Vérification des clés
if not TELEGRAM_TOKEN:
    raise ValueError("Le token Telegram (TELEGRAM_TOKEN) est manquant dans les variables d'environnement.")
if not OPENAI_API_KEY:
    raise ValueError("La clé API OpenAI (OPENAI_API) est manquante dans les variables d'environnement.")

# Configuration de l'API OpenAI
openai.api_key = OPENAI_API_KEY

# Fonction pour interagir avec l'API OpenAI
def openai_query(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.9,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Erreur lors de la requête OpenAI : {e}")
        return "Erreur. Essaie encore."

# Commande /start
async def start(update: Update, context: CallbackContext):
    message = (
        "Salut, moi c'est DailyBizBot. 🦾 \n"
        "Je balance des idées, des plans et parfois des piques. Tape une commande et accroche-toi."
    )
    await update.message.reply_text(message)

# Commande /news
async def news_business(update: Update, context: CallbackContext):
    prompt = (
        "Donne 5 idées de business actuelles en quelques mots : technologie, restauration, freelancing, e-commerce."
    )
    logger.info("Commande /news reçue")
    ideas = openai_query(prompt)
    await update.message.reply_text(f"Idées :\n{ideas}")

# Commande /plan
async def generate_business_plan(update: Update, context: CallbackContext):
    prompt = (
        "Génère un plan d'affaires rapide : problème, solution, cible, revenu."
    )
    logger.info("Commande /plan reçue")
    plan = openai_query(prompt)
    await update.message.reply_text(f"Plan :\n{plan}")

# Commande /anecdote
async def anecdote(update: Update, context: CallbackContext):
    prompt = (
        "Raconte une anecdote courte et sarcastique sur un entrepreneur célèbre."
    )
    logger.info("Commande /anecdote reçue")
    story = openai_query(prompt)
    await update.message.reply_text(f"Anecdote :\n{story}")

# Commande /bonsplans
async def bons_plans(update: Update, context: CallbackContext):
    prompt = "Partage un bon plan pour entrepreneurs débutants. Bref et efficace."
    logger.info("Commande /bonsplans reçue")
    deal = openai_query(prompt)
    await update.message.reply_text(f"Bon plan :\n{deal}")

# Réponse aux messages texte
async def handle_text(update: Update, context: CallbackContext):
    user_message = update.message.text
    prompt = (
        f"Tu es une assistante sarcastique en business. Réponds à ce message en une phrase : {user_message}"
    )
    logger.info(f"Message texte reçu : {user_message}")
    response = openai_query(prompt)
    await update.message.reply_text(response)

# Configuration du bot Telegram
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commandes du bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news_business))
    application.add_handler(CommandHandler("plan", generate_business_plan))
    application.add_handler(CommandHandler("anecdote", anecdote))
    application.add_handler(CommandHandler("bonsplans", bons_plans))

    # Handler pour les messages texte
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("✅ Le bot démarre...")
    application.run_polling()

if __name__ == "__main__":
    main()
