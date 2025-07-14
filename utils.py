#!/usr/bin/env python3
"""
Utility functions for LinkAce Classifier

Common helper functions and utilities
"""

import sys
import time
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse


def print_progress(current: int, total: int, prefix: str = "Progress"):
    """
    Print a progress bar

    Args:
        current: Current progress
        total: Total items
        prefix: Progress bar prefix
    """
    if total == 0:
        return

    percent = (current / total) * 100
    filled_length = int(50 * current // total)
    bar = "█" * filled_length + "-" * (50 - filled_length)

    print(f"\r{prefix}: |{bar}| {percent:.1f}% ({current}/{total})", end="", flush=True)

    if current == total:
        print()  # New line when complete


def format_timestamp() -> str:
    """Get formatted timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_message(message: str, level: str = "INFO", verbose: bool = True):
    """
    Log a message with timestamp and level

    Args:
        message: Message to log
        level: Log level (INFO, WARNING, ERROR)
        verbose: Whether to print verbose messages
    """
    if not verbose and level == "INFO":
        return

    timestamp = format_timestamp()

    # Color codes for different levels
    colors = {
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "RESET": "\033[0m",  # Reset
    }

    color = colors.get(level, "")
    reset = colors["RESET"]

    print(f"{color}[{timestamp}] {level}: {message}{reset}")


def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_domain(url: str) -> Optional[str]:
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


def truncate_string(text: str, max_length: int = 80) -> str:
    """
    Truncate string to maximum length

    Args:
        text: String to truncate
        max_length: Maximum length

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary

    Args:
        dictionary: Dictionary to get value from
        key: Key to look up
        default: Default value if key not found

    Returns:
        Value or default
    """
    return dictionary.get(key, default)


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation

    Args:
        message: Confirmation message
        default: Default response

    Returns:
        True if confirmed, False otherwise
    """
    default_text = "Y/n" if default else "y/N"
    response = input(f"{message} [{default_text}]: ").strip().lower()

    if not response:
        return default

    return response in ("y", "yes", "true", "1")


def save_results_to_csv(results: List[Dict[str, Any]], filename: str):
    """
    Save classification results to CSV file

    Args:
        results: List of classification results
        filename: Output filename
    """
    if not results:
        log_message("No results to save", "WARNING")
        return

    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "url",
                "title",
                "original_list_id",
                "classified_list_id",
                "confidence",
                "reasoning",
                "timestamp",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for result in results:
                link_data = result.get("link_data", {})
                classifications = result.get("classifications", [])

                if classifications:
                    for classification in classifications:
                        writer.writerow(
                            {
                                "url": link_data.get("url", ""),
                                "title": link_data.get("title", ""),
                                "original_list_id": link_data.get(
                                    "original_list_id", ""
                                ),
                                "classified_list_id": classification.get("list_id", ""),
                                "confidence": classification.get("confidence", ""),
                                "reasoning": classification.get("reasoning", ""),
                                "timestamp": format_timestamp(),
                            }
                        )
                else:
                    # No classifications found
                    writer.writerow(
                        {
                            "url": link_data.get("url", ""),
                            "title": link_data.get("title", ""),
                            "original_list_id": link_data.get("original_list_id", ""),
                            "classified_list_id": "",
                            "confidence": "",
                            "reasoning": "No classifications above threshold",
                            "timestamp": format_timestamp(),
                        }
                    )

        log_message(f"Results saved to {filename}", "INFO")

    except Exception as e:
        log_message(f"Error saving results to CSV: {e}", "ERROR")


def save_results_to_json(results: List[Dict[str, Any]], filename: str):
    """
    Save classification results to JSON file

    Args:
        results: List of classification results
        filename: Output filename
    """
    try:
        output_data = {
            "timestamp": format_timestamp(),
            "total_links": len(results),
            "results": results,
        }

        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)

        log_message(f"Results saved to {filename}", "INFO")

    except Exception as e:
        log_message(f"Error saving results to JSON: {e}", "ERROR")


def load_results_from_json(filename: str) -> List[Dict[str, Any]]:
    """
    Load classification results from JSON file

    Args:
        filename: Input filename

    Returns:
        List of classification results
    """
    try:
        with open(filename, "r", encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)

        log_message(f"Results loaded from {filename}", "INFO")
        return data.get("results", [])

    except Exception as e:
        log_message(f"Error loading results from JSON: {e}", "ERROR")
        return []


def print_classification_summary(results: List[Dict[str, Any]]):
    """
    Print a summary of classification results

    Args:
        results: List of classification results
    """
    if not results:
        log_message("No results to summarize", "WARNING")
        return

    total_links = len(results)
    classified_links = sum(1 for r in results if r.get("classifications"))
    unclassified_links = total_links - classified_links

    print("\n" + "=" * 60)
    print("📊 CLASSIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total links processed: {total_links}")
    print(f"Links classified: {classified_links}")
    print(f"Links not classified: {unclassified_links}")
    print(f"Classification rate: {(classified_links/total_links)*100:.1f}%")

    # Count classifications by list
    list_counts = {}
    confidence_scores = []

    for result in results:
        classifications = result.get("classifications", [])
        for classification in classifications:
            list_id = classification.get("list_id")
            confidence = classification.get("confidence", 0)

            if list_id not in list_counts:
                list_counts[list_id] = 0
            list_counts[list_id] += 1
            confidence_scores.append(confidence)

    if list_counts:
        print("\nClassifications by list:")
        for list_id, count in sorted(list_counts.items()):
            print(f"  List {list_id}: {count} links")

    if confidence_scores:
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        min_confidence = min(confidence_scores)
        max_confidence = max(confidence_scores)

        print("\nConfidence statistics:")
        print(f"  Average: {avg_confidence:.3f}")
        print(f"  Range: {min_confidence:.3f} - {max_confidence:.3f}")

    print("=" * 60)


def rate_limit_wait(last_call_time: float, rate_limit: float) -> float:
    """
    Wait for rate limiting if needed

    Args:
        last_call_time: Timestamp of last API call
        rate_limit: Minimum time between calls

    Returns:
        Current timestamp
    """
    current_time = time.time()
    elapsed = current_time - last_call_time

    if elapsed < rate_limit:
        wait_time = rate_limit - elapsed
        time.sleep(wait_time)
        return time.time()

    return current_time


def handle_keyboard_interrupt():
    """Handle keyboard interrupt gracefully"""
    print("\n\n⚠️  Operation interrupted by user")
    print("Exiting gracefully...")
    sys.exit(0)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
