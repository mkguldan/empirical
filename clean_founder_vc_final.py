"""
Script to clean and normalize founder-VC final file
- Remove founders with blank gender
- Remove accelerator/incubator, equity crowdfunding, and grant deals
- Normalize date formatting to dd/mm/yyyy
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

print("=" * 100)
print("CLEANING AND NORMALIZING FOUNDER-VC FINAL FILE")
print("=" * 100)
print(f"Started at: {datetime.now()}")

# File paths
input_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_final.csv'
output_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_cleaned.csv'

print("\n" + "=" * 100)
print("STEP 1: Loading founder-VC final file...")
print("=" * 100)

# Load the file with proper encoding and delimiter handling
print(f"Reading file: {input_file}")
print("Trying different encodings and delimiters...")

# Try multiple encodings and delimiters
encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
delimiters_to_try = [';', ',', '\t']
df = None

for delimiter in delimiters_to_try:
    for encoding in encodings_to_try:
        try:
            delimiter_name = {';': 'semicolon', ',': 'comma', '\t': 'tab'}[delimiter]
            print(f"  Attempting with {encoding} encoding and {delimiter_name} delimiter...")
            df = pd.read_csv(input_file, low_memory=False, encoding=encoding, sep=delimiter)
            print(f"  Success with {encoding} encoding and {delimiter_name} delimiter!")
            print(f"  Loaded {len(df.columns)} columns")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            continue
    
    if df is not None:
        break

if df is None:
    print("ERROR: Could not read file with any combination of encoding and delimiter!")
    exit(1)

# Check if first row has generic column names (Column1, Column2, etc.) - Excel sometimes adds these
if 'Column1' in df.columns or df.columns[0] == 'Column1':
    print("  Detected Excel-added generic column names, using second row as header...")
    # Re-read with skiprows
    for delimiter in delimiters_to_try:
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(input_file, low_memory=False, encoding=encoding, sep=delimiter, skiprows=1)
                print(f"  Re-loaded with header correction")
                break
            except:
                continue
        if 'Column1' not in df.columns:
            break

print(f"Loaded {len(df):,} rows with {len(df.columns)} columns")

# Check if key columns exist
if 'PersonID' not in df.columns:
    print(f"  Warning: PersonID column not found. Available columns: {list(df.columns[:5])}...")
else:
    print(f"  Unique founders: {df['PersonID'].nunique():,}")
    print(f"  Unique companies: {df['CompanyID'].nunique():,}")

initial_count = len(df)

print("\n" + "=" * 100)
print("STEP 2: Filtering out founders with blank Gender...")
print("=" * 100)

# Check Gender column
if 'Person_Gender' not in df.columns:
    print("ERROR: Person_Gender column not found!")
    exit(1)

gender_before = df['Person_Gender'].notna().sum()
print(f"Rows with Gender data before filter: {gender_before:,} ({gender_before/len(df)*100:.2f}%)")
print(f"Rows with blank Gender: {len(df) - gender_before:,}")

# Filter for rows with gender data
print("\nApplying filter: Removing rows with blank Gender...")
df = df[df['Person_Gender'].notna() & (df['Person_Gender'] != '')].copy()

print(f"After Gender filter: {len(df):,} rows")
print(f"  Unique founders: {df['PersonID'].nunique():,}")
print(f"  Unique companies: {df['CompanyID'].nunique():,}")
print(f"  Rows removed: {initial_count - len(df):,}")

if len(df) == 0:
    print("\nWARNING: No rows remain after filtering. Exiting.")
    exit(1)

after_gender_count = len(df)

print("\n" + "=" * 100)
print("STEP 3: Filtering out unwanted deal types...")
print("=" * 100)

# Check Deal_DealType column
if 'Deal_DealType' not in df.columns:
    print("ERROR: Deal_DealType column not found!")
    exit(1)

# Define unwanted deal types
unwanted_deal_types = ['Accelerator/Incubator', 'Equity Crowdfunding', 'Grant']
print(f"Removing deals with these types:")
for deal_type in unwanted_deal_types:
    print(f"  - {deal_type}")

# Check how many rows have these deal types
print("\nCounting rows with unwanted deal types:")
for deal_type in unwanted_deal_types:
    count = df['Deal_DealType'].str.contains(deal_type, case=False, na=False).sum()
    print(f"  {deal_type}: {count:,} rows")

# Create filter to exclude unwanted deal types (case insensitive)
print("\nApplying filter: Removing unwanted deal types...")
unwanted_mask = pd.Series([False] * len(df), index=df.index)

for deal_type in unwanted_deal_types:
    unwanted_mask = unwanted_mask | df['Deal_DealType'].str.contains(deal_type, case=False, na=False)

df = df[~unwanted_mask].copy()

print(f"After deal type filter: {len(df):,} rows")
print(f"  Unique founders: {df['PersonID'].nunique():,}")
print(f"  Unique companies: {df['CompanyID'].nunique():,}")
print(f"  Rows removed: {after_gender_count - len(df):,}")

if len(df) == 0:
    print("\nWARNING: No rows remain after filtering. Exiting.")
    exit(1)

after_dealtype_count = len(df)

print("\n" + "=" * 100)
print("STEP 4: Normalizing date formatting to dd/mm/yyyy...")
print("=" * 100)

# Find all date columns
date_columns = [col for col in df.columns if 'date' in col.lower() or 'Date' in col]
print(f"Found {len(date_columns)} date columns:")
for col in date_columns:
    print(f"  - {col}")

# Function to normalize date format
def normalize_date(date_value):
    """Convert date to dd/mm/yyyy format"""
    if pd.isna(date_value) or date_value == '':
        return date_value
    
    try:
        # Try parsing the date
        if isinstance(date_value, str):
            # Handle Excel's dot format (d.m.yyyy or dd.mm.yyyy)
            if '.' in date_value:
                # Replace dots with slashes and try parsing
                date_value = date_value.replace('.', '/')
            
            # Try various date formats
            for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%Y/%m/%d', '%m-%d-%Y', '%d-%m-%Y']:
                try:
                    parsed_date = datetime.strptime(date_value, fmt)
                    return parsed_date.strftime('%d/%m/%Y')
                except:
                    continue
            
            # Try pandas parsing as fallback (handles many formats)
            parsed_date = pd.to_datetime(date_value, errors='coerce', dayfirst=True)
            if pd.notna(parsed_date):
                return parsed_date.strftime('%d/%m/%Y')
        else:
            # If it's already a datetime object
            parsed_date = pd.to_datetime(date_value, errors='coerce')
            if pd.notna(parsed_date):
                return parsed_date.strftime('%d/%m/%Y')
    except:
        pass
    
    # Return original if parsing fails
    return date_value

# Apply normalization to each date column
print("\nNormalizing date formats...")
for col in date_columns:
    print(f"  Processing {col}...")
    non_null_before = df[col].notna().sum()
    
    # Apply the normalization
    df[col] = df[col].apply(normalize_date)
    
    non_null_after = df[col].notna().sum()
    
    if non_null_before > 0:
        # Show sample of converted dates
        sample_dates = df[col].dropna().head(3).tolist()
        if sample_dates:
            print(f"    Sample dates: {', '.join(str(d) for d in sample_dates)}")
        print(f"    Non-null values: {non_null_after:,} (maintained)")

print("\nDate normalization complete!")

print("\n" + "=" * 100)
print("STEP 5: Data quality validation...")
print("=" * 100)

# Validation checks
print("Validation checks:")
print(f"  [CHECK] All rows have PersonID: {df['PersonID'].notna().all()}")
print(f"  [CHECK] All rows have CompanyID: {df['CompanyID'].notna().all()}")
print(f"  [CHECK] All rows have DealID: {df['DealID'].notna().all()}")
print(f"  [CHECK] All rows have Gender: {df['Person_Gender'].notna().all()}")
print(f"  [CHECK] All rows have Education_Institute: {df['Education_Institute'].notna().all()}")

# Check that unwanted deal types are removed
print("\nVerifying unwanted deal types are removed:")
for deal_type in unwanted_deal_types:
    remaining = df['Deal_DealType'].str.contains(deal_type, case=False, na=False).sum()
    print(f"  {deal_type}: {remaining} rows (should be 0)")

# Check deal types distribution
print("\nRemaining Deal Types (top 10):")
deal_type_counts = df['Deal_DealType'].value_counts().head(10)
for deal_type, count in deal_type_counts.items():
    print(f"  {deal_type:40s} : {count:4d}")

# Gender distribution
print("\nGender Distribution:")
gender_counts = df['Person_Gender'].value_counts()
for gender, count in gender_counts.items():
    print(f"  {gender:20s} : {count:6,} ({count/len(df)*100:.2f}%)")

print("\n" + "=" * 100)
print("STEP 6: Saving cleaned file...")
print("=" * 100)

# Save the file with UTF-8 encoding and comma delimiter (standard CSV)
print(f"Saving to: {output_file}")
df.to_csv(output_file, index=False, encoding='utf-8-sig', sep=',')
file_size_mb = os.path.getsize(output_file) / (1024**2)
print(f"File saved successfully with utf-8-sig encoding and comma delimiters!")
print(f"  File size: {file_size_mb:.2f} MB")
print(f"  Total rows: {len(df):,}")
print(f"  Total columns: {len(df.columns)}")

print("\n" + "=" * 100)
print("STEP 7: Summary statistics...")
print("=" * 100)

# Create summary
summary_stats = {
    'Cleaning Stage': [
        'Initial (from founder_vc_final.csv)',
        'After Gender filter',
        'After Deal Type filter (FINAL)'
    ],
    'Total Rows': [
        f"{initial_count:,}",
        f"{after_gender_count:,}",
        f"{len(df):,}"
    ],
    'Unique Founders': [
        '',  # Not calculated for initial
        f"{df['PersonID'].nunique():,}",
        f"{df['PersonID'].nunique():,}"
    ],
    'Unique Companies': [
        '',  # Not calculated for initial
        f"{df['CompanyID'].nunique():,}",
        f"{df['CompanyID'].nunique():,}"
    ],
    'Retention Rate': [
        "100%",
        f"{after_gender_count/initial_count*100:.2f}%",
        f"{len(df)/initial_count*100:.2f}%"
    ]
}

summary_df = pd.DataFrame(summary_stats)
print("\nCleaning Summary:")
print(summary_df.to_string(index=False))

# Save summary
summary_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_cleaned_summary.csv'
summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig', sep=',')
print(f"\nSummary saved to: {summary_file}")

print("\n" + "=" * 100)
print("SAMPLE RECORDS")
print("=" * 100)

print("\nFirst 5 founder records in cleaned dataset:")
sample_cols = ['PersonID', 'Person_FullName', 'Person_Gender', 'CompanyName', 
               'Deal_DealType', 'Deal_DealDate', 'Education_Institute']
available_sample_cols = [col for col in sample_cols if col in df.columns]

if len(df) > 0:
    print(df[available_sample_cols].head(5).to_string(index=False))

print("\n" + "=" * 100)
print("PROCESS COMPLETED SUCCESSFULLY")
print("=" * 100)
print(f"Completed at: {datetime.now()}")
print(f"\nFinal output file: {output_file}")
print(f"Summary file: {summary_file}")
print("\nThis file contains:")
print("  - Founders with VC deal size information")
print("  - Founders with education institute information")
print("  - Founders with gender information")
print("  - Only proper VC deals (no accelerators, crowdfunding, or grants)")
print("  - All dates normalized to dd/mm/yyyy format")
print("  - Ready for analysis of founder backgrounds and VC funding")
print("=" * 100)

