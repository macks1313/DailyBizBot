import openai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
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
    raise ValueError("Le token Telegram (TELEGRAM_TOKEN) est manquant dans les variables d'environnement.")
if not OPENAI_API_KEY:
    raise ValueError("La clé API OpenAI (OPENAI_API_KEY) est manquante dans les variables d'environnement.")

openai.api_key = OPENAI_API_KEY

# États pour la commande /plan
PROBLEME, SOLUTION, CIBLE, REVENUS = range(4)

# Fonction pour interagir avec OpenAI
def openai_query(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.9,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Erreur lors de la requête OpenAI : {e}")
        return "Erreur lors de la génération du contenu. Réessaye plus tard."

# Commande /start
async def start(update: Update, context: CallbackContext):
    message = (
        "Bienvenue ! Moi, c'est DailyBizBot 🦾.\n"
        "Je suis là pour t'aider à créer des idées de business et même un plan d'affaires !\n\n"
        "Voici mes commandes :\n"
        "/news - Idées de business actuelles\n"
        "/plan - Créer un business plan simplifié\n"
        "/anecdote - Une anecdote sarcastique\n"
        "/bonsplans - Conseils pour entrepreneurs débutants\n"
        "/help - Afficher les commandes disponibles\n\n"
        "Essaye une commande pour commencer !"
    )
    await update.message.reply_text(message)

# Gestion interactive pour /plan
async def generate_business_plan_start(update: Update, context: CallbackContext):
    await update.message.reply_text("Commençons à créer ton business plan simplifié !\n\n🚀 Première question : Quel est le problème que ton business résout ?")
    return PROBLEME

async def collect_probleme(update: Update, context: CallbackContext):
    context.user_data['probleme'] = update.message.text
    await update.message.reply_text("👍 Super ! Maintenant, quelle est la solution que tu proposes pour ce problème ?")
    return SOLUTION

async def collect_solution(update: Update, context: CallbackContext):
    context.user_data['solution'] = update.message.text
    await update.message.reply_text("👌 Bien ! À qui s'adresse ton produit ou service ? (décris ta cible)")
    return CIBLE

async def collect_cible(update: Update, context: CallbackContext):
    context.user_data['cible'] = update.message.text
    await update.message.reply_text("✨ Presque fini ! Comment ton business va-t-il générer des revenus ?")
    return REVENUS

async def collect_revenus(update: Update, context: CallbackContext):
    context.user_data['revenus'] = update.message.text

    # Génération du business plan avec OpenAI
    prompt = (
        f"Génère un business plan simplifié en utilisant les informations suivantes :\n"
        f"Problème : {context.user_data['probleme']}\n"
        f"Solution : {context.user_data['solution']}\n"
        f"Cible : {context.user_data['cible']}\n"
        f"Revenus : {context.user_data['revenus']}\n"
        "Sois clair et concis."
    )
    business_plan = openai_query(prompt)

    await update.message.reply_text(f"Voici un plan d'affaires simplifié basé sur tes réponses :\n\n{business_plan}")
    return ConversationHandler.END

# Gestion en cas d'annulation
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Création du business plan annulée. Reviens quand tu veux !")
    return ConversationHandler.END

# Commande /help
async def help_command(update: Update, context: CallbackContext):
    message = (
        "Voici les commandes disponibles :\n"
        "/start - Présentation du bot\n"
        "/news - Obtenir des idées de business\n"
        "/plan - Créer un business plan simplifié\n"
        "/anecdote - Obtenir une anecdote sarcastique\n"
        "/bonsplans - Obtenir un conseil pratique\n\n"
        "Si tu écris un message, je répondrai avec un soupçon de sarcasme."
    )
    await update.message.reply_text(message)

# Commande /news
async def news_business(update: Update, context: CallbackContext):
    prompt = "Donne 5 idées de business actuelles en quelques mots : technologie, restauration, freelancing, e-commerce."
    ideas = openai_query(prompt)
    await update.message.reply_text(f"Voici 5 idées de business :\n{ideas}")

# Configuration principale du bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Gestion de la commande /plan avec un ConversationHandler
    plan_handler = ConversationHandler(
        entry_points=[CommandHandler("plan", generate_business_plan_start)],
        states={
            PROBLEME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_probleme)],
            SOLUTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_solution)],
            CIBLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_cible)],
            REVENUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_revenus)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Ajout des commandes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news_business))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(plan_handler)

    logger.info("✅ Le bot est prêt et fonctionne...")
    application.run_polling()

if __name__ == "__main__":
    main()