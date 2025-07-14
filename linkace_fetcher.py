#!/usr/bin/env python3
"""
LinkAce API Link Fetcher

This script fetches all links from specified LinkAce lists and outputs them to a CSV file.
The output format is: link.url,list_id

Usage:
    python linkace_fetcher.py [--api-url URL] [--api-token TOKEN] [--output FILE]
"""

import requests
import csv
import sys
import argparse
from typing import List, Dict, Any

# Default Configuration
DEFAULT_API_TOKEN = "YOUR_API_TOKEN_HERE"
DEFAULT_LIST_IDS = [12, 5, 4, 15, 3, 2, 7, 1, 17, 13]
DEFAULT_OUTPUT_FILE = "linkace_links.csv"

def get_links_from_list(api_base_url: str, api_token: str, list_id: int) -> List[Dict[str, Any]]:
    """
    Fetch all links from a specific list ID using pagination.
    
    Args:
        api_base_url: The base URL of the LinkAce API
        api_token: The API token for authentication
        list_id: The ID of the list to fetch links from
        
    Returns:
        List of link dictionaries
    """
    all_links = []
    url = f"{api_base_url}/lists/{list_id}/links"
    headers = {
        "Authorization": f"Bearer {api_token}",
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

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch links from LinkAce lists and export to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python linkace_fetcher.py --api-url https://linkace.example.com/api/v2
  python linkace_fetcher.py --api-url https://linkace.example.com/api/v2 --output my_links.csv
  python linkace_fetcher.py --api-url https://linkace.example.com/api/v2 --api-token your-token-here
        """
    )
    
    parser.add_argument(
        "--api-url", 
        required=True,
        help="Base URL of your LinkAce API (e.g., https://linkace.example.com/api/v2)"
    )
    parser.add_argument(
        "--api-token", 
        default=DEFAULT_API_TOKEN,
        help=f"API token for authentication (default: {DEFAULT_API_TOKEN[:20]}...)"
    )
    parser.add_argument(
        "--output", 
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output CSV file name (default: {DEFAULT_OUTPUT_FILE})"
    )
    parser.add_argument(
        "--list-ids",
        nargs="+",
        type=int,
        default=DEFAULT_LIST_IDS,
        help=f"List IDs to fetch links from (default: {DEFAULT_LIST_IDS})"
    )
    
    return parser.parse_args()

def main():
    """Main function to fetch all links and write to CSV."""
    args = parse_arguments()
    
    # Validate API URL format
    if not args.api_url.startswith(('http://', 'https://')):
        print("Error: API URL must start with http:// or https://")
        sys.exit(1)
    
    # Remove trailing slash if present
    api_base_url = args.api_url.rstrip('/')
    
    all_links = []
    
    print("Starting LinkAce API link fetching with pagination...")
    print(f"API URL: {api_base_url}")
    print(f"Target list IDs: {args.list_ids}")
    print(f"Output file: {args.output}")
    print()
    
    # Fetch links from each list
    for list_id in args.list_ids:
        links = get_links_from_list(api_base_url, args.api_token, list_id)
        
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
            with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
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
            
            print(f"\n✅ Success! Written {len(all_links)} links to {args.output}")
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

