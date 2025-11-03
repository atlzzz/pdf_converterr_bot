import img2pdf
from PIL import Image
import os
import io

def convert_image_to_pdf(image_data, filename=None):
    try:

        if isinstance(image_data, bytes):
            image_stream = io.BytesIO(image_data)
        else:
            image_stream = image_data
        
        if filename:
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in valid_extensions:
                return None, f"Неподдерживаемый формат изображения: {file_ext}"
        
        try:
            with Image.open(image_stream) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                temp_buffer = io.BytesIO()
                img.save(temp_buffer, format='JPEG')
                temp_buffer.seek(0)
                
                pdf_data = img2pdf.convert(temp_buffer)
                
            return pdf_data, None
            
        except Exception as img_error:
            return None, f"Ошибка обработки изображения: {str(img_error)}"
        
    except Exception as e:
        return None, f"Ошибка при конвертации: {str(e)}"

def convert_image_file_to_pdf(image_path, pdf_path=None):
    """
    Версия для работы с файлами на диске
    """
    try:
        if pdf_path is None:
            base_name = os.path.splitext(image_path)[0]
            pdf_path = base_name + ".pdf"
        
        if not os.path.exists(image_path):
            return None, f"Файл {image_path} не найден"
        
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        file_ext = os.path.splitext(image_path)[1].lower()
        
        if file_ext not in valid_extensions:
            return None, f"Неподдерживаемый формат изображения: {file_ext}"
        

        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(img2pdf.convert(image_path))
        
        return pdf_path, None
        
    except Exception as e:
        return None, f"Ошибка при конвертации: {str(e)}"
