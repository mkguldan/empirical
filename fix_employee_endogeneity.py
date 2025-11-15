"""
Fix Employee Count Endogeneity
================================

Problem: Current model uses employee count measured in 2022,
         but deals happened 2012-2022.
         This creates reverse causality!

Solution: Match each deal to employee count BEFORE the deal date.

Author: Empirical Methods Project
Date: November 15, 2024
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("FIXING EMPLOYEE COUNT ENDOGENEITY")
print("="*80)
print()

# =============================================================================
# STEP 1: Load Current Dataset
# =============================================================================
print("Step 1: Loading current dataset...")
current_data = pd.read_stata('data_final_streamlined.dta')
print(f"   [OK] Loaded {len(current_data):,} observations")
print(f"   [OK] Current columns: {len(current_data.columns)}")
print()

# Check what we have
print("   Current employee variable:")
print(f"   - Company_Employees: {current_data['Company_Employees'].notna().sum():,} non-missing")
print(f"   - Mean: {current_data['Company_Employees'].mean():.1f}")
print(f"   - Median: {current_data['Company_Employees'].median():.1f}")
print()

# =============================================================================
# STEP 2: Load Deal Data to Get Deal Dates
# =============================================================================
print("Step 2: Loading deal dates...")
deals = pd.read_csv('core_tables/Deal.csv')
print(f"   [OK] Loaded {len(deals):,} deals")

# Get deal date
deals_dates = deals[['DealID', 'DealDate']].copy()
deals_dates['DealDate'] = pd.to_datetime(deals_dates['DealDate'], errors='coerce')
print(f"   [OK] Parsed {deals_dates['DealDate'].notna().sum():,} deal dates")
print()

# =============================================================================
# STEP 3: Load Historical Employee Data
# =============================================================================
print("Step 3: Loading historical employee counts...")
employee_history = pd.read_csv('other_tables/CompanyEmployeeHistoryRelation.csv')
print(f"   [OK] Loaded {len(employee_history):,} employee observations")

# Parse dates
employee_history['Date'] = pd.to_datetime(employee_history['Date'], errors='coerce')
print(f"   [OK] Parsed {employee_history['Date'].notna().sum():,} dates")

# Check date range
min_date = employee_history['Date'].min()
max_date = employee_history['Date'].max()
print(f"   [OK] Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
print()

# =============================================================================
# STEP 4: Merge Deal Dates with Current Data
# =============================================================================
print("Step 4: Merging deal dates with current data...")
current_data = current_data.merge(deals_dates, on='DealID', how='left')
print(f"   [OK] Merged deal dates: {current_data['DealDate'].notna().sum():,} non-missing")
print()

# =============================================================================
# STEP 5: Match Each Deal to LAGGED Employee Count
# =============================================================================
print("Step 5: Matching deals to lagged employee counts...")
print("   This may take a few minutes...")
print()

def get_lagged_employee_count(company_id, deal_date, employee_df, lookback_days=180):
    """
    For a given company and deal date, find the employee count
    BEFORE the deal (ideally 1-6 months before).
    
    Strategy:
    1. Look for employee count 1-6 months BEFORE deal
    2. If not found, use closest PRIOR observation (up to 2 years back)
    3. If still not found, return NaN
    
    Parameters:
    -----------
    company_id : str
        Company ID
    deal_date : datetime
        Deal date
    employee_df : DataFrame
        Employee history data
    lookback_days : int
        Maximum days to look back for employee count
        
    Returns:
    --------
    employee_count : float or NaN
        Employee count before the deal, or NaN if not available
    days_before : int or NaN
        Days between employee measurement and deal
    """
    
    # Handle missing deal date
    if pd.isna(deal_date):
        return np.nan, np.nan
    
    # Get all employee records for this company
    company_records = employee_df[employee_df['CompanyID'] == company_id].copy()
    
    if len(company_records) == 0:
        return np.nan, np.nan
    
    # Filter to records BEFORE the deal
    company_records = company_records[company_records['Date'] < deal_date]
    
    if len(company_records) == 0:
        return np.nan, np.nan
    
    # Calculate days before deal
    company_records['days_before'] = (deal_date - company_records['Date']).dt.days
    
    # Strategy 1: Look for count 30-180 days before (1-6 months)
    recent = company_records[
        (company_records['days_before'] >= 30) & 
        (company_records['days_before'] <= lookback_days)
    ]
    
    if len(recent) > 0:
        # Use the most recent one in this window
        best_match = recent.loc[recent['days_before'].idxmin()]
        return best_match['EmployeeCount'], best_match['days_before']
    
    # Strategy 2: If no recent data, use closest prior (up to 2 years)
    prior = company_records[company_records['days_before'] <= 730]  # 2 years
    
    if len(prior) > 0:
        # Use the closest one
        best_match = prior.loc[prior['days_before'].idxmin()]
        return best_match['EmployeeCount'], best_match['days_before']
    
    # Strategy 3: No data found
    return np.nan, np.nan


# Apply to all deals
print("   Matching employee counts to deals...")
results = []

# Process in batches for progress updates
batch_size = 500
total_deals = len(current_data)

for i in range(0, total_deals, batch_size):
    batch = current_data.iloc[i:i+batch_size]
    
    for idx, row in batch.iterrows():
        emp_count, days_before = get_lagged_employee_count(
            row['CompanyID'], 
            row['DealDate'], 
            employee_history,
            lookback_days=180
        )
        results.append({
            'index': idx,
            'Employees_Lagged': emp_count,
            'Employees_Lag_Days': days_before
        })
    
    # Progress update
    processed = min(i + batch_size, total_deals)
    pct = (processed / total_deals) * 100
    print(f"   Progress: {processed:,}/{total_deals:,} ({pct:.1f}%)")

print()
print("   [OK] Matching complete!")
print()

# Convert results to DataFrame
results_df = pd.DataFrame(results)
results_df.set_index('index', inplace=True)

# Add to current data
current_data['Employees_Lagged'] = results_df['Employees_Lagged']
current_data['Employees_Lag_Days'] = results_df['Employees_Lag_Days']

# =============================================================================
# STEP 6: Analyze the Results
# =============================================================================
print("="*80)
print("RESULTS ANALYSIS")
print("="*80)
print()

print("1. DATA COVERAGE:")
print(f"   Total deals: {len(current_data):,}")
print(f"   Deals with LAGGED employee count: {current_data['Employees_Lagged'].notna().sum():,} ({current_data['Employees_Lagged'].notna().sum()/len(current_data)*100:.1f}%)")
print(f"   Deals with OLD employee count: {current_data['Company_Employees'].notna().sum():,} ({current_data['Company_Employees'].notna().sum()/len(current_data)*100:.1f}%)")
print()

print("2. COMPARISON - OLD vs LAGGED:")
print()
comparison = pd.DataFrame({
    'OLD (2022 count)': current_data['Company_Employees'].describe(),
    'LAGGED (Before deal)': current_data['Employees_Lagged'].describe()
})
print(comparison)
print()

print("3. TIME LAG STATISTICS:")
lag_stats = current_data['Employees_Lag_Days'].describe()
print(f"   Mean lag: {lag_stats['mean']:.0f} days ({lag_stats['mean']/30:.1f} months)")
print(f"   Median lag: {lag_stats['50%']:.0f} days ({lag_stats['50%']/30:.1f} months)")
print(f"   Min lag: {lag_stats['min']:.0f} days")
print(f"   Max lag: {lag_stats['max']:.0f} days ({lag_stats['max']/365:.1f} years)")
print()

print("4. HOW MUCH DID COMPANIES GROW?")
# For companies with both measures (calculate before rename)
both_available = current_data[
    current_data['Company_Employees'].notna() & 
    current_data['Employees_Lagged'].notna()
].copy()

# Calculate correlation now before rename
if len(both_available) > 0:
    correlation_old_new = both_available[['Employees_Lagged', 'Company_Employees']].corr().iloc[0, 1]
else:
    correlation_old_new = None

if len(both_available) > 0:
    both_available['Growth'] = (
        (both_available['Company_Employees'] - both_available['Employees_Lagged']) / 
        both_available['Employees_Lagged'] * 100
    )
    
    print(f"   Companies with both measures: {len(both_available):,}")
    print(f"   Mean growth: {both_available['Growth'].mean():.1f}%")
    print(f"   Median growth: {both_available['Growth'].median():.1f}%")
    print(f"   Companies that grew: {(both_available['Growth'] > 0).sum():,} ({(both_available['Growth'] > 0).sum()/len(both_available)*100:.1f}%)")
    print(f"   Mean employees BEFORE deal: {both_available['Employees_Lagged'].mean():.1f}")
    print(f"   Mean employees in 2022: {both_available['Company_Employees'].mean():.1f}")
    print()

# =============================================================================
# STEP 7: Create New Variables
# =============================================================================
print("="*80)
print("CREATING NEW VARIABLES")
print("="*80)
print()

# Create ln_Employees_Lagged
current_data['ln_Employees_Lagged'] = np.log(current_data['Employees_Lagged'])
print(f"[OK] Created ln_Employees_Lagged")

# Update missing indicator to reflect lagged data
current_data['Employees_Missing_Lagged'] = current_data['Employees_Lagged'].isna().astype(int)
print(f"[OK] Created Employees_Missing_Lagged")

# For missing lagged employees, impute with 0 (will be -inf in log, so we handle it)
current_data['ln_Employees_Lagged'] = current_data['ln_Employees_Lagged'].replace([np.inf, -np.inf], np.nan)

# Impute missing ln_Employees_Lagged with median (for regression purposes)
median_ln_emp = current_data['ln_Employees_Lagged'].median()
current_data['ln_Employees_Lagged'].fillna(median_ln_emp, inplace=True)
print(f"[OK] Imputed missing ln_Employees_Lagged with median ({median_ln_emp:.2f})")
print()

print("New variables created:")
print(f"   1. Employees_Lagged - Raw lagged employee count")
print(f"   2. ln_Employees_Lagged - Log of lagged employee count")
print(f"   3. Employees_Missing_Lagged - Indicator for missing lagged data")
print(f"   4. Employees_Lag_Days - Days between measurement and deal")
print()

# =============================================================================
# STEP 8: Export Updated Dataset
# =============================================================================
print("="*80)
print("EXPORTING UPDATED DATASET")
print("="*80)
print()

# Keep old variables for comparison (rename them)
current_data.rename(columns={
    'Company_Employees': 'Company_Employees_2022',
    'ln_Employees': 'ln_Employees_2022',
    'Employees_Missing': 'Employees_Missing_2022'
}, inplace=True)

print("Renamed old variables:")
print("   Company_Employees -> Company_Employees_2022")
print("   ln_Employees -> ln_Employees_2022")
print("   Employees_Missing -> Employees_Missing_2022")
print()

# Export to Stata
print("Exporting to Stata format...")
current_data.to_stata('data_fixed_endogeneity.dta', write_index=False, version=117)
print("   [OK] Saved: data_fixed_endogeneity.dta")
print()

# Export to CSV
print("Exporting to CSV format...")
current_data.to_csv('data_fixed_endogeneity.csv', index=False)
print("   [OK] Saved: data_fixed_endogeneity.csv")
print()

# =============================================================================
# STEP 9: Summary Statistics for Paper
# =============================================================================
print("="*80)
print("SUMMARY FOR YOUR PAPER")
print("="*80)
print()

print("Key Facts to Report:")
print(f"   • Original dataset: {len(current_data):,} deals (2012-2022)")
print(f"   • Lagged employee data available: {current_data['Employees_Lagged'].notna().sum():,} deals ({current_data['Employees_Lagged'].notna().sum()/len(current_data)*100:.1f}%)")
print(f"   • Mean time lag: {current_data['Employees_Lag_Days'].mean():.0f} days ({current_data['Employees_Lag_Days'].mean()/30:.1f} months)")
print(f"   • Median employee count BEFORE deal: {current_data['Employees_Lagged'].median():.0f}")
print(f"   • Median employee count in 2022: {current_data['Company_Employees_2022'].median():.0f}")

if len(both_available) > 0:
    print(f"   • Mean employee growth from deal to 2022: {both_available['Growth'].mean():.0f}%")
print()

print("Variables in new dataset:")
print(f"   Total columns: {len(current_data.columns)}")
print()
print("   NEW variables:")
print("   - Employees_Lagged: Employee count before deal")
print("   - ln_Employees_Lagged: Log(Employees_Lagged)")
print("   - Employees_Missing_Lagged: Missing indicator")
print("   - Employees_Lag_Days: Days between measurement and deal")
print()
print("   OLD variables (kept for comparison):")
print("   - Company_Employees_2022: Employee count in 2022")
print("   - ln_Employees_2022: Log(Employees 2022)")
print("   - Employees_Missing_2022: Missing indicator (2022)")
print()

# =============================================================================
# STEP 10: Create Diagnostic Plots Data
# =============================================================================
print("="*80)
print("DIAGNOSTIC CHECKS")
print("="*80)
print()

print("Creating diagnostic data for plots...")

# Check correlation between old and lagged
if correlation_old_new is not None:
    print(f"   Correlation (lagged vs 2022): {correlation_old_new:.3f}")
    print()

# Check by deal year
print("Coverage by year:")
year_coverage = current_data.groupby('Deal_Year').agg({
    'DealID': 'count',
    'Employees_Lagged': lambda x: x.notna().sum()
}).rename(columns={'DealID': 'Total', 'Employees_Lagged': 'With_Lagged'})
year_coverage['Coverage_%'] = (year_coverage['With_Lagged'] / year_coverage['Total'] * 100).round(1)
print(year_coverage)
print()

# Save diagnostics
diagnostics = {
    'total_deals': len(current_data),
    'lagged_available': int(current_data['Employees_Lagged'].notna().sum()),
    'coverage_pct': float(current_data['Employees_Lagged'].notna().sum()/len(current_data)*100),
    'mean_lag_days': float(current_data['Employees_Lag_Days'].mean()),
    'median_lag_days': float(current_data['Employees_Lag_Days'].median()),
    'correlation_old_new': float(correlation_old_new) if correlation_old_new is not None else None,
    'mean_growth_pct': float(both_available['Growth'].mean()) if len(both_available) > 0 else None
}

import json
with open('endogeneity_fix_diagnostics.json', 'w') as f:
    json.dump(diagnostics, f, indent=2)
print("[OK] Saved diagnostics: endogeneity_fix_diagnostics.json")
print()

# =============================================================================
# DONE!
# =============================================================================
print("="*80)
print("[OK] ENDOGENEITY FIX COMPLETE!")
print("="*80)
print()
print("Next steps:")
print("   1. Review the results above")
print("   2. Use 'data_fixed_endogeneity.dta' for your Stata models")
print("   3. Replace 'ln_Employees' with 'ln_Employees_Lagged' in your regressions")
print("   4. Replace 'Employees_Missing' with 'Employees_Missing_Lagged'")
print()
print("Your updated regression should look like:")
print()
print("   reghdfe ln_DealSize University_US_Rank Female \\")
print("       PhD_MD MBA_JD Masters \\")
print("       ln_Employees_Lagged Employees_Missing_Lagged Age_at_Deal \\")
print("       Stage_Seed Stage_Early, \\")
print("       absorb(Deal_Year Company_PrimaryIndustryGroup Company_HQState_Province) \\")
print("       vce(robust)")
print()
print("="*80)

