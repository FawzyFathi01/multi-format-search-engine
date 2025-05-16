import os
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.analysis import StemmingAnalyzer

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory for storing documents
DOCUMENTS_DIR = os.path.join(BASE_DIR, 'data', 'documents')

# Directory for storing indexes
INDEX_DIR = os.path.join(BASE_DIR, 'data', 'indexes')

# Poppler configuration for Windows
if os.name == 'nt':  # Windows
    POPPLER_PATH = os.environ.get('POPPLER_PATH', r'C:\Program Files\poppler-23.11.0\Library\bin')
    if not os.path.exists(POPPLER_PATH):
        print(f"WARNING: Poppler not found at {POPPLER_PATH}")
        print("Please install Poppler and set POPPLER_PATH environment variable")
        print("You can download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/")

# Create directories if they don't exist
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

# Create a stemming analyzer for better search results
analyzer = StemmingAnalyzer()

# Schema for Whoosh index
SCHEMA = Schema(
    filename=ID(stored=True),
    filetype=ID(stored=True),
    content=TEXT(stored=True, analyzer=analyzer),
    location=ID(stored=True),
    title=TEXT(stored=True, analyzer=analyzer),
    timestamp=DATETIME(stored=True)
)

# NLTK settings
NLTK_DATA = {
    'stopwords': 'english',
    'punkt': True,
    'averaged_perceptron_tagger': True,
    'wordnet': True
}

# Search configuration
SEARCH_CONFIG = {
    'limit': 20,  # Maximum number of results to return
    'min_score': 0.1,  # Minimum score threshold for results
    'fuzzy_distance': 2  # Maximum edit distance for fuzzy matching
}

# File type configurations
FILE_TYPES = {
    'pdf': {
        'extensions': ['.pdf'],
        'mime_types': ['application/pdf']
    },
    'txt': {
        'extensions': ['.txt'],
        'mime_types': ['text/plain']
    },
    'csv': {
        'extensions': ['.csv'],
        'mime_types': ['text/csv']
    },
    'excel': {
        'extensions': ['.xlsx', '.xls'],
        'mime_types': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
    },
    'json': {
        'extensions': ['.json'],
        'mime_types': ['application/json']
    }
}

# Flask settings
FLASK_CONFIG = {
    'SECRET_KEY': 'your-secret-key-here',
    'DEBUG': True
} 