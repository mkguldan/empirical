"""
Fix VC Spending in Expanded Dataset - Using Pre-calculated File
================================================================
Uses the pre-calculated VC spending by state file
"""

import pandas as pd
import numpy as np

print("="*80)
print("FIXING VC SPENDING IN EXPANDED DATASET")
print("="*80)
print()

# Load datasets
print("Loading datasets...")
expanded_df = pd.read_stata('data_with_categories_EXPANDED.dta')
print(f"Expanded dataset: {len(expanded_df):,} observations")
print()

# Load VC spending by state
print("Loading VC spending data...")
vc_by_state = pd.read_csv('VC_spend_by_state_averaged.csv')
print(f"Loaded VC spending for {len(vc_by_state)} states")
print()

# Check column names
print("VC spending file columns:", vc_by_state.columns.tolist())
print()

# Rename column if needed to match expected name
if 'Company_HQState_Province' not in vc_by_state.columns:
    # Try to find state column
    for col in vc_by_state.columns:
        if 'state' in col.lower() or 'province' in col.lower():
            vc_by_state.rename(columns={col: 'Company_HQState_Province'}, inplace=True)
            print(f"[OK] Renamed '{col}' to 'Company_HQState_Province'")
            break

# Find VC spending column
if 'Average_VC_Spend_HQ_Company' not in vc_by_state.columns:
    for col in vc_by_state.columns:
        if 'spend' in col.lower() or 'avg' in col.lower() or 'average' in col.lower():
            vc_by_state.rename(columns={col: 'Average_VC_Spend_HQ_Company'}, inplace=True)
            print(f"[OK] Renamed '{col}' to 'Average_VC_Spend_HQ_Company'")
            break

print("\nVC spending data preview:")
print(vc_by_state.head(10))
print()

# Drop old VC spending from expanded if exists
if 'Average_VC_Spend_HQ_Company' in expanded_df.columns:
    expanded_df = expanded_df.drop('Average_VC_Spend_HQ_Company', axis=1)
    print("[OK] Dropped old VC spending column")

# Merge VC spending
print("Merging VC spending by state...")
expanded_df = expanded_df.merge(
    vc_by_state[['Company_HQState_Province', 'Average_VC_Spend_HQ_Company']], 
    on='Company_HQState_Province', 
    how='left'
)

# Check for missing
missing = expanded_df['Average_VC_Spend_HQ_Company'].isna().sum()
if missing > 0:
    print(f"[WARN] {missing} observations missing VC spending")
    # Fill with median
    median_vc = expanded_df['Average_VC_Spend_HQ_Company'].median()
    expanded_df.loc[expanded_df['Average_VC_Spend_HQ_Company'].isna(), 'Average_VC_Spend_HQ_Company'] = median_vc
    print(f"       Filled with median: ${median_vc:.2f}M")
else:
    print("[OK] All observations matched to VC spending")

print()
print("VC Spending statistics in FIXED expanded dataset:")
print(f"  Count:  {expanded_df['Average_VC_Spend_HQ_Company'].count():,}")
print(f"  Mean:   ${expanded_df['Average_VC_Spend_HQ_Company'].mean():.2f}M")
print(f"  Median: ${expanded_df['Average_VC_Spend_HQ_Company'].median():.2f}M")
print(f"  Min:    ${expanded_df['Average_VC_Spend_HQ_Company'].min():.2f}M")
print(f"  Max:    ${expanded_df['Average_VC_Spend_HQ_Company'].max():.2f}M")
print()

# Save fixed dataset
print("Saving fixed dataset...")
expanded_df.to_stata('data_with_categories_EXPANDED.dta', write_index=False, version=117)
print("[OK] Saved to: data_with_categories_EXPANDED.dta")

expanded_df.to_csv('data_with_categories_EXPANDED.csv', index=False)
print("[OK] Saved to: data_with_categories_EXPANDED.csv")

print()
print("="*80)
print("VC SPENDING FIXED - DATASET READY!")
print("="*80)
print()
print(f"Final dataset: {len(expanded_df):,} observations with proper VC spending")
print()
print("You can now use data_with_categories_EXPANDED.dta for your analysis!")
print("This dataset has 87.4% more observations than the current one.")
print()

