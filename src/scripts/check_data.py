#!/usr/bin/env python3
"""
cameroon-administrative-data-platform/src/scripts/check_data.py

Check data quality and completeness before running dashboard
Run: python -m src.scripts.check_data
"""

import sys
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.config import config  # noqa: E402
import json  # noqa: E402
import pandas as pd  # noqa: E402


def check_data():
    """Check all required data files"""
    print("=" * 60)
    print("Cameroon Data Validation Check")
    print("=" * 60)
    print()

    errors = 0
    warnings = 0

    # Check output directory
    print("📁 Checking output directory...")
    if config.OUTPUT_DIR.exists():
        print(f"  ✓ Output directory: {config.OUTPUT_DIR}")
    else:
        print(f"  ✗ Output directory not found: {config.OUTPUT_DIR}")
        errors += 1

    # Check main dataset
    print("\n📊 Checking main dataset...")
    csv_path = config.OUTPUT_DIR / "cameroon_complete_dataset.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        print(f"  ✓ Dataset loaded: {len(df):,} records")
        print(f"    - Columns: {len(df.columns)}")
        print(f"    - Regions: {df['Region'].nunique()}")
        print(f"    - Departments: {df['Department_WOF'].nunique()}")
        print(f"    - Villages: {len(df)}")

        # Check population columns
        for year in [2005, 2010, 2015, 2020, 2025]:
            col = f"population_{year}"
            if col in df.columns:
                total = df[col].sum()
                print(f"    - Population {year}: {total:,.0f}")
            else:
                print(f"    ✗ Missing column: {col}")
                errors += 1
    else:
        print(f"  ✗ Dataset not found: {csv_path}")
        errors += 1

    # Check hierarchy JSON
    print("\n🏗 Checking hierarchy JSON...")
    json_path = config.OUTPUT_DIR / "cameroon_hierarchy.json"
    if json_path.exists():
        with open(json_path, 'r') as f:
            data = json.load(f)
        hierarchy = data.get("hierarchy", {})
        print(f"  ✓ Hierarchy loaded: {len(hierarchy)} regions")
    else:
        print(f"  ✗ Hierarchy not found: {json_path}")
        errors += 1

    # Check GeoBoundaries files
    print("\n🗺 Checking GeoBoundaries files...")
    for adm_file in [config.ADM1_FILE, config.ADM2_FILE, config.ADM3_FILE]:
        if adm_file.exists():
            print(f"  ✓ {adm_file.name}")
        else:
            print(f"  ✗ Missing: {adm_file.name}")
            warnings += 1

    # Check summary_by_region.csv
    print("\n📈 Checking summary files...")
    summary_path = config.OUTPUT_DIR / "summary_by_region.csv"
    if summary_path.exists():
        print(f"  ✓ summary_by_region.csv exists")  # noqa: F541
    else:
        print(f"  ✗ summary_by_region.csv not found")  # noqa: F541
        warnings += 1

    # Final summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")

    if errors == 0:
        print("\n✅ All required data is available!")
        print("   You can safely run the dashboard.")
        return True
    else:
        print("\n❌ Missing required data!")
        print("   Please run: cameroon-generate")
        return False


def console_main():
    """Entry point for console script (cameroon-check command)"""
    success = check_data()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    console_main()