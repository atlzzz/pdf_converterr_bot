import fitz  # PyMuPDF
from PIL import Image
import io
import os

def convert_pdf_to_images(pdf_data, dpi=150):
    """
    Конвертирует PDF в список изображений
    
    Args:
        pdf_data: PDF данные (bytes или file-like object)
        dpi: качество изображения (по умолчанию 150)
    
    Returns:
        tuple: (list_of_images, error_message)
    """
    try:
        # Открываем PDF из bytes или файла
        if isinstance(pdf_data, bytes):
            pdf_stream = io.BytesIO(pdf_data)
            pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
        else:
            pdf_document = fitz.open(pdf_data)
        
        images = []
        
        # Конвертируем каждую страницу
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # Создаем изображение страницы
            mat = fitz.Matrix(dpi/72, dpi/72)  # Матрица для увеличения DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Конвертируем в PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Конвертируем в RGB если нужно
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            images.append(img)
        
        pdf_document.close()
        return images, None
        
    except Exception as e:
        return None, f"Ошибка при конвертации PDF: {str(e)}"

def convert_pdf_to_images_zip(pdf_data, dpi=150):
    """
    Конвертирует PDF в ZIP архив с изображениями
    
    Returns:
        tuple: (zip_data, error_message)
    """
    import zipfile
    
    try:
        images, error = convert_pdf_to_images(pdf_data, dpi)
        if error:
            return None, error
        
        # Создаем ZIP архив в памяти
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, img in enumerate(images):
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG', quality=85)
                img_buffer.seek(0)
                
                zip_file.writestr(f"page_{i+1}.jpg", img_buffer.getvalue())
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue(), None
        
    except Exception as e:
        return None, f"Ошибка при создании ZIP архива: {str(e)}"

def convert_pdf_to_single_image(pdf_data, dpi=150):
    """
    Конвертирует первую страницу PDF в одно изображение
    
    Returns:
        tuple: (image_data, error_message)
    """
    try:
        images, error = convert_pdf_to_images(pdf_data, dpi)
        if error:
            return None, error
        
        if not images:
            return None, "PDF файл не содержит страниц"
        
        # Возвращаем только первую страницу
        img_buffer = io.BytesIO()
        images[0].save(img_buffer, format='JPEG', quality=85)
        img_buffer.seek(0)
        
        return img_buffer.getvalue(), None
        
    except Exception as e:
        return None, f"Ошибка при конвертации: {str(e)}"
