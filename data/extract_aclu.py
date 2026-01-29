#!/usr/bin/env python3
"""
Extract CBP fatal encounters data from ACLU detailed PDF
"""
import pdfplumber
import pandas as pd
import re
from datetime import datetime

def clean_text(text):
    """Clean and normalize text fields"""
    if text is None or text == '':
        return None
    return str(text).strip()

def parse_date(date_str):
    """Parse date string to standard format"""
    if not date_str or date_str == '':
        return None
    
    date_str = clean_text(date_str)
    
    # Try different date formats
    for fmt in ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y']:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except:
            continue
    
    return date_str  # Return original if parsing fails

def extract_aclu_data(pdf_path):
    """Extract table data from ACLU PDF"""
    all_rows = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Processing {len(pdf.pages)} pages...")
        
        for page_num, page in enumerate(pdf.pages, 1):
            if page_num % 10 == 0:
                print(f"  Page {page_num}/{len(pdf.pages)}")
            
            # Extract tables from the page
            tables = page.extract_tables()
            
            for table in tables:
                if not table:
                    continue
                
                # Skip header rows (first page has headers)
                start_idx = 1 if page_num == 1 else 0
                
                for row in table[start_idx:]:
                    if not row or len(row) < 10:  # Skip incomplete rows
                        continue
                    
                    # Skip if first cell is empty or looks like a header
                    if not row[0] or row[0] in ['#', 'Name', '']:
                        continue
                    
                    # Extract all columns
                    try:
                        case_num = clean_text(row[0])
                        name = clean_text(row[1])
                        age = clean_text(row[2])
                        date = parse_date(row[3])
                        location = clean_text(row[4])
                        state = clean_text(row[5])
                        nationality = clean_text(row[6])
                        incident_type = clean_text(row[7])
                        
                        # Binary flags (0/1)
                        minor = clean_text(row[8]) if len(row) > 8 else '0'
                        us_citizen_lpr = clean_text(row[9]) if len(row) > 9 else '0'
                        in_custody = clean_text(row[10]) if len(row) > 10 else '0'
                        off_duty = clean_text(row[11]) if len(row) > 11 else '0'
                        firearm = clean_text(row[12]) if len(row) > 12 else '0'
                        wall_related = clean_text(row[13]) if len(row) > 13 else '0'
                        vehicle_pursuit = clean_text(row[14]) if len(row) > 14 else '0'
                        cross_border_shooting = clean_text(row[15]) if len(row) > 15 else '0'
                        death_immigration_enforcement = clean_text(row[16]) if len(row) > 16 else '0'
                        
                        # Skip rows without essential data
                        if not name and not date:
                            continue
                        
                        all_rows.append({
                            'Case_Number': case_num,
                            'Name': name,
                            'Age': age,
                            'Date': date,
                            'Location': location,
                            'State': state,
                            'Nationality': nationality,
                            'Incident_Type': incident_type,
                            'Minor': minor,
                            'US_Citizen_LPR': us_citizen_lpr,
                            'In_Custody': in_custody,
                            'Off_Duty': off_duty,
                            'Firearm': firearm,
                            'Wall_Related': wall_related,
                            'Vehicle_Pursuit': vehicle_pursuit,
                            'Cross_Border_Shooting': cross_border_shooting,
                            'Death_Immigration_Enforcement': death_immigration_enforcement,
                            'Source': 'ACLU'
                        })
                    except Exception as e:
                        print(f"Error processing row on page {page_num}: {e}")
                        continue
    
    # Create DataFrame
    df = pd.DataFrame(all_rows)
    
    # Clean up the data
    df = df.drop_duplicates()
    
    # Convert binary flags to integers where possible
    binary_cols = ['Minor', 'US_Citizen_LPR', 'In_Custody', 'Off_Duty', 'Firearm', 
                   'Wall_Related', 'Vehicle_Pursuit', 'Cross_Border_Shooting', 
                   'Death_Immigration_Enforcement']
    
    for col in binary_cols:
        df[col] = df[col].apply(lambda x: 1 if str(x).strip() == '1' else 0)
    
    # Sort by date (most recent first)
    df = df.sort_values('Date', ascending=False)
    
    return df

if __name__ == '__main__':
    print("Extracting ACLU Fatal Encounters data...")
    df = extract_aclu_data('/home/ubuntu/cbp_deaths/aclu_detailed.pdf')
    
    print(f"\nExtracted {len(df)} records")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"In-custody deaths: {df['In_Custody'].sum()}")
    
    # Save to CSV
    output_file = '/home/ubuntu/cbp_deaths/aclu_extracted.csv'
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")
    
    # Save in-custody deaths separately
    custody_df = df[df['In_Custody'] == 1]
    custody_file = '/home/ubuntu/cbp_deaths/aclu_in_custody.csv'
    custody_df.to_csv(custody_file, index=False)
    print(f"In-custody deaths saved to {custody_file}")
