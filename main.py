from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging

from image_to_pdf import handle_image
from pdf_to_image import handle_pdf

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8105302690:AAEDx8wJW8myB-vchD2xOkTpWGbJniPSsz8"

def create_main_menu():
    keyboard = [
        [InlineKeyboardButton("📷 Изображение → PDF", callback_data="image_to_pdf")],
        [InlineKeyboardButton("📄 PDF → Изображения", callback_data="pdf_to_image")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_back_button():
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update, context):
    welcome_text = """
🤖 Добро пожаловать в PDF Converter Bot!

Выберите действие с помощью кнопок ниже:
"""
    await update.message.reply_text(
        welcome_text,
        reply_markup=create_main_menu()
    )


async def help_command(update, context):
    help_text = """
ℹ️ Помощь по использованию бота

Доступные функции:
• 📷 Конвертация изображений в PDF
• 📄 Извлечение изображений из PDF

Как использовать:
1. Нажмите нужную кнопку в меню
2. Отправьте файл соответствующего типа
3. Получите результат!

Поддерживаемые форматы:
📷 Изображения: JPG, PNG, BMP, GIF
📄 PDF: любые PDF файлы

Команды:
/start - начать работу
/menu - показать меню  
/help - помощь
"""
    await update.message.reply_text(
        help_text,
        reply_markup=create_main_menu()
    )


async def menu_command(update, context):
    await update.message.reply_text(
        "📋 Главное меню:",
        reply_markup=create_main_menu()
    )


async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "image_to_pdf":
        await query.edit_message_text(
            "📷 Конвертация изображения в PDF\n\n"
            "Отправьте изображение (JPG, PNG, etc.) и я создам PDF файл!",
            reply_markup=create_back_button()
        )

    elif data == "pdf_to_image":
        await query.edit_message_text(
            "📄 **Конвертация PDF в изображения**\n\n"
            "Отправьте PDF файл и я извлеку все страницы как изображения!",
            reply_markup=create_back_button()
        )

    elif data == "help":
        help_text = """
ℹ️ Помощь

• Изображение → PDF - отправьте фото
• PDF → Изображения - отправьте PDF файл
• Бот поддерживает популярные форматы

Выберите действие из меню и отправьте файл!
"""
        await query.edit_message_text(
            help_text,
            reply_markup=create_back_button()
        )

    elif data == "back":
        await query.edit_message_text(
            "📋 Главное меню:",
            reply_markup=create_main_menu()
        )


async def handle_text(update, context):
    text = update.message.text.lower()

    if text in ["меню", "menu", "кнопки", "start"]:
        await update.message.reply_text(
            "📋 Главное меню:",
            reply_markup=create_main_menu()
        )
    else:
        await update.message.reply_text(
            "🤖 Используйте кнопки меню для конвертации файлов:\n\n"
            "• 📷 Изображение → PDF\n"
            "• 📄 PDF → Изображения\n\n"
            "Или команды:\n"
            "/start - начать работу\n"
            "/menu - показать меню\n"
            "/help - помощь",
            reply_markup=create_main_menu()
        )


async def error_handler(update, context):
    logger.error(f"Ошибка: {context.error}")

    try:
        if update and hasattr(update, 'effective_chat'):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Произошла непредвиденная ошибка. Попробуйте еще раз.",
                reply_markup=create_main_menu()
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения об ошибке: {e}")



def setup_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_error_handler(error_handler)

    return application


def main():
    try:
        app = setup_bot()
        logger.info("🤖 Бот запускается...")
        logger.info("✅ Все модули подключены: image_to_pdf, pdf_to_image")
        logger.info("✅ Токен установлен, бот готов к работе!")
        app.run_polling()
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    main()
