#!/usr/bin/env python3
"""
HTTP API Server for LinkAce Classifier

Provides REST API endpoints for URL classification
"""

import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any
import threading
import logging

from ..core.config import ClassifierConfig
from ..services.classification_service import ClassificationService
from ..core.utils import log_message


class ClassificationAPIServer:
    """HTTP API server for LinkAce classification service"""

    def __init__(self, config: ClassifierConfig):
        """
        Initialize API server
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.classification_service = ClassificationService(config)
        
        # Request tracking for rate limiting
        self.request_counts = {}
        self.request_lock = threading.Lock()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        
        # Configure CORS if enabled
        if config.enable_cors:
            CORS(self.app)
        
        # Configure logging
        if not config.server_debug:
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
        
        # Register routes
        self._register_routes()
        
        # Preload classification lists
        log_message("Preloading classification lists...", "INFO")
        if self.classification_service.preload_classification_lists():
            log_message("Classification lists preloaded successfully", "INFO")
        else:
            log_message("Failed to preload classification lists", "WARNING")

    def _register_routes(self):
        """Register API routes"""
        
        @self.app.route('/classify', methods=['POST'])
        def classify_url():
            """Classify a URL endpoint"""
            return self._handle_classify_request()
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            """Get service status endpoint"""
            return self._handle_status_request()
        
        @self.app.route('/summary', methods=['GET'])
        def get_summary():
            """Get classification summary endpoint"""
            return self._handle_summary_request()
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors"""
            return jsonify({
                'error': 'Endpoint not found',
                'code': 404,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 404
        
        @self.app.errorhandler(405)
        def method_not_allowed(error):
            """Handle 405 errors"""
            return jsonify({
                'error': 'Method not allowed',
                'code': 405,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 405
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors"""
            return jsonify({
                'error': 'Internal server error',
                'code': 500,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 500

    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Check if client has exceeded rate limit
        
        Args:
            client_ip: Client IP address
            
        Returns:
            True if within rate limit, False otherwise
        """
        current_time = time.time()
        minute_ago = current_time - 60
        
        with self.request_lock:
            # Clean old requests
            if client_ip in self.request_counts:
                self.request_counts[client_ip] = [
                    req_time for req_time in self.request_counts[client_ip]
                    if req_time > minute_ago
                ]
            else:
                self.request_counts[client_ip] = []
            
            # Check rate limit
            if len(self.request_counts[client_ip]) >= self.config.max_requests_per_minute:
                return False
            
            # Add current request
            self.request_counts[client_ip].append(current_time)
            return True

    def _handle_classify_request(self) -> tuple:
        """Handle URL classification request"""
        start_time = time.time()
        
        try:
            # Check rate limiting
            client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
            if not self._check_rate_limit(client_ip):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'code': 429,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 429
            
            # Validate request
            if not request.is_json:
                return jsonify({
                    'error': 'Request must be JSON',
                    'code': 400,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 400
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'error': 'Request body cannot be empty',
                    'code': 400,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 400
            
            if 'url' not in data:
                return jsonify({
                    'error': 'Missing required field: url',
                    'code': 400,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 400
            
            url = data['url']
            
            if not isinstance(url, str) or not url.strip():
                return jsonify({
                    'error': 'URL must be a non-empty string',
                    'code': 400,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 400
            
            # Perform classification
            result = self.classification_service.classify_url(
                url.strip(),
                validate_url=self.config.enable_url_validation
            )
            
            # Handle classification errors
            if result.get('error'):
                if 'Invalid URL' in result['error'] or 'URL' in result['error']:
                    return jsonify({
                        'error': result['error'],
                        'code': 422,
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }), 422
                else:
                    return jsonify({
                        'error': result['error'],
                        'code': 500,
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }), 500
            
            # Return successful result
            response_data = {
                'url': result['url'],
                'classifications': result['classifications'],
                'timestamp': result['timestamp']
            }
            
            # Add normalized URL if available
            if 'normalized_url' in result:
                response_data['normalized_url'] = result['normalized_url']
            
            # Add processing time for debugging
            if self.config.verbose:
                response_data['processing_time_ms'] = result['processing_time_ms']
            
            log_message(
                f"Classified URL: {url} -> {len(result['classifications'])} results",
                "INFO",
                self.config.verbose
            )
            
            return jsonify(response_data), 200
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            log_message(error_msg, "ERROR")
            
            return jsonify({
                'error': 'Internal server error',
                'code': 500,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 500

    def _handle_status_request(self) -> tuple:
        """Handle service status request"""
        try:
            status = self.classification_service.get_service_status()
            return jsonify(status), 200
            
        except Exception as e:
            log_message(f"Error getting service status: {e}", "ERROR")
            return jsonify({
                'error': 'Error getting service status',
                'code': 500,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 500

    def _handle_summary_request(self) -> tuple:
        """Handle classification summary request"""
        try:
            summary = self.classification_service.get_classification_summary()
            
            if 'error' in summary:
                return jsonify({
                    'error': summary['error'],
                    'code': 500,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 500
            
            return jsonify(summary), 200
            
        except Exception as e:
            log_message(f"Error getting classification summary: {e}", "ERROR")
            return jsonify({
                'error': 'Error getting classification summary',
                'code': 500,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 500

    def run(self):
        """Run the HTTP server"""
        log_message(
            f"Starting LinkAce Classification API server on {self.config.server_host}:{self.config.server_port}",
            "INFO"
        )
        
        try:
            self.app.run(
                host=self.config.server_host,
                port=self.config.server_port,
                debug=self.config.server_debug,
                threaded=True
            )
        except Exception as e:
            log_message(f"Error running server: {e}", "ERROR")
            raise

    def get_app(self):
        """Get Flask app instance for testing"""
        return self.app


# Example usage for testing
if __name__ == "__main__":
    from ..core.config import ConfigManager, create_sample_config_file
    
    # Create sample configuration
    config_manager = ConfigManager()
    
    try:
        # Load configuration from file if available
        config_data = config_manager.load_from_file("config.json")
        
        if not config_data:
            print("No config.json found, creating sample...")
            create_sample_config_file()
            print("Please edit config.json with your settings and run again.")
        else:
            # Create config object
            config = ClassifierConfig(**config_data)
            
            # Create and run server
            server = ClassificationAPIServer(config)
            server.run()
            
    except Exception as e:
        print(f"Server startup failed: {e}")
        print("Please check your configuration and ensure all services are available.")