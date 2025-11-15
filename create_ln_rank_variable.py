import pandas as pd
import numpy as np

print("="*80)
print("CREATING ln(University_US_Rank) VARIABLE")
print("="*80)
print()

# Load the data
data = pd.read_stata('data_with_categories.dta')

print(f"Total observations: {len(data):,}")
print()

# Check current University_US_Rank
print("CURRENT University_US_Rank:")
print("-"*80)
print(f"Mean:     {data['University_US_Rank'].mean():.4f}")
print(f"Median:   {data['University_US_Rank'].median():.4f}")
print(f"Min:      {data['University_US_Rank'].min():.4f}")
print(f"Max:      {data['University_US_Rank'].max():.4f}")
print()

# Create ln(University_US_Rank)
data['ln_University_US_Rank'] = np.log(data['University_US_Rank'])

print("NEW ln_University_US_Rank:")
print("-"*80)
print(f"Mean:     {data['ln_University_US_Rank'].mean():.4f}")
print(f"Median:   {data['ln_University_US_Rank'].median():.4f}")
print(f"Min:      {data['ln_University_US_Rank'].min():.4f}")
print(f"Max:      {data['ln_University_US_Rank'].max():.4f}")
print()

print("INTERPRETATION GUIDE:")
print("-"*80)
print(f"ln(1) = {np.log(1):.4f}   <- Harvard/Stanford")
print(f"ln(5) = {np.log(5):.4f}   <- Top 5 schools")
print(f"ln(10) = {np.log(10):.4f}  <- Top 10 schools")
print(f"ln(20) = {np.log(20):.4f}  <- Top 20 schools")
print(f"ln(50) = {np.log(50):.4f}  <- Top 50 schools")
print(f"ln(100) = {np.log(100):.4f} <- Top 100 schools")
print()

# Save updated dataset
print("Saving updated dataset...")
data.to_stata('data_with_categories.dta', write_index=False, version=117)
print("[OK] Saved to: data_with_categories.dta")
print()

# Also save as CSV for inspection
data.to_csv('data_with_ln_rank.csv', index=False)
print("[OK] Saved to: data_with_ln_rank.csv")
print()

print("="*80)
print("COMPLETE!")
print("="*80)
print()
print("NEXT STEPS:")
print("1. Update .do files to use ln_University_US_Rank instead of University_US_Rank")
print("2. Re-run all analyses")
print("3. Interpret coefficient as: '1% increase in rank -> X% change in deal size'")

