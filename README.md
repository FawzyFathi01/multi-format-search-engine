# Multi-Format Search Engine

A powerful search engine that supports multiple file formats including PDF, CSV, TXT, and JSON files.

## Features

- Multi-format support (PDF, CSV, TXT, JSON)
- Advanced search capabilities:
  - Fuzzy matching
  - Wildcard matching
  - Case-insensitive search
  - Partial word matching
- Real-time indexing
- Clean and user-friendly interface

## Project Structure

```
.
├── app.py              # Main application file
├── config.py           # Configuration settings
├── requirements.txt    # Project dependencies
├── data/
│   ├── documents/     # Directory for documents to be indexed
│   └── indexes/       # Directory for search indexes
├── indexer/
│   ├── base.py        # Base indexer class
│   ├── pdf_indexer.py # PDF file indexer
│   ├── csv_indexer.py # CSV file indexer
│   ├── txt_indexer.py # Text file indexer
│   └── json_indexer.py # JSON file indexer
├── templates/
│   └── index.html     # Main search interface
└── static/
    ├── css/
    │   └── style.css  # Styling
    └── js/
        └── main.js    # Frontend functionality
```

## Setup

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Tesseract OCR for PDF text extraction:
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

4. Place your documents in the `data/documents` directory

## Running the Application

1. Start the application:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to `http://localhost:5000`

## Search Features

- **Fuzzy Matching**: Find similar words (e.g., "laptp" finds "laptop")
- **Wildcard Matching**: Find partial words (e.g., "lap*" finds "laptop")
- **Case-insensitive**: Search works regardless of letter case
- **Partial Matching**: Find words that contain your search term

## Supported File Formats

- **PDF**: Full text search with OCR support
- **CSV**: Search across all columns
- **TXT**: Plain text file search
- **JSON**: Search in both simple and nested JSON structures

## Contributing

Feel free to submit issues and enhancement requests! 