from PyPDF2 import PdfReader
from typing import List

def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks 