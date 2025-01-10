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
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

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

# États pour les étapes interactives
PROBLEME, SOLUTION, CIBLE, REVENUS, VALIDATION, NEWS_THEME, NEWS_TIME = range(7)

# Initialisation du scheduler pour les notifications automatiques
scheduler = BackgroundScheduler()
scheduler.start()

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
        "✨ Je suis ton assistant entrepreneurial, prêt à t'aider à réussir ! Voici ce que je peux faire pour toi :\n\n"
        "📋 *Créer un business plan simplifié* : `/plan` – Je te guide étape par étape pour créer ton plan d'affaires.\n"
        "💡 *Découvrir des idées de business* : `/news` – Choisis un thème et reçois des idées inspirantes.\n"
        "✅ *Valider ton idée de business* : `/validation` – Je t'aide à analyser et améliorer ton idée.\n"
        "📈 *Obtenir une stratégie marketing* : `/marketing` – Je propose une stratégie adaptée à ton projet.\n"
        "🛠️ *Accéder à des ressources utiles* : `/ressources` – Une boîte à outils pour entrepreneurs.\n"
        "⏰ *Planifier des notifications quotidiennes* : `/notifications` – Reçois des idées ou conseils à l'heure de ton choix.\n\n"
        "📬 Tape une commande ou pose-moi une question directement. Prêt à commencer ? 🚀"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# Commande /news (avec sélection de thème et planification)
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

async def collect_news_theme(update: Update, context: CallbackContext):
    context.user_data['news_theme'] = update.message.text
    await update.message.reply_text(
        f"👍 Super ! Tu as choisi le thème : *{context.user_data['news_theme']}*. 🕒 Maintenant, choisis une heure pour recevoir tes idées de business chaque jour (ex : 10:00).",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return NEWS_TIME

async def collect_news_time(update: Update, context: CallbackContext):
    time = update.message.text
    context.user_data['news_time'] = time

    # Planification des notifications
    chat_id = update.message.chat_id
    theme = context.user_data['news_theme']

    # Ajouter une tâche planifiée pour envoyer des idées
    scheduler.add_job(
        send_scheduled_news,
        trigger=CronTrigger.from_crontab(f"{time.split(':')[1]} {time.split(':')[0]} * * *"),
        args=[chat_id, theme],
        id=f"news_{chat_id}",
        replace_existing=True
    )

    await update.message.reply_text(
        f"✅ Parfait ! Tu recevras des idées sur le thème *{theme}* tous les jours à *{time}*. 🚀\n"
        "💡 Tu peux changer cela à tout moment avec la commande `/notifications`.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def send_scheduled_news(chat_id, theme):
    prompt = f"Donne-moi 3 idées de business innovantes dans le domaine : {theme}."
    ideas = openai_query(prompt)
    message = f"🌟 *Idées de business pour le thème : {theme}*\n\n{ideas}"
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    await application.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

# Commande /notifications
async def notifications(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🔔 Tu veux planifier ou modifier tes notifications quotidiennes ? Utilise la commande `/news` pour choisir un thème et une heure."
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

# Configuration principale du bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers interactifs
    news_handler = ConversationHandler(
        entry_points=[CommandHandler("news", news_start)],
        states={
            NEWS_THEME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_news_theme)],
            NEWS_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_news_time)],
        },
        fallbacks=[CommandHandler("cancel", notifications)],
    )

    # Ajout des commandes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ressources", resources))
    application.add_handler(news_handler)
    application.add_handler(CommandHandler("notifications", notifications))

    logger.info("✅ Le bot est prêt et fonctionne...")
    application.run_polling()

if __name__ == "__main__":
    main()