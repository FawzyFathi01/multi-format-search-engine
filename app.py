from flask import Flask, render_template, request, jsonify
from indexer.pdf_indexer import PDFIndexer
from indexer.txt_indexer import TextIndexer
from indexer.csv_indexer import CSVIndexer
from indexer.excel_indexer import ExcelIndexer
from indexer.json_indexer import JSONIndexer
from indexer.web_indexer import WebIndexer
import os
from config import DOCUMENTS_DIR
from sklearn.metrics import precision_score, recall_score, f1_score

app = Flask(__name__)

# Initialize indexers
print("Initializing indexers...")
indexers = {
    'pdf': PDFIndexer(),
    'txt': TextIndexer(),
    'csv': CSVIndexer(),
    'excel': ExcelIndexer(),
    'json': JSONIndexer(),
    'web': WebIndexer()
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    filetype = request.args.get('filetype', 'all')
    print(f"Received search query: {query}, filetype: {filetype}")
    if not query:
        print("Empty query received")
        return jsonify([])
    
    results = []
    if filetype and filetype != 'all':
        # Search only in the selected filetype indexer
        indexer = indexers.get(filetype)
        if indexer:
            try:
                print(f"Searching in {filetype} indexer only...")
                indexer_results = indexer.search(query)
                print(f"Found {len(indexer_results)} results in {filetype}")
                if indexer_results:
                    print(f"First result from {filetype}: {indexer_results[0]}")
                results.extend(indexer_results)
            except Exception as e:
                print(f"Error in {filetype} search: {str(e)}")
        else:
            print(f"No indexer found for filetype: {filetype}")
    else:
        # Search in all indexers
        for indexer_name, indexer in indexers.items():
            try:
                print(f"Searching in {indexer_name} indexer...")
                indexer_results = indexer.search(query)
                print(f"Found {len(indexer_results)} results in {indexer_name}")
                if indexer_results:
                    print(f"First result from {indexer_name}: {indexer_results[0]}")
                results.extend(indexer_results)
            except Exception as e:
                print(f"Error in {indexer_name} search: {str(e)}")
                continue
    
    # Sort results by score
    results.sort(key=lambda x: x['score'], reverse=True)
    print(f"Total results found: {len(results)}")
    if results:
        print(f"Top result: {results[0]}")
    
    return jsonify(results)

@app.route('/index')
def index_files():
    try:
        # Create documents directory if it doesn't exist
        if not os.path.exists(DOCUMENTS_DIR):
            os.makedirs(DOCUMENTS_DIR)
            print(f"Created documents directory at {DOCUMENTS_DIR}")
        
        # Index all files
        for indexer_name, indexer in indexers.items():
            try:
                print(f"Indexing files with {indexer_name} indexer...")
                indexer.index_all_files()
            except Exception as e:
                print(f"Error indexing files with {indexer_name}: {str(e)}")
                continue
        
        return jsonify({"status": "success", "message": "Files indexed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/metrics', methods=['POST'])
def metrics():
    """
    احسب Precision, Recall, F1-Score
    الطلب يجب أن يحتوي على:
    {
        "y_true": ["file1.txt", "file2.txt", ...],  # الملفات الصحيحة (ground truth)
        "y_pred": ["file1.txt", "file3.txt", ...]   # الملفات التي أرجعها البحث
    }
    """
    data = request.get_json()
    y_true = data.get('y_true', [])
    y_pred = data.get('y_pred', [])
    # حولهم إلى مجموعات
    y_true_set = set(y_true)
    y_pred_set = set(y_pred)
    # حساب القيم
    tp = len(y_true_set & y_pred_set)
    fp = len(y_pred_set - y_true_set)
    fn = len(y_true_set - y_pred_set)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return jsonify({
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
        "tp": tp,
        "fp": fp,
        "fn": fn
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    
    # Start indexing
    print("Starting indexing...")
    for indexer_name, indexer in indexers.items():
        try:
            print(f"Indexing files with {indexer_name} indexer...")
            indexer.index_all_files()
        except Exception as e:
            print(f"Error during indexing with {indexer_name}: {str(e)}")
            continue
    
    # Run the app
    print("Starting Flask application...")
    app.run(debug=True) 