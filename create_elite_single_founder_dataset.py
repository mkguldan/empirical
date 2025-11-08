"""
Create Elite Single Founder Dataset (Ivy + Top8 Only)
======================================================

Creates a dataset with ONLY single founders from Ivy League and Top 8 schools.
Excludes all "Other" universities.

Purpose:
- Direct comparison of Ivy vs Top8 without "Other" baseline
- Check if elite school effects differ within elite tier
- Avoid baseline contamination in dummy regressions
- Test whether results are driven by elite vs. non-elite or within-elite differences

Input: 
- deal_level_analysis_single_founders.csv (single founder data with university names)

Output:
- deal_level_analysis_single_founders_elite.csv
- deal_level_analysis_single_founders_elite.dta (Stata format)

Author: Empirical Methods Project, Bocconi University
Date: November 2024
"""

import pandas as pd
import numpy as np

print("="*80)
print("CREATING ELITE SINGLE FOUNDER DATASET (IVY + TOP8 ONLY)")
print("="*80)
print()

# ============================================================================
# STEP 1: Load single founder data
# ============================================================================

print("Step 1: Loading single founder dataset")
print("-" * 80)

single_df = pd.read_csv('deal_level_analysis_single_founders.csv')
print(f"Total single founder deals: {len(single_df):,}")

# Show distribution before filtering
print("\nEducation group distribution (before filtering):")
print(single_df['Education_Group'].value_counts())
print()

# ============================================================================
# STEP 2: Filter for Ivy and Top8 only
# ============================================================================

print("Step 2: Filtering for Ivy and Top8 schools only")
print("-" * 80)

# Keep only Ivy and Top8
elite_df = single_df[single_df['Education_Group'].isin(['Ivy', 'Top8'])].copy()

print(f"After filtering for elite schools: {len(elite_df):,} deals")
print(f"Dropped {len(single_df) - len(elite_df):,} deals from 'Other' schools")
print()

print("Education group distribution (after filtering):")
print(elite_df['Education_Group'].value_counts())
print(f"\nPercentage breakdown:")
print(f"  Ivy: {len(elite_df[elite_df['Education_Group']=='Ivy']):,} ({len(elite_df[elite_df['Education_Group']=='Ivy'])/len(elite_df)*100:.1f}%)")
print(f"  Top8: {len(elite_df[elite_df['Education_Group']=='Top8']):,} ({len(elite_df[elite_df['Education_Group']=='Top8'])/len(elite_df)*100:.1f}%)")
print()

# ============================================================================
# STEP 3: Create Ivy vs Top8 binary indicator
# ============================================================================

print("Step 3: Creating Ivy vs Top8 binary indicator")
print("-" * 80)

# Create a simple binary: 1 = Ivy, 0 = Top8
elite_df['Ivy_vs_Top8'] = (elite_df['Education_Group'] == 'Ivy').astype(int)

print(f"Created 'Ivy_vs_Top8' variable:")
print(f"  1 (Ivy): {elite_df['Ivy_vs_Top8'].sum():,}")
print(f"  0 (Top8): {(1-elite_df['Ivy_vs_Top8']).sum():,}")
print()

# ============================================================================
# STEP 4: Summary statistics
# ============================================================================

print("Step 4: Summary Statistics for Elite Single Founder Dataset")
print("-" * 80)

print("Deal Size Statistics (Elite Schools Only):")
print(f"  Mean: ${elite_df['Deal_DealSize_num'].mean():,.0f}")
print(f"  Median: ${elite_df['Deal_DealSize_num'].median():,.0f}")
print(f"  25th pct: ${elite_df['Deal_DealSize_num'].quantile(0.25):,.0f}")
print(f"  75th pct: ${elite_df['Deal_DealSize_num'].quantile(0.75):,.0f}")
print()

print("Deal Size by Group:")
for group in ['Ivy', 'Top8']:
    group_df = elite_df[elite_df['Education_Group'] == group]
    print(f"\n{group}:")
    print(f"  N: {len(group_df):,}")
    print(f"  Mean: ${group_df['Deal_DealSize_num'].mean():,.0f}")
    print(f"  Median: ${group_df['Deal_DealSize_num'].median():,.0f}")
    print(f"  Log mean: {group_df['log_DealSize'].mean():.3f}")
print()

print("Top 15 Universities (Elite Only):")
top_unis = elite_df['University_Name'].value_counts().head(15)
for uni, count in top_unis.items():
    print(f"  {uni}: {count}")
print()

# Gender distribution
print("Gender Distribution (Elite):")
print(f"  Female founders: {elite_df['Any_Female'].sum():,} ({elite_df['Any_Female'].mean()*100:.1f}%)")
print(f"  Male founders: {(1-elite_df['Any_Female']).sum():,} ({(1-elite_df['Any_Female']).mean()*100:.1f}%)")
print()

# Stage distribution
print("Deal Stage Distribution (Elite):")
print(f"  Seed: {elite_df['Stage_Seed'].sum():,} ({elite_df['Stage_Seed'].mean()*100:.1f}%)")
print(f"  Early: {elite_df['Stage_Early'].sum():,} ({elite_df['Stage_Early'].mean()*100:.1f}%)")
print(f"  Later: {elite_df['Stage_Later'].sum():,} ({elite_df['Stage_Later'].mean()*100:.1f}%)")
print()

# ============================================================================
# STEP 5: Export files
# ============================================================================

print("Step 5: Exporting files")
print("-" * 80)

# CSV export
csv_filename = 'deal_level_analysis_single_founders_elite.csv'
elite_df.to_csv(csv_filename, index=False)
print(f"[OK] Exported CSV: {csv_filename}")
print(f"  {len(elite_df):,} rows × {len(elite_df.columns)} columns")

# Stata export
try:
    dta_filename = 'deal_level_analysis_single_founders_elite.dta'
    elite_df.to_stata(dta_filename, write_index=False, version=117)
    print(f"[OK] Exported Stata: {dta_filename}")
except Exception as e:
    print(f"Stata export warning: {e}")
    print("  (You may need to install statsmodels: pip install statsmodels)")

print()

# ============================================================================
# STEP 6: Create documentation
# ============================================================================

print("Step 6: Creating documentation")
print("-" * 80)

doc = f"""# Elite Single Founder Dataset Documentation (Ivy + Top8 Only)

## Overview
This dataset contains **ONLY single founder companies from Ivy League and Top 8 schools**.

**All "Other" schools are EXCLUDED.**

## Sample Size
- **Total observations**: {len(elite_df):,}
- **Ivy League**: {len(elite_df[elite_df['Education_Group']=='Ivy']):,} ({len(elite_df[elite_df['Education_Group']=='Ivy'])/len(elite_df)*100:.1f}%)
- **Top 8**: {len(elite_df[elite_df['Education_Group']=='Top8']):,} ({len(elite_df[elite_df['Education_Group']=='Top8'])/len(elite_df)*100:.1f}%)
- **Dropped from single founder dataset**: {len(single_df) - len(elite_df):,} (all "Other" schools)

## Purpose

### Why Exclude "Other"?

1. **Direct Elite Comparison**: Compare Ivy vs. Top8 without non-elite baseline
2. **Within-Elite Effects**: Test if there are differences within the elite tier
3. **Baseline Clarity**: When using `i.Education_Group` in Stata, baseline (Top8) is clearly defined
4. **Test Hypothesis**: Is the "Ivy premium" vs. "Other" actually vs. "non-Ivy elite"?

### Research Questions This Enables

- **Q1**: Do Ivy founders raise more than Top8 founders? (within elite comparison)
- **Q2**: Are Top8 founders different from "Other"? (compare full sample to elite-only)
- **Q3**: Is the Ivy effect driven by Ivy vs. all others, or Ivy vs. other elite?

## Key Differences from Other Datasets

### vs. Full Dataset (`deal_level_analysis.csv`)
- Full: 7,774 deals (all team sizes, all school types)
- Elite: {len(elite_df):,} deals (single founders, Ivy + Top8 only)
- **Lost**: Teams AND "Other" schools

### vs. Single Founder Dataset (`deal_level_analysis_single_founders.csv`)
- Single: 5,589 deals (solo founders, all school types)
- Elite: {len(elite_df):,} deals (solo founders, Ivy + Top8 only)
- **Lost**: "Other" schools ({len(single_df) - len(elite_df):,} deals)

## New Variable

### Ivy_vs_Top8
Binary indicator for easier regression interpretation:
- **1** = Ivy League founder
- **0** = Top 8 founder

This is equivalent to `Education_Group == 'Ivy'` but more convenient for dummy regressions.

## Sample Characteristics

### Deal Sizes
**Overall (Elite):**
- Mean: ${elite_df['Deal_DealSize_num'].mean():,.0f}
- Median: ${elite_df['Deal_DealSize_num'].median():,.0f}

**By Group:**
{chr(10).join([f"- {group}: Mean ${elite_df[elite_df['Education_Group']==group]['Deal_DealSize_num'].mean():,.0f}, Median ${elite_df[elite_df['Education_Group']==group]['Deal_DealSize_num'].median():,.0f}" for group in ['Ivy', 'Top8']])}

### Top Universities (Elite Only)
{top_unis.head(10).to_string()}

### Gender
- Female founders: {elite_df['Any_Female'].sum():,} ({elite_df['Any_Female'].mean()*100:.1f}%)
- Male founders: {(1-elite_df['Any_Female']).sum():,} ({(1-elite_df['Any_Female']).mean()*100:.1f}%)

## Usage in Stata

### Main Specification: Ivy vs Top8 Direct Comparison

```stata
use deal_level_analysis_single_founders_elite.dta, clear

* Basic comparison (Top8 is omitted baseline)
reghdfe log_DealSize i.Education_Group Female_Share ///
    log_Employees Employees_Missing Age_at_Deal SyndicateSize, ///
    absorb(Deal_Year Company_PrimaryIndustryGroup ///
           Company_HQState_Province Company_YearFounded) ///
    vce(cluster CompanyID)

* Or use the binary indicator (equivalent)
reghdfe log_DealSize Ivy_vs_Top8 Female_Share ///
    log_Employees Employees_Missing Age_at_Deal SyndicateSize, ///
    absorb(Deal_Year Company_PrimaryIndustryGroup ///
           Company_HQState_Province Company_YearFounded) ///
    vce(cluster CompanyID)
```

**Interpretation**: 
- Coefficient on `1.Education_Group` (or `Ivy_vs_Top8`) shows Ivy premium **relative to Top8**
- Baseline = Top8 (clearly elite schools)
- Tests: "Among elite schools, does Ivy matter?"

### Compare to Full Sample

Run the same specification on different samples:

```stata
* Sample 1: All schools, all team sizes (Share variables)
use deal_level_analysis.dta, clear
reghdfe log_DealSize Share_Ivy Share_Top8 TeamSize [controls], absorb(FEs)
* Interpretation: Ivy vs. Other, Top8 vs. Other

* Sample 2: Single founders, all schools (Dummy)
use deal_level_analysis_single_founders.dta, clear
reghdfe log_DealSize i.Education_Group [controls], absorb(FEs)
* Interpretation: Ivy vs. Other, Top8 vs. Other (clean dummies)

* Sample 3: Single founders, elite only (Ivy vs Top8)
use deal_level_analysis_single_founders_elite.dta, clear
reghdfe log_DealSize Ivy_vs_Top8 [controls], absorb(FEs)
* Interpretation: Ivy vs. Top8 (within elite comparison)
```

### Heterogeneity: Ivy vs Top8 by Gender

```stata
use deal_level_analysis_single_founders_elite.dta, clear

* Interaction
reghdfe log_DealSize Ivy_vs_Top8##Female_Share ///
    log_Employees Employees_Missing Age_at_Deal SyndicateSize, ///
    absorb(Deal_Year Company_PrimaryIndustryGroup ///
           Company_HQState_Province Company_YearFounded) ///
    vce(cluster CompanyID)

* Marginal effects
margins, at(Ivy_vs_Top8=(0 1) Female_Share=(0 1))
marginsplot
```

### By Specific Elite University

```stata
use deal_level_analysis_single_founders_elite.dta, clear

* Among elite schools, which specific ones have the biggest premium?
reghdfe log_DealSize Harvard Stanford MIT Berkeley Penn Yale Columbia ///
    Female_Share log_Employees Employees_Missing Age_at_Deal SyndicateSize, ///
    absorb(Deal_Year Company_PrimaryIndustryGroup ///
           Company_HQState_Province Company_YearFounded) ///
    vce(cluster CompanyID)
```

## Three-Dataset Strategy

### Recommended Analysis Approach

**Table 1: Main Results (Full Sample)**
- Dataset: `deal_level_analysis.dta` (7,774 deals)
- Specification: Share_Ivy, Share_Top8, TeamSize
- Shows: Ivy effect vs. all others (including teams)

**Table 2: Robustness (Single Founders, All Schools)**
- Dataset: `deal_level_analysis_single_founders.dta` (5,589 deals)
- Specification: i.Education_Group (Ivy vs Other, Top8 vs Other)
- Shows: Solo founder Ivy effect vs. "Other" (no team confound)

**Table 3: Within-Elite Comparison (Single Founders, Elite Only)**
- Dataset: `deal_level_analysis_single_founders_elite.dta` ({len(elite_df):,} deals)
- Specification: Ivy_vs_Top8 (or i.Education_Group)
- Shows: Is Ivy different from Top8? (within elite tier)

### What Each Table Tells You

- **Table 1 → Table 2**: Are results robust to removing teams?
- **Table 2 → Table 3**: Is the Ivy effect vs. "Other" or vs. "Top8"?
- **If Table 3 coefficient ≈ 0**: Ivy ≈ Top8, effect is "elite vs. non-elite"
- **If Table 3 coefficient > 0**: Ivy > Top8, effect is "Ivy vs. everyone"

## Interpretation Guide

### Scenario 1: Ivy > Top8 in Elite Sample
**Finding**: Coefficient on `Ivy_vs_Top8` is positive and significant
**Interpretation**: 
- Ivy founders raise more than Top8 founders
- The "Ivy premium" is not just "elite vs. non-elite"
- Network effects specific to Ivy League

### Scenario 2: Ivy ≈ Top8 in Elite Sample
**Finding**: Coefficient on `Ivy_vs_Top8` is near zero or insignificant
**Interpretation**:
- Ivy and Top8 founders raise similar amounts
- The "Ivy premium" in full sample is really "elite vs. non-elite"
- All elite schools benefit equally from prestige/networks

### Scenario 3: Different by Gender/Industry
**Finding**: `Ivy_vs_Top8 × Female_Share` is significant
**Interpretation**:
- Within elite tier, Ivy vs. Top8 gap differs by founder gender
- Suggests network/signaling mechanisms vary

## Files Generated
1. `deal_level_analysis_single_founders_elite.csv` - CSV format
2. `deal_level_analysis_single_founders_elite.dta` - Stata format
3. `elite_single_founder_dataset_notes.md` - This documentation

## Comparison Table

| Dataset | N | Teams? | Schools | Best For |
|---------|---|--------|---------|----------|
| Full | 7,774 | Yes | All | Main results with Share_Ivy |
| Single Founders | 5,589 | No | All | Robustness without teams |
| **Elite Only** | **{len(elite_df):,}** | **No** | **Ivy+Top8** | **Within-elite comparison** |

---

**Created**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Script**: create_elite_single_founder_dataset.py  
**Sample**: {len(elite_df):,} elite single founder companies (Ivy + Top8 only)
"""

with open('elite_single_founder_dataset_notes.md', 'w', encoding='utf-8') as f:
    f.write(doc)
print("[OK] Created: elite_single_founder_dataset_notes.md")

print()
print("="*80)
print("ELITE SINGLE FOUNDER DATASET CREATION COMPLETE")
print("="*80)
print()
print(f"Created dataset with {len(elite_df):,} elite single founder companies")
print(f"  - Ivy League: {len(elite_df[elite_df['Education_Group']=='Ivy']):,}")
print(f"  - Top 8: {len(elite_df[elite_df['Education_Group']=='Top8']):,}")
print()
print("Files created:")
print("  1. deal_level_analysis_single_founders_elite.csv")
print("  2. deal_level_analysis_single_founders_elite.dta")
print("  3. elite_single_founder_dataset_notes.md")
print()
print("Use this dataset to:")
print("  - Directly compare Ivy vs. Top8 (within elite tier)")
print("  - Test if Ivy premium is vs. all others or vs. other elite")
print("  - Check gender/industry heterogeneity within elite schools")
print("="*80)


