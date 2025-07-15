#!/usr/bin/env python3
"""
URL Validation Module for LinkAce Classifier API

Provides URL validation, sanitization, and accessibility checking
"""

import re
import requests
from urllib.parse import urlparse, urlunparse
from typing import Tuple, Optional


class URLValidator:
    """Validates and normalizes URLs for classification"""

    def __init__(self, timeout: float = 5.0):
        """
        Initialize URL validator
        
        Args:
            timeout: Timeout for URL accessibility checks in seconds
        """
        self.timeout = timeout
        self.url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def validate_url_format(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format
        
        Args:
            url: URL to validate
            
        Returns:
            (is_valid, error_message)
        """
        if not url:
            return False, "URL cannot be empty"
            
        if not isinstance(url, str):
            return False, "URL must be a string"
            
        # Check basic URL pattern
        if not self.url_pattern.match(url):
            return False, "Invalid URL format"
            
        # Parse URL to check components
        try:
            parsed = urlparse(url)
            
            if not parsed.scheme:
                return False, "URL must include scheme (http:// or https://)"
                
            if not parsed.netloc:
                return False, "URL must include domain"
                
            if parsed.scheme not in ['http', 'https']:
                return False, "URL scheme must be http or https"
                
        except Exception as e:
            return False, f"URL parsing error: {str(e)}"
            
        return True, None

    def normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing unnecessary components
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        try:
            parsed = urlparse(url)
            
            # Remove fragment (anchor)
            normalized = urlunparse((
                parsed.scheme,
                parsed.netloc.lower(),  # lowercase domain
                parsed.path,
                parsed.params,
                parsed.query,
                ''  # remove fragment
            ))
            
            # Remove trailing slash if path is just '/'
            if normalized.endswith('/') and parsed.path == '/':
                normalized = normalized[:-1]
                
            return normalized
            
        except Exception:
            return url  # Return original if normalization fails

    def check_url_accessibility(self, url: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if URL is accessible
        
        Args:
            url: URL to check
            
        Returns:
            (is_accessible, error_message, status_code)
        """
        try:
            # Use HEAD request to check accessibility without downloading content
            response = requests.head(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                headers={'User-Agent': 'LinkAce-Classifier/1.0'}
            )
            
            # Consider 2xx and 3xx status codes as accessible
            if 200 <= response.status_code < 400:
                return True, None, response.status_code
            else:
                return False, f"HTTP {response.status_code}", response.status_code
                
        except requests.exceptions.Timeout:
            return False, "Request timeout", None
        except requests.exceptions.ConnectionError:
            return False, "Connection error", None
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None

    def validate_and_normalize(self, url: str, check_accessibility: bool = False) -> dict:
        """
        Complete URL validation and normalization
        
        Args:
            url: URL to validate
            check_accessibility: Whether to check if URL is accessible
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'original_url': url,
            'normalized_url': None,
            'is_valid': False,
            'is_accessible': None,
            'error': None,
            'status_code': None
        }
        
        # Validate format
        is_valid, error_msg = self.validate_url_format(url)
        if not is_valid:
            result['error'] = error_msg
            return result
            
        # Normalize URL
        normalized_url = self.normalize_url(url)
        result['normalized_url'] = normalized_url
        result['is_valid'] = True
        
        # Check accessibility if requested
        if check_accessibility:
            is_accessible, access_error, status_code = self.check_url_accessibility(normalized_url)
            result['is_accessible'] = is_accessible
            result['status_code'] = status_code
            
            if not is_accessible:
                result['error'] = access_error
        
        return result

    def extract_domain(self, url: str) -> Optional[str]:
        """
        Extract domain from URL
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain name or None if invalid
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return None

    def get_url_info(self, url: str) -> dict:
        """
        Get comprehensive URL information
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with URL components and metadata
        """
        try:
            parsed = urlparse(url)
            
            return {
                'scheme': parsed.scheme,
                'domain': parsed.netloc.lower(),
                'path': parsed.path,
                'query': parsed.query,
                'fragment': parsed.fragment,
                'port': parsed.port,
                'has_subdomain': len(parsed.netloc.split('.')) > 2,
                'path_depth': len([p for p in parsed.path.split('/') if p]),
                'has_query': bool(parsed.query),
                'has_fragment': bool(parsed.fragment)
            }
            
        except Exception:
            return {}


# Example usage and testing
if __name__ == "__main__":
    validator = URLValidator()
    
    test_urls = [
        "https://github.com/user/repo",
        "http://example.com",
        "https://subdomain.example.com/path?query=value",
        "invalid-url",
        "https://",
        "ftp://example.com",
        ""
    ]
    
    print("URL Validation Tests:")
    print("=" * 50)
    
    for url in test_urls:
        result = validator.validate_and_normalize(url, check_accessibility=False)
        print(f"URL: {url}")
        print(f"Valid: {result['is_valid']}")
        print(f"Normalized: {result['normalized_url']}")
        print(f"Error: {result['error']}")
        print("-" * 30)