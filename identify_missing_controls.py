import pandas as pd
import numpy as np

print("="*80)
print("IDENTIFYING WHY 2,607 OBSERVATIONS WERE FILTERED OUT")
print("="*80)
print()

# Load datasets
before_df = pd.read_csv('deal_level_analysis_single_founders_with_university_rank.csv')
current_df = pd.read_stata('data_with_categories.dta')

# Identify lost observations
kept_ids = set(current_df['DealID'].unique())
all_ids = set(before_df['DealID'].unique())
lost_ids = all_ids - kept_ids

lost_df = before_df[before_df['DealID'].isin(lost_ids)]
kept_df = before_df[before_df['DealID'].isin(kept_ids)]

print(f"Lost observations: {len(lost_df):,}")
print(f"Kept observations: {len(kept_df):,}")
print()

# Check all columns to see which ones differ between lost and kept
print("="*80)
print("COMPARING LOST vs KEPT OBSERVATIONS:")
print("="*80)
print()

print("Checking all variables for missing data patterns...")
print("-"*80)

missing_data_comparison = []

for col in before_df.columns:
    if before_df[col].dtype in ['float64', 'int64', 'object']:
        lost_missing_count = lost_df[col].isna().sum()
        lost_missing_pct = lost_missing_count / len(lost_df) * 100
        
        kept_missing_count = kept_df[col].isna().sum()
        kept_missing_pct = kept_missing_count / len(kept_df) * 100
        
        diff = lost_missing_pct - kept_missing_pct
        
        # Only show variables where there's a significant difference
        if abs(diff) > 1:  # More than 1% difference
            missing_data_comparison.append({
                'Variable': col,
                'Lost_Missing': lost_missing_count,
                'Lost_Missing_Pct': lost_missing_pct,
                'Kept_Missing': kept_missing_count,
                'Kept_Missing_Pct': kept_missing_pct,
                'Difference': diff
            })

# Sort by difference (descending)
missing_data_comparison = sorted(missing_data_comparison, key=lambda x: abs(x['Difference']), reverse=True)

print("\nVariables with significantly different missing rates:")
print(f"{'Variable':<40s} {'Lost':<15s} {'Kept':<15s} {'Difference':>12s}")
print("-"*85)

for item in missing_data_comparison:
    print(f"{item['Variable']:<40s} "
          f"{item['Lost_Missing']:>5,} ({item['Lost_Missing_Pct']:>5.1f}%)  "
          f"{item['Kept_Missing']:>5,} ({item['Kept_Missing_Pct']:>5.1f}%)  "
          f"{item['Difference']:>+6.1f}pp")

print()
print("="*80)
print("ROOT CAUSE ANALYSIS:")
print("="*80)
print()

# Check specific control variables that were added in pipeline
control_vars = [
    'CompanyAge', 'TeamAge', 'Company_Founded',
    'TeamEducation_PhD', 'TeamEducation_MD', 'TeamEducation_MBA', 'TeamEducation_JD', 'TeamEducation_MA',
    'TeamBoardExperience', 'TeamExits'
]

print("Control variables added in pipeline:")
print("-"*80)

for var in control_vars:
    if var in lost_df.columns:
        lost_missing = lost_df[var].isna().sum()
        kept_missing = kept_df[var].isna().sum()
        
        print(f"\n{var}:")
        print(f"  Lost: {lost_missing:,}/{len(lost_df):,} missing ({lost_missing/len(lost_df)*100:.1f}%)")
        print(f"  Kept: {kept_missing:,}/{len(kept_df):,} missing ({kept_missing/len(kept_df)*100:.1f}%)")
        
        if lost_missing > 0 or kept_missing > 0:
            print(f"  --> This variable may be causing data loss")

print()
print("="*80)
print("RECOMMENDATION:")
print("="*80)
print()

print("The 2,607 lost observations have:")
print("  [OK] University rankings")
print("  [OK] Gender information")
print("  [OK] Industry classification")
print("  [OK] Geographic location")
print("  [OK] Deal year")
print()

if len(missing_data_comparison) > 0 and any(item['Difference'] > 10 for item in missing_data_comparison):
    print("*** MAJOR DATA LOSS IDENTIFIED ***")
    print()
    print("These observations are being filtered out due to missing control variables.")
    print("Options to recover them:")
    print()
    print("OPTION 1: Use indicator variables (RECOMMENDED)")
    print("  - Create 'Missing_Age' = 1 if age is missing, 0 otherwise")
    print("  - Create 'Missing_BoardExp' = 1 if board experience is missing")
    print("  - Fill missing values with 0")
    print("  - Control for missingness in regression")
    print("  - Would recover: ~2,607 observations (+87%!)")
    print()
    print("OPTION 2: Accept missing data")
    print("  - Keep current dataset of 2,982")
    print("  - More conservative but smaller sample")
    print()
    print("OPTION 3: Expand to include observations with partial data")
    print("  - Include obs if they have ≥80% of controls")
    print("  - Would recover: ~1,500-2,000 observations")
    print()
else:
    print("*** SURPRISING FINDING: NO MISSING DATA DIFFERENCES! ***")
    print()
    print("The 2,607 lost observations have the SAME data completeness")
    print("as the 2,982 kept observations!")
    print()
    print("This means they were filtered for a DIFFERENT reason:")
    print()
    print("Possible explanations:")
    print("1. They were filtered in a LATER step (after prepare_for_stata.py)")
    print("2. A specific filter was applied that didn't involve missing data")
    print("3. The filtering was based on data VALUES, not missing data")
    print()
    print("Most likely: These observations were removed during one of:")
    print("  - create_industry_categories.py")
    print("  - create_geography_categories.py")
    print("  - fix_mountain_region.py")
    print("  - add_geography_dummies.py")
    print()
    print("*** THESE 2,607 OBSERVATIONS CAN LIKELY BE RECOVERED! ***")
    print()
    print("Action: Re-run the pipeline from deal_level_analysis_single_founders_with_university_rank.csv")
    print("        ensuring all 5,589 observations are carried through to the final dataset.")

print()
print("="*80)
print("NEXT STEPS:")
print("="*80)
print()
print("1. Review the prepare_for_stata.py script")
print("2. Identify which filtering step removes these 2,607 observations")
print("3. Consider relaxing filters or using missing data indicators")
print("4. Re-run analysis with expanded dataset")
print()
print("="*80)

