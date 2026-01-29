#!/usr/bin/env python3
"""
Extract CBP fatal encounters data from SBCC webpage
"""
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

def parse_sbcc_date(date_str):
    """Parse various date formats from SBCC"""
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # Try different formats
    formats = [
        '%B %d, %Y',  # January 1, 2020
        '%b %d, %Y',  # Jan 1, 2020
        '%m/%d/%Y',   # 1/1/2020
        '%m/%d/%y',   # 1/1/20
        '%Y-%m-%d',   # 2020-01-01
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except:
            continue
    
    return date_str

def extract_sbcc_data(html_path):
    """Extract narrative data from SBCC HTML page"""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    all_entries = []
    
    # Find the main content area
    # SBCC organizes entries by year in sections
    content = soup.find('div', class_='field-item')
    
    if not content:
        # Try alternative selectors
        content = soup.find('div', class_='node-content')
    
    if not content:
        content = soup.find('body')
    
    # Look for year headers and entries
    current_year = None
    
    # Find all paragraphs and headers
    for element in content.find_all(['h2', 'h3', 'p', 'div']):
        text = element.get_text(' ', strip=True)
        
        # Check if this is a year header
        year_match = re.search(r'\b(20\d{2})\b', text)
        if year_match and len(text) < 20:  # Short text likely a header
            current_year = year_match.group(1)
            continue
        
        # Look for entries with typical patterns
        # Pattern: Name, Age, Nationality, Date, Location, Cause
        if 'Age:' in text or 'Cause of Death:' in text or 'Nationality:' in text:
            entry = parse_sbcc_entry(text, current_year)
            if entry:
                all_entries.append(entry)
    
    df = pd.DataFrame(all_entries)
    
    if len(df) > 0:
        df = df.drop_duplicates()
        df = df.sort_values('Date', ascending=False)
    
    return df

def parse_sbcc_entry(text, year=None):
    """Parse a single SBCC narrative entry"""
    entry = {
        'Name': None,
        'Age': None,
        'Nationality': None,
        'Date': None,
        'Location': None,
        'Cause_of_Death': None,
        'Description': text,
        'Year': year,
        'Source': 'SBCC'
    }
    
    # Extract name (usually at the beginning)
    name_match = re.match(r'^([A-Z][a-zA-Z\s\-\.]+?)(?:,|\s+Age:|\s+Nationality:)', text)
    if name_match:
        entry['Name'] = name_match.group(1).strip()
    
    # Extract age
    age_match = re.search(r'Age:\s*(\d+|unknown|Unknown)', text, re.IGNORECASE)
    if age_match:
        age_val = age_match.group(1)
        entry['Age'] = age_val if age_val.lower() != 'unknown' else None
    
    # Extract nationality
    nat_match = re.search(r'Nationality:\s*([A-Za-z\s]+?)(?:\s+Cause|\s+Date|\s+Location|\.)', text)
    if nat_match:
        entry['Nationality'] = nat_match.group(1).strip()
    
    # Extract cause of death
    cause_match = re.search(r'Cause of Death:\s*([^\.]+)', text)
    if cause_match:
        entry['Cause_of_Death'] = cause_match.group(1).strip()
    
    # Extract date
    date_patterns = [
        r'Date:\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'Date:\s*(\d{1,2}/\d{1,2}/\d{2,4})',
        r'on\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'(\d{1,2}/\d{1,2}/\d{2,4})',
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text)
        if date_match:
            entry['Date'] = parse_sbcc_date(date_match.group(1))
            break
    
    # Extract location
    loc_match = re.search(r'Location:\s*([^\.]+)', text)
    if loc_match:
        entry['Location'] = loc_match.group(1).strip()
    else:
        # Try to find location from common patterns
        loc_patterns = [
            r'in\s+([A-Z][a-zA-Z\s]+,\s*[A-Z]{2})',
            r'near\s+([A-Z][a-zA-Z\s]+,\s*[A-Z]{2})',
        ]
        for pattern in loc_patterns:
            loc_match = re.search(pattern, text)
            if loc_match:
                entry['Location'] = loc_match.group(1).strip()
                break
    
    # Only return entry if we have at least a name or date
    if entry['Name'] or entry['Date']:
        return entry
    
    return None

if __name__ == '__main__':
    print("Extracting SBCC Fatal Encounters data...")
    df = extract_sbcc_data('/home/ubuntu/cbp_deaths/sbcc_page.html')
    
    print(f"\nExtracted {len(df)} records")
    if len(df) > 0:
        print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"Years covered: {sorted(df['Year'].dropna().unique())}")
    
    # Save to CSV
    output_file = '/home/ubuntu/cbp_deaths/sbcc_extracted.csv'
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")
