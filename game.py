from pypdf import PdfReader

def load_pdf_text(file_path):
    reader = PdfReader(file_path)
    extracted_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text