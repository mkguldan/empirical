"""
Script to create founder-VC analysis file
Focuses on founders and their companies' first VC deals
One row per founder
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

print("=" * 100)
print("FOUNDER-VC ANALYSIS FILE CREATION")
print("=" * 100)
print(f"Started at: {datetime.now()}")

# File paths
master_file = r'G:\School\BOCCONI\1st semester\empirical\master_file.csv'
output_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_analysis.csv'

print("\n" + "=" * 100)
print("STEP 1: Loading master file...")
print("=" * 100)

# Load the master file
print("Reading master file (this may take a few minutes due to file size)...")
df = pd.read_csv(master_file, low_memory=False)
print(f"Loaded {len(df):,} rows with {len(df.columns)} columns")

print("\n" + "=" * 100)
print("STEP 2: Identifying VC-related terms and filtering...")
print("=" * 100)

# Define VC-related terms (case insensitive matching)
vc_terms = [
    'VC', 'Venture Capital', 'Early Stage VC', 'Later Stage VC', 
    'Seed Round', 'Series A', 'Series B', 'Series C', 'Series D',
    'Series E', 'Series F', 'Series G', 'Series H',
    'venture capital-backed', 'vc-backed'
]

print("VC-related terms we're looking for:")
for term in vc_terms:
    print(f"  - {term}")

# Create a function to check if a value contains VC terms
def contains_vc_term(value):
    if pd.isna(value):
        return False
    value_str = str(value).lower()
    for term in vc_terms:
        if term.lower() in value_str:
            return True
    return False

# Filter for VC deals based on multiple columns
print("\nIdentifying VC deals...")
print("Checking Deal_DealType, Deal_DealType2, Deal_DealClass, and Investor_DealType columns...")

df['is_vc_deal'] = (
    df['Deal_DealType'].apply(contains_vc_term) |
    df['Deal_DealType2'].apply(contains_vc_term) |
    df['Deal_DealClass'].apply(contains_vc_term) |
    df['Investor_DealType'].apply(contains_vc_term)
)

# CRITICAL: Ensure Deal_DealClass contains "Venture Capital" or "VC"
print("\nApplying CRITICAL filter: Deal_DealClass must contain 'Venture Capital' or 'VC'...")
df['deal_class_has_vc'] = df['Deal_DealClass'].apply(contains_vc_term)
df['is_vc_deal'] = df['is_vc_deal'] & df['deal_class_has_vc']

vc_deals_count = df['is_vc_deal'].sum()
print(f"Found {vc_deals_count:,} rows with VC deals")

# Filter for founders only
print("\nFiltering for founders...")
print("Looking for 'founder' in Person_PrimaryPositionLevel column...")

df['is_founder'] = df['Person_PrimaryPositionLevel'].fillna('').str.lower().str.contains('founder', na=False)
founder_count = df['is_founder'].sum()
print(f"Found {founder_count:,} rows with founders")

# Apply both filters
print("\nApplying combined filters (VC deals + founders)...")
filtered_df = df[(df['is_vc_deal'] == True) & (df['is_founder'] == True)].copy()
print(f"After filtering: {len(filtered_df):,} rows")
print(f"  Unique companies: {filtered_df['CompanyID'].nunique():,}")
print(f"  Unique founders: {filtered_df['PersonID'].nunique():,}")
print(f"  Unique deals: {filtered_df['DealID'].nunique():,}")

if len(filtered_df) == 0:
    print("\nWARNING: No data matches the criteria. Exiting.")
    exit(1)

print("\n" + "=" * 100)
print("STEP 3: Finding first VC deal for each company...")
print("=" * 100)

# Convert deal date to datetime
print("Parsing deal dates...")
filtered_df['Deal_DealDate_parsed'] = pd.to_datetime(filtered_df['Deal_DealDate'], errors='coerce')

# Sort by CompanyID and Deal Date
print("Sorting by company and deal date...")
filtered_df = filtered_df.sort_values(['CompanyID', 'Deal_DealDate_parsed'])

# For each company, identify the first VC deal
print("Identifying first VC deal per company...")
first_vc_deals = filtered_df.groupby('CompanyID').agg({
    'DealID': 'first',
    'Deal_DealDate_parsed': 'first'
}).reset_index()
first_vc_deals.columns = ['CompanyID', 'FirstVCDealID', 'FirstVCDealDate']

print(f"Identified first VC deals for {len(first_vc_deals):,} companies")

# Merge back to get the first VC deal info
print("Merging first VC deal information back to dataset...")
filtered_df = filtered_df.merge(first_vc_deals, on='CompanyID', how='left')

print("\n" + "=" * 100)
print("STEP 4: Handling missing Investor_DealSize...")
print("=" * 100)

# Group by company to handle deal size logic
print("Checking for deals with missing Investor_DealSize...")

# For each company, if the first VC deal has no size, find another VC deal with size
def get_best_vc_deal(company_deals):
    """
    For a company's deals, return the first VC deal.
    If first VC deal has no Investor_DealSize, find next VC deal that does.
    """
    # Sort by date
    company_deals = company_deals.sort_values('Deal_DealDate_parsed')
    
    # Get first VC deal
    first_deal = company_deals.iloc[0]
    
    # Check if it has deal size
    if pd.notna(first_deal['Investor_DealSize']) and first_deal['Investor_DealSize'] != '':
        return first_deal['DealID']
    
    # If not, look for next deal with size
    deals_with_size = company_deals[company_deals['Investor_DealSize'].notna() & 
                                     (company_deals['Investor_DealSize'] != '')]
    
    if len(deals_with_size) > 0:
        return deals_with_size.iloc[0]['DealID']
    
    # If no deal has size, return first deal anyway
    return first_deal['DealID']

# Apply the logic per company
print("Determining optimal VC deal per company (prioritizing deals with size)...")
company_groups = filtered_df.groupby('CompanyID')
optimal_deals = {}

for company_id, company_data in company_groups:
    optimal_deal_id = get_best_vc_deal(company_data)
    optimal_deals[company_id] = optimal_deal_id

# Create a column for the optimal deal ID
filtered_df['OptimalVCDealID'] = filtered_df['CompanyID'].map(optimal_deals)

companies_with_size_change = filtered_df[filtered_df['FirstVCDealID'] != filtered_df['OptimalVCDealID']]['CompanyID'].nunique()
print(f"  {companies_with_size_change:,} companies had their deal adjusted to find one with size data")

print("\n" + "=" * 100)
print("STEP 5: Creating one row per founder with optimal VC deal...")
print("=" * 100)

# Filter to keep only rows matching the optimal VC deal for each company
print("Filtering to optimal VC deals...")
analysis_df = filtered_df[filtered_df['DealID'] == filtered_df['OptimalVCDealID']].copy()

print(f"After filtering to optimal deals: {len(analysis_df):,} rows")
print(f"  Unique companies: {analysis_df['CompanyID'].nunique():,}")
print(f"  Unique founders: {analysis_df['PersonID'].nunique():,}")
print(f"  Unique deals: {analysis_df['DealID'].nunique():,}")

# Remove duplicate person-company-deal combinations
print("\nRemoving duplicate person-company-deal combinations...")
analysis_df = analysis_df.drop_duplicates(subset=['PersonID', 'CompanyID', 'DealID'])
print(f"After removing duplicates: {len(analysis_df):,} rows")

# If a founder appears multiple times (multiple education records), take first occurrence
print("\nEnsuring one row per founder (keeping first occurrence if duplicates exist)...")
initial_count = len(analysis_df)
analysis_df = analysis_df.drop_duplicates(subset=['PersonID'], keep='first')
removed_count = initial_count - len(analysis_df)
print(f"Removed {removed_count:,} duplicate founder records (likely due to multiple education entries)")
print(f"Final dataset: {len(analysis_df):,} rows (one per founder)")

print("\n" + "=" * 100)
print("STEP 6: Data quality validation...")
print("=" * 100)

# Validation checks
print("Validation checks:")
print(f"  [CHECK] All rows have PersonID: {analysis_df['PersonID'].notna().all()}")
print(f"  [CHECK] All rows have CompanyID: {analysis_df['CompanyID'].notna().all()}")
print(f"  [CHECK] All rows have DealID: {analysis_df['DealID'].notna().all()}")
print(f"  [CHECK] All rows are VC deals: {analysis_df['is_vc_deal'].all()}")
print(f"  [CHECK] All rows are founders: {analysis_df['is_founder'].all()}")
print(f"  [CHECK] Deal_DealClass has VC: {analysis_df['deal_class_has_vc'].all()}")

# Check deal size availability
deals_with_size = analysis_df['Investor_DealSize'].notna().sum()
print(f"  [INFO] Rows with Investor_DealSize: {deals_with_size:,} ({deals_with_size/len(analysis_df)*100:.2f}%)")

# Check Deal_DealSize as alternative
deals_with_deal_size = analysis_df['Deal_DealSize'].notna().sum()
print(f"  [INFO] Rows with Deal_DealSize (alternative): {deals_with_deal_size:,} ({deals_with_deal_size/len(analysis_df)*100:.2f}%)")

print("\n" + "=" * 100)
print("STEP 7: Cleaning up and preparing final dataset...")
print("=" * 100)

# Keep parsed date for summary before removing
deal_date_min = analysis_df['Deal_DealDate_parsed'].min()
deal_date_max = analysis_df['Deal_DealDate_parsed'].max()

# Remove the temporary helper columns
columns_to_remove = ['is_vc_deal', 'is_founder', 'deal_class_has_vc', 
                     'Deal_DealDate_parsed', 'FirstVCDealID', 'FirstVCDealDate', 
                     'OptimalVCDealID']
analysis_df = analysis_df.drop(columns=columns_to_remove, errors='ignore')

print(f"Final dataset has {len(analysis_df.columns)} columns")

print("\n" + "=" * 100)
print("STEP 8: Saving final analysis file...")
print("=" * 100)

# Save the file
print(f"Saving to: {output_file}")
analysis_df.to_csv(output_file, index=False)
file_size_mb = os.path.getsize(output_file) / (1024**2)
print(f"File saved successfully!")
print(f"  File size: {file_size_mb:.2f} MB")
print(f"  Total rows: {len(analysis_df):,}")
print(f"  Total columns: {len(analysis_df.columns)}")

print("\n" + "=" * 100)
print("STEP 9: Creating summary statistics...")
print("=" * 100)

# Format date range
if pd.notna(deal_date_min) and pd.notna(deal_date_max):
    date_range_str = f"{deal_date_min.strftime('%Y-%m-%d')} to {deal_date_max.strftime('%Y-%m-%d')}"
else:
    date_range_str = "N/A"

summary_stats = {
    'Metric': [
        'Total founders in analysis',
        'Unique companies with VC funding',
        'Unique VC deals analyzed',
        'Founders with deal size data',
        'Average founders per company',
        'Companies with 1 founder',
        'Companies with 2+ founders',
        'Date range of VC deals'
    ],
    'Value': [
        f"{len(analysis_df):,}",
        f"{analysis_df['CompanyID'].nunique():,}",
        f"{analysis_df['DealID'].nunique():,}",
        f"{deals_with_size:,} ({deals_with_size/len(analysis_df)*100:.1f}%)",
        f"{len(analysis_df) / analysis_df['CompanyID'].nunique():.2f}",
        f"{(analysis_df.groupby('CompanyID').size() == 1).sum():,}",
        f"{(analysis_df.groupby('CompanyID').size() > 1).sum():,}",
        date_range_str
    ]
}

summary_df = pd.DataFrame(summary_stats)
print("\nSummary Statistics:")
print(summary_df.to_string(index=False))

# Save summary
summary_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_summary.csv'
summary_df.to_csv(summary_file, index=False)
print(f"\nSummary saved to: {summary_file}")

print("\n" + "=" * 100)
print("SAMPLE RECORDS")
print("=" * 100)

print("\nFirst 3 founder records:")
sample_cols = ['PersonID', 'Person_FullName', 'CompanyName', 'Company_YearFounded', 
               'Deal_DealType', 'Deal_DealDate', 'Deal_DealSize', 'Investor_DealSize']
available_sample_cols = [col for col in sample_cols if col in analysis_df.columns]
print(analysis_df[available_sample_cols].head(3).to_string(index=False))

print("\n" + "=" * 100)
print("PROCESS COMPLETED SUCCESSFULLY")
print("=" * 100)
print(f"Completed at: {datetime.now()}")
print(f"\nOutput file: {output_file}")
print(f"Summary file: {summary_file}")
print("\nThe file is ready for analysis of how founder backgrounds affect VC funding.")
print("=" * 100)

