import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Configuration de l'API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Fonction pour interagir avec l'API OpenAI
def openai_query(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return "Une erreur est survenue. Réessayez plus tard."

# Commande /start
async def start(update: Update, context: CallbackContext):
    message = (
        "👋 Bienvenue sur DailyBizBot, ton assistant préféré en entrepreneuriat et marketing ! 🎯\n\n"
        "Voici ce que je peux faire pour toi :\n\n"
        "1⃣ /news - Obtiens 5 idées de business brillantes ✨\n"
        "2⃣ /plan - Génère un business plan simple et efficace 📈\n"
        "3⃣ /anecdote - Une anecdote motivante pour te booster 🚀\n"
        "4⃣ /bonsplans - Découvre des bons plans irrésistibles 💡\n\n"
        "💬 Et si tu veux discuter, je suis là pour toi. Pose-moi tes questions ou partage tes idées, mais attention, je ne mâche pas mes mots ! 😏\n\n"
        "Tape une commande pour commencer ou dis-moi ce qui te passe par la tête."
    )
    await update.message.reply_text(message)

# Commande /news
async def news_business(update: Update, context: CallbackContext):
    prompt = (
        "Donne-moi 5 idées de business actuelles, chacune sur un thème différent "
        "(technologie, restauration, services locaux, freelancing, e-commerce)."
    )
    news = openai_query(prompt)
    await update.message.reply_text(f"📢 Voici 5 idées de business pour toi :\n\n{news}")

# Commande /plan
async def generate_business_plan(update: Update, context: CallbackContext):
    prompt = "Crée un business plan simple pour une idée donnée. Structure : marché, besoin, solution, revenus."
    plan = openai_query(prompt)
    await update.message.reply_text(f"📝 Voici un exemple de business plan :\n\n{plan}")

# Commande /anecdote
async def anecdote(update: Update, context: CallbackContext):
    prompt = "Donne une courte anecdote motivante sur l'entrepreneuriat."
    anecdote = openai_query(prompt)
    await update.message.reply_text(f"💡 Anecdote motivante :\n\n{anecdote}")

# Commande /bonsplans
async def bons_plans(update: Update, context: CallbackContext):
    prompt = "Partage un bon plan récent pour un entrepreneur débutant en France."
    bon_plan = openai_query(prompt)
    await update.message.reply_text(f"🔥 Bon plan du jour :\n\n{bon_plan}")

# Réponse aux messages texte
async def handle_text(update: Update, context: CallbackContext):
    user_message = update.message.text
    prompt = f"Tu es une assistante experte en entrepreneuriat et marketing. Réponds en français de manière concise et engageante à ce message utilisateur : {user_message}"
    response = openai_query(prompt)
    await update.message.reply_text(response)

# Configuration du bot Telegram
def main():
    # Récupérer le token Telegram depuis les variables d'environnement
    telegram_token = os.getenv("TELEGRAM_TOKEN")

    # Créer l'application
    application = Application.builder().token(telegram_token).build()

    # Commandes du bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news_business))
    application.add_handler(CommandHandler("plan", generate_business_plan))
    application.add_handler(CommandHandler("anecdote", anecdote))
    application.add_handler(CommandHandler("bonsplans", bons_plans))

    # Handler pour les messages texte
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Lancer le bot
    application.run_polling()

if __name__ == "__main__":
    main()
