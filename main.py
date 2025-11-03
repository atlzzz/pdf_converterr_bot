from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging
import os
from image_to_pdf import convert_image_to_pdf  # Импорт функции конвертации

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
        
        # ✅ ДОБАВЛЯЕМ ОБРАБОТЧИКИ ДЛЯ ИЗОБРАЖЕНИЙ
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(MessageHandler(filters.Document.IMAGE, self.handle_document_image))
        
        logger.info("Все обработчики настроены")

    async def start(self, update, context):
        await update.message.reply_text(
            "🤖 PDF Converter Bot запущен!\n"
            "Отправьте мне изображение (JPG, PNG, etc.) и я конвертирую его в PDF!\n"
            "/help - помощь"
        )

    async def help(self, update, context):
        await update.message.reply_text(
            "📖 Просто отправьте мне изображение в одном из форматов:\n"
            "• JPG, JPEG, PNG, BMP, TIFF, GIF\n\n"
            "И я преобразую его в PDF файл!"
        )

    async def handle_text(self, update, context):
        await update.message.reply_text("📎 Отправьте изображение для конвертации в PDF")

    async def handle_photo(self, update, context):
        """Обработка фото, отправленных через интерфейс фото"""
        try:
            await update.message.reply_text("⏳ Обрабатываю изображение...")
            
            # Получаем файл самого высокого качества (последний в списке)
            photo_file = await update.message.photo[-1].get_file()
            
            # Скачиваем изображение как bytes
            image_data = await photo_file.download_as_bytearray()
            
            # Конвертируем в PDF
            pdf_data, error = convert_image_to_pdf(bytes(image_data), "image.jpg")
            
            if error:
                await update.message.reply_text(f"❌ {error}")
                return
            
            # Отправляем PDF пользователю
            await update.message.reply_document(
                document=pdf_data,
                filename="converted.pdf",
                caption="✅ Ваше изображение было конвертировано в PDF"
            )
            logger.info(f"Успешно конвертировано фото для пользователя {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки фото: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке изображения")

    async def handle_document_image(self, update, context):
        """Обработка изображений, отправленных как документ (например, JPEG файл)"""
        try:
            await update.message.reply_text("⏳ Обрабатываю файл...")
            
            document = update.message.document
            
            # Проверяем размер файла
            if document.file_size > 20 * 1024 * 1024:  # 20MB
                await update.message.reply_text("❌ Файл слишком большой. Максимальный размер: 20MB")
                return
            
            # Получаем файл
            file = await document.get_file()
            
            # Скачиваем изображение как bytes
            image_data = await file.download_as_bytearray()
            
            # Конвертируем в PDF
            pdf_data, error = convert_image_to_pdf(bytes(image_data), document.file_name)
            
            if error:
                await update.message.reply_text(f"❌ {error}")
                return
            
            # Создаем имя для PDF файла
            original_name = os.path.splitext(document.file_name)[0]
            pdf_filename = f"{original_name}.pdf"
            
            # Отправляем PDF пользователю
            await update.message.reply_document(
                document=pdf_data,
                filename=pdf_filename,
                caption="✅ Ваше изображение было конвертировано в PDF"
            )
            logger.info(f"Успешно конвертирован документ {document.file_name} для пользователя {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки документа: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке файла")

    def run(self):
        logger.info("Запускаю бота...")
        self.app.run_polling()


if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN") or "8512509552:AAHtVARIMEFMLRptxWPqNy-Yga3GabJRexk"
    bot = SimplePDFBot(token)
    bot.run()
