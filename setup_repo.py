"""
Project Blue Nexus — Repository Setup Script
Run this ONCE from E:\BlueNexus\ to organize existing files into the repo structure.

Usage:
    cd E:\BlueNexus
    ocean_env\Scripts\activate
    python setup_repo.py
"""

import os
import shutil

print("Project Blue Nexus — Repository Setup")
print("=" * 50)

# Create directories
for d in ['data', 'output']:
    os.makedirs(d, exist_ok=True)
    print(f"  Created: {d}/")

# Move .nc data files to data/
nc_files = [f for f in os.listdir('.') if f.endswith('.nc')]
for f in nc_files:
    dest = os.path.join('data', f)
    if not os.path.exists(dest):
        shutil.move(f, dest)
        print(f"  Moved: {f} → data/{f}")
    else:
        print(f"  Skipped: {f} (already in data/)")

# Move .png output files to output/
png_files = [f for f in os.listdir('.') if f.endswith('.png') and f.startswith('lake_erie')]
for f in png_files:
    dest = os.path.join('output', f)
    if not os.path.exists(dest):
        shutil.move(f, dest)
        print(f"  Moved: {f} → output/{f}")
    else:
        print(f"  Skipped: {f} (already in output/)")

print()
print("Done! Your repo structure is ready.")
print()
print("Next steps:")
print("  1. Replace 01_Lake_Erie_SST_Analysis.ipynb with the new version")
print("  2. Verify: Kernel → Restart & Run All")
print("  3. Initialize git repo:")
print("       git init")
print("       git add .")
print('       git commit -m "Initial commit: Lake Erie SST & HAB analysis"')
print("       git remote add origin https://github.com/YOUR_USERNAME/BlueNexus.git")
print("       git push -u origin main")
