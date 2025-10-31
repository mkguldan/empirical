"""
Quick preview of the master file with sample records
"""
import pandas as pd

print("=" * 100)
print("MASTER FILE PREVIEW")
print("=" * 100)

# Load a sample
master_file = r'G:\School\BOCCONI\1st semester\empirical\master_file.csv'
print("\nLoading first 1000 rows...")
df = pd.read_csv(master_file, nrows=1000, low_memory=False)

print(f"\nDataset Info:")
print(f"  Shape: {df.shape}")
print(f"  Columns: {df.shape[1]}")
print(f"  Sample rows: {df.shape[0]}")

print("\n" + "=" * 100)
print("COLUMN LIST (60 columns)")
print("=" * 100)
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col}")

print("\n" + "=" * 100)
print("SAMPLE RECORD #1: Complete Company-Deal-Investor-Person Record")
print("=" * 100)

# Find a row with all IDs populated
complete_row = df[(df['CompanyID'].notna()) & 
                  (df['DealID'].notna()) & 
                  (df['InvestorID'].notna()) & 
                  (df['PersonID'].notna())].iloc[0]

print("\nCOMPANY INFORMATION:")
print(f"  CompanyID:         {complete_row['CompanyID']}")
print(f"  CompanyName:       {complete_row['CompanyName']}")
print(f"  HQ Country:        {complete_row['Company_HQCountry']}")
print(f"  HQ City:           {complete_row['Company_HQCity']}")
print(f"  Industry Sector:   {complete_row['Company_PrimaryIndustrySector']}")
print(f"  Year Founded:      {complete_row['Company_YearFounded']}")
print(f"  Financing Status:  {complete_row['Company_CompanyFinancingStatus']}")

print("\nDEAL INFORMATION:")
print(f"  DealID:            {complete_row['DealID']}")
print(f"  Deal Date:         {complete_row['Deal_DealDate']}")
print(f"  Deal Type:         {complete_row['Deal_DealType']}")
print(f"  Deal Size:         {complete_row['Deal_DealSize']}")
print(f"  Deal Status:       {complete_row['Deal_DealStatus']}")
print(f"  VC Round:          {complete_row['Deal_VCRound']}")

print("\nINVESTOR INFORMATION:")
print(f"  InvestorID:        {complete_row['InvestorID']}")
print(f"  Investor Deal Type: {complete_row['Investor_DealType']}")
print(f"  Investor Deal Size: {complete_row['Investor_DealSize']}")

print("\nPERSON INFORMATION:")
print(f"  PersonID:          {complete_row['PersonID']}")
print(f"  Full Name:         {complete_row['Person_FullName']}")
print(f"  Primary Company:   {complete_row['Person_PrimaryCompany']}")
print(f"  Position:          {complete_row['Person_PrimaryPosition']}")
print(f"  Gender:            {complete_row['Person_Gender']}")
print(f"  Location:          {complete_row['Person_Location']}")

if pd.notna(complete_row['Education_Degree']):
    print("\nEDUCATION INFORMATION:")
    print(f"  Degree:            {complete_row['Education_Degree']}")
    print(f"  Major:             {complete_row['Education_Major_Concentration']}")
    print(f"  Institute:         {complete_row['Education_Institute']}")
    print(f"  Graduating Year:   {complete_row['Education_GraduatingYear']}")

print("\n" + "=" * 100)
print("BASIC STATISTICS (from first 1000 rows)")
print("=" * 100)

print("\nData Availability:")
print(f"  Rows with all 4 IDs (Company, Deal, Investor, Person): {len(df[(df['CompanyID'].notna()) & (df['DealID'].notna()) & (df['InvestorID'].notna()) & (df['PersonID'].notna())])}")
print(f"  Rows with Company & Deal:                              {len(df[(df['CompanyID'].notna()) & (df['DealID'].notna())])}")
print(f"  Rows with Company, Deal & Investor:                    {len(df[(df['CompanyID'].notna()) & (df['DealID'].notna()) & (df['InvestorID'].notna())])}")

print("\nTop 10 Industries (where available):")
if df['Company_PrimaryIndustrySector'].notna().sum() > 0:
    industry_counts = df['Company_PrimaryIndustrySector'].value_counts().head(10)
    for industry, count in industry_counts.items():
        print(f"  {industry:40s} : {count:3d}")

print("\nTop 10 Deal Types (where available):")
if df['Deal_DealType'].notna().sum() > 0:
    deal_type_counts = df['Deal_DealType'].value_counts().head(10)
    for deal_type, count in deal_type_counts.items():
        print(f"  {deal_type:40s} : {count:3d}")

print("\n" + "=" * 100)
print("FILE READY FOR ANALYSIS")
print("=" * 100)
print(f"\nFile location: {master_file}")
print("You can now use this file in Excel, Python, R, or any other data analysis tool.")
print("\nSuggested next steps:")
print("  1. Open in Excel (if file size allows) or use Python/R for analysis")
print("  2. Filter by CompanyID to analyze specific companies")
print("  3. Group by DealID to analyze deals")
print("  4. Use PersonID to track individuals across companies")
print("  5. Join additional data using the ID fields")
print("=" * 100)


