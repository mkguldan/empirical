import pandas as pd
import numpy as np

print("="*80)
print("CHECKING UNIVERSITY_US_RANK VALUES")
print("="*80)
print()

# Load the data
data = pd.read_stata('data_with_categories.dta')

print(f"Total observations: {len(data):,}")
print()

# Check University_US_Rank values
print("UNIVERSITY_US_RANK STATISTICS:")
print("-"*80)
print(f"Mean:     {data['University_US_Rank'].mean():.4f}")
print(f"Median:   {data['University_US_Rank'].median():.4f}")
print(f"Min:      {data['University_US_Rank'].min():.4f}")
print(f"Max:      {data['University_US_Rank'].max():.4f}")
print(f"Std Dev:  {data['University_US_Rank'].std():.4f}")
print()

print("SAMPLE VALUES (first 20 observations):")
print("-"*80)
print(data['University_US_Rank'].head(20).values)
print()

print("DISTRIBUTION:")
print("-"*80)
print(data['University_US_Rank'].describe())
print()

# Check if these look like raw ranks (1-200) or logged ranks
print("INTERPRETATION:")
print("-"*80)
if data['University_US_Rank'].max() > 10:
    print("[OK] Values appear to be RAW RANKS (e.g., 1, 2, 3, ..., 200)")
    print("    These are NOT in ln format")
    print("    ln(1) = 0.00, ln(10) = 2.30, ln(100) = 4.61, ln(200) = 5.30")
elif data['University_US_Rank'].max() <= 6:
    print("[OK] Values appear to be LOGGED RANKS (ln format)")
    print("    ln(1) = 0.00, ln(10) = 2.30, ln(100) = 4.61, ln(200) = 5.30")
    print("    These ARE already in ln format!")
    print()
    print("REVERSE CALCULATION (what are the actual ranks?):")
    print(f"    Min ln value {data['University_US_Rank'].min():.4f} = Rank {np.exp(data['University_US_Rank'].min()):.1f}")
    print(f"    Max ln value {data['University_US_Rank'].max():.4f} = Rank {np.exp(data['University_US_Rank'].max()):.1f}")
    print(f"    Mean ln value {data['University_US_Rank'].mean():.4f} = Rank {np.exp(data['University_US_Rank'].mean()):.1f}")

print()
print("="*80)

