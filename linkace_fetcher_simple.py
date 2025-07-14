#!/usr/bin/env python3
"""
LinkAce API Link Fetcher (Simple Configuration Version)

This script fetches all links from specified LinkAce lists and outputs them to a CSV file.
The output format is: link.url,list_id

CONFIGURATION:
Edit the values below to match your LinkAce setup.
"""

import requests
import csv
import sys
from typing import List, Dict, Any

# ============================================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================================

# Your LinkAce API base URL (replace with your actual LinkAce instance URL)
API_BASE_URL = "https://shared.girard-davila.net/api/v2"

# Your API token (get this from your LinkAce user settings)
API_TOKEN = "YOUR_API_TOKEN_HERE"

# List IDs to fetch links from
LIST_IDS = [12, 5, 4, 15, 3, 2, 7, 1, 17, 13]

# Output CSV file name
OUTPUT_FILE = "linkace_links.csv"

# ============================================================================
# DO NOT EDIT BELOW THIS LINE
# ============================================================================

def get_links_from_list(list_id: int) -> List[Dict[str, Any]]:
    """
    Fetch all links from a specific list ID using pagination.
    
    Args:
        list_id: The ID of the list to fetch links from
        
    Returns:
        List of link dictionaries
    """
    all_links = []
    url = f"{API_BASE_URL}/lists/{list_id}/links"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    page = 1
    
    try:
        print(f"Fetching links from list ID {list_id}...")
        
        while url:
            # Add pagination parameters
            params = {"page": page}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            links = data.get("data", [])
            current_page = data.get("current_page", page)
            last_page = data.get("last_page", 1)
            next_page_url = data.get("next_page_url")
            
            print(f"  Page {current_page}/{last_page}: Found {len(links)} links")
            all_links.extend(links)
            
            # Check if there's a next page
            if next_page_url:
                # Use the full next_page_url provided by the API
                url = next_page_url
                # Remove params since the URL already contains them
                params = {}
                page += 1
            else:
                # No more pages
                break
        
        print(f"Total links found in list ID {list_id}: {len(all_links)}")
        return all_links
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching links from list ID {list_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return []
    except Exception as e:
        print(f"Unexpected error for list ID {list_id}: {e}")
        return []

def validate_configuration():
    """Validate the configuration before running."""
    if API_BASE_URL == "https://your-linkace-instance.com/api/v2":
        print("ERROR: Please update the API_BASE_URL in the configuration section!")
        print("Replace 'https://your-linkace-instance.com/api/v2' with your actual LinkAce API URL.")
        return False
    
    if not API_BASE_URL.startswith(('http://', 'https://')):
        print("ERROR: API_BASE_URL must start with http:// or https://")
        return False
    
    if not API_TOKEN:
        print("ERROR: API_TOKEN cannot be empty!")
        return False
    
    if not LIST_IDS:
        print("ERROR: LIST_IDS cannot be empty!")
        return False
    
    return True

def main():
    """Main function to fetch all links and write to CSV."""
    print("LinkAce API Link Fetcher")
    print("=" * 40)
    
    # Validate configuration
    if not validate_configuration():
        sys.exit(1)
    
    all_links = []
    
    print(f"API URL: {API_BASE_URL}")
    print(f"Target list IDs: {LIST_IDS}")
    print(f"Output file: {OUTPUT_FILE}")
    print()
    
    # Fetch links from each list
    for list_id in LIST_IDS:
        links = get_links_from_list(list_id)
        
        # Add list_id to each link for CSV output
        for link in links:
            link_data = {
                "url": link.get("url", ""),
                "list_id": list_id
            }
            all_links.append(link_data)
    
    # Write to CSV file
    if all_links:
        try:
            with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['url', 'list_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write data
                for link in all_links:
                    writer.writerow({
                        'url': link['url'],
                        'list_id': link['list_id']
                    })
            
            print(f"\n✅ Success! Written {len(all_links)} links to {OUTPUT_FILE}")
            print(f"📄 CSV format: url,list_id")
            
            # Show first few entries as preview
            if len(all_links) > 0:
                print(f"\n📋 Preview of first few entries:")
                for i, link in enumerate(all_links[:5]):
                    print(f"   {link['url']} -> List ID: {link['list_id']}")
                if len(all_links) > 5:
                    print(f"   ... and {len(all_links) - 5} more entries")
            
        except Exception as e:
            print(f"❌ Error writing to CSV file: {e}")
            sys.exit(1)
    else:
        print("⚠️  No links found to write to CSV file.")
        print("This could mean:")
        print("  - The list IDs don't exist")
        print("  - The API token doesn't have access to these lists")
        print("  - The API URL is incorrect")
        print("  - Network connectivity issues")
        sys.exit(1)

if __name__ == "__main__":
    main()

