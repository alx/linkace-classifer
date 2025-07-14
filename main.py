import re
import json
import pickle
from urllib.parse import urlparse, parse_qs
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional
import pandas as pd
from pathlib import Path

# Optional ML imports (install with: pip install scikit-learn)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: scikit-learn not available. Only rule-based classification will work.")


class URLClassifier:
    def __init__(self):
        self.categories = {}  # category -> set of domains/patterns
        self.domain_patterns = defaultdict(set)  # category -> domain patterns
        self.path_patterns = defaultdict(set)   # category -> path patterns
        self.keyword_patterns = defaultdict(set)  # category -> keywords
        self.ml_model = None
        self.ml_vectorizer = None
        
    def load_url_lists(self, data_source, format_type='auto'):
        """
        Load classified URLs from various formats
        
        Args:
            data_source: Can be:
                - Dict: {'category1': ['url1', 'url2'], 'category2': [...]}
                - File path to JSON, CSV, or text files
                - Directory path containing category files
            format_type: 'auto', 'json', 'csv', 'txt', 'directory'
        """
        if isinstance(data_source, dict):
            self._load_from_dict(data_source)
        elif isinstance(data_source, (str, Path)):
            path = Path(data_source)
            if path.is_dir():
                self._load_from_directory(path)
            elif format_type == 'auto':
                if path.suffix.lower() == '.json':
                    self._load_from_json(path)
                elif path.suffix.lower() == '.csv':
                    self._load_from_csv(path)
                else:
                    self._load_from_txt(path)
            elif format_type == 'json':
                self._load_from_json(path)
            elif format_type == 'csv':
                self._load_from_csv(path)
            elif format_type == 'txt':
                self._load_from_txt(path)
        
        self._extract_patterns()
        print(f"Loaded {len(self.categories)} categories with {sum(len(urls) for urls in self.categories.values())} URLs")
    
    def _load_from_dict(self, data_dict):
        """Load from dictionary format"""
        self.categories = {k: set(v) for k, v in data_dict.items()}
    
    def _load_from_json(self, file_path):
        """Load from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        self._load_from_dict(data)
    
    def _load_from_csv(self, file_path):
        """Load from CSV file (expects columns: url, category)"""
        df = pd.read_csv(file_path)
        data = defaultdict(list)
        for _, row in df.iterrows():
            data[row['category']].append(row['url'])
        self._load_from_dict(data)
    
    def _load_from_txt(self, file_path):
        """Load from text file (format: category:url per line)"""
        data = defaultdict(list)
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    category, url = line.split(':', 1)
                    data[category.strip()].append(url.strip())
        self._load_from_dict(data)
    
    def _load_from_directory(self, dir_path):
        """Load from directory where each file is a category"""
        data = {}
        for file_path in dir_path.glob('*.txt'):
            category = file_path.stem
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            data[category] = urls
        self._load_from_dict(data)
    
    def _extract_patterns(self):
        """Extract domain, path, and keyword patterns from categorized URLs"""
        for category, urls in self.categories.items():
            domains = set()
            paths = set()
            keywords = set()
            
            for url in urls:
                try:
                    parsed = urlparse(url)
                    domain = parsed.netloc.lower()
                    path = parsed.path.lower()
                    
                    # Extract domain patterns
                    domains.add(domain)
                    if domain.startswith('www.'):
                        domains.add(domain[4:])  # Also add without www
                    
                    # Extract path patterns
                    path_parts = [p for p in path.split('/') if p]
                    paths.update(path_parts)
                    
                    # Extract keywords from domain and path
                    all_text = domain + ' ' + path
                    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text)
                    keywords.update(word.lower() for word in words)
                    
                except Exception as e:
                    print(f"Error parsing URL {url}: {e}")
            
            self.domain_patterns[category] = domains
            self.path_patterns[category] = paths
            self.keyword_patterns[category] = keywords
    
    def _extract_url_features(self, url: str) -> Dict[str, any]:
        """Extract features from a URL for classification"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            query = parsed.query.lower()
            
            # Remove www prefix for matching
            clean_domain = domain[4:] if domain.startswith('www.') else domain
            
            features = {
                'domain': domain,
                'clean_domain': clean_domain,
                'path': path,
                'query': query,
                'has_subdomain': len(domain.split('.')) > 2,
                'path_depth': len([p for p in path.split('/') if p]),
                'has_query': bool(query),
                'url_length': len(url),
                'domain_length': len(domain),
                'path_segments': [p for p in path.split('/') if p],
                'keywords': re.findall(r'\b[a-zA-Z]{3,}\b', domain + ' ' + path)
            }
            
            return features
        except Exception:
            return {}
    
    def classify_rule_based(self, url: str) -> Tuple[Optional[str], float]:
        """
        Classify URL using rule-based approach
        
        Returns:
            (predicted_category, confidence_score)
        """
        features = self._extract_url_features(url)
        if not features:
            return None, 0.0
        
        scores = defaultdict(float)
        
        for category in self.categories:
            score = 0
            
            # Domain matching (highest weight)
            if features['clean_domain'] in self.domain_patterns[category]:
                score += 10
            elif features['domain'] in self.domain_patterns[category]:
                score += 10
            else:
                # Partial domain matching
                for domain_pattern in self.domain_patterns[category]:
                    if domain_pattern in features['domain'] or features['domain'] in domain_pattern:
                        score += 5
                        break
            
            # Path segment matching
            path_matches = 0
            for segment in features['path_segments']:
                if segment in self.path_patterns[category]:
                    path_matches += 1
            if path_matches > 0:
                score += min(path_matches * 2, 6)  # Cap at 6 points
            
            # Keyword matching
            keyword_matches = 0
            for keyword in features['keywords']:
                if keyword.lower() in self.keyword_patterns[category]:
                    keyword_matches += 1
            if keyword_matches > 0:
                score += min(keyword_matches, 4)  # Cap at 4 points
            
            scores[category] = score
        
        if scores:
            best_category = max(scores, key=scores.get)
            max_score = scores[best_category]
            if max_score > 0:
                confidence = min(max_score / 20.0, 1.0)  # Normalize to 0-1
                return best_category, confidence
        
        return None, 0.0
    
    def train_ml_model(self, test_size=0.2, random_state=42):
        """Train a machine learning model on the loaded data"""
        if not ML_AVAILABLE:
            raise ImportError("scikit-learn is required for ML classification")
        
        # Prepare training data
        urls = []
        labels = []
        for category, url_set in self.categories.items():
            for url in url_set:
                urls.append(url)
                labels.append(category)
        
        if len(urls) < 10:
            print("Warning: Very few URLs for training. Consider adding more data.")
        
        # Create feature text (domain + path + query)
        feature_texts = []
        for url in urls:
            features = self._extract_url_features(url)
            # Combine various URL parts for text analysis
            text_features = []
            text_features.append(features.get('domain', ''))
            text_features.append(features.get('path', ''))
            text_features.extend(features.get('keywords', []))
            feature_texts.append(' '.join(text_features))
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            feature_texts, labels, test_size=test_size, random_state=random_state, stratify=labels
        )
        
        # Create and train pipeline
        self.ml_model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('classifier', MultinomialNB())
        ])
        
        self.ml_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.ml_model.predict(X_test)
        print("ML Model Performance:")
        print(classification_report(y_test, y_pred))
        
        return self.ml_model
    
    def classify_ml(self, url: str) -> Tuple[Optional[str], float]:
        """
        Classify URL using machine learning model
        
        Returns:
            (predicted_category, confidence_score)
        """
        if not self.ml_model:
            raise ValueError("ML model not trained. Call train_ml_model() first.")
        
        features = self._extract_url_features(url)
        if not features:
            return None, 0.0
        
        # Prepare feature text
        text_features = []
        text_features.append(features.get('domain', ''))
        text_features.append(features.get('path', ''))
        text_features.extend(features.get('keywords', []))
        feature_text = ' '.join(text_features)
        
        # Predict
        prediction = self.ml_model.predict([feature_text])[0]
        
        # Get confidence (probability of predicted class)
        probabilities = self.ml_model.predict_proba([feature_text])[0]
        confidence = max(probabilities)
        
        return prediction, confidence
    
    def classify(self, url: str, method='hybrid') -> Dict[str, any]:
        """
        Classify a new URL
        
        Args:
            url: URL to classify
            method: 'rule_based', 'ml', or 'hybrid'
        
        Returns:
            Classification results with category, confidence, and method used
        """
        results = {
            'url': url,
            'rule_based': None,
            'ml': None,
            'final_prediction': None,
            'confidence': 0.0,
            'method_used': method
        }
        
        # Rule-based classification
        rule_category, rule_confidence = self.classify_rule_based(url)
        results['rule_based'] = {
            'category': rule_category,
            'confidence': rule_confidence
        }
        
        # ML classification (if available and trained)
        if self.ml_model and method in ['ml', 'hybrid']:
            try:
                ml_category, ml_confidence = self.classify_ml(url)
                results['ml'] = {
                    'category': ml_category,
                    'confidence': ml_confidence
                }
            except Exception as e:
                print(f"ML classification failed: {e}")
                results['ml'] = {'category': None, 'confidence': 0.0}
        
        # Determine final prediction
        if method == 'rule_based':
            results['final_prediction'] = rule_category
            results['confidence'] = rule_confidence
        elif method == 'ml' and results['ml']['category']:
            results['final_prediction'] = results['ml']['category']
            results['confidence'] = results['ml']['confidence']
        elif method == 'hybrid':
            # Use ML if available and confident, otherwise fall back to rules
            if (results['ml'] and results['ml']['category'] and 
                results['ml']['confidence'] > 0.7):
                results['final_prediction'] = results['ml']['category']
                results['confidence'] = results['ml']['confidence']
            elif rule_category:
                results['final_prediction'] = rule_category
                results['confidence'] = rule_confidence
            else:
                results['final_prediction'] = None
                results['confidence'] = 0.0
        
        return results
    
    def classify_batch(self, urls: List[str], method='hybrid') -> List[Dict[str, any]]:
        """Classify multiple URLs"""
        return [self.classify(url, method) for url in urls]
    
    def save_model(self, file_path: str):
        """Save the trained classifier to disk"""
        model_data = {
            'categories': self.categories,
            'domain_patterns': dict(self.domain_patterns),
            'path_patterns': dict(self.path_patterns),
            'keyword_patterns': dict(self.keyword_patterns),
            'ml_model': self.ml_model
        }
        
        with open(file_path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {file_path}")
    
    def load_model(self, file_path: str):
        """Load a trained classifier from disk"""
        with open(file_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.categories = model_data['categories']
        self.domain_patterns = defaultdict(set, model_data['domain_patterns'])
        self.path_patterns = defaultdict(set, model_data['path_patterns'])
        self.keyword_patterns = defaultdict(set, model_data['keyword_patterns'])
        self.ml_model = model_data['ml_model']
        print(f"Model loaded from {file_path}")
    
    def get_stats(self):
        """Get statistics about the loaded data"""
        stats = {
            'total_categories': len(self.categories),
            'total_urls': sum(len(urls) for urls in self.categories.values()),
            'categories': {}
        }
        
        for category, urls in self.categories.items():
            stats['categories'][category] = {
                'url_count': len(urls),
                'unique_domains': len(self.domain_patterns[category]),
                'path_patterns': len(self.path_patterns[category]),
                'keywords': len(self.keyword_patterns[category])
            }
        
        return stats


# Example usage and demonstration
def main():
    classifier = URLClassifier()
    classifier.load_url_lists("linkace_links.csv", "csv")
    
    # Test classification
    test_urls = [
        'https://www.facebook.com/newpage',
        'https://amazon.com/electronics/laptops',
        'https://bbc.com/news/technology',
        'https://unknown-site.com/page'
    ]
    
    print("\nClassifying test URLs:")
    for url in test_urls:
        result = classifier.classify(url, method='rule_based')
        print(f"URL: {url}")
        print(f"Predicted: {result['final_prediction']} (confidence: {result['confidence']:.2f})")
        print()
    
    # Train ML model if available
    print("=== Training ML Model ===")
    classifier.train_ml_model()

    print("\nML Classification results:")
    for url in test_urls:
        result = classifier.classify(url, method='hybrid')
        print(f"URL: {url}")
        print(f"Rule-based: {result['rule_based']['category']} ({result['rule_based']['confidence']:.2f})")
        if result['ml']:
            print(f"ML: {result['ml']['category']} ({result['ml']['confidence']:.2f})")
        print(f"Final: {result['final_prediction']} ({result['confidence']:.2f})")
        print()
    
    # Show statistics
    print("=== Classifier Statistics ===")
    stats = classifier.get_stats()
    print(f"Total categories: {stats['total_categories']}")
    print(f"Total URLs: {stats['total_urls']}")
    for category, cat_stats in stats['categories'].items():
        print(f"  {category}: {cat_stats['url_count']} URLs, {cat_stats['unique_domains']} domains")


if __name__ == "__main__":
    main()
