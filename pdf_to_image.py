import fitz
import os
import logging
from menu import create_main_menu

logger = logging.getLogger(__name__)


async def convert_pdf_to_images(pdf_path):
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF файл не найден: {pdf_path}")

        logger.info(f"Начинаю конвертацию PDF: {pdf_path}")
        pdf_document = fitz.open(pdf_path)
        image_paths = []
        logger.info(f"PDF содержит {len(pdf_document)} страниц")
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            image_path = f"{os.path.splitext(pdf_path)[0]}_page_{page_num + 1}.jpg"
            pix.save(image_path, "jpeg")
            image_paths.append(image_path)

            logger.info(f"Создана страница {page_num + 1}: {image_path}")

        pdf_document.close()
        logger.info(f"Конвертация завершена, создано {len(image_paths)} изображений")
        return image_paths

    except Exception as e:
        logger.error(f"Ошибка при конвертации PDF: {e}")
        raise Exception(f"Не удалось конвертировать PDF: {e}")


async def handle_pdf(update, context):
    try:
        await update.message.reply_text("🔄 Обрабатываю PDF файл...")
        document = update.message.document
        pdf_file = await document.get_file()
        pdf_path = f"temp_pdf_{update.message.message_id}.pdf"
        await pdf_file.download_to_drive(pdf_path)
        logger.info(f"PDF скачан: {pdf_path}")
        image_paths = await convert_pdf_to_images(pdf_path)
        for i, image_path in enumerate(image_paths):
            if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                with open(image_path, 'rb') as img_file:
                    await update.message.reply_photo(
                        photo=img_file,
                        caption=f"📄 Страница {i + 1}"
                    )
                os.remove(image_path)

        os.remove(pdf_path)

        await update.message.reply_text(f"✅ Готово! Извлечено {len(image_paths)} страниц.")

        await update.message.reply_text(
            "📋 Что дальше?",
            reply_markup=create_main_menu()
        )

    except Exception as e:
        logger.error(f"Ошибка в handle_pdf: {e}")
        await update.message.reply_text(f"❌ Ошибка при обработке PDF: {e}")

        await update.message.reply_text(
            "📋 Попробуйте ещё раз:",
            reply_markup=create_main_menu()
        )
