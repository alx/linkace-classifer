#!/usr/bin/env python3
"""
LinkAce API Client

A wrapper for the LinkAce API that provides methods for:
- Fetching links from lists
- Getting link details
- Updating link assignments
"""

import requests
import time
from typing import List, Dict, Any, Optional


class LinkAceClient:
    """Client for interacting with the LinkAce API"""

    def __init__(self, api_base_url: str, api_token: str):
        """
        Initialize the LinkAce API client

        Args:
            api_base_url: Base URL of the LinkAce API
                (e.g., https://linkace.example.com/api/v2)
            api_token: API token for authentication
        """
        self.api_base_url = api_base_url.rstrip("/")
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_list_links(self, list_id: int) -> List[Dict[str, Any]]:
        """
        Fetch all links from a specific list ID using pagination

        Args:
            list_id: The ID of the list to fetch links from

        Returns:
            List of link dictionaries
        """
        all_links = []
        url = f"{self.api_base_url}/lists/{list_id}/links"
        page = 1

        try:
            print(f"Fetching links from list ID {list_id}...")

            while url:
                params = {"page": page}

                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                data = response.json()
                links = data.get("data", [])
                current_page = data.get("current_page", page)
                last_page = data.get("last_page", 1)
                next_page_url = data.get("next_page_url")

                print(f"  Page {current_page}/{last_page}: Found {len(links)} links")
                all_links.extend(links)

                if next_page_url:
                    url = next_page_url
                    params = {}
                    page += 1
                else:
                    break

                # Rate limiting
                time.sleep(0.1)

            print(f"Total links found in list ID {list_id}: {len(all_links)}")
            return all_links

        except requests.exceptions.RequestException as e:
            print(f"Error fetching links from list ID {list_id}: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return []
        except Exception as e:
            print(f"Unexpected error for list ID {list_id}: {e}")
            return []

    def get_link_details(self, link_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific link

        Args:
            link_id: The ID of the link to get details for

        Returns:
            Link details dictionary or None if error
        """
        url = f"{self.api_base_url}/links/{link_id}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            return data.get("data")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching link details for ID {link_id}: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching link details for ID {link_id}: {e}")
            return None

    def update_link(self, link_id: int, new_list_ids: List[int]) -> bool:
        """
        Update a link's list assignments

        Args:
            link_id: The ID of the link to update
            new_list_ids: List of list IDs to assign the link to

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.api_base_url}/links/{link_id}"

        # First get current link data
        current_data = self.get_link_details(link_id)
        if not current_data:
            return False

        # Update only the lists field
        update_data = {"lists": new_list_ids}

        try:
            response = requests.put(url, headers=self.headers, json=update_data)
            response.raise_for_status()

            print(f"Successfully updated link {link_id} to lists {new_list_ids}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error updating link {link_id}: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return False
        except Exception as e:
            print(f"Unexpected error updating link {link_id}: {e}")
            return False

    def remove_link_from_list(self, link_id: int, list_id: int) -> bool:
        """
        Remove a link from a specific list

        Args:
            link_id: The ID of the link
            list_id: The ID of the list to remove from

        Returns:
            True if successful, False otherwise
        """
        # Get current link data
        current_data = self.get_link_details(link_id)
        if not current_data:
            return False

        # Get current list assignments
        current_lists = [lst["id"] for lst in current_data.get("lists", [])]

        # Remove the specified list
        if list_id in current_lists:
            new_lists = [lst_id for lst_id in current_lists if lst_id != list_id]
            return self.update_link(link_id, new_lists)

        return True  # Already not in the list

    def add_link_to_list(self, link_id: int, list_id: int) -> bool:
        """
        Add a link to a specific list

        Args:
            link_id: The ID of the link
            list_id: The ID of the list to add to

        Returns:
            True if successful, False otherwise
        """
        # Get current link data
        current_data = self.get_link_details(link_id)
        if not current_data:
            return False

        # Get current list assignments
        current_lists = [lst["id"] for lst in current_data.get("lists", [])]

        # Add the new list if not already present
        if list_id not in current_lists:
            new_lists = current_lists + [list_id]
            return self.update_link(link_id, new_lists)

        return True  # Already in the list

    def move_link_between_lists(
        self, link_id: int, from_list_id: int, to_list_id: int
    ) -> bool:
        """
        Move a link from one list to another

        Args:
            link_id: The ID of the link
            from_list_id: The ID of the source list
            to_list_id: The ID of the destination list

        Returns:
            True if successful, False otherwise
        """
        # Get current link data
        current_data = self.get_link_details(link_id)
        if not current_data:
            return False

        # Get current list assignments
        current_lists = [lst["id"] for lst in current_data.get("lists", [])]

        # Remove from source list and add to destination list
        new_lists = [lst_id for lst_id in current_lists if lst_id != from_list_id]
        if to_list_id not in new_lists:
            new_lists.append(to_list_id)

        return self.update_link(link_id, new_lists)

    def test_connection(self) -> bool:
        """
        Test the connection to the LinkAce API

        Returns:
            True if connection successful, False otherwise
        """
        url = f"{self.api_base_url}/user"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            print("✅ LinkAce API connection successful")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ LinkAce API connection failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error testing connection: {e}")
            return False
