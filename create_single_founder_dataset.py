"""
Create Single Founder Dataset with University Names
====================================================

Creates a separate analysis file containing only single founders (TeamSize=1)
with specific university names added back from the original founder-level data.

Purpose:
- Avoid teams being included in baseline when using dummy variables
- Identify specific universities driving results
- Check for outliers at the university level

Input: 
- deal_level_analysis.csv (deal-level data)
- founder_vc_final_formatted_with_groups.csv (original founder-level with university names)

Output:
- deal_level_analysis_single_founders.csv
- deal_level_analysis_single_founders.dta (Stata format)

Author: Empirical Methods Project, Bocconi University
Date: November 2024
"""

import pandas as pd
import numpy as np

print("="*80)
print("CREATING SINGLE FOUNDER DATASET WITH UNIVERSITY NAMES")
print("="*80)
print()

# ============================================================================
# STEP 1: Load deal-level data and filter for single founders
# ============================================================================

print("Step 1: Loading deal-level data and filtering for single founders")
print("-" * 80)

deal_df = pd.read_csv('deal_level_analysis.csv')
print(f"Total deals in dataset: {len(deal_df):,}")

# Filter for single founders only (TeamSize == 1)
single_df = deal_df[deal_df['TeamSize'] == 1].copy()
print(f"Single founder deals: {len(single_df):,} ({len(single_df)/len(deal_df)*100:.1f}%)")
print()

# ============================================================================
# STEP 2: Load original founder-level data with university names
# ============================================================================

print("Step 2: Loading original founder-level data with university names")
print("-" * 80)

founder_df = pd.read_csv('founder_vc_final_formatted_with_groups.csv')
print(f"Founder-level observations: {len(founder_df):,}")

# Keep only the columns we need for matching
founder_subset = founder_df[['DealID', 'PersonID', 'Education_Institute', 
                              'Person_FullName', 'University_Group']].copy()
print(f"Extracted university information for matching")
print()

# ============================================================================
# STEP 3: Match university names back to single founder deals
# ============================================================================

print("Step 3: Matching university names back to single founder deals")
print("-" * 80)

# Merge on DealID (since TeamSize=1, there's only one founder per deal)
# Use left join to keep all single founder deals
single_with_uni = single_df.merge(
    founder_subset[['DealID', 'Education_Institute', 'Person_FullName']],
    on='DealID',
    how='left'
)

# Check for any that didn't match
unmatched = single_with_uni['Education_Institute'].isna().sum()
if unmatched > 0:
    print(f"Warning: {unmatched} single founder deals didn't match to university names")
else:
    print(f"[OK] All {len(single_with_uni):,} single founder deals matched successfully")

# Rename Education_Institute to be clearer
single_with_uni = single_with_uni.rename(columns={
    'Education_Institute': 'University_Name'
})

print()

# ============================================================================
# STEP 4: Create University-specific indicators for top schools
# ============================================================================

print("Step 4: Creating university-specific dummy variables")
print("-" * 80)

# For convenience in regression, create dummies for specific universities
# These are the most common in the dataset

def create_uni_dummy(row, uni_list, dummy_name):
    """Create dummy variable for universities matching any pattern in list"""
    if pd.isna(row['University_Name']):
        return 0
    uni_lower = str(row['University_Name']).lower()
    return int(any(pattern.lower() in uni_lower for pattern in uni_list))

# Ivy League individual schools
single_with_uni['Harvard'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['harvard'], 'Harvard'), axis=1
)
single_with_uni['Stanford'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['stanford'], 'Stanford'), axis=1
)
single_with_uni['MIT'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['massachusetts institute of technology', 'mit ', ' mit'], 'MIT'), axis=1
)
single_with_uni['Yale'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['yale'], 'Yale'), axis=1
)
single_with_uni['Princeton'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['princeton'], 'Princeton'), axis=1
)
single_with_uni['Columbia'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['columbia'], 'Columbia'), axis=1
)
single_with_uni['Penn'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['university of pennsylvania', 'upenn', 'wharton'], 'Penn'), axis=1
)
single_with_uni['Cornell'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['cornell'], 'Cornell'), axis=1
)
single_with_uni['Brown'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['brown university', 'brown '], 'Brown'), axis=1
)
single_with_uni['Dartmouth'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['dartmouth'], 'Dartmouth'), axis=1
)
single_with_uni['Berkeley'] = single_with_uni.apply(
    lambda x: create_uni_dummy(x, ['berkeley', 'uc berkeley', 'ucb', 'cal berkeley'], 'Berkeley'), axis=1
)

# Count how many for each university
print("\nMost common universities in single founder dataset:")
print(f"  Harvard: {single_with_uni['Harvard'].sum()}")
print(f"  Stanford: {single_with_uni['Stanford'].sum()}")
print(f"  MIT: {single_with_uni['MIT'].sum()}")
print(f"  Berkeley: {single_with_uni['Berkeley'].sum()}")
print(f"  Penn (incl. Wharton): {single_with_uni['Penn'].sum()}")
print(f"  Yale: {single_with_uni['Yale'].sum()}")
print(f"  Columbia: {single_with_uni['Columbia'].sum()}")
print(f"  Princeton: {single_with_uni['Princeton'].sum()}")
print(f"  Cornell: {single_with_uni['Cornell'].sum()}")
print(f"  Brown: {single_with_uni['Brown'].sum()}")
print(f"  Dartmouth: {single_with_uni['Dartmouth'].sum()}")
print()

# ============================================================================
# STEP 5: Summary statistics
# ============================================================================

print("Step 5: Summary Statistics for Single Founder Dataset")
print("-" * 80)

print("Education Group Distribution (Single Founders):")
print(single_with_uni['Team_Education_Group'].value_counts())
print()

print("Deal Size Statistics (Single Founders):")
print(f"  Mean: ${single_with_uni['Deal_DealSize_num'].mean():,.0f}")
print(f"  Median: ${single_with_uni['Deal_DealSize_num'].median():,.0f}")
print(f"  25th pct: ${single_with_uni['Deal_DealSize_num'].quantile(0.25):,.0f}")
print(f"  75th pct: ${single_with_uni['Deal_DealSize_num'].quantile(0.75):,.0f}")
print()

print("Top 15 Universities (by frequency):")
top_unis = single_with_uni['University_Name'].value_counts().head(15)
for uni, count in top_unis.items():
    print(f"  {uni}: {count}")
print()

# ============================================================================
# STEP 6: Export files
# ============================================================================

print("Step 6: Exporting files")
print("-" * 80)

# CSV export
csv_filename = 'deal_level_analysis_single_founders.csv'
single_with_uni.to_csv(csv_filename, index=False)
print(f"[OK] Exported CSV: {csv_filename}")
print(f"  {len(single_with_uni):,} rows × {len(single_with_uni.columns)} columns")

# Stata export
try:
    dta_filename = 'deal_level_analysis_single_founders.dta'
    single_with_uni.to_stata(dta_filename, write_index=False, version=117)
    print(f"[OK] Exported Stata: {dta_filename}")
except Exception as e:
    print(f"Stata export warning: {e}")
    print("  (You may need to install statsmodels: pip install statsmodels)")

print()

# ============================================================================
# STEP 7: Create documentation
# ============================================================================

print("Step 7: Creating documentation")
print("-" * 80)

doc = f"""# Single Founder Dataset Documentation

## Overview
This dataset contains only **single founder companies** (TeamSize = 1) from the main deal-level dataset.

**Purpose:**
- Avoid teams being included in baseline when using dummy variables in regression
- Identify specific universities driving results
- Check for outliers at the university level

## Sample Size
- **Total observations**: {len(single_with_uni):,}
- **Percentage of full sample**: {len(single_with_uni)/len(deal_df)*100:.1f}%
- **All observations have**: TeamSize = 1

## Key Differences from Main Dataset

### New Variables Added
1. **University_Name**: Specific university name from Education_Institute
   - Matches back to original founder-level data
   - Allows identification of specific schools
   
2. **University-Specific Dummies**: Created for convenience
   - `Harvard`: =1 if founder attended Harvard
   - `Stanford`: =1 if founder attended Stanford
   - `MIT`: =1 if founder attended MIT
   - `Berkeley`: =1 if founder attended UC Berkeley
   - `Penn`: =1 if founder attended UPenn/Wharton
   - `Yale`, `Columbia`, `Princeton`, `Cornell`, `Brown`, `Dartmouth`: Similar
   - Use these to check if specific schools drive results

### Variables That Are Different
- `TeamSize`: Always = 1 (by construction)
- `Team_Gender`: Only "Single_Male" or "Single_Female" (no teams)
- All `Share_*` variables: Either 0 or 1 (no mixing since solo founder)
- `Any_*` variables: Same as `Share_*` for single founders

### Variables That Are the Same
- All deal characteristics (log_DealSize, Stage_*, etc.)
- All company controls (log_Employees, Age_at_Deal, etc.)
- All fixed effects identifiers (Deal_Year, Industry, State, etc.)
- Education group classification (Ivy/Top8/Other)

## Sample Characteristics

### Education Groups (Single Founders)
{single_with_uni['Team_Education_Group'].value_counts().to_string()}

### Deal Size
- Mean: ${single_with_uni['Deal_DealSize_num'].mean():,.0f}
- Median: ${single_with_uni['Deal_DealSize_num'].median():,.0f}

### Most Common Universities
{top_unis.head(10).to_string()}

## Usage in Stata

### Basic Regression with Dummies
```stata
* Load single founder dataset
use deal_level_analysis_single_founders.dta, clear

* Check sample
tab Team_Education_Group

* Baseline with categorical dummy (omitted category = Other)
reghdfe log_DealSize i.Team_Education_Group Female_Share ///
    log_Employees Employees_Missing Age_at_Deal SyndicateSize, ///
    absorb(Deal_Year Company_PrimaryIndustryGroup ///
           Company_HQState_Province Company_YearFounded) ///
    vce(cluster CompanyID)

* Interpretation: Coefficients show Ivy and Top8 premium relative to Other
* Note: No team composition issues - all are single founders
```

### Check Specific Universities
```stata
* Which specific universities drive the Ivy premium?
reghdfe log_DealSize Harvard Stanford MIT Berkeley Penn Yale Columbia ///
    Female_Share log_Employees Employees_Missing Age_at_Deal SyndicateSize, ///
    absorb(Deal_Year Company_PrimaryIndustryGroup ///
           Company_HQState_Province Company_YearFounded) ///
    vce(cluster CompanyID)

* Interpretation: Each dummy shows that school's premium relative to all other schools
```

### Outlier Analysis
```stata
* Find deals with extreme sizes by university
preserve
keep if !missing(University_Name)
bysort University_Name: egen mean_deal = mean(log_DealSize)
bysort University_Name: egen sd_deal = sd(log_DealSize)
gen z_score = (log_DealSize - mean_deal) / sd_deal
list University_Name CompanyName Deal_DealSize_num if abs(z_score) > 3
restore

* Check if results robust to dropping outliers
drop if abs(z_score) > 3
* Re-run main regression
```

## Why Single Founders Only?

### The Problem with Teams in Dummy Variable Regression
When using dummy variables (i.e. `i.Team_Education_Group`):
- Omitted category (baseline) = "Other" 
- But in full sample, "Other" includes both:
  - Pure "Other" teams (all founders from Other schools)
  - Mixed teams (some Ivy/Top8, some Other)
  
This makes interpretation unclear.

### The Solution: Single Founders
With single founders only:
- Omitted category = Pure "Other" (one founder from Other school)
- Ivy dummy = Pure "Ivy" (one founder from Ivy)
- Top8 dummy = Pure "Top8" (one founder from Top8)
- **Clean interpretation**: Effect of being from Ivy vs. Other, no team mixing

### Trade-off
- **Gain**: Cleaner interpretation, no team composition confounds
- **Cost**: Smaller sample ({len(single_with_uni):,} vs. {len(deal_df):,})
- **Recommend**: Run both - full sample with Share_Ivy (main) and single founders with dummies (robustness)

## Comparing to Full Sample

### Full Sample Approach (Recommended for Main Results)
```stata
use deal_level_analysis.dta, clear

reghdfe log_DealSize Share_Ivy Share_Top8 TeamSize Female_Share ///
    log_Employees Employees_Missing Age_at_Deal SyndicateSize, ///
    absorb(Deal_Year Company_PrimaryIndustryGroup ///
           Company_HQState_Province Company_YearFounded) ///
    vce(cluster CompanyID)
```
- Uses all {len(deal_df):,} observations
- Share_Ivy captures intensity (0-1)
- Controls for TeamSize

### Single Founder Approach (Robustness)
```stata
use deal_level_analysis_single_founders.dta, clear

reghdfe log_DealSize i.Team_Education_Group Female_Share ///
    log_Employees Employees_Missing Age_at_Deal SyndicateSize, ///
    absorb(Deal_Year Company_PrimaryIndustryGroup ///
           Company_HQState_Province Company_YearFounded) ///
    vce(cluster CompanyID)
```
- Uses {len(single_with_uni):,} observations
- i.Team_Education_Group are clean dummies
- No team mixing issues

## Files Generated
1. `deal_level_analysis_single_founders.csv` - CSV format
2. `deal_level_analysis_single_founders.dta` - Stata format
3. `single_founder_dataset_notes.md` - This documentation

## Columns in Dataset
Total: {len(single_with_uni.columns)} columns

**All columns from main dataset**, plus:
- `University_Name`: Specific university name
- `Person_FullName`: Founder's name (for reference)
- University dummies: `Harvard`, `Stanford`, `MIT`, `Berkeley`, `Penn`, `Yale`, `Columbia`, `Princeton`, `Cornell`, `Brown`, `Dartmouth`

---

**Created**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Script**: create_single_founder_dataset.py
"""

with open('single_founder_dataset_notes.md', 'w', encoding='utf-8') as f:
    f.write(doc)
print("[OK] Created: single_founder_dataset_notes.md")

print()
print("="*80)
print("SINGLE FOUNDER DATASET CREATION COMPLETE")
print("="*80)
print()
print(f"Created dataset with {len(single_with_uni):,} single founder companies")
print(f"Added specific university names and {11} university dummy variables")
print()
print("Files created:")
print("  1. deal_level_analysis_single_founders.csv")
print("  2. deal_level_analysis_single_founders.dta")
print("  3. single_founder_dataset_notes.md")
print()
print("Use this dataset to:")
print("  - Run regressions with clean dummy variables (no team mixing)")
print("  - Identify which specific universities drive results")
print("  - Check for outliers at the university level")
print("="*80)

