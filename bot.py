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

# États pour les conversations interactives
PROBLEME, NEWS_THEME = range(2)

# Fonction pour interagir avec OpenAI
def openai_query(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,  # Réponse courte
            temperature=0.8,  # Ton légèrement créatif
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
        "⏰ /notifications - Planifie des notifications quotidiennes pour recevoir des idées ou conseils.\n"
        "❌ /cancel - Annule la commande en cours.\n\n"
        "📬 Tape une commande ou pose-moi une question directement. Je suis prêt à t’aider à réussir ! 🚀"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# Commande /plan
async def generate_business_plan_start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📋 *Créons ton business plan simplifié !*\n\n"
        "🚀 Première étape : Décris le *problème* que ton business résout. "
        "Exemple : Les gens manquent de temps pour cuisiner sainement.\n\n"
        "❌ Tape /cancel à tout moment pour annuler."
    )
    return PROBLEME

async def collect_probleme(update: Update, context: CallbackContext):
    probleme = update.message.text
    await update.message.reply_text(
        f"👍 Merci ! Maintenant, quelle est la *solution* pour résoudre ce problème ?\n\n"
        "❌ Tape /cancel à tout moment pour annuler."
    )
    return ConversationHandler.END

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
        "👉 Clique sur un thème ou tape un autre domaine qui t'intéresse.\n"
        "❌ Tape /cancel à tout moment pour annuler.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return NEWS_THEME

async def collect_news_theme(update: Update, context: CallbackContext):
    theme = update.message.text
    await update.message.reply_text(
        f"🌟 Super choix ! Voici quelques idées dans le thème : *{theme}*.\n\n"
        "💡 Exemple d'idées :\n"
        "1. Application de gestion d'équipe.\n"
        "2. Plateforme de freelance spécialisée.\n\n"
        "❌ Tape /cancel si tu veux arrêter."
    )
    return ConversationHandler.END

# Commande /validation
async def validation_business(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "✅ *Validation d'idée de business* :\n\n"
        "Décris ton idée, et je te donnerai une analyse complète, incluant la viabilité, les obstacles, et des suggestions d'amélioration. 💡"
    )

# Commande /marketing
async def marketing(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📈 *Stratégie marketing personnalisée* :\n\n"
        "Décris ton produit/service et ta cible, et je te proposerai une stratégie marketing adaptée ! 🚀"
    )

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

# Commande /cancel
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "❌ *Commande annulée.* Si tu veux recommencer, tape une nouvelle commande ou pose-moi une question !"
    )
    return ConversationHandler.END

# Gestion des messages texte non commandés
async def handle_text(update: Update, context: CallbackContext):
    user_message = update.message.text
    logger.info(f"Message reçu : {user_message}")

    # Créer le prompt pour OpenAI
    prompt = (
        f"Tu es un expert en entrepreneuriat et marketing. Réponds au message suivant avec des conseils professionnels, "
        f"en utilisant un ton sarcastique subtil, sans jamais mentionner que tu es sarcastique. "
        f"La réponse doit être courte et concise. Voici le message : {user_message}"
    )

    # Générer une réponse avec OpenAI
    response = openai_query(prompt)

    # Envoyer la réponse générée à l'utilisateur
    await update.message.reply_text(response)

# Configuration principale du bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Gestion des conversations
    plan_handler = ConversationHandler(
        entry_points=[CommandHandler("plan", generate_business_plan_start)],
        states={
            PROBLEME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_probleme)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    news_handler = ConversationHandler(
        entry_points=[CommandHandler("news", news_start)],
        states={
            NEWS_THEME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_news_theme)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Ajout des commandes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(plan_handler)
    application.add_handler(news_handler)
    application.add_handler(CommandHandler("validation", validation_business))
    application.add_handler(CommandHandler("marketing", marketing))
    application.add_handler(CommandHandler("ressources", resources))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("✅ Le bot est prêt et fonctionne...")
    application.run_polling()

if __name__ == "__main__":
    main()