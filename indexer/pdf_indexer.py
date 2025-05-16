import os
import PyPDF2
from datetime import datetime
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser, FuzzyTermPlugin, WildcardPlugin
from whoosh.analysis import StemmingAnalyzer
from config import INDEX_DIR, SCHEMA

class PDFIndexer:
    def __init__(self):
        print("Initializing PDF indexer...")
        self.index_dir = os.path.join(INDEX_DIR, 'pdf')
        if not os.path.exists(self.index_dir):
            print(f"Creating PDF index directory at {self.index_dir}")
            os.makedirs(self.index_dir)
        
        # Create or open the index
        if not os.path.exists(os.path.join(self.index_dir, 'index')):
            print("Creating new PDF index...")
            self.ix = create_in(self.index_dir, SCHEMA)
        else:
            print("Opening existing PDF index...")
            self.ix = open_dir(self.index_dir)

    def index_file(self, file_path):
        """Index a PDF file using PyPDF2 only"""
        print(f"Indexing PDF file: {file_path}")
        try:
            # Extract text using PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                for i, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                            print(f"Extracted text from page {i+1}")
                        else:
                            print(f"Warning: No text found on page {i+1}")
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {i+1} in {file_path}: {str(e)}")
                        continue

            # Add document to index
            writer = self.ix.writer()
            writer.add_document(
                filename=os.path.basename(file_path),
                filetype='pdf',
                content=text_content,
                location=file_path,
                title=os.path.basename(file_path),
                timestamp=datetime.now()
            )
            writer.commit()
            print(f"Successfully indexed {file_path}")

        except Exception as e:
            print(f"Error processing PDF {file_path}: {str(e)}")
            return False
        return True

    def search(self, query_text):
        print(f"Searching PDF index for: {query_text}")
        try:
            with self.ix.searcher() as searcher:
                parser = MultifieldParser(["content", "title"], self.ix.schema)
                parser.add_plugin(FuzzyTermPlugin())
                parser.add_plugin(WildcardPlugin())
                # دعم الاستعلامات المنطقية والعبارية
                queries = [
                    query_text,
                    f"*{query_text}*",
                    f"{query_text}~",
                    query_text.lower(),
                    query_text.upper()
                ]
                all_results = []
                for q in queries:
                    try:
                        query = parser.parse(q)
                        results = searcher.search(query, limit=20)
                        for result in results:
                            result_dict = {
                                'filename': result['filename'],
                                'filetype': result['filetype'],
                                'content': result['content'],
                                'location': result['location'],
                                'title': result['title'],
                                'score': result.score
                            }
                            if result_dict not in all_results:
                                all_results.append(result_dict)
                    except Exception as e:
                        print(f"Error with query {q}: {str(e)}")
                        continue
                all_results.sort(key=lambda x: x['score'], reverse=True)
                return all_results
        except Exception as e:
            print(f"Error searching PDF index: {str(e)}")
            return []

    def index_all_files(self):
        """Index all PDF files in the documents directory"""
        from config import DOCUMENTS_DIR
        print(f"Scanning for PDF files in {DOCUMENTS_DIR}")
        pdf_files = []
        for root, _, files in os.walk(DOCUMENTS_DIR):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    pdf_files.append(file_path)
                    print(f"Found PDF file: {file_path}")
        
        print(f"Found {len(pdf_files)} PDF files to index")
        for file_path in pdf_files:
            self.index_file(file_path) 