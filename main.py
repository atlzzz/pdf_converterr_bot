from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallBackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import os
from image_to_pdf import convert_image_to_pdf  # Импорт функции конвертации
from pdf_to_image import convert_pdf_to_images_zip, convert_pdf_to_single_image

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
        self.app.add_handler(CommandHandler("pdf2img", self.pdf2img_help))
        self.app.add_handler(MessageHandler(filters.TEXT, self.handle_text))
        
        # ✅ ДОБАВЛЯЕМ ОБРАБОТЧИКИ ДЛЯ ИЗОБРАЖЕНИЙ
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(MessageHandler(filters.Document.IMAGE, self.handle_document_image))

        # ✅ НОВЫЕ ОБРАБОТЧИКИ ДЛЯ PDF ФАЙЛОВ
    self.app.add_handler(MessageHandler(filters.Document.PDF, self.handle_pdf_document))
    
    # Обработчик callback для кнопок
    self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        logger.info("Все обработчики настроены")

    async def start(self, update, context):
    await update.message.reply_text(
        "🤖 PDF Converter Bot запущен!\n\n"
        "📁 **Конвертация изображений в PDF:**\n"
        "Просто отправьте мне изображение (JPG, PNG, etc.)\n\n"
        "📄 **Конвертация PDF в изображения:**\n"
        "Отправьте PDF файл или используйте /pdf2img\n\n"
        "/help - помощь"
    )

    async def help(self, update, context):
    await update.message.reply_text(
        "📖 **Доступные функции:**\n\n"
        "🖼️ **Изображение → PDF:**\n"
        "• Отправьте изображение (JPG, JPEG, PNG, BMP, TIFF, GIF)\n\n"
        "📄 **PDF → Изображения:**\n"
        "• Отправьте PDF файл\n"
        "• Или используйте /pdf2img для справки\n\n"
        "Я поддерживаю файлы до 20MB!"
    )
        
        async def pdf2img_help(self, update, context):
    """Справка по конвертации PDF в изображения"""
    await update.message.reply_text(
        "📄 **Конвертация PDF в изображения:**\n\n"
        "Просто отправьте мне PDF файл и я:\n"
        "• Предложу варианты конвертации\n"
        "• Могу создать ZIP архив со всеми страницами\n"
        "• Или отправить первую страницу как изображение\n\n"
        "Максимальный размер файла: 20MB"
    )

    async def handle_text(self, update, context):
    await update.message.reply_text(
        "📎 Отправьте:\n"
        "• Изображение для конвертации в PDF\n"
        "• PDF файл для конвертации в изображения\n"
        "• /help для справки"
    )

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

    async def handle_pdf_document(self, update, context):
    """Обработка PDF файлов"""
    try:
        await update.message.reply_text("⏳ Обрабатываю PDF файл...")
        
        document = update.message.document
        
        # Проверяем размер файла
        if document.file_size > 20 * 1024 * 1024:  # 20MB
            await update.message.reply_text("❌ Файл слишком большой. Максимальный размер: 20MB")
            return
        
        # Получаем файл
        file = await document.get_file()
        
        # Скачиваем PDF как bytes
        pdf_data = await file.download_as_bytearray()
        
        # Создаем клавиатуру с вариантами конвертации
        keyboard = [
            [
                InlineKeyboardButton("📦 Все страницы (ZIP)", callback_data=f"zip_{document.file_id}"),
                InlineKeyboardButton("🖼️ Первая страница", callback_data=f"single_{document.file_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📄 Выберите вариант конвертации:",
            reply_markup=reply_markup
        )
        
        # Сохраняем данные PDF в контексте
        context.user_data[f"pdf_{document.file_id}"] = bytes(pdf_data)
        
    except Exception as e:
        logger.error(f"Ошибка обработки PDF: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке PDF файла")

    async def handle_callback(self, update, context):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    file_id = callback_data.split('_')[1]
    
    # Получаем сохраненные данные PDF
    pdf_data = context.user_data.get(f"pdf_{file_id}")
    
    if not pdf_data:
        await query.edit_message_text("❌ Данные PDF не найдены. Попробуйте отправить файл снова.")
        return
    
    try:
        if callback_data.startswith("zip_"):
            # Конвертируем все страницы в ZIP
            await query.edit_message_text("⏳ Создаю ZIP архив со всеми страницами...")
            
            zip_data, error = convert_pdf_to_images_zip(pdf_data)
            
            if error:
                await query.edit_message_text(f"❌ {error}")
                return
            
            # Отправляем ZIP архив
            original_name = os.path.splitext(query.message.reply_to_message.document.file_name)[0]
            zip_filename = f"{original_name}_pages.zip"
            
            await query.message.reply_document(
                document=zip_data,
                filename=zip_filename,
                caption="📦 Все страницы PDF конвертированы в изображения"
            )
            await query.edit_message_text("✅ Готово!")
            
        elif callback_data.startswith("single_"):
            # Конвертируем первую страницу
            await query.edit_message_text("⏳ Конвертирую первую страницу...")
            
            image_data, error = convert_pdf_to_single_image(pdf_data)
            
            if error:
                await query.edit_message_text(f"❌ {error}")
                return
            
            # Отправляем изображение
            original_name = os.path.splitext(query.message.reply_to_message.document.file_name)[0]
            image_filename = f"{original_name}_page1.jpg"
            
            await query.message.reply_document(
                document=image_data,
                filename=image_filename,
                caption="🖼️ Первая страница PDF"
            )
            await query.edit_message_text("✅ Готово!")
        
        # Удаляем сохраненные данные
        context.user_data.pop(f"pdf_{file_id}", None)
        
    except Exception as e:
        logger.error(f"Ошибка конвертации PDF: {e}")
        await query.edit_message_text("❌ Произошла ошибка при конвертации")

    def run(self):
        logger.info("Запускаю бота...")
        self.app.run_polling()


if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN") or "8512509552:AAHtVARIMEFMLRptxWPqNy-Yga3GabJRexk"
    bot = SimplePDFBot(token)
    bot.run()
