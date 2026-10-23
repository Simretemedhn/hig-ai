"""
src/ingestion/ocr_parser.py

Module for reading Ethiopian legal PDFs (Negarit Gazettes) 
and extracting clean page-by-page text.
"""

from pathlib import Path
from typing import Dict, List, Any
import pdfplumber


class LegalPDFParser:
    """Extracts raw text from digital Ethiopian legal PDFs."""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found at: {self.pdf_path}")

    def extract_pages(self) -> List[Dict[str, Any]]:
        """
        Parses the PDF page by page.
        
        Returns:
            List of dicts containing page_number and extracted_text.
        """
        extracted_data = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_index, page in enumerate(pdf.pages, start=1):
                # Extract raw text from page
                text = page.extract_text()
                
                if text:
                    extracted_data.append({
                        "page_number": page_index,
                        "text": text.strip()
                    })
                else:
                    # Logging page if text extraction fails (e.g., scanned image)
                    print(f"[Warning] Page {page_index} returned empty text. Might require OCR.")

        return extracted_data


if __name__ == "__main__":
    # Test script execution
    sample_path = "data/raw_pdf/amharic/sample_proclamation.pdf"
    
    print(f"--- Running OCR Parser Test on: {sample_path} ---")
    try:
        parser = LegalPDFParser(sample_path)
        pages = parser.extract_pages()
        print(f"Successfully parsed {len(pages)} pages.\n")
        
        if pages:
            print("--- First Page Sample ---")
            print(pages[0]["text"][:400])
    except FileNotFoundError as err:
        print(f"[INFO] {err}")
        print("Please place a sample PDF file inside 'data/raw_pdf/amharic/' to execute the test.")