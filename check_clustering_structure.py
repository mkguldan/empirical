import pandas as pd
import numpy as np

print("="*80)
print("CHECKING CLUSTERING STRUCTURE")
print("="*80)
print()

# Load the data
data = pd.read_stata('data_with_categories.dta')

print(f"Total observations (deals): {len(data):,}")
print()

# Check if we have company identifiers
print("AVAILABLE ID VARIABLES:")
print("-"*80)
id_candidates = [col for col in data.columns if 'ID' in col.upper() or 'Company' in col]
for col in id_candidates[:20]:  # Show first 20
    print(f"  - {col}")
print()

# Check for repeated companies
if 'CompanyID' in data.columns:
    print("COMPANY-LEVEL CLUSTERING:")
    print("-"*80)
    company_counts = data['CompanyID'].value_counts()
    n_unique_companies = data['CompanyID'].nunique()
    n_repeated = (company_counts > 1).sum()
    max_deals = company_counts.max()
    
    print(f"Unique companies:              {n_unique_companies:,}")
    print(f"Companies with multiple deals: {n_repeated:,} ({n_repeated/n_unique_companies*100:.1f}%)")
    print(f"Max deals per company:         {max_deals}")
    print()
    
    print("DISTRIBUTION OF DEALS PER COMPANY:")
    print(company_counts.value_counts().sort_index().head(10))
    print()
    
    if n_repeated > 0:
        print("*** CLUSTERING BY COMPANY IS NECESSARY! ***")
        print(f"    {n_repeated:,} companies have multiple deals in your sample")
        print(f"    Standard errors will be UNDERSTATED without clustering")
    else:
        print("[OK] Each company appears only once - no clustering needed")
    print()

# Check for repeated universities
if 'University_US_Rank' in data.columns:
    # We need a university ID - let's see if we can identify universities
    print("UNIVERSITY-LEVEL CLUSTERING:")
    print("-"*80)
    
    # Count unique university ranks as proxy for universities
    uni_counts = data['University_US_Rank'].value_counts()
    n_unique_unis = data['University_US_Rank'].nunique()
    avg_per_uni = len(data) / n_unique_unis
    
    print(f"Unique universities (by rank): {n_unique_unis}")
    print(f"Average deals per university:  {avg_per_uni:.1f}")
    print()
    
    print("TOP 10 UNIVERSITIES BY DEAL COUNT:")
    print(uni_counts.head(10))
    print()
    
    print("*** CLUSTERING BY UNIVERSITY AS ROBUSTNESS CHECK ***")
    print(f"    Multiple founders from same university -> correlated errors")
    print(f"    Especially important if treatment (university rank) is at uni-level")
    print()

# Check for Year clustering
if 'Deal_Year' in data.columns:
    print("YEAR-LEVEL CLUSTERING:")
    print("-"*80)
    year_counts = data['Deal_Year'].value_counts().sort_index()
    print(year_counts)
    print()
    print("*** YEAR CLUSTERING IS ALSO RELEVANT ***")
    print(f"    Macro shocks affect all deals in same year")
    print()

print("="*80)
print("RECOMMENDATION:")
print("="*80)
print()
print("PRIMARY:   vce(cluster CompanyID)")
print("           -> Accounts for multiple rounds per company")
print()
print("ROBUSTNESS:")
print("  1. vce(cluster University_ID)")
print("     -> Accounts for correlation among alumni from same school")
print("  2. Two-way clustering: cluster(CompanyID Deal_Year)")
print("     -> Accounts for both company + time correlations")
print()
print("EXPECTED IMPACT:")
print("  - Standard errors will likely INCREASE (by 20-50%)")
print("  - Some marginally significant results may become non-significant")
print("  - This is the CORRECT inference - current SEs are understated")
print()

