#!/usr/bin/env python3
"""
Demo script for LinkAce Classifier

Demonstrates the classifier using the existing CSV data without needing
live API connections
"""

import csv
import json
from typing import Dict, List, Any
from ollama_client import OllamaClient
from utils import log_message, print_classification_summary


def load_csv_data(filename: str) -> List[Dict[str, Any]]:
    """Load link data from CSV file"""
    links = []

    try:
        with open(filename, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                links.append(
                    {
                        "url": row["url"],
                        "title": row["url"].split("/")[
                            -1
                        ],  # Use last part of URL as title
                        "description": "",
                        "id": len(links) + 1,
                        "category": row.get("category", "unknown"),
                    }
                )
    except Exception as e:
        log_message(f"Error loading CSV data: {e}", "ERROR")

    return links


def group_links_by_category(
    links: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """Group links by their category"""
    grouped = {}

    for link in links:
        category = link.get("category", "unknown")
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(link)

    return grouped


def demo_classification():
    """Demonstrate the classification process"""
    print("🔗 LinkAce Classifier Demo")
    print("=" * 50)

    # Load existing CSV data
    print("📂 Loading existing link data...")
    all_links = load_csv_data("linkace_links.csv")

    if not all_links:
        print("❌ No data found in linkace_links.csv")
        return

    print(f"✅ Loaded {len(all_links)} links")

    # Group links by category
    grouped_links = group_links_by_category(all_links)

    print(f"📊 Found {len(grouped_links)} categories:")
    for category, links in grouped_links.items():
        print(f"  Category {category}: {len(links)} links")

    # Simulate classification lists (use some categories as classification targets)
    categories = list(grouped_links.keys())
    if len(categories) < 2:
        print("❌ Need at least 2 categories for demo")
        return

    # Use first category as input, others as classification targets
    input_category = categories[0]
    classify_categories = categories[1:4]  # Use up to 3 categories

    input_links = grouped_links[input_category][:5]  # Take first 5 links
    classify_lists_data = {
        i: grouped_links[cat][:10]  # Take first 10 links from each category
        for i, cat in enumerate(classify_categories, 1)
    }

    print("\n🎯 Demo Setup:")
    print(f"Input links: {len(input_links)} from category {input_category}")
    print(f"Classification lists: {len(classify_lists_data)} lists")
    for list_id, links in classify_lists_data.items():
        print(f"  List {list_id}: {len(links)} links")

    # Test Ollama connection
    print("\n🤖 Testing Ollama connection...")
    ollama_client = OllamaClient(ollama_url="http://localhost:11434", model="qwen3:8b")

    if not ollama_client.test_connection():
        print("❌ Ollama connection failed - running offline demo")
        return demo_offline_classification(input_links, classify_lists_data)

    print("✅ Ollama connection successful")

    # Perform classification
    print(f"\n🔍 Classifying {len(input_links)} links...")
    results = []

    for i, link in enumerate(input_links):
        print(f"\nProcessing link {i+1}/{len(input_links)}: {link['url']}")

        try:
            classifications = ollama_client.classify_with_threshold(
                link, classify_lists_data, threshold=0.8
            )

            result = {"link_data": link, "classifications": classifications}

            results.append(result)

            if classifications:
                print(
                    f"  ✅ Found {len(classifications)} high-confidence classifications:"
                )
                for classification in classifications:
                    list_id = classification["list_id"]
                    confidence = classification["confidence"]
                    reasoning = classification.get("reasoning", "No reasoning provided")
                    print(f"    List {list_id}: {confidence:.3f} - {reasoning}")
            else:
                print("  ⚠️  No classifications above threshold")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({"link_data": link, "classifications": []})

    # Print summary
    print_classification_summary(results)

    # Save results
    with open("demo_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n💾 Results saved to demo_results.json")


def demo_offline_classification(
    input_links: List[Dict[str, Any]],
    classify_lists_data: Dict[int, List[Dict[str, Any]]],
):
    """Demonstrate classification without Ollama (offline mode)"""
    print("\n🔄 Running offline classification demo...")

    # Simple rule-based classification for demo
    results = []

    for link in input_links:
        url = link["url"]
        domain = url.split("/")[2] if len(url.split("/")) > 2 else url

        classifications = []

        # Simple domain-based classification
        for list_id, classify_links in classify_lists_data.items():
            # Check if any link in the classification list shares the same domain
            for classify_link in classify_links:
                classify_domain = (
                    classify_link["url"].split("/")[2]
                    if len(classify_link["url"].split("/")) > 2
                    else classify_link["url"]
                )

                if domain == classify_domain:
                    classifications.append(
                        {
                            "list_id": list_id,
                            "confidence": 0.9,
                            "reasoning": f"Same domain: {domain}",
                        }
                    )
                    break
                elif domain in classify_domain or classify_domain in domain:
                    classifications.append(
                        {
                            "list_id": list_id,
                            "confidence": 0.75,
                            "reasoning": f"Similar domain: {domain} ~ "
                            f"{classify_domain}",
                        }
                    )
                    break

        # Filter by threshold
        high_confidence = [c for c in classifications if c["confidence"] >= 0.8]

        result = {"link_data": link, "classifications": high_confidence}

        results.append(result)

        print(f"📎 {url}")
        if high_confidence:
            for classification in high_confidence:
                print(
                    f"  → List {classification['list_id']}: "
                    f"{classification['confidence']:.3f}"
                )
        else:
            print("  → No high-confidence classifications")

    print_classification_summary(results)

    return results


if __name__ == "__main__":
    demo_classification()
