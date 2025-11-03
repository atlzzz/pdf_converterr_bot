from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import os
import time
from image_to_pdf import convert_image_to_pdf
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
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(MessageHandler(filters.Document.IMAGE, self.handle_document_image))
        self.app.add_handler(MessageHandler(filters.Document.PDF, self.handle_pdf_document))
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        logger.info("Все обработчики настроены")

    async def start(self, update, context):
        await update.message.reply_text(
            "🤖 PDF Converter Bot запущен!\n\n"
            "📁 Конвертация изображений в PDF:\n"
            "Просто отправьте мне изображение (JPG, PNG, etc.)\n\n"
            "📄 Конвертация PDF в изображения:\n"
            "Отправьте PDF файл или используйте /pdf2img\n\n"
            "/help - помощь"
        )

    async def help(self, update, context):
        await update.message.reply_text(
            "📖 Доступные функции:\n\n"
            "🖼️ Изображение → PDF:\n"
            "• Отправьте изображение (JPG, JPEG, PNG, BMP, TIFF, GIF)\n\n"
            "📄 PDF → Изображения:\n"
            "• Отправьте PDF файл\n"
            "• Или используйте /pdf2img для справки\n\n"
            "Я поддерживаю файлы до 20MB!"
        )

    async def pdf2img_help(self, update, context):
        await update.message.reply_text(
            "📄 Конвертация PDF в изображения:\n\n"
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
        try:
            await update.message.reply_text("⏳ Обрабатываю изображение...")
            photo_file = await update.message.photo[-1].get_file()
            image_data = await photo_file.download_as_bytearray()
            pdf_data, error = convert_image_to_pdf(bytes(image_data), "image.jpg")
            
            if error:
                await update.message.reply_text(f"❌ {error}")
                return
            
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
        try:
            await update.message.reply_text("⏳ Обрабатываю файл...")
            document = update.message.document
            
            if document.file_size > 20 * 1024 * 1024:
                await update.message.reply_text("❌ Файл слишком большой. Максимальный размер: 20MB")
                return
            
            file = await document.get_file()
            image_data = await file.download_as_bytearray()
            pdf_data, error = convert_image_to_pdf(bytes(image_data), document.file_name)
            
            if error:
                await update.message.reply_text(f"❌ {error}")
                return
            
            original_name = os.path.splitext(document.file_name)[0]
            pdf_filename = f"{original_name}.pdf"
            
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
            logger.info("Начало обработки PDF файла")
            await update.message.reply_text("⏳ Обрабатываю PDF файл...")
            
            document = update.message.document
            logger.info(f"Получен PDF файл: {document.file_name}, размер: {document.file_size}")
            
            # Проверяем размер файла
            if document.file_size > 20 * 1024 * 1024:
                logger.warning("Файл слишком большой")
                await update.message.reply_text("❌ Файл слишком большой. Максимальный размер: 20MB")
                return
            
            # Получаем файл
            logger.info("Получаем файл из Telegram...")
            file = await document.get_file()
            
            # Скачиваем PDF как bytes
            logger.info("Скачиваем файл...")
            pdf_data = await file.download_as_bytearray()
            logger.info(f"Файл скачан, размер: {len(pdf_data)} байт")
            
            # Сохраняем данные PDF в контексте с простым ключом
            # Используем временный ID вместо file_id
            temp_id = str(int(time.time() * 1000))  # Создаем уникальный временный ID
            file_key = f"pdf_{temp_id}"
            context.user_data[file_key] = {
                'data': bytes(pdf_data),
                'filename': document.file_name
            }
            logger.info(f"Данные сохранены в context.user_data с ключом: {file_key}")
            
            # Создаем клавиатуру с вариантами конвертации
            # Используем временный ID вместо file_id в callback_data
            keyboard = [
                [
                    InlineKeyboardButton("📦 Все страницы (ZIP)", callback_data=f"zip_{temp_id}"),
                    InlineKeyboardButton("🖼️ Первая страница", callback_data=f"single_{temp_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            logger.info("Отправляем клавиатуру с вариантами выбора")
            await update.message.reply_text(
                "📄 Выберите вариант конвертации:",
                reply_markup=reply_markup
            )
            logger.info("Обработка PDF завершена успешно")
            
        except Exception as e:
            logger.error(f"Ошибка обработки PDF: {str(e)}", exc_info=True)
            await update.message.reply_text("❌ Произошла ошибка при обработке PDF файла")

    async def handle_callback(self, update, context):
        """Обработка нажатий на кнопки"""
        try:
            query = update.callback_query
            await query.answer()
            
            callback_data = query.data
            logger.info(f"Получен callback: {callback_data}")
            temp_id = callback_data.split('_')[1]
            
            # Получаем сохраненные данные PDF
            file_key = f"pdf_{temp_id}"
            pdf_info = context.user_data.get(file_key)
            
            if not pdf_info:
                logger.error(f"Данные не найдены для ключа: {file_key}")
                await query.edit_message_text("❌ Данные PDF не найдены. Попробуйте отправить файл снова.")
                return
            
            pdf_data = pdf_info['data']
            original_filename = pdf_info['filename']
            logger.info(f"Найдены данные PDF: {original_filename}, размер: {len(pdf_data)} байт")
            
            if callback_data.startswith("zip_"):
                await self._handle_zip_conversion(query, pdf_data, original_filename, file_key, context)
            elif callback_data.startswith("single_"):
                await self._handle_single_conversion(query, pdf_data, original_filename, file_key, context)
                
        except Exception as e:
            logger.error(f"Ошибка в handle_callback: {str(e)}", exc_info=True)
            await query.edit_message_text("❌ Произошла ошибка при конвертации")

    async def _handle_zip_conversion(self, query, pdf_data, original_filename, file_key, context):
        """Обработка конвертации в ZIP"""
        try:
            await query.edit_message_text("⏳ Создаю ZIP архив со всеми страницами...")
            logger.info("Начало конвертации PDF в ZIP")
            
            zip_buffer, error = convert_pdf_to_images_zip(pdf_data)
            
            if error:
                logger.error(f"Ошибка конвертации в ZIP: {error}")
                await query.edit_message_text(f"❌ {error}")
                return
            
            original_name = os.path.splitext(original_filename)[0]
            zip_filename = f"{original_name}_pages.zip"
            
            logger.info("Отправляем ZIP архив...")
            await query.message.reply_document(
                document=zip_buffer,
                filename=zip_filename,
                caption="📦 Все страницы PDF конвертированы в изображения"
            )
            await query.edit_message_text("✅ Готово!")
            logger.info("ZIP архив успешно отправлен")
            
            # Удаляем сохраненные данные
            context.user_data.pop(file_key, None)
            
        except Exception as e:
            logger.error(f"Ошибка в _handle_zip_conversion: {str(e)}", exc_info=True)
            raise

    async def _handle_single_conversion(self, query, pdf_data, original_filename, file_key, context):
        """Обработка конвертации одной страницы"""
        try:
            await query.edit_message_text("⏳ Конвертирую первую страницу...")
            logger.info("Начало конвертации первой страницы PDF")
            
            image_buffer, error = convert_pdf_to_single_image(pdf_data)
            
            if error:
                logger.error(f"Ошибка конвертации одной страницы: {error}")
                await query.edit_message_text(f"❌ {error}")
                return
            
            original_name = os.path.splitext(original_filename)[0]
            image_filename = f"{original_name}_page1.jpg"
            
            logger.info("Отправляем изображение...")
            await query.message.reply_document(
                document=image_buffer,
                filename=image_filename,
                caption="🖼️ Первая страница PDF"
            )
            await query.edit_message_text("✅ Готово!")
            logger.info("Изображение успешно отправлено")
            
            # Удаляем сохраненные данные
            context.user_data.pop(file_key, None)
            
        except Exception as e:
            logger.error(f"Ошибка в _handle_single_conversion: {str(e)}", exc_info=True)
            raise

    def run(self):
        logger.info("Запускаю бота...")
        self.app.run_polling()

if __name__ == "__main__":
    from config import BOT_TOKEN
    token = os.getenv("BOT_TOKEN") or BOT_TOKEN
    logger.info("Запуск бота...")
    bot = SimplePDFBot(token)
    bot.run()
