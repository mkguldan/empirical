"""
Script to examine unique Education_Degree values
"""
import pandas as pd

# Load the file
input_file = r'G:\School\BOCCONI\1st semester\empirical\founder_vc_cleaned.csv'
print(f"Loading file: {input_file}")

# Try different delimiters
df = None
for delimiter in [';', ',', '\t']:
    try:
        df = pd.read_csv(input_file, low_memory=False, sep=delimiter)
        if len(df.columns) > 5:  # Valid file should have many columns
            print(f"Successfully loaded with '{delimiter}' delimiter")
            break
    except:
        continue

if df is None:
    print("ERROR: Could not load file")
    exit(1)

print(f"Loaded {len(df):,} rows")

# Get unique Education_Degree values
if 'Education_Degree' in df.columns:
    unique_degrees = df['Education_Degree'].dropna().unique()
    print(f"\nFound {len(unique_degrees)} unique degree values:")
    print("=" * 80)
    
    # Sort and display
    for degree in sorted(unique_degrees):
        count = (df['Education_Degree'] == degree).sum()
        print(f"{degree:60s} : {count:5d}")
    
    # Show value counts
    print("\n" + "=" * 80)
    print("Top 20 most common degrees:")
    print("=" * 80)
    degree_counts = df['Education_Degree'].value_counts().head(20)
    for degree, count in degree_counts.items():
        print(f"{degree:60s} : {count:5d}")
else:
    print("ERROR: Education_Degree column not found!")
    print(f"Available columns: {list(df.columns)}")




