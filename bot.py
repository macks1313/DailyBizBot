import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import os

# Configuration des logs
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Clés API
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vérification des clés API
if not TELEGRAM_TOKEN:
    logger.error("Le token Telegram est manquant. Vérifiez la variable d'environnement TELEGRAM_T.")
if not OPENAI_API_KEY:
    logger.error("La clé API OpenAI est manquante. Vérifiez la variable d'environnement OPENAI_API.")

# Configuration de l'API OpenAI
openai.api_key = OPENAI_API_KEY

# Fonction pour interagir avec l'API OpenAI
def openai_query(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.8,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Erreur lors de la requête OpenAI : {e}")
        return "Désolé, une erreur est survenue. Réessaye plus tard."

# Commande /start
async def start(update: Update, context: CallbackContext):
    message = (
        "👋 Salut, moi c'est DailyBizBot, ton partenaire en business et marketing, mais pas que. "
        "Je suis là pour te guider, te challenger et, soyons honnêtes, te taquiner un peu aussi ! 😏\n\n"
        "Voici ce que je peux faire pour toi :\n"
        "1⃣ /news - Des idées de business qui claquent 🚀\n"
        "2⃣ /plan - Un plan simple mais impactant 📈\n"
        "3⃣ /anecdote - Une dose d'inspiration (ou d'ironie) 💡\n"
        "4⃣ /bonsplans - Les bons plans à ne pas rater 🤑\n\n"
        "💬 Dis-moi ce que tu veux savoir ou fais juste un coucou. Mais prépare-toi, je ne mâche pas mes mots !"
    )
    await update.message.reply_text(message)

# Commande /news
async def news_business(update: Update, context: CallbackContext):
    prompt = (
        "Donne-moi 5 idées de business actuelles et innovantes, sur des thèmes variés : technologie, restauration, services locaux, freelancing, et e-commerce."
    )
    logger.info("Commande /news reçue")
    ideas = openai_query(prompt)
    await update.message.reply_text(f"📢 Voici 5 idées de business pour toi :\n\n{ideas}")

# Commande /plan
async def generate_business_plan(update: Update, context: CallbackContext):
    prompt = (
        "Génère un business plan simple pour une idée donnée. Structure : problème, solution, marché cible, modèle économique, étapes clés."
    )
    logger.info("Commande /plan reçue")
    plan = openai_query(prompt)
    await update.message.reply_text(f"📝 Voici un business plan :\n\n{plan}")

# Commande /anecdote
async def anecdote(update: Update, context: CallbackContext):
    prompt = (
        "Raconte une anecdote motivante et un peu sarcastique sur un entrepreneur célèbre."
    )
    logger.info("Commande /anecdote reçue")
    story = openai_query(prompt)
    await update.message.reply_text(f"💡 Voici une anecdote :\n\n{story}")

# Commande /bonsplans
async def bons_plans(update: Update, context: CallbackContext):
    prompt = "Partage un bon plan pour les entrepreneurs débutants en 2025."
    logger.info("Commande /bonsplans reçue")
    deal = openai_query(prompt)
    await update.message.reply_text(f"🔥 Bon plan du jour :\n\n{deal}")

# Réponse aux messages texte
async def handle_text(update: Update, context: CallbackContext):
    user_message = update.message.text
    prompt = (
        f"Tu es une assistante experte en entrepreneuriat et marketing, avec une touche sarcastique. "
        f"Réponds en français de manière engageante et utile à ce message : {user_message}"
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

    logger.info("Le bot est en cours de démarrage...")
    application.run_polling()

if __name__ == "__main__":
    main()
