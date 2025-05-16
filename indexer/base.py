from abc import ABC, abstractmethod
from datetime import datetime
from whoosh.fields import Schema, ID, TEXT, DATETIME
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import FuzzyTerm, Wildcard
from whoosh.analysis import StemmingAnalyzer
import os

from config import INDEX_DIR, SCHEMA
from utils.text_processor import TextProcessor

class BaseIndexer(ABC):
    def __init__(self):
        self.text_processor = TextProcessor()
        self.schema = Schema(
            filename=ID(stored=True),
            filetype=ID(stored=True),
            content=TEXT(stored=True),
            location=ID(stored=True),
            title=TEXT(stored=True),
            timestamp=DATETIME(stored=True)
        )
        self._ensure_index()
        self.analyzer = StemmingAnalyzer()
        self.query_parser = QueryParser("content", schema=SCHEMA)

    def _ensure_index(self):
        """Ensure the index directory exists and create it if it doesn't"""
        if not os.path.exists(INDEX_DIR):
            os.makedirs(INDEX_DIR)
        
        try:
            self.ix = open_dir(INDEX_DIR)
        except:
            # If index doesn't exist, create it
            self.ix = create_in(INDEX_DIR, SCHEMA)

    @abstractmethod
    def process_file(self, file_path):
        """Process a file and return a list of documents to index"""
        pass

    def index_file(self, file_path):
        """Index a file using the Whoosh indexer"""
        try:
            # Process the file
            documents = self.process_file(file_path)
            
            # Get the writer
            writer = self.ix.writer()
            
            # Add each document to the index
            for doc in documents:
                writer.add_document(
                    filename=doc['filename'],
                    filetype=doc['filetype'],
                    content=doc['content'],
                    location=doc['location'],
                    title=doc['title'],
                    timestamp=datetime.now()
                )
            
            # Commit the changes
            writer.commit()
            return True
        except Exception as e:
            print(f"Error indexing file {file_path}: {str(e)}")
            return False

    def index_document(self, path, content, metadata=None):
        """Index a document with its content and metadata"""
        writer = self.ix.writer()
        try:
            writer.add_document(
                path=path,
                content=content,
                title=metadata.get('title', '') if metadata else '',
                created=metadata.get('created', datetime.now()) if metadata else datetime.now(),
                modified=metadata.get('modified', datetime.now()) if metadata else datetime.now()
            )
            writer.commit()
            return True
        except Exception as e:
            writer.cancel()
            print(f"Error indexing document {path}: {str(e)}")
            return False

    def search(self, query, filetype=None, limit=20):
        """Search the index with various query types"""
        try:
            # Create a searcher
            searcher = self.ix.searcher()
            
            # Parse the query
            if ' AND ' in query:
                # Handle AND queries
                terms = query.split(' AND ')
                q = MultifieldParser(['content', 'title'], self.schema).parse(' AND '.join(terms))
            elif ' OR ' in query:
                # Handle OR queries
                terms = query.split(' OR ')
                q = MultifieldParser(['content', 'title'], self.schema).parse(' OR '.join(terms))
            elif '*' in query:
                # Handle wildcard queries
                q = Wildcard('content', query)
            elif '~' in query:
                # Handle fuzzy queries
                term = query.replace('~', '')
                q = FuzzyTerm('content', term)
            else:
                # Handle phrase queries
                q = QueryParser('content', self.schema).parse(query)
            
            # Apply filetype filter if specified
            if filetype:
                q = q & QueryParser('filetype', self.schema).parse(filetype)
            
            # Execute the search
            results = searcher.search(q, limit=limit)
            
            # Process results
            processed_results = []
            for result in results:
                processed_results.append({
                    'filename': result['filename'],
                    'filetype': result['filetype'],
                    'content': result['content'],
                    'location': result['location'],
                    'title': result['title'],
                    'score': result.score
                })
            
            return processed_results
        except Exception as e:
            print(f"Error searching: {str(e)}")
            return []
        finally:
            searcher.close()

    def clear_index(self):
        """Clear all documents from the index"""
        writer = self.ix.writer()
        try:
            writer.delete_by_query(None)
            writer.commit()
            return True
        except Exception as e:
            writer.cancel()
            print(f"Error clearing index: {str(e)}")
            return False 