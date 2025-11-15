import pandas as pd
import numpy as np

print("="*80)
print("STAGE DISTRIBUTION IN DATASET")
print("="*80)
print()

# Load the data
data = pd.read_stata('data_with_categories.dta')

print(f"Total observations: {len(data):,}")
print()

# Check Stage variables
print("STAGE DISTRIBUTION:")
print("-"*80)

seed_count = data['Stage_Seed'].sum()
early_count = data['Stage_Early'].sum()

# Later is neither Seed nor Early
later_count = len(data[(data['Stage_Seed'] == 0) & (data['Stage_Early'] == 0)])

total_staged = seed_count + early_count + later_count

print(f"Seed Round (Stage_Seed=1):       {seed_count:>6,} ({seed_count/len(data)*100:>5.1f}%)")
print(f"Early Stage VC (Stage_Early=1):  {early_count:>6,} ({early_count/len(data)*100:>5.1f}%)")
print(f"Later Stage VC (Stage_Later):    {later_count:>6,} ({later_count/len(data)*100:>5.1f}%)")
print("-"*80)
print(f"Total:                           {total_staged:>6,} ({total_staged/len(data)*100:>5.1f}%)")
print()

# Check if there are any missing/other categories
other = len(data) - total_staged
if other > 0:
    print(f"[WARNING] {other:,} observations don't fit any stage category")
print()

print("="*80)
print("COMPLETE!")
print("="*80)

