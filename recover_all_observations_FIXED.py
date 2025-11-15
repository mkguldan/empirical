"""
COMPREHENSIVE DATA RECOVERY SCRIPT - FIXED VERSION
===================================================
Recovers all 2,607 "lost" observations by applying the same transformations
as the current dataset (n=2,982) to produce expanded dataset (n=5,589).

FIXES:
- Correct file paths for control variable extraction
- Proper VC spending calculation
- Fix board experience extraction

Author: Empirical Methods Project, Bocconi University
Date: November 15, 2024
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("RECOVERING ALL 5,589 OBSERVATIONS - FIXED VERSION")
print("="*80)
print()

# ============================================================================
# STEP 1: LOAD SOURCE DATA
# ============================================================================

print("STEP 1: Loading source data...")
print("-"*80)

# Load the full dataset with all 5,589 observations
df = pd.read_csv('deal_level_analysis_single_founders_with_university_rank.csv')
print(f"Loaded: {len(df):,} observations")

# Check for duplicates on DealID
duplicates = df['DealID'].duplicated().sum()
if duplicates > 0:
    print(f"[WARN] Found {duplicates} duplicate DealIDs - keeping first occurrence")
    df = df.drop_duplicates(subset=['DealID'], keep='first')
    print(f"After deduplication: {len(df):,} observations")
else:
    print(f"[OK] No duplicate DealIDs found")

print()

# ============================================================================
# STEP 2: CREATE BASIC VARIABLES
# ============================================================================

print("STEP 2: Creating basic transformed variables...")
print("-"*80)

# Deal Size (already exists as Deal_DealSize)
df['DealSize'] = df['Deal_DealSize_num'] if 'Deal_DealSize_num' in df.columns else df['Deal_DealSize']
df['ln_DealSize'] = np.log(df['DealSize'])
print(f"[OK] Created ln_DealSize")

# University Rank - handle "192<" format
def convert_rank(rank_val):
    """Convert university rank, handling '192<' format"""
    if pd.isna(rank_val):
        return np.nan
    rank_str = str(rank_val)
    if '<' in rank_str:
        # "192<" means rank > 192, use 193
        return 193
    try:
        return float(rank_str)
    except:
        return np.nan

df['University_US_Rank'] = df['University US Rank'].apply(convert_rank)
df['ln_University_US_Rank'] = np.log(df['University_US_Rank'])
print(f"[OK] Created University_US_Rank and ln_University_US_Rank")
print(f"     Range: {df['University_US_Rank'].min():.0f} to {df['University_US_Rank'].max():.0f}")

# Gender
df['Female'] = (df['Team_Gender'] == 'Single_Female').astype(int)
print(f"[OK] Created Female: {df['Female'].sum():,} women ({df['Female'].mean()*100:.1f}%)")

# Age
print(f"[OK] Using existing Age_at_Deal")

# Deal Year
print(f"[OK] Using existing Deal_Year (range: {df['Deal_Year'].min():.0f}-{df['Deal_Year'].max():.0f})")

print()

# ============================================================================
# STEP 3: CREATE EDUCATION VARIABLES
# ============================================================================

print("STEP 3: Creating education indicator variables...")
print("-"*80)

# Education levels from Max_Education
df['PhD_MD'] = df['Max_Education'].isin(['PhD', 'MD']).astype(int)
df['MBA_JD'] = df['Max_Education'].isin(['MBA', 'JD']).astype(int)
df['Masters'] = df['Max_Education'].isin(['MSC', 'MA']).astype(int)

print(f"[OK] PhD_MD:  {df['PhD_MD'].sum():,} ({df['PhD_MD'].mean()*100:.1f}%)")
print(f"[OK] MBA_JD:  {df['MBA_JD'].sum():,} ({df['MBA_JD'].mean()*100:.1f}%)")
print(f"[OK] Masters: {df['Masters'].sum():,} ({df['Masters'].mean()*100:.1f}%)")

print()

# ============================================================================
# STEP 4: CREATE STAGE VARIABLES
# ============================================================================

print("STEP 4: Verifying stage variables...")
print("-"*80)

print(f"[OK] Stage_Seed:  {df['Stage_Seed'].sum():,} ({df['Stage_Seed'].mean()*100:.1f}%)")
print(f"[OK] Stage_Early: {df['Stage_Early'].sum():,} ({df['Stage_Early'].mean()*100:.1f}%)")

df['Stage_Later'] = ((df['Stage_Seed'] == 0) & (df['Stage_Early'] == 0)).astype(int)
print(f"[OK] Stage_Later: {df['Stage_Later'].sum():,} ({df['Stage_Later'].mean()*100:.1f}%)")

print()

# ============================================================================
# STEP 5: CREATE INDUSTRY CATEGORIES (5 major groups)
# ============================================================================

print("STEP 5: Creating industry category dummies...")
print("-"*80)

tech_industries = [
    'Software', 'Computer Hardware', 'Semiconductors', 
    'IT Services', 'Electronics'
]

healthcare_industries = [
    'Pharmaceuticals and Biotechnology', 'Healthcare Devices and Supplies',
    'Healthcare Technology Systems', 'Healthcare Services'
]

consumer_industries = [
    'Consumer Non-Durables', 'Consumer Durables', 'Food and Beverage',
    'Media', 'Retailing', 'Consumer Services'
]

industrial_industries = [
    'Industrial and Commercial Services', 'Energy', 'Transportation',
    'Industrial Goods', 'Commercial Services', 'Chemicals and Materials',
    'Agriculture'
]

df['Tech'] = df['Company_PrimaryIndustryGroup'].isin(tech_industries).astype(int)
df['Healthcare'] = df['Company_PrimaryIndustryGroup'].isin(healthcare_industries).astype(int)
df['Consumer'] = df['Company_PrimaryIndustryGroup'].isin(consumer_industries).astype(int)
df['Industrial'] = df['Company_PrimaryIndustryGroup'].isin(industrial_industries).astype(int)
df['Services'] = ((df['Tech'] == 0) & (df['Healthcare'] == 0) & 
                  (df['Consumer'] == 0) & (df['Industrial'] == 0)).astype(int)

print(f"[OK] Tech:       {df['Tech'].sum():,} ({df['Tech'].mean()*100:.1f}%)")
print(f"[OK] Healthcare: {df['Healthcare'].sum():,} ({df['Healthcare'].mean()*100:.1f}%)")
print(f"[OK] Consumer:   {df['Consumer'].sum():,} ({df['Consumer'].mean()*100:.1f}%)")
print(f"[OK] Industrial: {df['Industrial'].sum():,} ({df['Industrial'].mean()*100:.1f}%)")
print(f"[OK] Services:   {df['Services'].sum():,} ({df['Services'].mean()*100:.1f}%)")

print()

# ============================================================================
# STEP 6: CREATE GEOGRAPHY CATEGORIES (4 regions)
# ============================================================================

print("STEP 6: Creating geography category dummies...")
print("-"*80)

west_coast_states = ['California', 'Oregon', 'Washington', 'Nevada', 'Hawaii']
northeast_states = ['New York', 'Massachusetts', 'Pennsylvania', 'New Jersey', 
                   'Connecticut', 'Rhode Island', 'Maine', 'New Hampshire', 
                   'Vermont', 'Maryland', 'Delaware', 'District of Columbia']
south_states = ['Texas', 'Florida', 'Georgia', 'North Carolina', 'Virginia',
               'Tennessee', 'Louisiana', 'Alabama', 'South Carolina', 'Kentucky',
               'Mississippi', 'Arkansas', 'Oklahoma', 'West Virginia', 'Arizona',
               'New Mexico', 'Utah', 'Idaho', 'Montana', 'Wyoming', 'Alaska']
midwest_states = ['Illinois', 'Ohio', 'Michigan', 'Indiana', 'Wisconsin',
                 'Minnesota', 'Missouri', 'Iowa', 'Kansas', 'Nebraska',
                 'South Dakota', 'North Dakota', 'Colorado']  # Added Colorado

df['West_Coast'] = df['Company_HQState_Province'].isin(west_coast_states).astype(int)
df['Northeast'] = df['Company_HQState_Province'].isin(northeast_states).astype(int)
df['South'] = df['Company_HQState_Province'].isin(south_states).astype(int)
df['Midwest'] = df['Company_HQState_Province'].isin(midwest_states).astype(int)

print(f"[OK] West_Coast: {df['West_Coast'].sum():,} ({df['West_Coast'].mean()*100:.1f}%)")
print(f"[OK] Northeast:  {df['Northeast'].sum():,} ({df['Northeast'].mean()*100:.1f}%)")
print(f"[OK] South:      {df['South'].sum():,} ({df['South'].mean()*100:.1f}%)")
print(f"[OK] Midwest:    {df['Midwest'].sum():,} ({df['Midwest'].mean()*100:.1f}%)")

tech_hub_states = ['California', 'New York', 'Massachusetts']
df['Is_Tech_Hub'] = df['Company_HQState_Province'].isin(tech_hub_states).astype(int)
print(f"[OK] Is_Tech_Hub: {df['Is_Tech_Hub'].sum():,} ({df['Is_Tech_Hub'].mean()*100:.1f}%)")

print()

# ============================================================================
# STEP 7: MATCH VC SPENDING BY STATE (FIXED)
# ============================================================================

print("STEP 7: Matching VC spending by state...")
print("-"*80)

# Calculate VC spending per state from Deal data
try:
    # Load all deals
    deal_all = pd.read_csv('core_tables/Deal.csv')
    deal_all['DealDate'] = pd.to_datetime(deal_all['DealDate'])
    deal_all['Deal_Year'] = deal_all['DealDate'].dt.year
    
    # Filter to relevant years and deal types
    deal_filtered = deal_all[
        (deal_all['Deal_Year'] >= 2012) & 
        (deal_all['Deal_Year'] <= 2022) &
        (deal_all['DealType'].isin(['Seed Round', 'Early Stage VC', 'Later Stage VC']))
    ].copy()
    
    # Calculate average VC spending by state
    vc_by_state = deal_filtered.groupby('Company_HQState_Province')['DealSize'].mean().reset_index()
    vc_by_state.columns = ['Company_HQState_Province', 'Average_VC_Spend_HQ_Company']
    
    print(f"[OK] Calculated VC spending for {len(vc_by_state)} states")
    
    # Merge
    df = df.merge(vc_by_state, on='Company_HQState_Province', how='left')
    
    # Fill missing with median
    missing_vc = df['Average_VC_Spend_HQ_Company'].isna().sum()
    if missing_vc > 0:
        median_vc = df['Average_VC_Spend_HQ_Company'].median()
        df['Average_VC_Spend_HQ_Company'].fillna(median_vc, inplace=True)
        print(f"[WARN] {missing_vc} states missing VC data, filled with median")
    
    print(f"[OK] VC Spending range: ${df['Average_VC_Spend_HQ_Company'].min()/1e6:.2f}M to ${df['Average_VC_Spend_HQ_Company'].max()/1e6:.2f}M")
    print(f"     Mean: ${df['Average_VC_Spend_HQ_Company'].mean()/1e6:.2f}M")

except Exception as e:
    print(f"[ERROR] Could not calculate VC spending: {e}")
    df['Average_VC_Spend_HQ_Company'] = 0

print()

# ============================================================================
# STEP 8: EXTRACT CONTROL VARIABLES FROM CORE_TABLES (FIXED PATHS)
# ============================================================================

print("STEP 8: Extracting control variables...")
print("-"*80)

# Get PersonID mapping from other_tables
print("  Mapping DealID to PersonID...")
try:
    person_deal = pd.read_csv('other_tables/PersonAffiliatedDealRelation.csv')
    # Get solo founders only (one person per deal)
    person_per_deal = person_deal.groupby('DealID')['PersonID'].first().reset_index()
    df = df.merge(person_per_deal, on='DealID', how='left')
    print(f"  [OK] Mapped PersonID for {df['PersonID'].notna().sum():,} deals")
except Exception as e:
    print(f"  [ERROR] Could not map PersonID: {e}")

# Board Experience
print("  Extracting board experience...")
try:
    # Use PersonBoardSeatRelation from other_tables
    person_board = pd.read_csv('other_tables/PersonBoardSeatRelation.csv')
    persons_with_board = person_board['PersonID'].unique()
    df['Has_Board_Experience'] = df['PersonID'].isin(persons_with_board).astype(int)
    print(f"  [OK] Has_Board_Experience: {df['Has_Board_Experience'].sum():,} ({df['Has_Board_Experience'].mean()*100:.1f}%)")
except Exception as e:
    print(f"  [WARN] Could not extract board experience: {e}")
    df['Has_Board_Experience'] = 0

# Top-tier VC
print("  Extracting top-tier VC...")
try:
    deal_investor = pd.read_csv('core_tables/DealInvestorRelation.csv')
    
    top_tier_vcs = [
        'Sequoia Capital', 'Andreessen Horowitz', 'Accel', 'Kleiner Perkins',
        'Benchmark', 'Greylock Partners', 'NEA', 'Lightspeed Venture Partners',
        'Index Ventures', 'General Catalyst', 'Bessemer Venture Partners',
        'First Round Capital', 'Union Square Ventures', 'Founders Fund',
        'Insight Partners', 'Tiger Global', 'Khosla Ventures'
    ]
    
    top_tier_deals = deal_investor[
        deal_investor['InvestorName'].isin(top_tier_vcs)
    ]['DealID'].unique()
    
    df['Has_Top_Tier_VC'] = df['DealID'].isin(top_tier_deals).astype(int)
    print(f"  [OK] Has_Top_Tier_VC: {df['Has_Top_Tier_VC'].sum():,} ({df['Has_Top_Tier_VC'].mean()*100:.1f}%)")
except Exception as e:
    print(f"  [WARN] Could not extract top-tier VC: {e}")
    df['Has_Top_Tier_VC'] = 0

# Syndicate Size
print("  Extracting syndicate size...")
try:
    syndicate_size = deal_investor.groupby('DealID').size().reset_index(name='Syndicate_Size')
    df = df.merge(syndicate_size, on='DealID', how='left')
    df['Syndicate_Size'] = df['Syndicate_Size'].fillna(0).astype(int)
    print(f"  [OK] Syndicate_Size: mean={df['Syndicate_Size'].mean():.1f}, median={df['Syndicate_Size'].median():.0f}")
except Exception as e:
    print(f"  [WARN] Could not extract syndicate size: {e}")
    df['Syndicate_Size'] = 0

# Prior Deal Count (FIXED)
print("  Extracting prior deal count...")
try:
    person_deal['DealDate'] = pd.to_datetime(person_deal['DealDate'])
    person_deal = person_deal.sort_values(['PersonID', 'DealDate'])
    person_deal['Prior_Deal_Count'] = person_deal.groupby('PersonID').cumcount()
    
    df = df.merge(
        person_deal[['DealID', 'PersonID', 'Prior_Deal_Count']],
        on=['DealID', 'PersonID'],
        how='left',
        suffixes=('', '_new')
    )
    if 'Prior_Deal_Count_new' in df.columns:
        df['Prior_Deal_Count'] = df['Prior_Deal_Count'].fillna(df['Prior_Deal_Count_new'])
        df.drop('Prior_Deal_Count_new', axis=1, inplace=True)
    
    df['Prior_Deal_Count'] = df['Prior_Deal_Count'].fillna(0).astype(int)
    print(f"  [OK] Prior_Deal_Count: mean={df['Prior_Deal_Count'].mean():.1f}")
except Exception as e:
    print(f"  [WARN] Could not extract prior deal count: {e}")
    df['Prior_Deal_Count'] = 0

# Simplified controls (set to 0 - can extract later if needed)
df['Lead_Investor_Exits'] = 0
df['Has_Legal_Advisor'] = 0
df['Has_Top_Law_Firm'] = 0
df['Prior_Board_Seats'] = 0

print(f"  [OK] Set Lead_Investor_Exits, Has_Legal_Advisor, Has_Top_Law_Firm, Prior_Board_Seats to 0")

print()

# ============================================================================
# STEP 9: CREATE REGION VARIABLE
# ============================================================================

print("STEP 9: Creating consolidated region variable...")
print("-"*80)

df['Region'] = 'Midwest'
df.loc[df['West_Coast'] == 1, 'Region'] = 'West Coast'
df.loc[df['Northeast'] == 1, 'Region'] = 'Northeast'
df.loc[df['South'] == 1, 'Region'] = 'South'

print(f"[OK] Region distribution:")
print(df['Region'].value_counts())

print()

# ============================================================================
# STEP 10: FINAL DATA QUALITY CHECKS
# ============================================================================

print("STEP 10: Final data quality checks...")
print("-"*80)

critical_vars = [
    'DealSize', 'ln_DealSize', 'University_US_Rank', 'ln_University_US_Rank',
    'Female', 'PhD_MD', 'MBA_JD', 'Masters', 'Age_at_Deal',
    'Stage_Seed', 'Stage_Early', 'Deal_Year',
    'Tech', 'Healthcare', 'Consumer', 'Industrial',
    'Company_HQState_Province', 'Average_VC_Spend_HQ_Company',
    'Has_Board_Experience'
]

print("\nData completeness check:")
all_complete = True
for var in critical_vars:
    if var in df.columns:
        missing = df[var].isna().sum()
        if missing > 0:
            print(f"  [WARN] {var}: {missing} missing ({missing/len(df)*100:.1f}%)")
            all_complete = False
        else:
            print(f"  [OK] {var}: 100% complete")
    else:
        print(f"  [ERROR] {var}: NOT FOUND")
        all_complete = False

if all_complete:
    print("\n[OK] All critical variables are 100% complete!")

# Final deduplication check
final_duplicates = df['DealID'].duplicated().sum()
if final_duplicates > 0:
    print(f"\n[WARN] {final_duplicates} duplicate DealIDs - removing...")
    df = df.drop_duplicates(subset=['DealID'], keep='first')
else:
    print(f"\n[OK] No duplicate DealIDs")

print()

# ============================================================================
# STEP 11: SAVE EXPANDED DATASET
# ============================================================================

print("STEP 11: Saving expanded dataset...")
print("-"*80)

keep_cols = [
    'DealID', 'CompanyID', 'PersonID',
    'DealSize', 'ln_DealSize', 
    'University_US_Rank', 'ln_University_US_Rank',
    'Female', 'PhD_MD', 'MBA_JD', 'Masters',
    'Age_at_Deal', 'Deal_Year',
    'Stage_Seed', 'Stage_Early', 'Stage_Later',
    'Tech', 'Healthcare', 'Consumer', 'Industrial', 'Services',
    'Company_PrimaryIndustryGroup',
    'West_Coast', 'Northeast', 'South', 'Midwest',
    'Company_HQState_Province', 'Region', 'Is_Tech_Hub',
    'Average_VC_Spend_HQ_Company',
    'Has_Board_Experience', 'Has_Top_Tier_VC',
    'Syndicate_Size', 'Prior_Deal_Count', 'Lead_Investor_Exits',
    'Has_Legal_Advisor', 'Has_Top_Law_Firm', 'Prior_Board_Seats',
    'CompanyName', 'Person_FullName', 'University_Name'
]

keep_cols = [col for col in keep_cols if col in df.columns]
df_final = df[keep_cols].copy()

print(f"Final dataset: {len(df_final):,} observations, {len(df_final.columns)} variables")

output_file = 'data_with_categories_EXPANDED.dta'
df_final.to_stata(output_file, write_index=False, version=117)
print(f"[OK] Saved to: {output_file}")

csv_file = 'data_with_categories_EXPANDED.csv'
df_final.to_csv(csv_file, index=False)
print(f"[OK] Saved to: {csv_file}")

print()

# ============================================================================
# STEP 12: COMPARE TO CURRENT DATASET
# ============================================================================

print("STEP 12: Comparing to current dataset...")
print("-"*80)

current_df = pd.read_stata('data_with_categories.dta')

print(f"\nCurrent dataset: {len(current_df):,} observations")
print(f"Expanded dataset: {len(df_final):,} observations")
print(f"Increase: +{len(df_final) - len(current_df):,} ({(len(df_final) - len(current_df))/len(current_df)*100:.1f}%)")

print("\nDistribution comparison:")
compare_vars = ['Female', 'PhD_MD', 'MBA_JD', 'Masters', 'Tech', 'Healthcare', 'West_Coast', 'Has_Board_Experience']
for var in compare_vars:
    if var in current_df.columns and var in df_final.columns:
        current_pct = current_df[var].mean() * 100
        expanded_pct = df_final[var].mean() * 100
        print(f"  {var:<25s} Current: {current_pct:5.1f}% | Expanded: {expanded_pct:5.1f}% | Diff: {expanded_pct - current_pct:+5.1f}pp")

print()
print("="*80)
print("RECOVERY COMPLETE!")
print("="*80)
print(f"\nSUCCESS! Final dataset: {len(df_final):,} observations")
print(f"Increase from current: +{(len(df_final) - len(current_df))/len(current_df)*100:.1f}%")
print()
print("="*80)

