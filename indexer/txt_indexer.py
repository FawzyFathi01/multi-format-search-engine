import os
from datetime import datetime
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser, FuzzyTermPlugin, WildcardPlugin
from whoosh.analysis import StemmingAnalyzer
from config import INDEX_DIR, SCHEMA

class TextIndexer:
    def __init__(self):
        print("Initializing Text indexer...")
        self.index_dir = os.path.join(INDEX_DIR, 'txt')
        if not os.path.exists(self.index_dir):
            print(f"Creating Text index directory at {self.index_dir}")
            os.makedirs(self.index_dir)
        
        # Create or open the index
        if not os.path.exists(os.path.join(self.index_dir, 'index')):
            print("Creating new Text index...")
            self.ix = create_in(self.index_dir, SCHEMA)
        else:
            print("Opening existing Text index...")
            self.ix = open_dir(self.index_dir)

    def index_file(self, file_path):
        """Index a text file"""
        print(f"Indexing text file: {file_path}")
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Add document to index
            writer = self.ix.writer()
            writer.add_document(
                filename=os.path.basename(file_path),
                filetype='txt',
                content=content,
                location=file_path,
                title=os.path.basename(file_path),
                timestamp=datetime.now()
            )
            writer.commit()
            print(f"Successfully indexed {file_path}")
            return True

        except Exception as e:
            print(f"Error processing text file {file_path}: {str(e)}")
            return False

    def search(self, query_text):
        """Search the index"""
        print(f"Searching Text index for: {query_text}")
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
            print(f"Error searching Text index: {str(e)}")
            return []

    def index_all_files(self):
        """Index all text files in the documents directory"""
        from config import DOCUMENTS_DIR
        print(f"Scanning for text files in {DOCUMENTS_DIR}")
        txt_files = []
        for root, _, files in os.walk(DOCUMENTS_DIR):
            for file in files:
                if file.lower().endswith('.txt'):
                    file_path = os.path.join(root, file)
                    txt_files.append(file_path)
                    print(f"Found text file: {file_path}")
        
        print(f"Found {len(txt_files)} text files to index")
        for file_path in txt_files:
            self.index_file(file_path) 