#!/usr/bin/env python3
"""
Classification Service for LinkAce Classifier API

Provides single URL classification functionality extracted from the main classifier
"""

import time
from datetime import datetime
from typing import Dict, List, Any

from ..api.linkace import LinkAceClient
from ..api.ollama import OllamaClient
from ..core.config import ClassifierConfig
from ..validation.url_validator import URLValidator
from ..core.utils import log_message


class ClassificationService:
    """Service for classifying individual URLs"""

    def __init__(self, config: ClassifierConfig):
        """
        Initialize classification service

        Args:
            config: Configuration object
        """
        self.config = config
        self.linkace_client = LinkAceClient(
            config.linkace_api_url, config.linkace_api_token
        )
        self.ollama_client = OllamaClient(config.ollama_url, config.ollama_model)
        self.url_validator = URLValidator()

        # Cache for classification lists to avoid repeated API calls
        self._classification_lists_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes cache TTL

    def _get_classification_lists(self) -> Dict[int, List[Dict[str, Any]]]:
        """
        Get classification lists with caching

        Returns:
            Dictionary mapping list ID to list of links
        """
        current_time = time.time()

        # Check if cache is valid
        if (
            self._classification_lists_cache is not None
            and self._cache_timestamp is not None
            and current_time - self._cache_timestamp < self._cache_ttl
        ):
            return self._classification_lists_cache

        # Load fresh data
        log_message("Loading classification lists...", "INFO", self.config.verbose)
        classify_lists_data = {}

        for list_id in self.config.classify_list_ids:
            try:
                links = self.linkace_client.get_list_links(list_id)
                classify_lists_data[list_id] = links
                log_message(
                    f"Loaded {len(links)} links from list {list_id}",
                    "INFO",
                    self.config.verbose,
                )
            except Exception as e:
                log_message(f"Error loading list {list_id}: {e}", "ERROR")
                classify_lists_data[list_id] = []

        # Update cache
        self._classification_lists_cache = classify_lists_data
        self._cache_timestamp = current_time

        total_links = sum(len(links) for links in classify_lists_data.values())
        log_message(
            f"Loaded {total_links} total links from {len(classify_lists_data)} classification lists",
            "INFO",
        )

        return classify_lists_data

    def _create_link_data_from_url(self, url: str) -> Dict[str, Any]:
        """
        Create link data structure from URL

        Args:
            url: URL to analyze

        Returns:
            Link data dictionary
        """
        # Get URL information
        url_info = self.url_validator.get_url_info(url)
        domain = url_info.get("domain", "")
        path = url_info.get("path", "")

        # Extract title from URL (simple heuristic)
        title = ""
        if path and path != "/":
            # Use last path segment as title
            path_parts = [p for p in path.split("/") if p]
            if path_parts:
                title = path_parts[-1].replace("-", " ").replace("_", " ").title()

        if not title:
            # Use domain as title
            if domain:
                title = domain.replace("www.", "").split(".")[0].title()

        return {
            "url": url,
            "title": title,
            "description": f"Link from {domain}",
            "id": None,  # No ID for external URLs
            "domain": domain,
            "path": path,
            "metadata": url_info,
        }

    def classify_url(self, url: str, validate_url: bool = True) -> Dict[str, Any]:
        """
        Classify a single URL

        Args:
            url: URL to classify
            validate_url: Whether to validate URL format and accessibility

        Returns:
            Classification result dictionary
        """
        result = {
            "url": url,
            "classifications": [],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": None,
            "processing_time_ms": 0,
        }

        start_time = time.time()

        try:
            # Validate URL if requested
            if validate_url:
                validation_result = self.url_validator.validate_and_normalize(
                    url,
                    check_accessibility=False,  # Skip accessibility check for API speed
                )

                if not validation_result["is_valid"]:
                    result["error"] = validation_result["error"]
                    return result

                # Use normalized URL
                url = validation_result["normalized_url"]
                result["normalized_url"] = url

            # Create link data structure
            link_data = self._create_link_data_from_url(url)

            # Get classification lists data
            classify_lists_data = self._get_classification_lists()

            if not classify_lists_data:
                result["error"] = "No classification lists available"
                return result

            # Perform classification using Ollama
            log_message(f"Classifying URL: {url}", "INFO", self.config.verbose)

            classifications = self.ollama_client.classify_with_threshold(
                link_data, classify_lists_data, self.config.confidence_threshold
            )

            # Format results
            result["classifications"] = classifications

            log_message(
                f"Classification complete: {len(classifications)} matches found",
                "INFO",
                self.config.verbose,
            )

        except Exception as e:
            error_msg = f"Classification error: {str(e)}"
            log_message(error_msg, "ERROR")
            result["error"] = error_msg

        finally:
            # Calculate processing time
            end_time = time.time()
            result["processing_time_ms"] = int((end_time - start_time) * 1000)

        return result

    def get_service_status(self) -> Dict[str, Any]:
        """
        Get service status and health information

        Returns:
            Service status dictionary
        """
        status = {
            "service": "LinkAce Classification Service",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "linkace_api": "unknown",
            "ollama": "unknown",
            "classification_lists": {
                "count": 0,
                "total_links": 0,
                "cache_status": "empty",
            },
        }

        # Test LinkAce API connection
        try:
            if self.linkace_client.test_connection():
                status["linkace_api"] = "connected"
            else:
                status["linkace_api"] = "disconnected"
        except Exception:
            status["linkace_api"] = "error"

        # Test Ollama connection
        try:
            if self.ollama_client.test_connection():
                status["ollama"] = "connected"
            else:
                status["ollama"] = "disconnected"
        except Exception:
            status["ollama"] = "error"

        # Check classification lists cache
        if self._classification_lists_cache is not None:
            status["classification_lists"]["count"] = len(
                self._classification_lists_cache
            )
            status["classification_lists"]["total_links"] = sum(
                len(links) for links in self._classification_lists_cache.values()
            )

            # Check cache freshness
            if self._cache_timestamp is not None:
                cache_age = time.time() - self._cache_timestamp
                if cache_age < self._cache_ttl:
                    status["classification_lists"]["cache_status"] = "fresh"
                else:
                    status["classification_lists"]["cache_status"] = "stale"

        return status

    def clear_cache(self):
        """Clear the classification lists cache"""
        self._classification_lists_cache = None
        self._cache_timestamp = None
        log_message("Classification lists cache cleared", "INFO")

    def preload_classification_lists(self) -> bool:
        """
        Preload classification lists into cache

        Returns:
            True if successful, False otherwise
        """
        try:
            self._get_classification_lists()
            return True
        except Exception as e:
            log_message(f"Error preloading classification lists: {e}", "ERROR")
            return False

    def get_classification_summary(self) -> Dict[str, Any]:
        """
        Get summary of available classification lists

        Returns:
            Summary dictionary
        """
        try:
            classify_lists_data = self._get_classification_lists()

            summary = {"total_lists": len(classify_lists_data), "lists": []}

            for list_id, links in classify_lists_data.items():
                list_info = {
                    "list_id": list_id,
                    "link_count": len(links),
                    "domains": list(
                        set(
                            self.url_validator.extract_domain(link.get("url", ""))
                            for link in links
                            if self.url_validator.extract_domain(link.get("url", ""))
                        )
                    )[
                        :10
                    ],  # Show first 10 unique domains
                }
                summary["lists"].append(list_info)

            return summary

        except Exception as e:
            return {"error": f"Error getting classification summary: {str(e)}"}


# Example usage
if __name__ == "__main__":
    from config import ConfigManager

    # Create sample configuration
    config_manager = ConfigManager()

    # You would normally load this from config file or CLI args
    sample_config_data = {
        "linkace_api_url": "https://your-linkace-instance.com/api/v2",
        "linkace_api_token": "your-token-here",
        "classify_list_ids": [1, 2, 3],
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3.2",
        "confidence_threshold": 0.8,
        "verbose": True,
    }

    try:
        # This would fail with placeholder values, but shows the usage
        config = ClassifierConfig(**sample_config_data)
        service = ClassificationService(config)

        # Test URL classification
        test_url = "https://github.com/user/repo"
        result = service.classify_url(test_url)

        print("Classification Result:")
        print(f"URL: {result['url']}")
        print(f"Classifications: {len(result['classifications'])}")
        print(f"Processing Time: {result['processing_time_ms']}ms")

        if result["error"]:
            print(f"Error: {result['error']}")

        # Get service status
        status = service.get_service_status()
        print(f"\nService Status:")
        print(f"LinkAce API: {status['linkace_api']}")
        print(f"Ollama: {status['ollama']}")

    except Exception as e:
        print(f"Service initialization failed: {e}")
        print("This is expected with placeholder configuration values.")
