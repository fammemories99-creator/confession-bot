import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running fine!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# === CONFIGURATION ===
BOT_TOKEN = os.getenv("BOT_TOKEN")  # your bot token set in Render
CONFESSION_CHANNEL = os.getenv("CONFESSION_CHANNEL")  # your channel username e.g. @KMKConfession25_26

# Add multiple admin Telegram IDs
ADMINS = [5646830261]  # replace with your Telegram ID(s)

# === COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💌 Send your confession here. I’ll post it anonymously!")

# Handle confessions
async def confess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    # Log confession privately to admins
    log_message = f"🕵️‍♂️ From @{user.username or 'NoUsername'} (ID: {user.id}):\n{text}"
    for admin_id in ADMINS:
        await context.bot.send_message(chat_id=admin_id, text=log_message)

    # Post anonymously to channel
    post = f"🫣 Anonymous Confession:\n\n{text}"
    await context.bot.send_message(chat_id=CONFESSION_CHANNEL, text=post)

    await update.message.reply_text("✅ Your confession has been sent anonymously!")

# Delete a message from the confession channel (admin only)
async def delete_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id not in ADMINS:
        return
    try:
        message_id = int(context.args[0])
        await context.bot.delete_message(chat_id=CONFESSION_CHANNEL, message_id=message_id)
        await update.message.reply_text(f"🗑 Deleted message ID {message_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Block a user (admin only)
async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id not in ADMINS:
        return
    try:
        user_id = int(context.args[0])
        await context.bot.ban_chat_member(CONFESSION_CHANNEL, user_id)
        await update.message.reply_text(f"🚫 Blocked user {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# === MAIN ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("delete", delete_msg))
    app.add_handler(CommandHandler("block", block_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, confess))

    print("🤖 Bot is running on Render 24/7...")
    app.run_polling()

if __name__ == "__main__":
    main()
