"""
Script to categorize education degrees and format deal size as US currency
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

print("=" * 100)
print("CATEGORIZING EDUCATION DEGREES AND FORMATTING CURRENCY")
print("=" * 100)
print(f"Started at: {datetime.now()}")

# File paths
input_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_cleaned.csv'
output_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_final_formatted.csv'

print("\n" + "=" * 100)
print("STEP 1: Loading file...")
print("=" * 100)

# Load with delimiter detection
df = None
for delimiter in [';', ',', '\t']:
    try:
        delimiter_name = {';': 'semicolon', ',': 'comma', '\t': 'tab'}[delimiter]
        print(f"  Trying {delimiter_name} delimiter...")
        df = pd.read_csv(input_file, low_memory=False, sep=delimiter)
        if len(df.columns) > 5:  # Valid file should have many columns
            print(f"  Success with {delimiter_name} delimiter!")
            break
    except:
        continue

if df is None:
    print("ERROR: Could not load file")
    exit(1)

print(f"Loaded {len(df):,} rows with {len(df.columns)} columns")

print("\n" + "=" * 100)
print("STEP 2: Examining Education_Degree values...")
print("=" * 100)

if 'Education_Degree' not in df.columns:
    print("ERROR: Education_Degree column not found!")
    exit(1)

unique_degrees = df['Education_Degree'].dropna().unique()
print(f"Found {len(unique_degrees)} unique degree values")

# Show top degree types
print("\nTop 15 most common degrees:")
degree_counts = df['Education_Degree'].value_counts().head(15)
for degree, count in degree_counts.items():
    print(f"  {degree:50s} : {count:5d}")

print("\n" + "=" * 100)
print("STEP 3: Creating degree categorization logic...")
print("=" * 100)

def categorize_degree(degree_value):
    """
    Categorize degree into: ASC, BSC, MSC, JD, PHD, MBA, CHA
    Conservative approach - when unclear, use Other
    
    Categories:
    - ASC: Associate degrees or equivalent
    - BSC: Bachelor's degrees or equivalent
    - MSC: Master's degrees or equivalent (excluding MBA and JD)
    - JD: Juris Doctor degrees
    - PHD: Doctoral or PhD degrees
    - MBA: Master of Business Administration degrees
    - CHA: Chartered/Certified professional accountant and analyst certifications
    - Other: Everything else
    """
    if pd.isna(degree_value) or degree_value == '' or str(degree_value).strip() == '':
        return 'Other'
    
    degree_str = str(degree_value).strip().lower()
    
    # If it just says "degree" or vague terms, put in Other
    if degree_str in ['degree', 'graduate', 'major', 'minor', 'undergraduate studies']:
        return 'Other'
    
    # CHA: Chartered/Certified professional accountant and analyst certifications
    # Check for CPA, CFA, CA, Chartered Accountant, etc.
    cha_patterns = [
        'cpa', 'c.p.a', 'certified public accountant',
        'cfa', 'c.f.a', 'chartered financial analyst',
        'chartered accountant', 'ca ', ' ca', 'c.a',
        'cma', 'c.m.a', 'certified management accountant',
        'acca', 'chartered certified accountant'
    ]
    for pattern in cha_patterns:
        if pattern in degree_str:
            return 'CHA'
    
    # MBA: Master of Business Administration (check BEFORE general masters)
    # This is critical - MBA must be checked before MSC
    mba_patterns = [
        'mba', 'm.b.a', 'master of business administration',
        'emba', 'e.m.b.a', 'executive mba'
    ]
    for pattern in mba_patterns:
        if pattern in degree_str:
            return 'MBA'
    
    # JD: Juris Doctor (check BEFORE PhDs)
    jd_patterns = [
        'jd', 'j.d', 'juris doctor', 'doctor of law',
        'jd/mba', 'mba/jd'
    ]
    for pattern in jd_patterns:
        if pattern in degree_str:
            return 'JD'
    
    # PHD: Doctoral or PhD degrees
    phd_patterns = [
        'ph.d', 'phd', 'ph. d', 'doctor of philosophy',
        'doctorate', 'doctoral', 'dphil', 'd.phil',
        'md/phd', 'phd/md',
        'doctor of science', 'dsc', 'd.sc', 'ds (doctor',
        'doctor of medicine', 'md (doctor', 'm.d (doctor',
        'doctor of dental', 'dds', 'd.d.s', 'dmd', 'd.m.d',
        'doctor of pharmacy', 'pharm.d', 'pharmd',
        'doctor of veterinary', 'dvm', 'd.v.m',
        'ded (doctor', 'ed.d', 'doctor of education',
        'psyd', 'psy.d', 'doctor of psychology',
        'postdoc', 'post doc', 'post-doc', 'postdoctoral',
        'post doctoral', 'post-doctoral', 'post graduate studies',
        'honorary doctorate', 'mbbs'
    ]
    for pattern in phd_patterns:
        if pattern in degree_str:
            return 'PHD'
    
    # MSC: Master's degrees (excluding MBA and JD, which were already checked)
    msc_patterns = [
        'master', 'masters', "master's",
        'msc', 'm.sc', 'ms (master', 'm.s (master',
        'ma (master', 'm.a (master',
        'me (master', 'm.eng', 'master of engineering',
        'mem ', 'm.e.m', 'master of engineering management',
        'mfa', 'm.f.a', 'master of fine arts',
        'mpa', 'm.p.a', 'master of public',
        'mpp', 'm.p.p', 'master of public policy',
        'mph', 'm.p.h', 'master of public health',
        'mps', 'm.p.s', 'master of professional studies',
        'msw', 'm.s.w', 'master of social work',
        'med ', 'm.ed', 'master of education',
        'mdes', 'm.des', 'master of design',
        'mas (master', 'm.a.s (master',
        'mj (master', 'master of jurisprudence',
        'llm', 'll.m', 'master of law',
        'm.phil', 'master of philosophy',
        'm.tech', 'master of technology',
        'integrated masters', 'postgraduate degree',
        'post graduate diploma', 'pgdm'
    ]
    for pattern in msc_patterns:
        if pattern in degree_str:
            return 'MSC'
    
    # BSC: Bachelor's degrees or equivalent
    bsc_patterns = [
        'bachelor', 'bachelors', "bachelor's",
        'ba (bachelor', 'b.a (bachelor',
        'bs (bachelor', 'b.s (bachelor', 'bsc ',
        'bba', 'b.b.a', 'bachelor of business',
        'be (bachelor', 'b.e (bachelor', 'be/bs',
        'b.tech', 'bachelor of technology', 'btech',
        'bfa', 'b.f.a', 'bachelor of fine arts',
        'b.comm', 'bachelor of commerce', 'bcomm',
        'llb', 'll.b', 'bachelor of law',
        'bdes', 'b.des', 'bachelor of design',
        'bas (bachelor', 'b.a.s (bachelor',
        'bsbe', 'bsfs',
        'dual b.s', 'dual-degree', 'sb & sm',
        'engineering diploma', 'business management diploma',
        'honors business administration', 'honors degree',
        'graduated cum laude'
    ]
    for pattern in bsc_patterns:
        if pattern in degree_str:
            return 'BSC'
    
    # ASC: Associate degrees or equivalent
    asc_patterns = [
        'aa (associate', 'a.a (associate',
        'as (associate', 'a.s (associate',
        'aas (associate', 'a.a.s (associate',
        'associate degree', 'associate of'
    ]
    for pattern in asc_patterns:
        if pattern in degree_str:
            return 'ASC'
    
    # Catch-all for vague qualifications  
    # Check for standalone "diploma" (not part of a degree name like "engineering diploma")
    if degree_str == 'diploma' or any(term in degree_str for term in ['certificate', 'fellowship', 'amp', ' cs', 'dea,', 'graduate engineer']):
        return 'Other'
    
    # If nothing matches, return Other
    return 'Other'

print("Degree categorization logic created with patterns for:")
print("  - ASC: Associate degrees (AA, AS, AAS, Associate Degree)")
print("  - BSC: Bachelor's degrees (BA, BS, BBA, BE, B.Tech, BFA, etc.)")
print("  - MSC: Master's degrees (MS, MA, ME, MFA, MPA, MPP, LLM, etc.) - excludes MBA")
print("  - JD: Juris Doctor degrees (JD, Doctor of Law)")
print("  - PHD: Doctoral degrees (PhD, MD, DDS, DVM, EdD, PsyD, Postdoc, etc.)")
print("  - MBA: Master of Business Administration (MBA, EMBA)")
print("  - CHA: Chartered/Certified certifications (CPA, CFA, CA, CMA, ACCA)")
print("  - Other: Everything else (including vague terms like 'Degree', 'Graduate')")

print("\n" + "=" * 100)
print("STEP 4: Applying categorization...")
print("=" * 100)

# Apply categorization
df['Education_Category'] = df['Education_Degree'].apply(categorize_degree)

# Show distribution
print("\nEducation Category Distribution:")
category_counts = df['Education_Category'].value_counts()
for category, count in category_counts.items():
    percentage = count / len(df) * 100
    print(f"  {category:15s} : {count:6,} ({percentage:5.2f}%)")

# Show some examples of categorization
print("\nSample categorizations:")
sample_df = df[['Education_Degree', 'Education_Category']].drop_duplicates().head(20)
for idx, row in sample_df.iterrows():
    print(f"  {str(row['Education_Degree']):50s} -> {row['Education_Category']}")

print("\n" + "=" * 100)
print("STEP 5: Formatting Deal_DealSize as US currency...")
print("=" * 100)

if 'Deal_DealSize' not in df.columns:
    print("WARNING: Deal_DealSize column not found!")
    print(f"Available columns with 'Deal' or 'Size': {[col for col in df.columns if 'deal' in col.lower() or 'size' in col.lower()]}")
else:
    def format_as_currency(value):
        """
        Format value as US currency
        Values are in millions of USD
        """
        if pd.isna(value) or value == '':
            return ''
        
        try:
            # Convert to float
            if isinstance(value, str):
                # Remove any existing currency symbols or commas
                value = value.replace('$', '').replace(',', '').strip()
            
            num_value = float(value)
            
            # Value is in millions, so multiply by 1,000,000
            actual_value = num_value * 1_000_000
            
            # Format as currency
            return f"${actual_value:,.2f}"
        except:
            return str(value)
    
    print("Formatting Deal_DealSize values...")
    print(f"  Non-null values before: {df['Deal_DealSize'].notna().sum():,}")
    
    # Show some before values
    sample_before = df['Deal_DealSize'].dropna().head(5).tolist()
    print(f"  Sample before: {sample_before}")
    
    # Apply formatting
    df['Deal_DealSize'] = df['Deal_DealSize'].apply(format_as_currency)
    
    # Show some after values
    sample_after = df['Deal_DealSize'].replace('', pd.NA).dropna().head(5).tolist()
    print(f"  Sample after: {sample_after}")
    print(f"  Non-empty values after: {(df['Deal_DealSize'] != '').sum():,}")

# Also format Investor_DealSize if it exists
if 'Investor_DealSize' in df.columns:
    print("\nFormatting Investor_DealSize values...")
    print(f"  Non-null values before: {df['Investor_DealSize'].notna().sum():,}")
    df['Investor_DealSize'] = df['Investor_DealSize'].apply(format_as_currency)
    sample_after = df['Investor_DealSize'].replace('', pd.NA).dropna().head(5).tolist()
    print(f"  Sample after: {sample_after}")

print("\n" + "=" * 100)
print("STEP 6: Saving formatted file...")
print("=" * 100)

# Save the file
print(f"Saving to: {output_file}")
df.to_csv(output_file, index=False, encoding='utf-8-sig', sep=',')
file_size_mb = os.path.getsize(output_file) / (1024**2)
print(f"File saved successfully!")
print(f"  File size: {file_size_mb:.2f} MB")
print(f"  Total rows: {len(df):,}")
print(f"  Total columns: {len(df.columns)}")

print("\n" + "=" * 100)
print("STEP 7: Summary statistics...")
print("=" * 100)

# Create summary
summary_stats = {
    'Education Category': list(category_counts.index),
    'Count': [f"{c:,}" for c in category_counts.values],
    'Percentage': [f"{c/len(df)*100:.2f}%" for c in category_counts.values]
}

summary_df = pd.DataFrame(summary_stats)
print("\nEducation Category Summary:")
print(summary_df.to_string(index=False))

# Save summary
summary_file = r'G:\School\BOCCONI\1st semester\empirical\education_category_summary.csv'
summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig', sep=',')
print(f"\nSummary saved to: {summary_file}")

print("\n" + "=" * 100)
print("SAMPLE RECORDS")
print("=" * 100)

print("\nFirst 5 records showing new columns:")
sample_cols = ['Person_FullName', 'Education_Degree', 'Education_Category', 
               'Deal_DealSize', 'CompanyName']
available_sample_cols = [col for col in sample_cols if col in df.columns]

if len(df) > 0:
    print(df[available_sample_cols].head(5).to_string(index=False))

print("\n" + "=" * 100)
print("PROCESS COMPLETED SUCCESSFULLY")
print("=" * 100)
print(f"Completed at: {datetime.now()}")
print(f"\nFinal output file: {output_file}")
print(f"Summary file: {summary_file}")
print("\nNew additions to the dataset:")
print("  - Education_Category: Categorized degrees (ASC/BSC/MSC/JD/PHD/MBA/CHA/Other)")
print("  - Deal_DealSize: Formatted as US currency (values in millions converted to dollars)")
print("\nCategory descriptions:")
print("  - ASC: Associate degrees or equivalent")
print("  - BSC: Bachelor's degrees or equivalent")
print("  - MSC: Master's degrees (excluding MBA and JD)")
print("  - JD: Juris Doctor degrees")
print("  - PHD: Doctoral or PhD degrees")
print("  - MBA: Master of Business Administration")
print("  - CHA: Chartered/Certified professional certifications")
print("  - Other: Vague or unclassifiable degrees")
print("=" * 100)

