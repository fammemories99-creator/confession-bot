import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# ==============================
# 🔧 Configuration
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # your BotFather token
CONFESSION_CHANNEL = os.getenv("CONFESSION_CHANNEL")  # e.g. "@KMKConfession25_26"
ADMINS = [5646830261]  # add more admin IDs here if needed

# ==============================
# 🌐 Flask Keep-Alive Server
# ==============================
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 KMK Confession Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ==============================
# 💬 Bot Handlers
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💌 Welcome to KMK Confession Bot!\n"
        "Send me your confession and I’ll post it anonymously.\n\n"
        "⚠️ Please keep your confession respectful and free from hate speech."
    )

# Log every user and message
async def log_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text if update.message else "(non-text message)"
    print(f"📋 User Info → ID={user.id}, Username={user.username}, Name={user.first_name} {user.last_name}, Text={text}")

# Post confessions anonymously to channel
async def confess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if not text:
        await update.message.reply_text("❌ Only text confessions are allowed.")
        return

    # Send to confession channel
    await context.bot.send_message(
        chat_id=CONFESSION_CHANNEL,
        text=f"🫣 Anonymous Confession:\n{text}"
    )

    # Notify admins privately
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"🕵️‍♂️ From @{user.username or 'NoUsername'} (ID: {user.id})\n{text}"
            )
        except Exception as e:
            print(f"Error notifying admin {admin_id}: {e}")

    await update.message.reply_text("✅ Your confession has been sent anonymously.")

# ==============================
# 🚀 Main Function
# ==============================
def main():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app_bot.add_handler(CommandHandler("start", start))

    # Log all incoming messages (for Render log display)
    app_bot.add_handler(MessageHandler(filters.ALL, log_user))

    # Confession handler (text messages only)
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, confess))

    print("🤖 KMK Confession Bot is running on Render 24/7...")
    app_bot.run_polling()

# ==============================
# 🧠 Run Flask + Bot Together
# ==============================
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    main()
