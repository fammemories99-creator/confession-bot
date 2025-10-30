# ============================================================
# Telegram Confession Bot with Flask (Render 24/7 Hosting)
# ============================================================

import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ============================================================
# FLASK KEEP-ALIVE SERVER
# ============================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 KMK Confession Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))  # Render detects 8080 automatically
    app.run(host='0.0.0.0', port=port)

# ============================================================
# TELEGRAM BOT CONFIGURATION
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CONFESSION_CHANNEL = os.getenv("CONFESSION_CHANNEL")

# Multiple admins (Telegram user IDs)
ADMINS = [5646830261]  # Add more admin IDs if needed

# ============================================================
# BOT COMMANDS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💌 Welcome to KMK Confession Bot!\n\n"
        "Send me your confession and I’ll post it anonymously in the channel."
    )

async def confess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text.strip()

    if not text:
        await update.message.reply_text("Please send a text message only.")
        return

    # Log confession privately to admins
    log_message = f"🕵️‍♂️ From @{user.username or 'NoUsername'} (ID: {user.id}):\n{text}"
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=log_message)
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

    # Post anonymously to the confession channel
    post = f"🫣 Anonymous Confession:\n\n{text}"
    try:
        await context.bot.send_message(chat_id=CONFESSION_CHANNEL, text=post)
        await update.message.reply_text("✅ Your confession has been posted anonymously!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to post confession: {e}")

async def delete_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id not in ADMINS:
        return
    try:
        message_id = int(context.args[0])
        await context.bot.delete_message(chat_id=CONFESSION_CHANNEL, message_id=message_id)
        await update.message.reply_text(f"🗑 Deleted message ID {message_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error deleting message: {e}")

async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id not in ADMINS:
        return
    try:
        user_id = int(context.args[0])
        await context.bot.ban_chat_member(CONFESSION_CHANNEL, user_id)
        await update.message.reply_text(f"🚫 Blocked user {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error blocking user: {e}")

async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id not in ADMINS:
        return
    admin_list = "\n".join(str(a) for a in ADMINS)
    await update.message.reply_text(f"👑 Current Admins:\n{admin_list}")

# ============================================================
# MAIN APP FUNCTION
# ============================================================

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set in Render Environment Variables!")
    if not CONFESSION_CHANNEL:
        raise ValueError("CONFESSION_CHANNEL not set in Render Environment Variables!")

    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("delete", delete_msg))
    app_telegram.add_handler(CommandHandler("block", block_user))
    app_telegram.add_handler(CommandHandler("admins", list_admins))

    # Message handler (confession messages)
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, confess))

    print("🤖 Telegram Confession Bot is now running...")
    app_telegram.run_polling()

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()  # Start keep-alive web server
    main()                                      # Run Telegram bot
