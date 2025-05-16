import os
import pandas as pd
from datetime import datetime
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser, FuzzyTermPlugin, WildcardPlugin
from whoosh.analysis import StemmingAnalyzer, StandardAnalyzer
from config import INDEX_DIR, SCHEMA

class CSVIndexer:
    def __init__(self):
        print("Initializing CSV indexer...")
        self.index_dir = os.path.join(INDEX_DIR, 'csv')
        if not os.path.exists(self.index_dir):
            print(f"Creating CSV index directory at {self.index_dir}")
            os.makedirs(self.index_dir)
        
        # Create or open the index
        if not os.path.exists(os.path.join(self.index_dir, 'index')):
            print("Creating new CSV index...")
            self.ix = create_in(self.index_dir, SCHEMA)
        else:
            print("Opening existing CSV index...")
            self.ix = open_dir(self.index_dir)

    def index_file(self, file_path):
        """Index a CSV file"""
        print(f"Indexing CSV file: {file_path}")
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Process each row
            writer = self.ix.writer()
            for i, row in df.iterrows():
                # Convert row to string representation with column names
                content_parts = []
                for col_name, value in row.items():
                    if pd.notna(value):  # Only include non-null values
                        content_parts.append(f"{col_name}: {value}")
                
                content = ' '.join(content_parts)
                
                # Add document to index
                writer.add_document(
                    filename=os.path.basename(file_path),
                    filetype='csv',
                    content=content,
                    location=f'row_{i+1}',
                    title=f'{os.path.basename(file_path)} - Row {i+1}',
                    timestamp=datetime.now()
                )
            
            writer.commit()
            print(f"Successfully indexed {file_path}")
            return True

        except Exception as e:
            print(f"Error processing CSV file {file_path}: {str(e)}")
            return False

    def search(self, query_text):
        """Search the index"""
        print(f"Searching CSV index for: {query_text}")
        try:
            with self.ix.searcher() as searcher:
                # Create a parser that searches in both title and content
                parser = MultifieldParser(["content", "title"], self.ix.schema)
                parser.add_plugin(FuzzyTermPlugin())  # Add fuzzy matching
                parser.add_plugin(WildcardPlugin())   # Add wildcard matching
                
                # Try different query variations
                queries = [
                    query_text,                    # Original query
                    f"*{query_text}*",            # Wildcard match
                    f"{query_text}~",             # Fuzzy match
                    query_text.lower(),           # Lowercase
                    query_text.upper()            # Uppercase
                ]
                
                all_results = []
                for q in queries:
                    try:
                        # Parse the query
                        query = parser.parse(q)
                        print(f"Trying query: {q}")
                        
                        # Search with fuzzy matching
                        results = searcher.search(query, limit=20)
                        print(f"Found {len(results)} results for query: {q}")
                        
                        # Add results to all_results
                        for result in results:
                            result_dict = {
                                'filename': result['filename'],
                                'filetype': result['filetype'],
                                'content': result['content'],
                                'location': result['location'],
                                'title': result['title'],
                                'score': result.score
                            }
                            # Only add if not already in results
                            if result_dict not in all_results:
                                all_results.append(result_dict)
                    except Exception as e:
                        print(f"Error with query {q}: {str(e)}")
                        continue
                
                # Sort results by score
                all_results.sort(key=lambda x: x['score'], reverse=True)
                
                # Print debug information
                print(f"Total unique results found: {len(all_results)}")
                for i, result in enumerate(all_results):
                    print(f"Result {i+1}:")
                    print(f"  Title: {result['title']}")
                    print(f"  Filename: {result['filename']}")
                    print(f"  Score: {result['score']}")
                    if result['content']:
                        print(f"  Content preview: {result['content'][:100]}...")
                
                return all_results
        except Exception as e:
            print(f"Error searching CSV index: {str(e)}")
            return []

    def index_all_files(self):
        """Index all CSV files in the documents directory"""
        from config import DOCUMENTS_DIR
        print(f"Scanning for CSV files in {DOCUMENTS_DIR}")
        csv_files = []
        for root, _, files in os.walk(DOCUMENTS_DIR):
            for file in files:
                if file.lower().endswith('.csv'):
                    file_path = os.path.join(root, file)
                    csv_files.append(file_path)
                    print(f"Found CSV file: {file_path}")
        
        print(f"Found {len(csv_files)} CSV files to index")
        for file_path in csv_files:
            self.index_file(file_path) 