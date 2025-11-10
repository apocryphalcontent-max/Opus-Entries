"""Check subjects pool for placeholders and statistics."""
import json
from pathlib import Path
from collections import Counter

# Load the 12K pool
pool_path = Path("subjects_pool_ULTIMATE_12000.json")

if not pool_path.exists():
    print(f"ERROR: {pool_path} not found!")
    exit(1)

with open(pool_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*80)
print("SUBJECTS POOL STATISTICS")
print("="*80)
print(f"\nTotal entries: {len(data)}")

# Check for placeholders
placeholders = [
    e for e in data 
    if 'PLACEHOLDER' in str(e) or 'TODO' in str(e) or 
       'TBD' in str(e) or '...' in e.get('subject', '')
]
print(f"Placeholders/TODOs: {len(placeholders)}")

if placeholders:
    print("\nPlaceholder entries:")
    for p in placeholders[:10]:
        print(f"  - {p.get('subject', 'N/A')} [{p.get('category', 'N/A')}]")

# Category distribution
categories = Counter(e.get('category', 'Unknown') for e in data)
print("\nCategory Distribution:")
for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cat:40s}: {count:5d}")

# Tier distribution
tiers = Counter(e.get('tier', 'Unknown') for e in data)
print("\nTier Distribution:")
for tier, count in sorted(tiers.items()):
    print(f"  {tier:20s}: {count:5d}")

# Sample entries per category
print("\nSample Entries by Category:")
for cat in list(categories.keys())[:5]:
    samples = [e for e in data if e.get('category') == cat][:2]
    print(f"\n  {cat}:")
    for s in samples:
        print(f"    - {s.get('subject')}")

print("\n" + "="*80)
print("File check complete!")
print("="*80)
