"""
Prepare Deal-Level Analysis File for Stata
===========================================

Transforms founder-level data into deal-level analysis file with:
- Team composition variables (education, gender, majors)
- Company and deal characteristics
- Fixed effects identifiers
- Ready for regression analysis in Stata

Input: founder_vc_final_formatted_with_groups.csv (founder-level)
Output: deal_level_analysis.csv/.dta (deal-level, one row per company/deal)

Author: Empirical Methods Project, Bocconi University
Last Updated: November 2024
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime

print("="*80)
print("FOUNDER-VC DATA PREPARATION FOR STATA ANALYSIS")
print("="*80)
print()

# ============================================================================
# PHASE 1: LOAD AND INITIAL FILTERING
# ============================================================================

print("PHASE 1: Loading and Initial Filtering")
print("-" * 80)

# Load founder-level data
df = pd.read_csv('founder_vc_final_formatted_with_groups.csv')
print(f"Loaded founder-level data: {len(df):,} rows × {df.shape[1]} columns")

initial_companies = df['CompanyID'].nunique()
initial_deals = df['DealID'].nunique()
initial_founders = df['PersonID'].nunique()
print(f"Initial: {initial_companies:,} companies, {initial_deals:,} deals, {initial_founders:,} founders")
print()

# ============================================================================
# PHASE 2: GEOGRAPHY FILTER - US ONLY
# ============================================================================

print("PHASE 2: Geography Filter - US Only")
print("-" * 80)

# Define US states (50 states + DC)
us_states = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
    'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
    'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
    'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
    'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
    'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
    'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
    'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
    'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
    'West Virginia', 'Wisconsin', 'Wyoming', 'District of Columbia'
]

# Check current states
print(f"Unique states/provinces before filter: {df['Company_HQState_Province'].nunique()}")
non_us = df[~df['Company_HQState_Province'].isin(us_states)]['Company_HQState_Province'].value_counts()
if len(non_us) > 0:
    print(f"Non-US locations found: {len(non_us)}")
    print(non_us.head(10))

# Filter to US only
df = df[df['Company_HQState_Province'].isin(us_states)].copy()
print(f"After US filter: {len(df):,} rows ({df['CompanyID'].nunique():,} companies)")
print()

# ============================================================================
# PHASE 3: PARSE DATES AND FILTER MISSING DEAL_YEAR
# ============================================================================

print("PHASE 3: Parsing Deal Dates and Filtering Missing Years")
print("-" * 80)

def parse_deal_date(date_str):
    """Parse DD.MM.YYYY format"""
    if pd.isna(date_str):
        return None
    try:
        # Format: 30.5.2014
        return pd.to_datetime(date_str, format='%d.%m.%Y', errors='coerce')
    except:
        return None

df['Deal_Date_Parsed'] = df['Deal_DealDate'].apply(parse_deal_date)
df['Deal_Year'] = df['Deal_Date_Parsed'].dt.year

print(f"Date parsing:")
print(f"  Valid dates: {df['Deal_Date_Parsed'].notna().sum():,}")
print(f"  Missing dates: {df['Deal_Date_Parsed'].isna().sum():,}")

# Filter out deals with missing Deal_Year
before_year_filter = len(df)
df = df[df['Deal_Year'].notna()].copy()
print(f"After excluding missing Deal_Year: {len(df):,} rows (dropped {before_year_filter - len(df):,})")
print(f"  Year range: {df['Deal_Year'].min():.0f} - {df['Deal_Year'].max():.0f}")
print()

# ============================================================================
# PHASE 4: PARSE DEAL AMOUNTS
# ============================================================================

print("PHASE 4: Parsing Deal Amounts")
print("-" * 80)

def parse_deal_size(amount_str):
    """Parse $X,XXX,XXX.XX format"""
    if pd.isna(amount_str):
        return None
    try:
        # Remove $, commas
        cleaned = str(amount_str).replace('$', '').replace(',', '')
        value = float(cleaned)
        return value if value > 0 else None
    except:
        return None

df['Deal_DealSize_num'] = df['Deal_DealSize'].apply(parse_deal_size)

print(f"Amount parsing:")
print(f"  Valid amounts: {df['Deal_DealSize_num'].notna().sum():,}")
print(f"  Missing/zero amounts: {df['Deal_DealSize_num'].isna().sum():,}")
print(f"  Amount range: ${df['Deal_DealSize_num'].min():,.0f} - ${df['Deal_DealSize_num'].max():,.0f}")
print(f"  Median: ${df['Deal_DealSize_num'].median():,.0f}")

# Exclude rows with missing deal size
before_filter = len(df)
df = df[df['Deal_DealSize_num'].notna()].copy()
print(f"After excluding missing deal size: {len(df):,} rows (dropped {before_filter - len(df):,})")
print()

# Create log amount
df['log_DealSize'] = np.log(df['Deal_DealSize_num'])

# ============================================================================
# PHASE 5: COMPANY CONTROLS
# ============================================================================

print("PHASE 5: Creating Company Controls")
print("-" * 80)

# Log employees with missing indicator
df['Employees_Missing'] = df['Company_Employees'].isna().astype(int)
df['log_Employees'] = np.log(df['Company_Employees'])
df.loc[df['Company_Employees'].isna(), 'log_Employees'] = np.nan

print(f"Employees: {df['Employees_Missing'].sum():,} missing ({df['Employees_Missing'].mean()*100:.1f}%)")

# Age at deal
df['Age_at_Deal'] = df['Deal_Year'] - df['Company_YearFounded']
print(f"Age at deal: mean = {df['Age_at_Deal'].mean():.1f} years, range = {df['Age_at_Deal'].min():.0f}-{df['Age_at_Deal'].max():.0f}")
print()

# ============================================================================
# PHASE 6: MAP MAJORS TO CATEGORIES
# ============================================================================

print("PHASE 6: Mapping Majors to Broad Categories")
print("-" * 80)

def categorize_major(major_str):
    """Map major to one of 8 broad categories"""
    if pd.isna(major_str):
        return 'Missing'
    
    major_lower = str(major_str).lower()
    
    # Computer Science / Engineering
    cs_keywords = ['computer', 'software', 'programming', 'information system', 
                   'information technology', 'data science', 'artificial intelligence',
                   'machine learning', 'electrical engineering', 'computer engineering',
                   'systems engineering', 'engineering', 'mechanical', 'civil',
                   'industrial', 'aerospace', 'chemical engineering', 'bioengineering']
    if any(kw in major_lower for kw in cs_keywords):
        return 'CS_Engineering'
    
    # Natural Sciences
    science_keywords = ['mathematics', 'physics', 'chemistry', 'biology', 'math',
                       'biochemistry', 'biophysics', 'neuroscience', 'molecular',
                       'genetics', 'applied math', 'statistics', 'astrophysics',
                       'geology', 'environmental science']
    if any(kw in major_lower for kw in science_keywords):
        return 'Natural_Sciences'
    
    # Medicine / Health Sciences
    med_keywords = ['medicine', 'medical', 'health', 'nursing', 'pharmacy',
                   'biomedical', 'clinical', 'anatomy', 'physiology', 'pathology',
                   'immunology', 'epidemiology', 'public health', 'dentistry']
    if any(kw in major_lower for kw in med_keywords):
        return 'Medicine_Health'
    
    # Business / Finance / Economics
    business_keywords = ['business', 'finance', 'economics', 'accounting', 'marketing',
                        'management', 'mba', 'entrepreneurship', 'commerce', 'banking',
                        'strategy', 'operations', 'real estate', 'investment']
    if any(kw in major_lower for kw in business_keywords):
        return 'Business_Econ'
    
    # Social Sciences
    social_keywords = ['psychology', 'sociology', 'anthropology', 'political science',
                      'government', 'international relations', 'policy', 'geography',
                      'social work', 'education', 'communications']
    if any(kw in major_lower for kw in social_keywords):
        return 'Social_Sciences'
    
    # Humanities / Arts
    humanities_keywords = ['history', 'english', 'literature', 'philosophy', 'art',
                          'music', 'theater', 'language', 'linguistics', 'creative writing',
                          'film', 'design', 'architecture', 'media studies']
    if any(kw in major_lower for kw in humanities_keywords):
        return 'Humanities_Arts'
    
    # Law
    if 'law' in major_lower or 'legal' in major_lower or 'jurisprudence' in major_lower:
        return 'Law'
    
    # Default
    return 'Other'

df['Major_Category'] = df['Education_Major_Concentration'].apply(categorize_major)

print("Major categories distribution:")
print(df['Major_Category'].value_counts())
print()

# ============================================================================
# PHASE 7: EDUCATION LEVEL
# ============================================================================

print("PHASE 7: Education Level Ranking")
print("-" * 80)

def rank_education(degree_cat):
    """Rank education levels"""
    if pd.isna(degree_cat):
        return 0
    degree_cat = str(degree_cat).upper()
    if 'PHD' in degree_cat:
        return 7
    elif 'MD' in degree_cat or 'DOCTOR OF MEDICINE' in degree_cat:
        return 6
    elif 'JD' in degree_cat:
        return 5
    elif 'MBA' in degree_cat:
        return 4
    elif 'MSC' in degree_cat or 'MASTER' in degree_cat:
        return 3
    elif 'BSC' in degree_cat or 'BACHELOR' in degree_cat:
        return 2
    elif 'ASC' in degree_cat or 'ASSOCIATE' in degree_cat:
        return 1
    else:
        return 0

df['Education_Rank'] = df['Education_Category'].apply(rank_education)
print(f"Education ranking complete")
print()

# ============================================================================
# PHASE 8: COLLAPSE TO DEAL LEVEL - TEAM COMPOSITION
# ============================================================================

print("PHASE 8: Collapsing to Deal Level with Team Composition")
print("-" * 80)

# Group by DealID and compute team composition
deal_teams = []

for deal_id, group in df.groupby('DealID'):
    team_dict = {'DealID': deal_id}
    
    # Team size
    team_dict['TeamSize'] = group['PersonID'].nunique()
    
    # University group counts
    ivy_count = (group['University_Group'] == 'Ivy').sum()
    top8_count = (group['University_Group'] == 'Top8').sum()
    other_count = (group['University_Group'] == 'Other').sum()
    
    # Share variables (continuous)
    team_dict['Share_Ivy'] = ivy_count / team_dict['TeamSize']
    team_dict['Share_Top8'] = top8_count / team_dict['TeamSize']
    team_dict['Share_Other'] = other_count / team_dict['TeamSize']
    
    # Binary indicators
    team_dict['Any_Ivy'] = int(ivy_count > 0)
    team_dict['Any_Top8'] = int(top8_count > 0)
    
    # Hierarchical category (mutually exclusive: Ivy > Top8 > Other)
    if ivy_count > 0:
        team_dict['Team_Education_Group'] = 'Ivy'
    elif top8_count > 0:
        team_dict['Team_Education_Group'] = 'Top8'
    else:
        team_dict['Team_Education_Group'] = 'Other'
    
    # Max pedigree (numeric: Ivy=3, Top8=2, Other=1)
    if ivy_count > 0:
        team_dict['Max_Pedigree'] = 3
    elif top8_count > 0:
        team_dict['Max_Pedigree'] = 2
    else:
        team_dict['Max_Pedigree'] = 1
    
    # Gender composition
    female_count = (group['Person_Gender'] == 'Female').sum()
    male_count = (group['Person_Gender'] == 'Male').sum()
    
    team_dict['Female_Share'] = female_count / team_dict['TeamSize']
    team_dict['Any_Female'] = int(female_count > 0)
    
    # Team gender category
    if team_dict['TeamSize'] == 1:
        if female_count == 1:
            team_dict['Team_Gender'] = 'Single_Female'
        else:
            team_dict['Team_Gender'] = 'Single_Male'
    else:
        if female_count == team_dict['TeamSize']:
            team_dict['Team_Gender'] = 'All_Female'
        elif male_count == team_dict['TeamSize']:
            team_dict['Team_Gender'] = 'All_Male'
        else:
            team_dict['Team_Gender'] = 'Mixed'
    
    # Major composition
    major_counts = group['Major_Category'].value_counts()
    team_dict['Team_Major_Dominant'] = major_counts.index[0] if len(major_counts) > 0 else 'Missing'
    
    # STEM share (CS_Engineering + Natural_Sciences)
    stem_count = ((group['Major_Category'] == 'CS_Engineering') | 
                  (group['Major_Category'] == 'Natural_Sciences')).sum()
    team_dict['Team_STEM_Share'] = stem_count / team_dict['TeamSize']
    
    # Business share
    business_count = (group['Major_Category'] == 'Business_Econ').sum()
    team_dict['Team_Business_Share'] = business_count / team_dict['TeamSize']
    
    # CS flag
    team_dict['Any_CS'] = int((group['Major_Category'] == 'CS_Engineering').any())
    
    # Max education
    team_dict['Max_Education_Rank'] = group['Education_Rank'].max()
    
    # Map rank back to label
    rank_to_label = {7: 'PhD', 6: 'MD', 5: 'JD', 4: 'MBA', 3: 'MSC', 2: 'BSC', 1: 'ASC', 0: 'Other'}
    team_dict['Max_Education'] = rank_to_label.get(team_dict['Max_Education_Rank'], 'Other')
    
    # Investor syndicate size
    investor_count = group['InvestorID'].nunique()
    # Subtract 1 if all are NaN (nunique counts NaN as 1)
    if group['InvestorID'].isna().all():
        investor_count = 0
    team_dict['SyndicateSize'] = investor_count
    team_dict['Investor_Missing'] = int(group['InvestorID'].isna().all())
    
    # Keep first occurrence of deal/company variables (they're the same within deal)
    first_row = group.iloc[0]
    
    # Company info
    team_dict['CompanyID'] = first_row['CompanyID']
    team_dict['CompanyName'] = first_row['CompanyName']
    team_dict['Company_Employees'] = first_row['Company_Employees']
    team_dict['log_Employees'] = first_row['log_Employees']
    team_dict['Employees_Missing'] = first_row['Employees_Missing']
    team_dict['Company_YearFounded'] = first_row['Company_YearFounded']
    team_dict['Company_PrimaryIndustrySector'] = first_row['Company_PrimaryIndustrySector']
    team_dict['Company_PrimaryIndustryGroup'] = first_row['Company_PrimaryIndustryGroup']
    team_dict['Company_HQCity'] = first_row['Company_HQCity']
    team_dict['Company_HQState_Province'] = first_row['Company_HQState_Province']
    
    # Deal info
    team_dict['Deal_DealDate'] = first_row['Deal_DealDate']
    team_dict['Deal_Year'] = first_row['Deal_Year']
    team_dict['Deal_DealSize'] = first_row['Deal_DealSize']
    team_dict['Deal_DealSize_num'] = first_row['Deal_DealSize_num']
    team_dict['log_DealSize'] = first_row['log_DealSize']
    team_dict['Deal_DealStatus'] = first_row['Deal_DealStatus']
    team_dict['Deal_DealType'] = first_row['Deal_DealType']
    team_dict['Deal_DealClass'] = first_row['Deal_DealClass']
    team_dict['Deal_BusinessStatus'] = first_row['Deal_BusinessStatus']
    team_dict['Deal_SiteLocation'] = first_row['Deal_SiteLocation']
    team_dict['Age_at_Deal'] = first_row['Age_at_Deal']
    
    deal_teams.append(team_dict)

# Create deal-level dataframe
deal_df = pd.DataFrame(deal_teams)

print(f"Collapsed to deal-level: {len(deal_df):,} rows")
print(f"  Unique companies: {deal_df['CompanyID'].nunique():,}")
print(f"  Unique deals: {deal_df['DealID'].nunique():,}")
print()

# ============================================================================
# PHASE 9: STAGE VARIABLES
# ============================================================================

print("PHASE 9: Creating Stage Variables")
print("-" * 80)

deal_df['Stage_Seed'] = (deal_df['Deal_DealType'] == 'Seed Round').astype(int)
deal_df['Stage_Early'] = (deal_df['Deal_DealType'] == 'Early Stage VC').astype(int)
deal_df['Stage_Later'] = (deal_df['Deal_DealType'] == 'Later Stage VC').astype(int)

# Stage order (1=Seed, 2=Early, 3=Later)
stage_map = {
    'Seed Round': 1,
    'Early Stage VC': 2,
    'Later Stage VC': 3
}
deal_df['Stage_Order'] = deal_df['Deal_DealType'].map(stage_map)

print("Stage distribution:")
print(deal_df['Deal_DealType'].value_counts())
print()

# ============================================================================
# PHASE 10: REGION CATEGORIES
# ============================================================================

print("PHASE 10: Creating Region Categories")
print("-" * 80)

# Define US regions
northeast = ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island',
             'Vermont', 'New Jersey', 'New York', 'Pennsylvania']
south = ['Delaware', 'Florida', 'Georgia', 'Maryland', 'North Carolina', 'South Carolina',
         'Virginia', 'West Virginia', 'Alabama', 'Kentucky', 'Mississippi', 'Tennessee',
         'Arkansas', 'Louisiana', 'Oklahoma', 'Texas', 'District of Columbia']
midwest = ['Illinois', 'Indiana', 'Michigan', 'Ohio', 'Wisconsin', 'Iowa', 'Kansas',
           'Minnesota', 'Missouri', 'Nebraska', 'North Dakota', 'South Dakota']
west = ['Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada', 'New Mexico', 'Utah',
        'Wyoming', 'Alaska', 'California', 'Hawaii', 'Oregon', 'Washington']

def assign_region(state):
    if state in northeast:
        return 'Northeast'
    elif state in south:
        return 'South'
    elif state in midwest:
        return 'Midwest'
    elif state in west:
        return 'West'
    else:
        return 'Other'

deal_df['Region'] = deal_df['Company_HQState_Province'].apply(assign_region)

print("Region distribution:")
print(deal_df['Region'].value_counts())
print()

# ============================================================================
# PHASE 11: VALIDATION CHECKS
# ============================================================================

print("PHASE 11: Validation Checks")
print("-" * 80)

# Check 1: Share variables sum to 1
deal_df['Share_Sum'] = deal_df['Share_Ivy'] + deal_df['Share_Top8'] + deal_df['Share_Other']
share_check = np.allclose(deal_df['Share_Sum'], 1.0)
print(f"Share variables sum to 1.0: {share_check}")
if not share_check:
    print(f"  Max deviation: {(deal_df['Share_Sum'] - 1.0).abs().max():.6f}")

# Check 2: 1:1 mapping company to deal
company_deal_check = deal_df.groupby('CompanyID')['DealID'].nunique().max() == 1
print(f"1:1 mapping CompanyID to DealID: {company_deal_check}")

# Check 3: No missing key variables
print(f"Missing values in key variables:")
print(f"  log_DealSize: {deal_df['log_DealSize'].isna().sum()}")
print(f"  Deal_Year: {deal_df['Deal_Year'].isna().sum()}")
print(f"  Team_Education_Group: {deal_df['Team_Education_Group'].isna().sum()}")
print(f"  Region: {deal_df['Region'].isna().sum()}")
print()

# ============================================================================
# PHASE 12: SUMMARY STATISTICS
# ============================================================================

print("PHASE 12: Summary Statistics")
print("-" * 80)

print("Deal Size:")
print(f"  Mean: ${deal_df['Deal_DealSize_num'].mean():,.0f}")
print(f"  Median: ${deal_df['Deal_DealSize_num'].median():,.0f}")
print(f"  25th pct: ${deal_df['Deal_DealSize_num'].quantile(0.25):,.0f}")
print(f"  75th pct: ${deal_df['Deal_DealSize_num'].quantile(0.75):,.0f}")
print()

print("Team Composition:")
print(f"  Mean TeamSize: {deal_df['TeamSize'].mean():.2f}")
print(f"  Mean Share_Ivy: {deal_df['Share_Ivy'].mean():.3f}")
print(f"  Mean Share_Top8: {deal_df['Share_Top8'].mean():.3f}")
print(f"  Mean Female_Share: {deal_df['Female_Share'].mean():.3f}")
print()

print("Team Education Group:")
print(deal_df['Team_Education_Group'].value_counts())
print()

print("Team Gender:")
print(deal_df['Team_Gender'].value_counts())
print()

# ============================================================================
# PHASE 13: EXPORT FILES
# ============================================================================

print("PHASE 13: Exporting Files")
print("-" * 80)

# CSV export
csv_filename = 'deal_level_analysis.csv'
deal_df.to_csv(csv_filename, index=False)
print(f"Exported CSV: {csv_filename}")
print(f"  {len(deal_df):,} rows × {len(deal_df.columns)} columns")

# Stata export
try:
    dta_filename = 'deal_level_analysis.dta'
    deal_df.to_stata(dta_filename, write_index=False, version=117)
    print(f"Exported Stata: {dta_filename}")
except Exception as e:
    print(f"Stata export warning: {e}")
    print("  (You may need to install statsmodels: pip install statsmodels)")

print()

# ============================================================================
# PHASE 14: CREATE DOCUMENTATION
# ============================================================================

print("PHASE 14: Creating Documentation")
print("-" * 80)

# Create comprehensive documentation
doc = f"""# Data Preparation Log
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Sample Composition

### Initial Data (Founder-Level)
- Total rows: {initial_founders:,}
- Unique companies: {initial_companies:,}
- Unique deals: {initial_deals:,}
- Unique founders: {initial_founders:,}

### Final Data (Deal-Level)
- Total rows: {len(deal_df):,}
- Unique companies: {deal_df['CompanyID'].nunique():,}
- Unique deals: {deal_df['DealID'].nunique():,}

### Filtering Steps
1. **Geography Filter (US only)**: Kept {len(df):,} founder observations
2. **Deal Year Filter**: Excluded {before_year_filter - len(df):,} observations with missing Deal_Year
3. **Deal Size Filter**: Excluded {before_filter - len(df):,} observations with missing/zero deal size
4. **Collapse to Deal-Level**: Aggregated founder observations → {len(deal_df):,} deals

## Key Statistics

### Deal Size Distribution
- Mean: ${deal_df['Deal_DealSize_num'].mean():,.0f}
- Median: ${deal_df['Deal_DealSize_num'].median():,.0f}
- Range: ${deal_df['Deal_DealSize_num'].min():,.0f} - ${deal_df['Deal_DealSize_num'].max():,.0f}

### Team Composition
- Mean TeamSize: {deal_df['TeamSize'].mean():.2f}
- Mean Share_Ivy: {deal_df['Share_Ivy'].mean():.3f} ({deal_df['Share_Ivy'].mean()*100:.1f}%)
- Mean Share_Top8: {deal_df['Share_Top8'].mean():.3f} ({deal_df['Share_Top8'].mean()*100:.1f}%)
- Mean Female_Share: {deal_df['Female_Share'].mean():.3f} ({deal_df['Female_Share'].mean()*100:.1f}%)

### Education Group Distribution
{deal_df['Team_Education_Group'].value_counts().to_string()}

### Stage Distribution
{deal_df['Deal_DealType'].value_counts().to_string()}

### Region Distribution
{deal_df['Region'].value_counts().to_string()}

## Files Generated
1. deal_level_analysis.csv - Main analysis file (CSV format)
2. deal_level_analysis.dta - Stata format with labels
3. data_preparation_log.md - This documentation file

## Data Structure
- CompanyID to DealID mapping: {company_deal_check} (1:1 confirmed)
- Share variables sum check: {share_check}
- No missing Deal_Year in final dataset (all filtered out)
"""

with open('data_preparation_log.md', 'w', encoding='utf-8') as f:
    f.write(doc)
print("Created: data_preparation_log.md")

print()
print("="*80)
print("DATA PREPARATION COMPLETE")
print("="*80)
print()
print(f"Final dataset: {len(deal_df):,} deals (companies) ready for Stata analysis")
print()
print("Files created:")
print("  1. deal_level_analysis.csv")
print("  2. deal_level_analysis.dta (Stata format)")
print("  3. data_preparation_log.md (documentation)")
print()
print("Next steps:")
print("  1. Load deal_level_analysis.dta in Stata")
print("  2. Run descriptive statistics and balance checks")
print("  3. Estimate baseline model with reghdfe")
print("  4. Test heterogeneity specifications")
print("="*80)

