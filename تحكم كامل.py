from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import base64
import hashlib
import urllib.parse
import qrcode
import io

TOKEN = "8991135489:AAGQtzaKtT91_RYLXUvCHNzw6qFruP2sveg"

ADMIN_ID = 123456789  # 8270761077 تيليجرام

user_mode = {}
history = {}

# MAIN MENU
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Base64", callback_data="base64")],
        [InlineKeyboardButton("🔢 Hex", callback_data="hex")],
        [InlineKeyboardButton("🌐 URL", callback_data="url")],
        [InlineKeyboardButton("🔑 SHA256", callback_data="sha")],
        [InlineKeyboardButton("📷 QR Code", callback_data="qr")],
        [InlineKeyboardButton("📊 My History", callback_data="history")]
    ])

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_mode.pop(update.effective_user.id, None)

    await update.message.reply_text(
        "🚀 PRO MAX TOOL BOT\nاختر أداة:",
        reply_markup=main_menu()
    )

# BUTTONS
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id

    if data in ["base64", "hex", "url", "sha", "qr"]:
        user_mode[uid] = data
        await query.edit_message_text("✍️ أرسل النص الآن:", reply_markup=main_menu())

    elif data == "history":
        user_data = history.get(uid, [])
        text = "\n\n".join(user_data[-10:]) if user_data else "لا يوجد سجل"
        await query.edit_message_text(f"📊 آخر عملياتك:\n\n{text}", reply_markup=main_menu())

# TEXT HANDLER
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text
    mode = user_mode.get(uid)

    if uid not in history:
        history[uid] = []

    result = None

    try:
        if mode == "base64":
            result = base64.b64encode(text.encode()).decode()

        elif mode == "hex":
            result = text.encode().hex()

        elif mode == "url":
            result = urllib.parse.quote(text)

        elif mode == "sha":
            result = hashlib.sha256(text.encode()).hexdigest()

        elif mode == "qr":
            img = qrcode.make(text)
            bio = io.BytesIO()
            img.save(bio, format="PNG")
            bio.seek(0)
            await update.message.reply_photo(photo=bio)
            result = "QR Generated"

        if result:
            history[uid].append(f"{mode}: {result}")

            if mode != "qr":
                await update.message.reply_text(f"✅ النتيجة:\n{result}")

    except:
        await update.message.reply_text("❌ خطأ في الإدخال")

# RUN BOT
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()