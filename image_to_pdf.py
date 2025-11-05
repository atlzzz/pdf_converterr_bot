import os
import logging
from menu import create_main_menu

logger = logging.getLogger(__name__)


async def convert_image_to_pdf(image_path):
    try:

        from PIL import Image

        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')

            base_name = os.path.splitext(image_path)[0]
            pdf_path = f"{base_name}.pdf"

            img.save(pdf_path, "PDF", resolution=100.0)

            logger.info(f"Успешно конвертировано: {image_path} -> {pdf_path}")
            return pdf_path

    except Exception as e:
        logger.error(f"Ошибка при конвертации {image_path}: {e}")
        raise Exception(f"Не удалось конвертировать изображение в PDF: {e}")


async def handle_image(update, context):
    try:
        await update.message.reply_text("🔄 Конвертирую изображение в PDF...")

        photo_file = await update.message.photo[-1].get_file()
        image_path = f"temp_{update.message.message_id}.jpg"
        await photo_file.download_to_drive(image_path)
        pdf_path = await convert_image_to_pdf(image_path)
        with open(pdf_path, 'rb') as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename="converted.pdf",
                caption="✅ Ваш PDF файл готов!"
            )

        os.remove(image_path)
        os.remove(pdf_path)

        await update.message.reply_text(
            "📋 Что дальше?",
            reply_markup=create_main_menu()
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

        await update.message.reply_text(
            "📋 Попробуйте ещё раз:",
            reply_markup=create_main_menu()
        )
