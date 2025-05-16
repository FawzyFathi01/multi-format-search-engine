import os
import json
from datetime import datetime
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser, FuzzyTermPlugin, WildcardPlugin
from whoosh.analysis import StemmingAnalyzer
from config import INDEX_DIR, SCHEMA

class JSONIndexer:
    def __init__(self):
        print("Initializing JSON indexer...")
        self.index_dir = os.path.join(INDEX_DIR, 'json')
        if not os.path.exists(self.index_dir):
            print(f"Creating JSON index directory at {self.index_dir}")
            os.makedirs(self.index_dir)
        
        # Create or open the index
        if not os.path.exists(os.path.join(self.index_dir, 'index')):
            print("Creating new JSON index...")
            self.ix = create_in(self.index_dir, SCHEMA)
        else:
            print("Opening existing JSON index...")
            self.ix = open_dir(self.index_dir)

    def index_file(self, file_path):
        """Index a JSON file"""
        print(f"Indexing JSON file: {file_path}")
        try:
            # Read the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add document to index
            writer = self.ix.writer()
            
            # Handle both simple and nested JSON structures
            if isinstance(data, dict):
                # If the JSON has title and content fields, use them directly
                if 'title' in data and 'content' in data:
                    writer.add_document(
                        filename=os.path.basename(file_path),
                        filetype='json',
                        content=data['content'],
                        location=file_path,
                        title=data['title'],
                        timestamp=datetime.now()
                    )
                else:
                    # Flatten nested JSON and index each field
                    flattened_data = self._flatten_json(data)
                    for key, value in flattened_data.items():
                        if value is not None:  # Skip null values
                            writer.add_document(
                                filename=os.path.basename(file_path),
                                filetype='json',
                                content=str(value),
                                location=f"{file_path}#{key}",
                                title=f"{os.path.basename(file_path)} - {key}",
                                timestamp=datetime.now()
                            )
            elif isinstance(data, list):
                # Handle JSON arrays
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        flattened_item = self._flatten_json(item)
                        for key, value in flattened_item.items():
                            if value is not None:  # Skip null values
                                writer.add_document(
                                    filename=os.path.basename(file_path),
                                    filetype='json',
                                    content=str(value),
                                    location=f"{file_path}#{i}.{key}",
                                    title=f"{os.path.basename(file_path)} - Item {i+1} - {key}",
                                    timestamp=datetime.now()
                                )
                    else:
                        # Handle simple array items
                        writer.add_document(
                            filename=os.path.basename(file_path),
                            filetype='json',
                            content=str(item),
                            location=f"{file_path}#{i}",
                            title=f"{os.path.basename(file_path)} - Item {i+1}",
                            timestamp=datetime.now()
                        )
            
            writer.commit()
            print(f"Successfully indexed {file_path}")
            return True

        except Exception as e:
            print(f"Error processing JSON file {file_path}: {str(e)}")
            return False

    def _flatten_json(self, data, prefix=''):
        """Flatten nested JSON data into key-value pairs"""
        flattened = {}
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    flattened.update(self._flatten_json(value, new_key))
                else:
                    flattened[new_key] = value
        elif isinstance(data, list):
            for i, value in enumerate(data):
                new_key = f"{prefix}[{i}]"
                if isinstance(value, (dict, list)):
                    flattened.update(self._flatten_json(value, new_key))
                else:
                    flattened[new_key] = value
        
        return flattened

    def search(self, query_text):
        """Search the index"""
        print(f"Searching JSON index for: {query_text}")
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
            print(f"Error searching JSON index: {str(e)}")
            return []

    def index_all_files(self):
        """Index all JSON files in the documents directory"""
        from config import DOCUMENTS_DIR
        print(f"Scanning for JSON files in {DOCUMENTS_DIR}")
        json_files = []
        for root, _, files in os.walk(DOCUMENTS_DIR):
            for file in files:
                if file.lower().endswith('.json'):
                    file_path = os.path.join(root, file)
                    json_files.append(file_path)
                    print(f"Found JSON file: {file_path}")
        
        print(f"Found {len(json_files)} JSON files to index")
        for file_path in json_files:
            self.index_file(file_path) 