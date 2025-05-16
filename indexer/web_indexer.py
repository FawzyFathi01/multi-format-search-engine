import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser, FuzzyTermPlugin, WildcardPlugin
from config import INDEX_DIR, SCHEMA

from indexer.base import BaseIndexer

class WebIndexer(BaseIndexer):
    def __init__(self):
        super().__init__()
        self.filetype = 'web'
        print("Initializing Web indexer...")
        self.index_dir = os.path.join(INDEX_DIR, 'web')
        if not os.path.exists(self.index_dir):
            print(f"Creating Web index directory at {self.index_dir}")
            os.makedirs(self.index_dir)
        if not os.path.exists(os.path.join(self.index_dir, 'index')):
            print("Creating new Web index...")
            self.ix = create_in(self.index_dir, SCHEMA)
        else:
            print("Opening existing Web index...")
            self.ix = open_dir(self.index_dir)

    def process_file(self, file_path):
        """Process a web page and return a list of documents to index"""
        documents = []
        
        try:
            # Read URLs from the file
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            # Process each URL
            for url in urls:
                try:
                    # Fetch the web page
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    
                    # Parse the HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract title
                    title = soup.title.string if soup.title else url
                    
                    # Extract paragraphs
                    paragraphs = soup.find_all('p')
                    content = ' '.join(p.get_text() for p in paragraphs)
                    
                    # Create document
                    doc = {
                        'filename': url,
                        'filetype': self.filetype,
                        'content': content,
                        'location': url,
                        'title': title
                    }
                    documents.append(doc)
                except Exception as e:
                    print(f"Error processing URL {url}: {str(e)}")
                    continue
            
            return documents
        except Exception as e:
            print(f"Error processing web file {file_path}: {str(e)}")
            return []

    def index_url(self, url):
        print(f"Indexing web page: {url}")
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else url
            paragraphs = ' '.join(p.get_text(separator=' ', strip=True) for p in soup.find_all('p'))
            content = paragraphs.strip()
            writer = self.ix.writer()
            writer.add_document(
                filename=url,
                filetype='web',
                content=content,
                location=url,
                title=title,
                timestamp=datetime.now()
            )
            writer.commit()
            print(f"Successfully indexed {url}")
            return True
        except Exception as e:
            print(f"Error indexing web page {url}: {str(e)}")
            return False

    def search(self, query_text):
        print(f"Searching Web index for: {query_text}")
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
            print(f"Error searching Web index: {str(e)}")
            return []

    def index_all_files(self):
        # This function can be customized to read URLs from a file or list
        urls_file = os.path.join(os.path.dirname(__file__), 'web_urls.txt')
        if not os.path.exists(urls_file):
            print(f"No web_urls.txt file found at {urls_file}")
            return
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"Found {len(urls)} URLs to index")
        for url in urls:
            self.index_url(url) 