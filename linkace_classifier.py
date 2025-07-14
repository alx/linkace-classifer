#!/usr/bin/env python3
"""
LinkAce Link Classifier

Automatically classify links from an input list into classification lists
using AI-powered analysis via Ollama server.
"""

import sys
import time
import argparse
import signal
from typing import List, Dict, Any, Optional

from linkace_api import LinkAceClient
from ollama_client import OllamaClient
from config import ConfigManager, ClassifierConfig
from utils import (
    print_progress, log_message, confirm_action, save_results_to_csv,
    save_results_to_json, print_classification_summary, rate_limit_wait,
    handle_keyboard_interrupt
)


class LinkClassifier:
    """Main class for classifying links using LinkAce API and Ollama"""
    
    def __init__(self, config: ClassifierConfig):
        """
        Initialize the classifier
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.linkace_client = LinkAceClient(config.linkace_api_url, config.linkace_api_token)
        self.ollama_client = OllamaClient(config.ollama_url, config.ollama_model)
        self.results = []
        self.last_api_call = 0
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        handle_keyboard_interrupt()
    
    def test_connections(self) -> bool:
        """
        Test connections to LinkAce API and Ollama server
        
        Returns:
            True if both connections successful, False otherwise
        """
        log_message("Testing connections...", "INFO", self.config.verbose)
        
        # Test LinkAce API connection
        if not self.linkace_client.test_connection():
            log_message("LinkAce API connection failed", "ERROR")
            return False
        
        # Test Ollama connection
        if not self.ollama_client.test_connection():
            log_message("Ollama server connection failed", "ERROR")
            return False
        
        log_message("All connections successful", "INFO", self.config.verbose)
        return True
    
    def load_input_list(self) -> List[Dict[str, Any]]:
        """
        Load links from the input list
        
        Returns:
            List of link data from input list
        """
        log_message(f"Loading links from input list {self.config.input_list_id}...", "INFO")
        
        links = self.linkace_client.get_list_links(self.config.input_list_id)
        
        if not links:
            log_message("No links found in input list", "WARNING")
            return []
        
        log_message(f"Loaded {len(links)} links from input list", "INFO")
        return links
    
    def load_classification_lists(self) -> Dict[int, List[Dict[str, Any]]]:
        """
        Load all classification lists data
        
        Returns:
            Dictionary mapping list ID to list of links
        """
        log_message("Loading classification lists...", "INFO")
        
        classify_lists_data = {}
        
        for list_id in self.config.classify_list_ids:
            log_message(f"Loading classification list {list_id}...", "INFO", self.config.verbose)
            
            # Rate limiting
            self.last_api_call = rate_limit_wait(self.last_api_call, self.config.api_rate_limit)
            
            links = self.linkace_client.get_list_links(list_id)
            classify_lists_data[list_id] = links
            
            log_message(f"Loaded {len(links)} links from list {list_id}", "INFO", self.config.verbose)
        
        total_classify_links = sum(len(links) for links in classify_lists_data.values())
        log_message(f"Loaded {total_classify_links} total links from {len(classify_lists_data)} classification lists", "INFO")
        
        return classify_lists_data
    
    def classify_link(self, link_data: Dict[str, Any], 
                     classify_lists_data: Dict[int, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Classify a single link
        
        Args:
            link_data: Link data to classify
            classify_lists_data: Classification lists data
            
        Returns:
            List of classifications above threshold
        """
        url = link_data.get('url', 'N/A')
        
        try:
            # Get detailed link information if needed
            link_id = link_data.get('id')
            if link_id and not link_data.get('description'):
                detailed_link = self.linkace_client.get_link_details(link_id)
                if detailed_link:
                    link_data.update(detailed_link)
            
            # Classify using Ollama
            classifications = self.ollama_client.classify_with_threshold(
                link_data, classify_lists_data, self.config.confidence_threshold
            )
            
            if classifications:
                log_message(f"Classified {url} -> {len(classifications)} lists", "INFO", self.config.verbose)
                for classification in classifications:
                    list_id = classification['list_id']
                    confidence = classification['confidence']
                    log_message(f"  List {list_id}: {confidence:.3f}", "INFO", self.config.verbose)
            else:
                log_message(f"No classifications above threshold for {url}", "INFO", self.config.verbose)
            
            return classifications
            
        except Exception as e:
            log_message(f"Error classifying {url}: {e}", "ERROR")
            return []
    
    def move_link_to_lists(self, link_data: Dict[str, Any], 
                          target_list_ids: List[int]) -> bool:
        """
        Move a link from input list to target lists
        
        Args:
            link_data: Link data
            target_list_ids: List of target list IDs
            
        Returns:
            True if successful, False otherwise
        """
        link_id = link_data.get('id')
        if not link_id:
            log_message("Link ID not found, cannot move link", "ERROR")
            return False
        
        url = link_data.get('url', 'N/A')
        
        try:
            # Remove from input list and add to target lists
            success = True
            
            for target_list_id in target_list_ids:
                if not self.linkace_client.add_link_to_list(link_id, target_list_id):
                    success = False
                    log_message(f"Failed to add {url} to list {target_list_id}", "ERROR")
                else:
                    log_message(f"Added {url} to list {target_list_id}", "INFO", self.config.verbose)
                
                # Rate limiting
                self.last_api_call = rate_limit_wait(self.last_api_call, self.config.api_rate_limit)
            
            # Remove from input list if all additions successful
            if success:
                if not self.linkace_client.remove_link_from_list(link_id, self.config.input_list_id):
                    log_message(f"Failed to remove {url} from input list", "ERROR")
                    success = False
                else:
                    log_message(f"Removed {url} from input list", "INFO", self.config.verbose)
            
            return success
            
        except Exception as e:
            log_message(f"Error moving {url}: {e}", "ERROR")
            return False
    
    def process_links(self, input_links: List[Dict[str, Any]], 
                     classify_lists_data: Dict[int, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Process all links for classification
        
        Args:
            input_links: Links from input list
            classify_lists_data: Classification lists data
            
        Returns:
            List of processing results
        """
        log_message(f"Processing {len(input_links)} links...", "INFO")
        
        results = []
        processed_count = 0
        moved_count = 0
        
        for i, link_data in enumerate(input_links):
            url = link_data.get('url', 'N/A')
            
            # Progress indicator
            print_progress(i + 1, len(input_links), f"Processing links")
            
            try:
                # Classify the link
                classifications = self.classify_link(link_data, classify_lists_data)
                
                # Store result
                result = {
                    'link_data': link_data,
                    'classifications': classifications,
                    'moved': False,
                    'success': False
                }
                
                # Move link if classifications found and not in dry run mode
                if classifications and not self.config.dry_run:
                    target_list_ids = [c['list_id'] for c in classifications]
                    
                    if self.move_link_to_lists(link_data, target_list_ids):
                        result['moved'] = True
                        result['success'] = True
                        moved_count += 1
                        log_message(f"Moved {url} to lists {target_list_ids}", "INFO")
                    else:
                        log_message(f"Failed to move {url}", "ERROR")
                
                elif classifications and self.config.dry_run:
                    target_list_ids = [c['list_id'] for c in classifications]
                    log_message(f"DRY RUN: Would move {url} to lists {target_list_ids}", "INFO")
                    result['success'] = True
                
                results.append(result)
                processed_count += 1
                
            except Exception as e:
                log_message(f"Error processing {url}: {e}", "ERROR")
                results.append({
                    'link_data': link_data,
                    'classifications': [],
                    'moved': False,
                    'success': False,
                    'error': str(e)
                })
        
        log_message(f"Processed {processed_count}/{len(input_links)} links", "INFO")
        if not self.config.dry_run:
            log_message(f"Moved {moved_count} links to classification lists", "INFO")
        
        return results
    
    def run(self):
        """Main execution method"""
        try:
            log_message("Starting LinkAce Link Classifier", "INFO")
            
            # Test connections
            if not self.test_connections():
                log_message("Connection tests failed, exiting", "ERROR")
                sys.exit(1)
            
            # Load input list
            input_links = self.load_input_list()
            if not input_links:
                log_message("No links to process, exiting", "ERROR")
                sys.exit(1)
            
            # Load classification lists
            classify_lists_data = self.load_classification_lists()
            if not classify_lists_data:
                log_message("No classification lists loaded, exiting", "ERROR")
                sys.exit(1)
            
            # Confirm operation if not dry run
            if not self.config.dry_run:
                if not confirm_action(f"Process {len(input_links)} links and move them to classification lists?"):
                    log_message("Operation cancelled by user", "INFO")
                    sys.exit(0)
            
            # Process links
            self.results = self.process_links(input_links, classify_lists_data)
            
            # Print summary
            print_classification_summary(self.results)
            
            # Save results if requested
            if self.config.output_file:
                if self.config.output_file.endswith('.json'):
                    save_results_to_json(self.results, self.config.output_file)
                else:
                    save_results_to_csv(self.results, self.config.output_file)
            
            log_message("Classification complete", "INFO")
            
        except KeyboardInterrupt:
            handle_keyboard_interrupt()
        except Exception as e:
            log_message(f"Unexpected error: {e}", "ERROR")
            sys.exit(1)


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="LinkAce Link Classifier - Automatically classify links using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --api-url https://linkace.example.com/api/v2 --token YOUR_TOKEN --input-list 12 --classify-lists 1,2,3
  %(prog)s --config config.json --dry-run
  %(prog)s --api-url https://linkace.example.com/api/v2 --token YOUR_TOKEN --input-list 12 --classify-lists 1,2,3 --output results.csv
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--api-url",
        help="LinkAce API base URL (e.g., https://linkace.example.com/api/v2)"
    )
    parser.add_argument(
        "--token",
        help="LinkAce API token"
    )
    parser.add_argument(
        "--input-list",
        type=int,
        help="Input list ID to classify links from"
    )
    parser.add_argument(
        "--classify-lists",
        type=lambda x: [int(i.strip()) for i in x.split(',')],
        help="Comma-separated list of classification list IDs"
    )
    
    # Optional arguments
    parser.add_argument(
        "--config",
        help="Configuration file path"
    )
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama server URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--ollama-model",
        default="llama3.2",
        help="Ollama model to use (default: llama3.2)"
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.8,
        help="Confidence threshold for classification (default: 0.8)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actual changes)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--output-file",
        help="Output file for results (CSV or JSON)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.create_config(args, args.config)
    
    # Print configuration if verbose
    if config.verbose:
        config_manager.print_config(config)
    
    # Create and run classifier
    classifier = LinkClassifier(config)
    classifier.run()


if __name__ == "__main__":
    main()