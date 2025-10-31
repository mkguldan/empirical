"""
Script to further filter founder-VC analysis file
Keeps only founders with deal size and education institute data
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

print("=" * 100)
print("FINAL FILTERING: FOUNDER-VC ANALYSIS WITH DEAL SIZE AND EDUCATION")
print("=" * 100)
print(f"Started at: {datetime.now()}")

# File paths
input_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_analysis.csv'
output_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_final.csv'

print("\n" + "=" * 100)
print("STEP 1: Loading founder-VC analysis file...")
print("=" * 100)

# Load the file with proper encoding handling
print(f"Reading file: {input_file}")
print("Trying different encodings...")

# Try multiple encodings
encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
df = None

for encoding in encodings_to_try:
    try:
        print(f"  Attempting with {encoding} encoding...")
        df = pd.read_csv(input_file, low_memory=False, encoding=encoding)
        print(f"  Success with {encoding} encoding!")
        break
    except UnicodeDecodeError:
        print(f"  Failed with {encoding}")
        continue
    except Exception as e:
        print(f"  Error with {encoding}: {e}")
        continue

if df is None:
    print("ERROR: Could not read file with any encoding!")
    exit(1)
print(f"Loaded {len(df):,} rows with {len(df.columns)} columns")
print(f"  Unique founders: {df['PersonID'].nunique():,}")
print(f"  Unique companies: {df['CompanyID'].nunique():,}")

print("\n" + "=" * 100)
print("STEP 2: Filtering for rows with deal size...")
print("=" * 100)

# Check which deal size columns exist and have data
print("Checking deal size columns...")

has_investor_deal_size = 'Investor_DealSize' in df.columns
has_deal_deal_size = 'Deal_DealSize' in df.columns

if has_investor_deal_size:
    investor_size_count = df['Investor_DealSize'].notna().sum()
    print(f"  Investor_DealSize: {investor_size_count:,} rows with data ({investor_size_count/len(df)*100:.2f}%)")

if has_deal_deal_size:
    deal_size_count = df['Deal_DealSize'].notna().sum()
    print(f"  Deal_DealSize: {deal_size_count:,} rows with data ({deal_size_count/len(df)*100:.2f}%)")

# Filter for rows with deal size (check both columns)
print("\nApplying filter: Keep rows with deal size data...")

if has_investor_deal_size and has_deal_deal_size:
    # Keep rows that have data in either column
    filtered_df = df[
        (df['Investor_DealSize'].notna() & (df['Investor_DealSize'] != '')) | 
        (df['Deal_DealSize'].notna() & (df['Deal_DealSize'] != ''))
    ].copy()
    print("  Filter: Keeping rows with Investor_DealSize OR Deal_DealSize")
elif has_investor_deal_size:
    filtered_df = df[df['Investor_DealSize'].notna() & (df['Investor_DealSize'] != '')].copy()
    print("  Filter: Keeping rows with Investor_DealSize")
elif has_deal_deal_size:
    filtered_df = df[df['Deal_DealSize'].notna() & (df['Deal_DealSize'] != '')].copy()
    print("  Filter: Keeping rows with Deal_DealSize")
else:
    print("  ERROR: No deal size columns found!")
    exit(1)

print(f"\nAfter deal size filter: {len(filtered_df):,} rows")
print(f"  Unique founders: {filtered_df['PersonID'].nunique():,}")
print(f"  Unique companies: {filtered_df['CompanyID'].nunique():,}")
print(f"  Rows removed: {len(df) - len(filtered_df):,}")

if len(filtered_df) == 0:
    print("\nWARNING: No rows remain after filtering. Exiting.")
    exit(1)

print("\n" + "=" * 100)
print("STEP 3: Filtering for founders with education institute data...")
print("=" * 100)

# Check Education_Institute column
if 'Education_Institute' not in filtered_df.columns:
    print("ERROR: Education_Institute column not found!")
    exit(1)

education_count_before = filtered_df['Education_Institute'].notna().sum()
print(f"Rows with Education_Institute data: {education_count_before:,} ({education_count_before/len(filtered_df)*100:.2f}%)")

# Filter for rows with education institute
print("\nApplying filter: Keep rows with Education_Institute data...")
final_df = filtered_df[filtered_df['Education_Institute'].notna() & (filtered_df['Education_Institute'] != '')].copy()

print(f"\nAfter education filter: {len(final_df):,} rows")
print(f"  Unique founders: {final_df['PersonID'].nunique():,}")
print(f"  Unique companies: {final_df['CompanyID'].nunique():,}")
print(f"  Rows removed: {len(filtered_df) - len(final_df):,}")

if len(final_df) == 0:
    print("\nWARNING: No rows remain after filtering. Exiting.")
    exit(1)

print("\n" + "=" * 100)
print("STEP 4: Data quality validation...")
print("=" * 100)

# Validation checks
print("Validation checks:")
print(f"  [CHECK] All rows have PersonID: {final_df['PersonID'].notna().all()}")
print(f"  [CHECK] All rows have CompanyID: {final_df['CompanyID'].notna().all()}")
print(f"  [CHECK] All rows have DealID: {final_df['DealID'].notna().all()}")
print(f"  [CHECK] All rows have Education_Institute: {final_df['Education_Institute'].notna().all()}")

# Check deal size
if has_investor_deal_size:
    investor_size_final = final_df['Investor_DealSize'].notna().sum()
    print(f"  [CHECK] Rows with Investor_DealSize: {investor_size_final:,} ({investor_size_final/len(final_df)*100:.2f}%)")

if has_deal_deal_size:
    deal_size_final = final_df['Deal_DealSize'].notna().sum()
    print(f"  [CHECK] Rows with Deal_DealSize: {deal_size_final:,} ({deal_size_final/len(final_df)*100:.2f}%)")

print("\n" + "=" * 100)
print("STEP 5: Saving final filtered file...")
print("=" * 100)

# Save the file with UTF-8 encoding
print(f"Saving to: {output_file}")
final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
file_size_mb = os.path.getsize(output_file) / (1024**2)
print(f"File saved successfully!")
print(f"  File size: {file_size_mb:.2f} MB")
print(f"  Total rows: {len(final_df):,}")
print(f"  Total columns: {len(final_df.columns)}")

print("\n" + "=" * 100)
print("STEP 6: Summary statistics...")
print("=" * 100)

# Create summary
summary_stats = {
    'Filter Stage': [
        'Initial (from founder_vc_analysis.csv)',
        'After deal size filter',
        'After education institute filter (FINAL)'
    ],
    'Total Rows': [
        f"{len(df):,}",
        f"{len(filtered_df):,}",
        f"{len(final_df):,}"
    ],
    'Unique Founders': [
        f"{df['PersonID'].nunique():,}",
        f"{filtered_df['PersonID'].nunique():,}",
        f"{final_df['PersonID'].nunique():,}"
    ],
    'Unique Companies': [
        f"{df['CompanyID'].nunique():,}",
        f"{filtered_df['CompanyID'].nunique():,}",
        f"{final_df['CompanyID'].nunique():,}"
    ],
    'Retention Rate': [
        "100%",
        f"{len(filtered_df)/len(df)*100:.2f}%",
        f"{len(final_df)/len(df)*100:.2f}%"
    ]
}

summary_df = pd.DataFrame(summary_stats)
print("\nFiltering Summary:")
print(summary_df.to_string(index=False))

# Save summary
summary_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_final_summary.csv'
summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
print(f"\nSummary saved to: {summary_file}")

print("\n" + "=" * 100)
print("SAMPLE RECORDS")
print("=" * 100)

print("\nFirst 5 founder records in final dataset:")
sample_cols = ['PersonID', 'Person_FullName', 'CompanyName', 
               'Deal_DealSize', 'Investor_DealSize', 'Education_Institute', 'Education_Degree']
available_sample_cols = [col for col in sample_cols if col in final_df.columns]

if len(final_df) > 0:
    print(final_df[available_sample_cols].head(5).to_string(index=False))

print("\n" + "=" * 100)
print("ADDITIONAL STATISTICS")
print("=" * 100)

# Top education institutes
print("\nTop 10 Education Institutes:")
top_institutes = final_df['Education_Institute'].value_counts().head(10)
for i, (institute, count) in enumerate(top_institutes.items(), 1):
    print(f"  {i:2d}. {institute:50s} : {count:4d} founders")

# Distribution of founders per company
print("\nFounders per Company Distribution:")
founders_per_company = final_df.groupby('CompanyID').size()
print(f"  Companies with 1 founder:  {(founders_per_company == 1).sum():,}")
print(f"  Companies with 2 founders: {(founders_per_company == 2).sum():,}")
print(f"  Companies with 3+ founders: {(founders_per_company >= 3).sum():,}")
print(f"  Average founders per company: {founders_per_company.mean():.2f}")
print(f"  Max founders in a company: {founders_per_company.max()}")

print("\n" + "=" * 100)
print("PROCESS COMPLETED SUCCESSFULLY")
print("=" * 100)
print(f"Completed at: {datetime.now()}")
print(f"\nFinal output file: {output_file}")
print(f"Summary file: {summary_file}")
print("\nThis file contains founders with:")
print("  - VC deal size information")
print("  - Education institute information")
print("  - Ready for analysis of founder backgrounds and VC funding")
print("=" * 100)

