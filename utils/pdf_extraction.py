import pdfplumber
from tqdm import tqdm

def extract_text_from_pdf(file_path):
    text = ""
    print('extracting text...')
    with pdfplumber.open(file_path) as pdf:
        for page in tqdm(pdf.pages):
            text += page.extract_text()
    return text
