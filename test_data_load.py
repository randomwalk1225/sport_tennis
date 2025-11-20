"""
Test data loading for extended years
"""

from data_manager import TennisDataManager
import sys

manager = TennisDataManager()

print("Testing data load for 2000-2024...")
sys.stdout.flush()

years = list(range(2000, 2025))
print(f"Loading {len(years)} years: {years[0]} to {years[-1]}")
sys.stdout.flush()

df = manager.load_matches('atp', years=years)

if df is not None:
    print(f"[+] SUCCESS: Loaded {len(df)} matches")
    print(f"[+] Columns: {len(df.columns)}")
    print(f"[+] Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
else:
    print("[-] FAILED to load data")

sys.stdout.flush()
