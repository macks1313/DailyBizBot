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
PROBLEME, SOLUTION, CIBLE, REVENUS, MARKETING, FINANCES = range(6)

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
        return "Erreur lors de la génération du contenu. Réessaye plus tard."

# Commande /start
async def start(update: Update, context: CallbackContext):
    message = (
        "Bienvenue sur *DailyBizBot* 🦾 !\n\n"
        "Voici ce que je peux faire pour toi :\n"
        "- *Idées de business* (/news)\n"
        "- *Création d'un business plan simplifié* (/plan)\n"
        "- *Stratégies marketing adaptées* (/marketing)\n"
        "- *Conseils financiers pour ton projet* (/finances)\n\n"
        "Tape une commande pour commencer ou pose-moi une question directe !"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# Gestion interactive pour /plan
async def generate_business_plan_start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Commençons la création de ton business plan !\n\n🚀 Première étape : Décris le problème que ton business résout."
    )
    return PROBLEME

async def collect_probleme(update: Update, context: CallbackContext):
    context.user_data['probleme'] = update.message.text
    await update.message.reply_text(
        "👍 Super ! Maintenant, quelle est la *solution* que tu proposes pour résoudre ce problème ?"
    )
    return SOLUTION

async def collect_solution(update: Update, context: CallbackContext):
    context.user_data['solution'] = update.message.text
    await update.message.reply_text(
        "👌 Bien ! À qui s'adresse ton produit ou service ? Décris ta *cible*."
    )
    return CIBLE

async def collect_cible(update: Update, context: CallbackContext):
    context.user_data['cible'] = update.message.text
    await update.message.reply_text(
        "✨ Presque fini ! Comment ton business va-t-il *générer des revenus* ?"
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
        f"Voici ton business plan simplifié :\n\n{business_plan}\n\n"
        "Tu veux aller plus loin ? Essaye /marketing pour une stratégie marketing ou /finances pour des conseils financiers !"
    )
    return ConversationHandler.END

# Commande /marketing
async def marketing_strategy(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Décris ton produit/service et ta cible en quelques mots pour que je puisse te proposer une stratégie marketing personnalisée."
    )
    return MARKETING

async def collect_marketing_info(update: Update, context: CallbackContext):
    user_input = update.message.text
    prompt = (
        f"Propose une stratégie marketing pour le produit/service suivant : {user_input}.\n"
        "Précise des tactiques digitales (réseaux sociaux, SEO) et des approches directes."
    )
    strategy = openai_query(prompt)
    await update.message.reply_text(f"Voici une stratégie marketing adaptée :\n\n{strategy}")
    return ConversationHandler.END

# Commande /finances
async def financial_advice(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Dis-moi combien tu souhaites investir ou ton budget initial, et je te donnerai des conseils financiers adaptés pour ton projet."
    )
    return FINANCES

async def collect_financial_info(update: Update, context: CallbackContext):
    user_input = update.message.text
    prompt = (
        f"Donne des conseils financiers pour un projet avec le budget suivant : {user_input}. "
        "Propose des stratégies de gestion des coûts, d'investissement initial, et des astuces pour maximiser les revenus."
    )
    advice = openai_query(prompt)
    await update.message.reply_text(f"Voici des conseils financiers adaptés :\n\n{advice}")
    return ConversationHandler.END

# Gestion en cas d'annulation
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Action annulée. Reviens quand tu veux !")
    return ConversationHandler.END

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

    # Gestion de la commande /marketing
    marketing_handler = ConversationHandler(
        entry_points=[CommandHandler("marketing", marketing_strategy)],
        states={
            MARKETING: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_marketing_info)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Gestion de la commande /finances
    finances_handler = ConversationHandler(
        entry_points=[CommandHandler("finances", financial_advice)],
        states={
            FINANCES: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_financial_info)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Ajout des commandes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(plan_handler)
    application.add_handler(marketing_handler)
    application.add_handler(finances_handler)

    logger.info("✅ Le bot est prêt et fonctionne...")
    application.run_polling()

if __name__ == "__main__":
    main()