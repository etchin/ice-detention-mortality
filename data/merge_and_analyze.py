#!/usr/bin/env python3
"""
Merge and analyze CBP death data from all sources
"""
import pandas as pd
import numpy as np
from datetime import datetime
import re

def standardize_date(date_str):
    """Convert various date formats to YYYY-MM-DD"""
    if pd.isna(date_str) or date_str == '' or date_str is None:
        return None
    
    date_str = str(date_str).strip()
    
    # Already in correct format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    
    # Try various formats
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%m/%d/%y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%d/%m/%Y',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except:
            continue
    
    # Try to extract year at least
    year_match = re.search(r'\b(20\d{2})\b', date_str)
    if year_match:
        return f"{year_match.group(1)}-01-01"  # Default to Jan 1 if only year
    
    return date_str

def extract_year(date_str):
    """Extract year from date string"""
    if pd.isna(date_str) or date_str == '':
        return None
    
    date_str = str(date_str)
    
    # Try to parse as date first
    try:
        if '-' in date_str:
            return int(date_str.split('-')[0])
    except:
        pass
    
    # Look for 4-digit year
    year_match = re.search(r'\b(20\d{2})\b', date_str)
    if year_match:
        return int(year_match.group(1))
    
    return None

def merge_datasets():
    """Merge ACLU and SBCC datasets"""
    print("Loading datasets...")
    
    # Load ACLU data
    aclu_df = pd.read_csv('/home/ubuntu/cbp_deaths/aclu_extracted.csv')
    print(f"ACLU records: {len(aclu_df)}")
    
    # Load SBCC data
    sbcc_df = pd.read_csv('/home/ubuntu/cbp_deaths/sbcc_extracted.csv')
    print(f"SBCC records: {len(sbcc_df)}")
    
    # Load BJS data
    bjs_df = pd.read_csv('/home/ubuntu/cbp_deaths/bjs_official_counts.csv')
    print(f"BJS records: {len(bjs_df)}")
    
    # Standardize ACLU dates
    aclu_df['Date_Standardized'] = aclu_df['Date'].apply(standardize_date)
    aclu_df['Year'] = aclu_df['Date_Standardized'].apply(extract_year)
    
    # Standardize SBCC dates
    sbcc_df['Date_Standardized'] = sbcc_df['Date'].apply(standardize_date)
    sbcc_df['Year_Extracted'] = sbcc_df['Date_Standardized'].apply(extract_year)
    # Use Year_Extracted if available, otherwise use Year column
    sbcc_df['Year'] = sbcc_df['Year_Extracted'].fillna(sbcc_df['Year'].apply(lambda x: int(x) if pd.notna(x) and str(x).isdigit() else None))
    
    # Rename SBCC columns to match ACLU where possible
    sbcc_renamed = sbcc_df.rename(columns={
        'Cause_of_Death': 'Incident_Type_SBCC',
        'Description': 'SBCC_Description'
    })
    
    # Create a unified dataset
    # Start with ACLU as base (more structured data)
    merged = aclu_df.copy()
    
    # Add SBCC-specific columns
    merged['SBCC_Cause_of_Death'] = None
    merged['SBCC_Description'] = None
    merged['In_SBCC'] = 0
    
    # Try to match SBCC records to ACLU records
    print("\nMatching SBCC records to ACLU records...")
    matches = 0
    
    for idx, sbcc_row in sbcc_renamed.iterrows():
        # Try to find match in ACLU data
        matched = False
        
        if pd.notna(sbcc_row['Name']) and sbcc_row['Name'] != 'Unknown':
            # Match by name and approximate date
            name_matches = merged[
                (merged['Name'].str.lower() == sbcc_row['Name'].lower()) |
                (merged['Name'].str.contains(sbcc_row['Name'], case=False, na=False))
            ]
            
            if len(name_matches) > 0:
                # If multiple matches, try to narrow by year
                if pd.notna(sbcc_row['Year']):
                    year_matches = name_matches[name_matches['Year'] == sbcc_row['Year']]
                    if len(year_matches) > 0:
                        name_matches = year_matches
                
                # Update first match with SBCC data
                match_idx = name_matches.index[0]
                merged.at[match_idx, 'SBCC_Cause_of_Death'] = sbcc_row['Incident_Type_SBCC']
                merged.at[match_idx, 'SBCC_Description'] = sbcc_row['SBCC_Description']
                merged.at[match_idx, 'In_SBCC'] = 1
                matched = True
                matches += 1
    
    print(f"Matched {matches} SBCC records to ACLU records")
    
    # Add unmatched SBCC records as new entries
    print("\nAdding unmatched SBCC records...")
    unmatched_sbcc = []
    
    for idx, sbcc_row in sbcc_renamed.iterrows():
        # Check if this was matched
        if pd.notna(sbcc_row['Name']) and sbcc_row['Name'] != 'Unknown':
            name_in_merged = merged[
                (merged['Name'].str.lower() == sbcc_row['Name'].lower()) |
                (merged['Name'].str.contains(sbcc_row['Name'], case=False, na=False))
            ]
            if len(name_in_merged) > 0:
                continue  # Already matched
        
        # Add as new record
        new_record = {
            'Case_Number': None,
            'Name': sbcc_row['Name'],
            'Age': sbcc_row['Age'],
            'Date': sbcc_row['Date'],
            'Date_Standardized': sbcc_row['Date_Standardized'],
            'Location': sbcc_row['Location'],
            'State': None,
            'Nationality': sbcc_row['Nationality'],
            'Incident_Type': sbcc_row['Incident_Type_SBCC'],
            'Minor': 0,
            'US_Citizen_LPR': 0,
            'In_Custody': 0,  # SBCC doesn't specify custody status
            'Off_Duty': 0,
            'Firearm': 0,
            'Wall_Related': 0,
            'Vehicle_Pursuit': 0,
            'Cross_Border_Shooting': 0,
            'Death_Immigration_Enforcement': 0,
            'Source': 'SBCC_Only',
            'Year': sbcc_row['Year'],
            'SBCC_Cause_of_Death': sbcc_row['Incident_Type_SBCC'],
            'SBCC_Description': sbcc_row['SBCC_Description'],
            'In_SBCC': 1
        }
        unmatched_sbcc.append(new_record)
    
    print(f"Adding {len(unmatched_sbcc)} unmatched SBCC records")
    
    if len(unmatched_sbcc) > 0:
        unmatched_df = pd.DataFrame(unmatched_sbcc)
        merged = pd.concat([merged, unmatched_df], ignore_index=True)
    
    # Update Source column
    merged['Source'] = merged.apply(lambda row: 
        'ACLU+SBCC' if row['Source'] == 'ACLU' and row['In_SBCC'] == 1 
        else row['Source'], axis=1)
    
    # Sort by date
    merged = merged.sort_values('Date_Standardized', ascending=False)
    
    return merged, bjs_df

def analyze_data(merged_df, bjs_df):
    """Generate analysis and statistics"""
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\nTotal records: {len(merged_df)}")
    print(f"Records from ACLU only: {len(merged_df[merged_df['Source'] == 'ACLU'])}")
    print(f"Records from SBCC only: {len(merged_df[merged_df['Source'] == 'SBCC_Only'])}")
    print(f"Records in both ACLU and SBCC: {len(merged_df[merged_df['Source'] == 'ACLU+SBCC'])}")
    
    print(f"\nIn-custody deaths: {merged_df['In_Custody'].sum()}")
    print(f"Deaths involving firearms: {merged_df['Firearm'].sum()}")
    print(f"Deaths involving vehicle pursuit: {merged_df['Vehicle_Pursuit'].sum()}")
    print(f"Wall-related deaths: {merged_df['Wall_Related'].sum()}")
    print(f"Cross-border shootings: {merged_df['Cross_Border_Shooting'].sum()}")
    
    # Year-by-year breakdown
    print("\n" + "-"*60)
    print("DEATHS BY YEAR")
    print("-"*60)
    
    year_stats = merged_df.groupby('Year').agg({
        'Name': 'count',
        'In_Custody': 'sum',
        'Firearm': 'sum',
        'Vehicle_Pursuit': 'sum'
    }).rename(columns={
        'Name': 'Total_Deaths',
        'In_Custody': 'In_Custody_Deaths',
        'Firearm': 'Firearm_Deaths',
        'Vehicle_Pursuit': 'Vehicle_Pursuit_Deaths'
    })
    
    print(year_stats.to_string())
    
    # BJS comparison
    print("\n" + "-"*60)
    print("BJS OFFICIAL COUNTS COMPARISON (FY 2016-2019)")
    print("-"*60)
    
    bjs_cbp = bjs_df[bjs_df['Agency'] == 'Customs and Border Protection']
    print("\nBJS CBP Data:")
    print(bjs_cbp.to_string(index=False))
    
    print("\nACLU/SBCC Data for same years:")
    for year in [2016, 2017, 2018, 2019]:
        year_data = merged_df[merged_df['Year'] == year]
        in_custody = year_data['In_Custody'].sum()
        total = len(year_data)
        print(f"  {year}: {total} total deaths, {in_custody} in custody")
    
    return year_stats

def main():
    print("Merging and analyzing CBP death data...\n")
    
    # Merge datasets
    merged_df, bjs_df = merge_datasets()
    
    # Analyze
    year_stats = analyze_data(merged_df, bjs_df)
    
    # Save merged dataset
    print("\n" + "="*60)
    print("SAVING OUTPUT FILES")
    print("="*60)
    
    output_file = '/home/ubuntu/cbp_deaths/cbp_deaths_merged.csv'
    merged_df.to_csv(output_file, index=False)
    print(f"\nMerged dataset saved to: {output_file}")
    
    # Save in-custody deaths
    custody_df = merged_df[merged_df['In_Custody'] == 1]
    custody_file = '/home/ubuntu/cbp_deaths/cbp_deaths_in_custody.csv'
    custody_df.to_csv(custody_file, index=False)
    print(f"In-custody deaths saved to: {custody_file}")
    
    # Save year statistics
    year_file = '/home/ubuntu/cbp_deaths/cbp_deaths_by_year.csv'
    year_stats.to_csv(year_file)
    print(f"Year statistics saved to: {year_file}")
    
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)

if __name__ == '__main__':
    main()
