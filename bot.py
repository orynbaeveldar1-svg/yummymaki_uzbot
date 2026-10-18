import os, json, logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or "0")
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not WEBAPP_URL.startswith("https://"):
        await update.message.reply_text(
            "Добро пожаловать в Yummy maki! 🍣\n"
            "Сайт пока не подключён. Администратору нужно задать WEBAPP_URL (HTTPS) после публикации сайта."
        )
        return
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("🍣 Открыть Yummy maki", web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Добро пожаловать в Yummy maki! 🍣\nВыберите язык и оформите заказ:",
        reply_markup=kb
    )

async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = update.effective_message.web_app_data.data
    try:
        order = json.loads(raw)
        lang = order.get("lang", "ru")
        title = "🆕 Новый заказ Yummy maki" if lang == "ru" else "🆕 Yangi Yummy maki buyurtmasi"
        lines = [
            title,
            f"Имя / Ism: {order.get('name','—')}",
            f"Телефон: {order.get('phone','—')}",
            f"Адрес: {order.get('address','—')}",
            "",
            "Состав / Buyurtma:"
        ]
        for item in order.get("items", []):
            lines.append(f"• {item.get('name','')} × {item.get('qty', 0)} — {item.get('lineTotal', 0)} сум")
        lines.append(f"\nИтого / Jami: {order.get('total', 0)} сум")
        lines.append(f"Telegram ID: {update.effective_user.id}")
        await update.effective_message.reply_text(
            ("Заказ отправлен администратору. Спасибо!" if lang == "ru" else "Buyurtma administratorga yuborildi. Rahmat!")
        )
        if ADMIN_ID:
            await context.bot.send_message(ADMIN_ID, "\n".join(lines))
    except Exception:
        logging.exception("Invalid Web App order data")
        await update.effective_message.reply_text("Не удалось обработать заказ. Попробуйте ещё раз.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Нажмите /start, чтобы открыть Yummy maki.")

def main():
    if not TOKEN:
        raise SystemExit("Set BOT_TOKEN environment variable first.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    app.run_polling()

if __name__ == "__main__":
    main()
