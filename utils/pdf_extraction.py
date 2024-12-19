from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm
import re

def extract_text_from_page(image):
    return pytesseract.image_to_string(image)

def clean_text(text):
    patterns = [
        # Email addresses
        (r'\S+@\S+\.\S+', ''),
        
        # Citations:
        # [1] or [1,2] or [1-3] style
        (r'\[[\d,\s-]+\]', ''),
        
        # (Author, YEAR) style
        (r'\([A-Za-z]+,\s*\d{4}[a-z]?\)', ''),
        
        # (Author et al., YEAR) style
        (r'\([A-Za-z]+\s+et\s+al\.,?\s*\d{4}[a-z]?\)', ''),
        
        # Multiple author citations (Smith and Jones, 2020)
        (r'\([A-Za-z]+\s+(?:and|&)\s+[A-Za-z]+,\s*\d{4}[a-z]?\)', ''),
        
        # Figure and table captions:
        # Full line captions
        (r'(?m)^(?:Figure|Fig\.|Table)\s+\d+[.:][^\n]+$', ''),
        
        # Inline captions
        (r'(?:Figure|Fig\.|Table)\s+\d+[.:][^.]+\.', ''),
        
        # Supplementary figure references
        (r'(?:Supplementary|Supp\.)\s+(?:Figure|Fig\.|Table)\s+\d+[.:][^.]+\.', ''),
        
        # Extended figure references
        (r'(?:see|c\.f\.|compare|refer to)\s+(?:Figure|Fig\.|Table)\s+\d+', ''),
        
        # Clean up any author affiliations with emails
        (r'(?m)^.*@.*$', ''),
        
        # Clean up resulting whitespace
        (r'\s+', ' '),
        (r'\n\s*\n+', '\n\n')
    ]
    
    # Apply all patterns
    cleaned_text = text
    for pattern, replacement in patterns:
        cleaned_text = re.sub(pattern, replacement, cleaned_text)
    
    return cleaned_text.strip()

def extract_text_from_pdf(file_path):
    full_text = []
    
    print("convert_from_path...")
    pages = convert_from_path(file_path)

    print("extract_text_from_page...")
    for page in tqdm(pages):
        text = extract_text_from_page(page)
        full_text.append(text)
    
    full_text = " ".join(full_text)
    return clean_text(full_text)
