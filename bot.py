import openai
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
    raise ValueError("Le token Telegram (TELEGRAM_TOKEN) est manquant.")
if not OPENAI_API_KEY:
    raise ValueError("La clé API OpenAI (OPENAI_API_KEY) est manquante.")

openai.api_key = OPENAI_API_KEY

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

# Commande /plan
async def generate_business_plan_start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📋 *Créons ton business plan simplifié !*\n\n"
        "🚀 Première étape : Décris le *problème* que ton business résout. "
        "Exemple : Les gens manquent de temps pour cuisiner sainement."
    )
    return PROBLEME

# Commande /news
async def news_start(update: Update, context: CallbackContext):
    keyboard = [
        ["🌐 Technologie", "🍔 Restauration"],
        ["🎨 Freelancing", "📦 E-commerce"],
        ["📚 Éducation", "Autre thème"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "💡 *Choisis un thème pour tes idées de business* :\n"
        "1️⃣ 🌐 Technologie\n"
        "2️⃣ 🍔 Restauration\n"
        "3️⃣ 🎨 Freelancing\n"
        "4️⃣ 📦 E-commerce\n"
        "5️⃣ 📚 Éducation\n\n"
        "👉 Clique sur un thème ou tape un autre domaine qui t'intéresse.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return NEWS_THEME

# Commande /validation
async def validation_business(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "✅ *Validation d'idée de business* :\n\n"
        "Décris ton idée, et je te donnerai une analyse complète, incluant la viabilité, les obstacles, et des suggestions d'amélioration. 💡"
    )
    return VALIDATION

# Commande /marketing
async def marketing(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📈 *Stratégie marketing personnalisée* :\n\n"
        "Décris ton produit/service et ta cible, et je te proposerai une stratégie marketing adaptée ! 🚀"
    )
    return MARKETING

# Commande /ressources
async def resources(update: Update, context: CallbackContext):
    message = (
        "📚 *Outils et ressources pour entrepreneurs :*\n\n"
        "🛠️ [Canva](https://www.canva.com) - Crée des designs professionnels.\n"
        "📊 [Google Trends](https://trends.google.com) - Analyse les tendances du marché.\n"
        "📈 [HubSpot](https://www.hubspot.com) - CRM gratuit pour gérer tes contacts.\n"
        "🎓 [Coursera](https://www.coursera.org) - Cours en ligne gratuits.\n"
        "💡 [Startup School](https://www.startupschool.org) - Ressources pour startups.\n\n"
        "👉 Clique sur un lien pour en savoir plus !"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# Commande /notifications
async def notifications(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🔔 *Planification des notifications* :\n\n"
        "Utilise la commande /news pour choisir un thème et une heure, afin de recevoir des idées ou conseils quotidiennement. ⏰"
    )

# Configuration principale du bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Ajout des commandes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("plan", generate_business_plan_start))
    application.add_handler(CommandHandler("news", news_start))
    application.add_handler(CommandHandler("validation", validation_business))
    application.add_handler(CommandHandler("marketing", marketing))
    application.add_handler(CommandHandler("ressources", resources))
    application.add_handler(CommandHandler("notifications", notifications))

    logger.info("✅ Le bot est prêt et fonctionne...")
    application.run_polling()

if __name__ == "__main__":
    main()