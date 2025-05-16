import PyPDF2
import os
from typing import List, Dict, Any

class PDFScanner:
    def __init__(self):
        self.supported_extensions = ['.pdf']

    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        Scan a PDF file and extract its content and metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"Unsupported file type: {file_path}")

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"

                # Get metadata
                metadata = pdf_reader.metadata if pdf_reader.metadata else {}
                
                return {
                    'content': text_content,
                    'metadata': metadata,
                    'num_pages': len(pdf_reader.pages),
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path)
                }

        except Exception as e:
            raise Exception(f"Error scanning PDF file {file_path}: {str(e)}")

    def is_supported(self, file_path: str) -> bool:
        """
        Check if the file type is supported
        """
        return any(file_path.lower().endswith(ext) for ext in self.supported_extensions) 