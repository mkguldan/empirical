import pandas as pd
import numpy as np

print("="*80)
print("ANALYZING THE 2,607 LOST OBSERVATIONS")
print("="*80)
print()

# Load the dataset before filtering (single founders with US university rank)
before_df = pd.read_csv('deal_level_analysis_single_founders_with_university_rank.csv')
print(f"Before filtering: {len(before_df):,} observations")
print()

# Load the current final dataset
current_df = pd.read_stata('data_with_categories.dta')
print(f"Final dataset: {len(current_df):,} observations")
print()

# Identify lost observations
if 'DealID' in before_df.columns and 'DealID' in current_df.columns:
    kept_ids = set(current_df['DealID'].unique())
    all_ids = set(before_df['DealID'].unique())
    lost_ids = all_ids - kept_ids
    
    print(f"Lost observations: {len(lost_ids):,}")
    print()
    
    # Separate into kept and lost
    lost_df = before_df[before_df['DealID'].isin(lost_ids)]
    kept_df = before_df[before_df['DealID'].isin(kept_ids)]
    
    print("="*80)
    print("WHY WERE THESE 2,607 OBSERVATIONS LOST?")
    print("="*80)
    print()
    
    # Check each potential filtering criterion
    print("MISSING DATA ANALYSIS:")
    print("-"*80)
    print()
    
    # Check key variables
    key_vars_to_check = [
        'DealSize', 'CompanyAge', 'TeamAge', 'Company_Founded', 
        'Company_PrimaryIndustryGroup', 'Company_HQState_Province',
        'Deal_Year', 'TeamUS_Rank', 'Team_Gender'
    ]
    
    for var in key_vars_to_check:
        if var in lost_df.columns and var in kept_df.columns:
            lost_missing = lost_df[var].isna().sum()
            lost_missing_pct = lost_missing / len(lost_df) * 100
            
            kept_missing = kept_df[var].isna().sum()
            kept_missing_pct = kept_missing / len(kept_df) * 100
            
            print(f"{var:35s}:")
            print(f"  Lost obs missing:  {lost_missing:>5,} ({lost_missing_pct:>5.1f}%)")
            print(f"  Kept obs missing:  {kept_missing:>5,} ({kept_missing_pct:>5.1f}%)")
            print(f"  Difference:        {lost_missing_pct - kept_missing_pct:>+6.1f}pp")
            print()
    
    print("="*80)
    print("POTENTIAL TO RECOVER LOST OBSERVATIONS:")
    print("="*80)
    print()
    
    # Check if lost observations have all required data
    required_for_analysis = {
        'DealSize': 'Deal size (required for ln_DealSize)',
        'TeamUS_Rank': 'US university ranking',
        'Team_Gender': 'Gender information',
        'Company_PrimaryIndustryGroup': 'Industry classification',
        'Company_HQState_Province': 'Geographic location',
        'Deal_Year': 'Deal year (for fixed effects)'
    }
    
    # Count how many lost obs have complete data on each required variable
    print("Completeness of LOST observations on required variables:")
    print("-"*80)
    
    recoverable = lost_df.copy()
    for var, description in required_for_analysis.items():
        if var in recoverable.columns:
            before_count = len(recoverable)
            recoverable = recoverable[recoverable[var].notna()]
            after_count = len(recoverable)
            lost_count = before_count - after_count
            
            print(f"\n{var} ({description}):")
            print(f"  Have data:    {after_count:>5,} obs")
            print(f"  Missing data: {lost_count:>5,} obs ({lost_count/before_count*100:.1f}%)")
    
    print()
    print("-"*80)
    print(f"Potentially recoverable observations: {len(recoverable):,}")
    print(f"Would increase dataset to: {len(current_df) + len(recoverable):,} (+{len(recoverable)/len(current_df)*100:.1f}%)")
    print("-"*80)
    print()
    
    if len(recoverable) > 0:
        print("*** EXPANSION IS POSSIBLE! ***")
        print()
        print(f"You can recover up to {len(recoverable):,} observations by:")
        print()
        print("1. Re-running the data preparation pipeline (prepare_for_stata.py)")
        print("2. Ensuring all control variables are properly extracted")
        print("3. Using zero/indicator variables for missing optional controls")
        print()
        
        # Show characteristics of recoverable observations
        print("Characteristics of potentially recoverable observations:")
        print("-"*80)
        
        if 'Deal_Year' in recoverable.columns:
            print("\nYear distribution:")
            print(recoverable['Deal_Year'].value_counts().sort_index())
        
        if 'Company_PrimaryIndustryGroup' in recoverable.columns:
            print("\nIndustry distribution:")
            print(recoverable['Company_PrimaryIndustryGroup'].value_counts().head(10))
        
        if 'TeamUS_Rank' in recoverable.columns:
            print("\nUniversity rank distribution:")
            print(f"  Mean:   {recoverable['TeamUS_Rank'].mean():.1f}")
            print(f"  Median: {recoverable['TeamUS_Rank'].median():.1f}")
            print(f"  Min:    {recoverable['TeamUS_Rank'].min():.1f}")
            print(f"  Max:    {recoverable['TeamUS_Rank'].max():.1f}")
        
        if 'DealSize' in recoverable.columns:
            print("\nDeal size distribution:")
            print(f"  Mean:   ${recoverable['DealSize'].mean()/1e6:.2f}M")
            print(f"  Median: ${recoverable['DealSize'].median()/1e6:.2f}M")
        
        print()
    else:
        print("*** NO RECOVERABLE OBSERVATIONS ***")
        print()
        print("All lost observations are missing at least one required variable.")
        print("Current dataset of 2,982 is MAXIMUM possible given data requirements.")
    
else:
    print("[ERROR] Cannot identify lost observations - DealID not found in both datasets")

print()
print("="*80)
print("COMPLETE!")
print("="*80)

