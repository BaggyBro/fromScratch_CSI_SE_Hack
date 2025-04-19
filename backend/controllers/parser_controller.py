import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io

def extract_text_from_pdf(pdf_file):
    try:
        pdf_data = pdf_file.read()
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        full_text = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)
            full_text += text + "\n"

        return full_text.strip()

    except Exception as e:
        return f"Error processing PDF: {e}"
