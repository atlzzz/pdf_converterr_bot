from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
