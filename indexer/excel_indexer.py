import os
import pandas as pd
from datetime import datetime
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser, FuzzyTermPlugin, WildcardPlugin
from config import INDEX_DIR, SCHEMA

class ExcelIndexer:
    def __init__(self):
        print("Initializing Excel indexer...")
        self.index_dir = os.path.join(INDEX_DIR, 'excel')
        if not os.path.exists(self.index_dir):
            print(f"Creating Excel index directory at {self.index_dir}")
            os.makedirs(self.index_dir)
        if not os.path.exists(os.path.join(self.index_dir, 'index')):
            print("Creating new Excel index...")
            self.ix = create_in(self.index_dir, SCHEMA)
        else:
            print("Opening existing Excel index...")
            self.ix = open_dir(self.index_dir)

    def index_file(self, file_path):
        print(f"Indexing Excel file: {file_path}")
        try:
            excel_file = pd.ExcelFile(file_path)
            writer = self.ix.writer()
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                for i, row in df.iterrows():
                    content = ' '.join(str(value) for value in row.values if pd.notnull(value))
                    writer.add_document(
                        filename=os.path.basename(file_path),
                        filetype='excel',
                        content=content,
                        location=f"{file_path}#sheet_{sheet_name}_row_{i+1}",
                        title=f"{os.path.basename(file_path)} - {sheet_name} - Row {i+1}",
                        timestamp=datetime.now()
                    )
            writer.commit()
            print(f"Successfully indexed {file_path}")
            return True
        except Exception as e:
            print(f"Error processing Excel file {file_path}: {str(e)}")
            return False

    def search(self, query_text):
        print(f"Searching Excel index for: {query_text}")
        try:
            with self.ix.searcher() as searcher:
                parser = MultifieldParser(["content", "title"], self.ix.schema)
                parser.add_plugin(FuzzyTermPlugin())
                parser.add_plugin(WildcardPlugin())
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
            print(f"Error searching Excel index: {str(e)}")
            return []

    def index_all_files(self):
        from config import DOCUMENTS_DIR
        print(f"Scanning for Excel files in {DOCUMENTS_DIR}")
        excel_files = []
        for root, _, files in os.walk(DOCUMENTS_DIR):
            for file in files:
                if file.lower().endswith('.xlsx'):
                    file_path = os.path.join(root, file)
                    excel_files.append(file_path)
                    print(f"Found Excel file: {file_path}")
        print(f"Found {len(excel_files)} Excel files to index")
        for file_path in excel_files:
            self.index_file(file_path) 