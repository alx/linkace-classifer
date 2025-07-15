#!/usr/bin/env python3
"""
Ollama Client for Link Classification

Handles communication with Ollama server for AI-powered link classification
"""

import requests
import json
import re
from typing import Dict, List, Any, Optional


class OllamaClient:
    """Client for interacting with Ollama server for link classification"""

    def __init__(
        self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2"
    ):
        """
        Initialize the Ollama client

        Args:
            ollama_url: URL of the Ollama server
            model: Model to use for classification
        """
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.headers = {"Content-Type": "application/json"}

    def test_connection(self) -> bool:
        """
        Test the connection to the Ollama server

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            response.raise_for_status()
            print("✅ Ollama server connection successful")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama server connection failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error testing Ollama connection: {e}")
            return False

    def _generate_classification_prompt(
        self,
        link_data: Dict[str, Any],
        classify_lists_data: Dict[int, List[Dict[str, Any]]],
    ) -> str:
        """
        Generate a prompt for link classification

        Args:
            link_data: Data about the link to classify
            classify_lists_data: Data about classification lists

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a link classifier. Your task is to analyze a link and
determine which classification lists it belongs to based on the content and
context of existing links in those lists.

LINK TO CLASSIFY:
URL: {link_data.get('url', 'N/A')}
Title: {link_data.get('title', 'N/A')}
Description: {link_data.get('description', 'N/A')}

CLASSIFICATION LISTS:
"""

        for list_id, links in classify_lists_data.items():
            prompt += f"\nList ID {list_id}:\n"

            # Get sample URLs and titles from the list
            sample_links = links[:5]  # Show first 5 links as examples
            for link in sample_links:
                url = link.get("url", "N/A")
                title = link.get("title", "N/A")
                prompt += f"  - {url} (Title: {title})\n"

            if len(links) > 5:
                prompt += f"  ... and {len(links) - 5} more links\n"

        prompt += """

TASK:
Analyze the link to classify and determine which classification lists it
belongs to. Consider:
1. URL domain and path similarity
2. Title and description content similarity
3. Thematic relevance to existing links in each list
4. Topic and subject matter alignment

For each classification list, provide a confidence score from 0.0 to 1.0
indicating how well the link fits that list.

RESPONSE FORMAT:
Provide your response in the following JSON format:
{
  "classifications": [
    {
      "list_id": <list_id>,
      "confidence": <0.0-1.0>,
      "reasoning": "<brief explanation>"
    }
  ]
}

Only include classifications where you have some confidence (>0.1). Be
precise with confidence scores.
"""

        return prompt

    def _parse_classification_response(
        self, response_text: str
    ) -> List[Dict[str, Any]]:
        """
        Parse the classification response from Ollama

        Args:
            response_text: Raw response text from Ollama

        Returns:
            List of classification results
        """
        try:
            # Try to extract JSON from the response
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return data.get("classifications", [])
            else:
                print("Warning: Could not extract JSON from classification response")
                return []

        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse classification response as JSON: {e}")
            return []
        except Exception as e:
            print(f"Warning: Unexpected error parsing classification response: {e}")
            return []

    def classify_link(
        self,
        link_data: Dict[str, Any],
        classify_lists_data: Dict[int, List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """
        Classify a link against the available classification lists

        Args:
            link_data: Data about the link to classify
            classify_lists_data: Data about classification lists

        Returns:
            List of classification results with confidence scores
        """
        if not classify_lists_data:
            print("Warning: No classification lists provided")
            return []

        prompt = self._generate_classification_prompt(link_data, classify_lists_data)

        try:
            # Send request to Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent results
                    "num_predict": 1000,  # Limit response length
                },
            }

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()

            response_data = response.json()
            response_text = response_data.get("response", "")

            # Parse the classification results
            classifications = self._parse_classification_response(response_text)

            # Validate and clean up results
            valid_classifications = []
            for classification in classifications:
                if isinstance(classification, dict):
                    list_id = classification.get("list_id")
                    confidence = classification.get("confidence", 0.0)
                    reasoning = classification.get("reasoning", "")

                    # Validate confidence score
                    if (
                        isinstance(confidence, (int, float))
                        and 0.0 <= confidence <= 1.0
                    ):
                        valid_classifications.append(
                            {
                                "list_id": list_id,
                                "confidence": float(confidence),
                                "reasoning": reasoning,
                            }
                        )

            return valid_classifications

        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error during classification: {e}")
            return []

    def classify_with_threshold(
        self,
        link_data: Dict[str, Any],
        classify_lists_data: Dict[int, List[Dict[str, Any]]],
        threshold: float = 0.8,
    ) -> List[Dict[str, Any]]:
        """
        Classify a link and return only results above the confidence threshold

        Args:
            link_data: Data about the link to classify
            classify_lists_data: Data about classification lists
            threshold: Minimum confidence threshold (default: 0.8)

        Returns:
            List of classification results above threshold
        """
        all_classifications = self.classify_link(link_data, classify_lists_data)

        # Filter by threshold
        high_confidence_classifications = [
            classification
            for classification in all_classifications
            if classification["confidence"] >= threshold
        ]

        return high_confidence_classifications

    def get_best_classification(
        self,
        link_data: Dict[str, Any],
        classify_lists_data: Dict[int, List[Dict[str, Any]]],
    ) -> Optional[Dict[str, Any]]:
        """
        Get the best (highest confidence) classification for a link

        Args:
            link_data: Data about the link to classify
            classify_lists_data: Data about classification lists

        Returns:
            Best classification or None if no classifications
        """
        classifications = self.classify_link(link_data, classify_lists_data)

        if not classifications:
            return None

        # Return the classification with highest confidence
        return max(classifications, key=lambda x: x["confidence"])

    def batch_classify(
        self,
        links_data: List[Dict[str, Any]],
        classify_lists_data: Dict[int, List[Dict[str, Any]]],
        threshold: float = 0.8,
    ) -> List[Dict[str, Any]]:
        """
        Classify multiple links in batch

        Args:
            links_data: List of link data to classify
            classify_lists_data: Data about classification lists
            threshold: Minimum confidence threshold

        Returns:
            List of results with classifications for each link
        """
        results = []

        for i, link_data in enumerate(links_data):
            print(
                f"Classifying link {i+1}/{len(links_data)}: "
                f"{link_data.get('url', 'N/A')}"
            )

            classifications = self.classify_with_threshold(
                link_data, classify_lists_data, threshold
            )

            results.append({"link_data": link_data, "classifications": classifications})

        return results
