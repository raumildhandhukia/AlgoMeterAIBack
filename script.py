#!/usr/bin/env python3
import json
import requests
import time
from pathlib import Path

# Path to the company JSON file
COMPANY_JSON_PATH = Path(__file__).parent / "data" / "company.json"
# API endpoint base URL
API_BASE_URL = "http://localhost:3000/api/company-list"
# Output file for failed requests
FAILED_REQUESTS_FILE = Path(__file__).parent / "failed_companies.txt"

def load_companies():
    """Load the company data from the JSON file."""
    try:
        with open(COMPANY_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('companyTags', [])
    except Exception as e:
        print(f"Error loading company data: {e}")
        return []

def check_company_endpoint(company_name, slug):
    """Check if the company endpoint returns a 200 status code."""
    url = f"{API_BASE_URL}?slug={slug}"
    try:
        print(f"Checking endpoint for {company_name} ({slug})...")
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def main():
    # Load companies from the JSON file
    companies = load_companies()
    print(f"Loaded {len(companies)} companies")
    
    # Track failed companies
    failed_companies = []
    
    # Process each company
    for i, company in enumerate(companies):
        name = company.get('name', f"Unknown Company {i}")
        slug = company.get('slug')
        if not slug:
            print(f"Skipping company at index {i}: No slug found")
            continue
        
        # Check if the endpoint returns a 200 status code
        if not check_company_endpoint(name, slug):
            print(f"❌ Failed: {name} ({slug})")
            failed_companies.append(f"{name} ({slug})")
        else:
            print(f"✅ Success: {name} ({slug})")
            
        # Add a small delay to avoid overwhelming the server
        time.sleep(0.5)
    
    # Write failed companies to a file
    if failed_companies:
        with open(FAILED_REQUESTS_FILE, 'w', encoding='utf-8') as f:
            f.write(f"Total failed companies: {len(failed_companies)}\n\n")
            for company in failed_companies:
                f.write(f"{company}\n")
        print(f"\nCompleted checking company endpoints. {len(failed_companies)} failures saved to {FAILED_REQUESTS_FILE}")
    else:
        print("\nCompleted checking company endpoints. All requests were successful!")

if __name__ == "__main__":
    main()