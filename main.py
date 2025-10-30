from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimplePDFBot:
    def __init__(self, token):
        self.token = token
        self.app = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(MessageHandler(filters.TEXT, self.handle_text))
        logger.info("Базовые обработчики настроены")

    async def start(self, update, context):
        await update.message.reply_text(
            "🤖 PDF Converter Bot запущен!\n"
            "Отправьте изображение или PDF файл\n"
            "/help - помощь"
        )

    async def help(self, update, context):
        await update.message.reply_text(
            "📖 Просто отправьте:\n"
            "• Изображение → получите PDF\n"
            "• PDF файл → получите изображения\n\n"
            "Функции в разработке..."
        )

    async def handle_text(self, update, context):
        await update.message.reply_text("📎 Отправьте файл для конвертации")

    def run(self):
        logger.info("Запускаю бота...")
        self.app.run_polling()


if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN") or "8105302690:AAEDx8wJW8myB-vchD2xOkTpWGbJniPSsz8"
    bot = SimplePDFBot(token)
    bot.run()
