import nltk
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag

class TextProcessor:
    def __init__(self):
        # Download required NLTK data
        for resource in ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'wordnet']:
            try:
                nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
            except LookupError:
                nltk.download(resource)
        
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.punctuation = set(string.punctuation)

    def preprocess(self, text):
        """Apply all text preprocessing steps"""
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove punctuation and stopwords
        tokens = [token for token in tokens if token not in self.punctuation and token not in self.stop_words]
        
        # POS tagging
        pos_tags = pos_tag(tokens)
        
        # Lemmatization
        lemmatized = []
        for word, tag in pos_tags:
            # Convert POS tag to WordNet format
            wn_tag = self._get_wordnet_pos(tag)
            if wn_tag:
                lemmatized.append(self.lemmatizer.lemmatize(word, wn_tag))
            else:
                lemmatized.append(self.lemmatizer.lemmatize(word))
        
        return ' '.join(lemmatized)

    def _get_wordnet_pos(self, tag):
        """Convert POS tag to WordNet format"""
        tag_dict = {
            'J': 'a',  # Adjective
            'N': 'n',  # Noun
            'V': 'v',  # Verb
            'R': 'r'   # Adverb
        }
        return tag_dict.get(tag[0])

    def get_keywords(self, text, top_n=10):
        """Extract keywords from text"""
        # Preprocess text
        processed_text = self.preprocess(text)
        
        # Tokenize and count frequencies
        tokens = word_tokenize(processed_text)
        freq_dist = nltk.FreqDist(tokens)
        
        # Return top N keywords
        return [word for word, freq in freq_dist.most_common(top_n)]

    def create_snippet(self, text, query_terms, max_length=200):
        """Create a text snippet containing query terms"""
        # Find the first occurrence of any query term
        text_lower = text.lower()
        query_terms = [term.lower() for term in query_terms]
        
        # Find the position of the first query term
        first_pos = float('inf')
        for term in query_terms:
            pos = text_lower.find(term)
            if pos != -1 and pos < first_pos:
                first_pos = pos
        
        if first_pos == float('inf'):
            return text[:max_length] + '...'
        
        # Calculate start and end positions for the snippet
        start = max(0, first_pos - max_length // 2)
        end = min(len(text), first_pos + max_length // 2)
        
        # Add ellipsis if needed
        prefix = '...' if start > 0 else ''
        suffix = '...' if end < len(text) else ''
        
        return prefix + text[start:end] + suffix 