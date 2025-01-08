import cohere
from telegram.ext import Updater, CommandHandler, CallbackContext

# Clés API
TELEGRAM_TOKEN = "7797419882:AAF-GAzNn37bdtgRB942vxLGM0NkSimQ0oo"
COHERE_API_KEY = "KqL2Y8SUnkg267IwwFHFBELHiwGKzBIo1sh294As"

# Configuration de Cohere
cohere_client = cohere.Client(COHERE_API_KEY)

# Fonction pour interagir avec l'API Cohere
def cohere_query(prompt):
    try:
        response = cohere_client.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return "Une erreur est survenue. Réessayez plus tard."

# Commande /start
def start(update, context: CallbackContext):
    message = (
        "Bienvenue sur DailyBizBot ! Voici ce que je peux faire pour toi :\n\n"
        "1️⃣ /news - Obtiens 5 idées de business\n"
        "2️⃣ /plan - Génère un business plan simple\n"
        "3️⃣ /anecdote - Reçois une anecdote motivante\n"
        "4️⃣ /bonsplans - Découvre des bons plans\n\n"
        "Tape une commande pour commencer."
    )
    update.message.reply_text(message)

# Commande /news
def news_business(update, context: CallbackContext):
    prompt = (
        "Donne-moi 5 idées de business actuelles, chacune sur un thème différent "
        "(technologie, restauration, services locaux, freelancing, e-commerce)."
    )
    news = cohere_query(prompt)
    update.message.reply_text(f"Voici 5 idées de business :\n\n{news}")

# Commande /plan
def generate_business_plan(update, context: CallbackContext):
    prompt = "Crée un business plan simple pour une idée donnée. Structure : marché, besoin, solution, revenus."
    plan = cohere_query(prompt)
    update.message.reply_text(f"Voici un exemple de business plan :\n\n{plan}")

# Commande /anecdote
def anecdote(update, context: CallbackContext):
    prompt = "Donne une courte anecdote motivante sur l'entrepreneuriat."
    anecdote = cohere_query(prompt)
    update.message.reply_text(f"Anecdote motivante :\n\n{anecdote}")

# Commande /bonsplans
def bons_plans(update, context: CallbackContext):
    prompt = "Partage un bon plan récent pour un entrepreneur débutant en France."
    bon_plan = cohere_query(prompt)
    update.message.reply_text(f"Bon plan du jour :\n\n{bon_plan}")

# Configuration du bot Telegram
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commandes du bot
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("news", news_business))
    dp.add_handler(CommandHandler("plan", generate_business_plan))
    dp.add_handler(CommandHandler("anecdote", anecdote))
    dp.add_handler(CommandHandler("bonsplans", bons_plans))

    # Lancer le bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
