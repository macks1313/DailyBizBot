import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
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

# Vérification des clés
if not TELEGRAM_TOKEN:
    raise ValueError("Le token Telegram (TELEGRAM_TOKEN) est manquant dans les variables d'environnement.")
if not OPENAI_API_KEY:
    raise ValueError("La clé API OpenAI (OPENAI_API_KEY) est manquante dans les variables d'environnement.")

# Configuration de l'API OpenAI
openai.api_key = OPENAI_API_KEY

# Fonction pour interagir avec l'API OpenAI
def openai_query(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.9,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Erreur lors de la requête OpenAI : {e}")
        return "Une erreur s'est produite. Réessaye un peu plus tard."

# Commande /start
async def start(update: Update, context: CallbackContext):
    message = (
        "Salut ! Moi, c'est DailyBizBot 🦾.\n"
        "Je suis là pour te donner des idées, des conseils, et même te lancer quelques piques si tu traînes trop.\n\n"
        "Voici ce que je peux faire pour toi :\n"
        "/news - Idées de business\n"
        "/plan - Générer un plan d'affaires rapide\n"
        "/anecdote - Une anecdote sarcastique sur un entrepreneur célèbre\n"
        "/bonsplans - Un conseil pour entrepreneurs débutants\n"
        "Ou écris-moi directement, et je te répondrai."
    )
    await update.message.reply_text(message)

# Commande /news
async def news_business(update: Update, context: CallbackContext):
    prompt = "Donne 5 idées de business actuelles en quelques mots : technologie, restauration, freelancing, e-commerce."
    logger.info("Commande /news reçue")
    ideas = openai_query(prompt)
    await update.message.reply_text(f"Voici 5 idées :\n{ideas}")

# Commande /plan
async def generate_business_plan(update: Update, context: CallbackContext):
    prompt = (
        "Génère un plan d'affaires rapide en format simple : problème, solution, cible, revenus. Reste clair et concis."
    )
    logger.info("Commande /plan reçue")
    plan = openai_query(prompt)
    await update.message.reply_text(f"Plan d'affaires :\n{plan}")

# Commande /anecdote
async def anecdote(update: Update, context: CallbackContext):
    prompt = "Raconte une anecdote courte et sarcastique sur un entrepreneur célèbre."
    logger.info("Commande /anecdote reçue")
    story = openai_query(prompt)
    await update.message.reply_text(f"Anecdote :\n{story}")

# Commande /bonsplans
async def bons_plans(update: Update, context: CallbackContext):
    prompt = "Donne un bon plan ou conseil rapide pour les entrepreneurs débutants. Bref et pratique."
    logger.info("Commande /bonsplans reçue")
    deal = openai_query(prompt)
    await update.message.reply_text(f"Bon plan :\n{deal}")

# Réponse aux messages texte
async def handle_text(update: Update, context: CallbackContext):
    user_message = update.message.text
    prompt = (
        f"Tu es une assistante sarcastique spécialisée en business et startups. Réponds au message suivant en une ou deux phrases : {user_message}"
    )
    logger.info(f"Message texte reçu : {user_message}")
    response = openai_query(prompt)
    await update.message.reply_text(response)

# Commande /help
async def help_command(update: Update, context: CallbackContext):
    message = (
        "Voici les commandes disponibles :\n"
        "/start - Présentation du bot\n"
        "/news - Obtenir des idées de business\n"
        "/plan - Générer un plan d'affaires rapide\n"
        "/anecdote - Obtenir une anecdote sarcastique\n"
        "/bonsplans - Obtenir un conseil pratique\n"
        "Ou écris-moi directement, et je te répondrai avec du sarcasme !"
    )
    await update.message.reply_text(message)

# Gestion des erreurs
async def error_handler(update: object, context: CallbackContext):
    logger.error(f"Erreur : {context.error}")
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("Oups, une erreur est survenue. Réessaye un peu plus tard !")

# Configuration du bot Telegram
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commandes du bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news_business))
    application.add_handler(CommandHandler("plan", generate_business_plan))
    application.add_handler(CommandHandler("anecdote", anecdote))
    application.add_handler(CommandHandler("bonsplans", bons_plans))
    application.add_handler(CommandHandler("help", help_command))

    # Handler pour les messages texte
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Gestion des erreurs
    application.add_error_handler(error_handler)

    logger.info("✅ Le bot démarre...")
    application.run_polling()

if __name__ == "__main__":
    main()