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
    raise ValueError("Le token Telegram (TELEGRAM_TOKEN) est manquant.")
if not OPENAI_API_KEY:
    raise ValueError("La clé API OpenAI (OPENAI_API_KEY) est manquante.")

openai.api_key = OPENAI_API_KEY

# États pour les étapes interactives
PROBLEME, SOLUTION, CIBLE, REVENUS, MARKETING, VALIDATION = range(6)

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
        "🔍 *Découvrir des idées de business* : /news\n"
        "📋 *Créer un business plan* : /plan\n"
        "📈 *Stratégies marketing* : /marketing\n"
        "✅ *Valider une idée de business* : /validation\n"
        "🛠️ *Accéder à des outils et ressources* : /ressources\n\n"
        "⚡ Pose-moi une question ou utilise une commande pour commencer !\n"
        "💡 N'oublie pas : les entrepreneurs audacieux réussissent toujours ! 🚀"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# Gestion interactive pour /plan
async def generate_business_plan_start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📋 *Créons ton business plan simplifié !*\n\n"
        "🚀 Première étape : Décris le *problème* que ton business résout. "
        "Exemple : Les gens manquent de temps pour cuisiner sainement."
    )
    return PROBLEME

async def collect_probleme(update: Update, context: CallbackContext):
    context.user_data['probleme'] = update.message.text
    await update.message.reply_text(
        "👍 Super ! Maintenant, quelle est la *solution* que tu proposes pour résoudre ce problème ?\n"
        "Exemple : Je livre des repas sains et équilibrés directement chez eux."
    )
    return SOLUTION

async def collect_solution(update: Update, context: CallbackContext):
    context.user_data['solution'] = update.message.text
    await update.message.reply_text(
        "👌 Bien joué ! À qui s'adresse ton produit ou service ? Décris ta *cible*.\n"
        "Exemple : Les jeunes actifs entre 25 et 40 ans vivant en ville."
    )
    return CIBLE

async def collect_cible(update: Update, context: CallbackContext):
    context.user_data['cible'] = update.message.text
    await update.message.reply_text(
        "✨ Dernière étape ! Comment ton business va-t-il *générer des revenus* ?\n"
        "Exemple : Un abonnement mensuel à 50 €."
    )
    return REVENUS

async def collect_revenus(update: Update, context: CallbackContext):
    context.user_data['revenus'] = update.message.text

    # Génération du business plan avec OpenAI
    prompt = (
        f"Génère un business plan simplifié en utilisant les informations suivantes :\n"
        f"- Problème : {context.user_data['probleme']}\n"
        f"- Solution : {context.user_data['solution']}\n"
        f"- Cible : {context.user_data['cible']}\n"
        f"- Revenus : {context.user_data['revenus']}\n"
        "Présente-le sous un format clair et structuré."
    )
    business_plan = openai_query(prompt)

    await update.message.reply_text(
        f"🚀 *Ton business plan est prêt !*\n\n{business_plan}\n\n"
        "🔔 Tu peux maintenant explorer d'autres fonctionnalités comme :\n"
        "📈 Stratégies marketing : /marketing\n"
        "✅ Validation d'idée : /validation\n"
        "🛠️ Outils pratiques : /ressources"
    )
    return ConversationHandler.END

# Commande /news
async def news_business(update: Update, context: CallbackContext):
    prompt = "Donne 5 idées de business innovantes et actuelles dans différents domaines."
    ideas = openai_query(prompt)
    await update.message.reply_text(f"💡 *Idées de business à explorer :*\n\n{ideas}")

# Commande /validation
async def validation_business(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "💭 Décris ton idée de business et je te dirai si elle est viable, avec des conseils pour l'améliorer."
    )
    return VALIDATION

async def collect_validation(update: Update, context: CallbackContext):
    user_input = update.message.text
    prompt = (
        f"Analyse l'idée de business suivante et donne une évaluation complète : {user_input}.\n"
        "Inclut la viabilité, les obstacles potentiels, et des suggestions d'amélioration."
    )
    evaluation = openai_query(prompt)
    await update.message.reply_text(f"📊 *Analyse de ton idée :*\n\n{evaluation}")
    return ConversationHandler.END

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

# Gestion en cas d'annulation
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("❌ *Action annulée.* Reviens quand tu veux pour continuer !")
    return ConversationHandler.END

# Configuration principale du bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers interactifs
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

    validation_handler = ConversationHandler(
        entry_points=[CommandHandler("validation", validation_business)],
        states={
            VALIDATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_validation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Ajout des commandes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news_business))
    application.add_handler(CommandHandler("ressources", resources))
    application.add_handler(plan_handler)
    application.add_handler(validation_handler)

    logger.info("✅ Le bot est prêt et fonctionne...")
    application.run_polling()

if __name__ == "__main__":
    main()