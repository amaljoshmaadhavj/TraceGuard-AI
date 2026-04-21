#!/usr/bin/env python
"""Test path resolution from backend"""

import sys
import os
import json
from pathlib import Path

# Simulate being in backend/routes/stats.py
print("=" * 60)
print("PATH RESOLUTION TEST")
print("=" * 60)

# Method 1: Direct path from project root
catalog_direct = Path("data_parsed/evidence_catalog.json").resolve()
print(f"\n1. Direct path method:")
print(f"   Path: {catalog_direct}")
print(f"   Exists: {catalog_direct.exists()}")

# Method 2: Simulating stats.py implementation
PROJECT_ROOT = Path(__file__).parent
DATA_PARSED_DIR = PROJECT_ROOT / "data_parsed"
catalog_stats = DATA_PARSED_DIR / "evidence_catalog.json"
print(f"\n2. Stats.py method (from project root):")
print(f"   PROJECT_ROOT: {PROJECT_ROOT}")
print(f"   DATA_PARSED_DIR: {DATA_PARSED_DIR}")
print(f"   catalog_path: {catalog_stats}")
print(f"   Exists: {catalog_stats.exists()}")

# Method 3: Simulating from backend directory
backend_path = Path("backend/routes/stats.py")
PROJECT_ROOT_FROM_BACKEND = backend_path.parent.parent.parent
DATA_PARSED_DIR_FROM_BACKEND = PROJECT_ROOT_FROM_BACKEND / "data_parsed"
catalog_from_backend = DATA_PARSED_DIR_FROM_BACKEND / "evidence_catalog.json"
print(f"\n3. From backend directory simulation:")
print(f"   backend_path: {backend_path}")
print(f"   PROJECT_ROOT: {PROJECT_ROOT_FROM_BACKEND}")
print(f"   DATA_PARSED_DIR: {DATA_PARSED_DIR_FROM_BACKEND}")
print(f"   catalog_path: {catalog_from_backend}")
print(f"   Exists: {catalog_from_backend.exists()}")

# Load and verify catalog
if catalog_direct.exists():
    with open(catalog_direct, 'r') as f:
        catalog = json.load(f)
    print(f"\n✅ CATALOG LOADED SUCCESSFULLY:")
    print(f"   Total Events: {catalog.get('total_events', 0)}")
    print(f"   Total Files: {catalog.get('total_files', 0)}")
    print(f"   Event Categories: {list(catalog.get('evidence', {}).keys())}")
    print(f"   Severity Distribution: {catalog.get('severity_distribution', {})}")
else:
    print(f"\n❌ CATALOG NOT FOUND")

print("\n" + "=" * 60)
