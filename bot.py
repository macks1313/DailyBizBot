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
            max_tokens=300,  # Réponse plus détaillée pour certains cas
            temperature=0.7,  # Ton légèrement créatif
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
        "📋 /plan - Génère un business plan avec l'IA étape par étape.\n"
        "💡 /news - Obtiens des idées de business générées par l'IA selon un thème.\n"
        "✅ /validation - Analyse ton idée de business avec l'IA.\n"
        "📈 /marketing - Génère une stratégie marketing adaptée avec l'IA.\n"
        "🛠️ /ressources - Reçois des ressources générées par l'IA pour entrepreneurs.\n"
        "⏰ /notifications - Planifie des notifications d'idées ou conseils.\n"
        "❌ /cancel - Annule une commande en cours.\n\n"
        "📬 Pose-moi une question ou tape une commande, je suis prêt à t’aider ! 🚀"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# Commande /plan
async def generate_business_plan_start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📋 *Créons ton business plan simplifié !*\n\n"
        "🚀 Première étape : Décris le *problème* que ton business résout.\n"
        "❌ Tape /cancel à tout moment pour annuler."
    )
    return PROBLEME

async def collect_probleme(update: Update, context: CallbackContext):
    probleme = update.message.text
    context.user_data['probleme'] = probleme

    # Utilisation de l'IA pour générer un plan
    prompt = (
        f"Génère une section d'un business plan basé sur ce problème : {probleme}. "
        "Présente la solution et les bénéfices principaux."
    )
    response = openai_query(prompt)
    await update.message.reply_text(f"📋 Voici une idée pour ton plan :\n\n{response}")
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
        "👉 Clique sur un thème ou tape un autre domaine.\n"
        "❌ Tape /cancel à tout moment pour annuler.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return NEWS_THEME

async def collect_news_theme(update: Update, context: CallbackContext):
    theme = update.message.text
    prompt = f"Génère 5 idées de business innovantes dans le domaine : {theme}."
    response = openai_query(prompt)
    await update.message.reply_text(f"🌟 Voici des idées pour le thème *{theme}* :\n\n{response}")
    return ConversationHandler.END

# Commande /validation
async def validation_business(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "✅ *Validation d'idée de business* :\n\n"
        "Décris ton idée et je l'analyserai avec l'IA pour te donner des conseils."
    )

async def handle_validation(update: Update, context: CallbackContext):
    idea = update.message.text
    prompt = f"Analyse cette idée de business : {idea}. Inclut les avantages, inconvénients, et suggestions d'amélioration."
    response = openai_query(prompt)
    await update.message.reply_text(f"📊 Voici l'analyse :\n\n{response}")

# Commande /marketing
async def marketing(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📈 *Stratégie marketing personnalisée* :\n\n"
        "Décris ton produit/service et ta cible, et je te proposerai une stratégie marketing adaptée avec l'IA ! 🚀"
    )

async def handle_marketing(update: Update, context: CallbackContext):
    description = update.message.text
    prompt = f"Génère une stratégie marketing pour : {description}. Inclut réseaux sociaux, SEO et publicité."
    response = openai_query(prompt)
    await update.message.reply_text(f"📈 Voici une stratégie marketing :\n\n{response}")

# Commande /ressources
async def resources(update: Update, context: CallbackContext):
    prompt = (
        "Liste 5 outils utiles pour les entrepreneurs avec une brève description de leur utilité. "
        "Inclut des outils pour le marketing, la gestion et le design."
    )
    response = openai_query(prompt)
    await update.message.reply_text(f"🛠️ *Ressources pour entrepreneurs* :\n\n{response}")

# Commande /cancel
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "❌ *Commande annulée.* Si tu veux recommencer, tape une nouvelle commande ou pose-moi une question !"
    )
    return ConversationHandler.END

# Gestion des messages texte non commandés
async def handle_text(update: Update, context: CallbackContext):
    user_message = update.message.text
    prompt = (
        f"Tu es un expert en entrepreneuriat et marketing. Réponds à ce message avec des conseils professionnels, "
        f"en utilisant un ton sarcastique subtil, sans jamais mentionner que tu es sarcastique. "
        f"La réponse doit être courte et concise. Voici le message : {user_message}"
    )
    response = openai_query(prompt)
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_validation))
    application.add_handler(CommandHandler("marketing", marketing))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_marketing))
    application.add_handler(CommandHandler("ressources", resources))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("✅ Le bot est prêt et fonctionne...")
    application.run_polling()

if __name__ == "__main__":
    main()