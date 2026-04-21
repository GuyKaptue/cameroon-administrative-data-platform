#!/usr/bin/env python3
"""
cameroon_population_pipeline/src/core/diagnostic.py

Complete diagnostic script to list ALL departments, arrondissements, and villages
from WOF and config for comparison.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import config
from core.geospatial_loader import load_geospatial_data

import geopandas as gpd


def run_diagnostic():
    """Run complete diagnostic checks on all data."""
    print("\n" + "="*100)
    print("🔍 CAMEROON DATA COMPLETE DIAGNOSTIC")
    print("="*100)

    # =========================================================
    # 1. Load GeoBoundaries
    # =========================================================
    print("\n📁 1. Loading GeoBoundaries...")
    adm1, adm2, adm3, _ = load_geospatial_data()

    print(f"\n   ADM1 (Regions): {len(adm1)}")
    print(f"   ADM2 (Departments): {len(adm2)}")
    print(f"   ADM3 (Arrondissements): {len(adm3)}")

    # =========================================================
    # 2. Load WOF
    # =========================================================
    print("\n📁 2. Loading WOF Localities...")
    wof_path = config.WOF_LOCALITY_SHP

    if wof_path.exists():
        wof_gdf = gpd.read_file(wof_path)
        wof_gdf.columns = [c.lower().replace(":", "_") for c in wof_gdf.columns]

        localities = wof_gdf[wof_gdf["lat"].notna() & wof_gdf["lon"].notna()].copy()
        localities["Village"] = localities["name"].str.upper().str.strip()
        localities["Lat_Village"] = localities["lat"]
        localities["Lon_Village"] = localities["lon"]

        print(f"   Loaded {len(localities):,} villages")
    else:
        print(f"   ❌ WOF file not found: {wof_path}")
        return

    # =========================================================
    # 3. LIST ALL CONFIG DEPARTMENTS
    # =========================================================
    print("\n" + "="*100)
    print("📋 3. ALL CONFIG DEPARTMENTS (DEPT_POPULATION_2005)")
    print("="*100)

    config_depts = sorted(config.DEPT_POPULATION_2005.keys())
    print(f"\n   Total: {len(config_depts)} departments\n")

    for i, dept in enumerate(config_depts, 1):
        pop = config.DEPT_POPULATION_2005[dept]
        print(f"   {i:3}. {dept:35} | Population 2005: {pop:>12,}")

    # =========================================================
    # 4. LIST ALL ADM2 DEPARTMENTS (from GeoBoundaries)
    # =========================================================
    print("\n" + "="*100)
    print("🗺️ 4. ALL ADM2 DEPARTMENTS (from GeoBoundaries)")
    print("="*100)

    if not adm2.empty:
        adm2_depts = sorted(adm2["Department"].tolist())
        print(f"\n   Total: {len(adm2_depts)} departments\n")

        for i, dept in enumerate(adm2_depts, 1):
            lat = adm2[adm2["Department"] == dept]["Lat_Department"].iloc[0]
            lon = adm2[adm2["Department"] == dept]["Lon_Department"].iloc[0]
            print(f"   {i:3}. {dept:35} | Centroid: ({lat:.4f}, {lon:.4f})")
    else:
        print("   No ADM2 data available")

    # =========================================================
    # 5. COMPARE CONFIG vs ADM2 DEPARTMENTS
    # =========================================================
    print("\n" + "="*100)
    print("🔍 5. DEPARTMENT NAME COMPARISON (Config vs ADM2)")
    print("="*100)

    config_dept_set = set(config_depts)
    adm2_dept_set = set(adm2_depts) if not adm2.empty else set()

    # Exact matches
    exact_matches = config_dept_set & adm2_dept_set
    print(f"\n   ✅ Exact matches: {len(exact_matches)} / {len(config_depts)}")

    # Missing in ADM2
    missing_in_adm2 = config_dept_set - adm2_dept_set
    if missing_in_adm2:
        print(f"\n   ⚠️ Config departments NOT in ADM2: {len(missing_in_adm2)}")
        for dept in sorted(missing_in_adm2):
            print(f"      - {dept}")

    # Extra in ADM2
    extra_in_adm2 = adm2_dept_set - config_dept_set
    if extra_in_adm2:
        print(f"\n   ⚠️ ADM2 departments NOT in Config: {len(extra_in_adm2)}")
        for dept in sorted(extra_in_adm2):
            print(f"      - {dept}")

    # =========================================================
    # 6. LIST ALL CONFIG ARRONDISSEMENTS (2005)
    # =========================================================
    print("\n" + "="*100)
    print("📋 6. ALL CONFIG ARRONDISSEMENTS (ARRONDISSEMENT_POPULATION_2005)")
    print("="*100)

    config_arrs = sorted(config.ARRONDISSEMENT_POPULATION_2005.items())
    print(f"\n   Total: {len(config_arrs)} arrondissements\n")

    for i, (arr_name, pop) in enumerate(config_arrs, 1):
        print(f"   {i:3}. {arr_name:45} | Population 2005: {pop:>12,}")

    # =========================================================
    # 7. LIST ALL CONFIG ARRONDISSEMENTS (2010)
    # =========================================================
    print("\n" + "="*100)
    print("📋 7. ALL CONFIG ARRONDISSEMENTS (ARRONDISSEMENT_POPULATION_2010)")
    print("="*100)

    config_arrs_2010 = sorted(config.ARRONDISSEMENT_POPULATION_2010.items())
    print(f"\n   Total: {len(config_arrs_2010)} arrondissements\n")

    for i, (arr_name, pop) in enumerate(config_arrs_2010, 1):
        print(f"   {i:3}. {arr_name:45} | Population 2010: {pop:>12,}")

    # =========================================================
    # 8. LIST ALL ADM3 ARRONDISSEMENTS (from GeoBoundaries)
    # =========================================================
    print("\n" + "="*100)
    print("🗺️ 8. ALL ADM3 ARRONDISSEMENTS (from GeoBoundaries)")
    print("="*100)

    if not adm3.empty:
        adm3_arrs = adm3[["Arrondissement", "Lat_Arrondissement", "Lon_Arrondissement"]].copy()
        adm3_arrs = adm3_arrs.sort_values("Arrondissement")

        print(f"\n   Total: {len(adm3_arrs)} arrondissements\n")

        for i, row in adm3_arrs.iterrows():
            arr_name = row["Arrondissement"]
            lat = row["Lat_Arrondissement"]
            lon = row["Lon_Arrondissement"]
            print(f"   {i+1:3}. {arr_name:45} | Centroid: ({lat:.4f}, {lon:.4f})")
    else:
        print("   No ADM3 data available")

    # =========================================================
    # 9. COMPARE CONFIG vs ADM3 ARRONDISSEMENTS
    # =========================================================
    print("\n" + "="*100)
    print("🔍 9. ARRONDISSEMENT NAME COMPARISON (Config vs ADM3)")
    print("="*100)

    config_arr_set = set(config.ARRONDISSEMENT_POPULATION_2005.keys())
    adm3_arr_set = set(adm3_arrs["Arrondissement"].tolist()) if not adm3.empty else set()

    # Exact matches
    exact_arr_matches = config_arr_set & adm3_arr_set
    print(f"\n   ✅ Exact matches: {len(exact_arr_matches)} / {len(config_arr_set)}")

    if exact_arr_matches:
        print("\n   Matching arrondissements:")
        for arr in sorted(exact_arr_matches)[:20]:
            print(f"      - {arr}")
        if len(exact_arr_matches) > 20:
            print(f"      ... and {len(exact_arr_matches) - 20} more")

    # Missing in ADM3
    missing_in_adm3 = config_arr_set - adm3_arr_set
    if missing_in_adm3:
        print(f"\n   ⚠️ Config arrondissements NOT in ADM3: {len(missing_in_adm3)}")
        for arr in sorted(missing_in_adm3)[:30]:
            print(f"      - {arr}")
        if len(missing_in_adm3) > 30:
            print(f"      ... and {len(missing_in_adm3) - 30} more")

    # Extra in ADM3
    extra_in_adm3 = adm3_arr_set - config_arr_set
    if extra_in_adm3:
        print(f"\n   ⚠️ ADM3 arrondissements NOT in Config: {len(extra_in_adm3)}")
        for arr in sorted(extra_in_adm3)[:30]:
            print(f"      - {arr}")
        if len(extra_in_adm3) > 30:
            print(f"      ... and {len(extra_in_adm3) - 30} more")

    # =========================================================
    # 10. LIST ALL UNIQUE VILLAGES FROM WOF
    # =========================================================
    print("\n" + "="*100)
    print("🏘️ 10. ALL VILLAGES FROM WOF (First 100)")
    print("="*100)

    wof_villages = sorted(localities["Village"].unique())
    print(f"\n   Total unique villages: {len(wof_villages):,}\n")

    for i, village in enumerate(wof_villages[:100], 1):
        print(f"   {i:4}. {village}")
    if len(wof_villages) > 100:
        print(f"\n   ... and {len(wof_villages) - 100} more villages")

    # =========================================================
    # 11. WOF COUNTY_ID DISTRIBUTION (Departments by ID)
    # =========================================================
    print("\n" + "="*100)
    print("📊 11. WOF COUNTY_ID DISTRIBUTION (Unique Department IDs)")
    print("="*100)

    if "county_id" in localities.columns:
        county_ids = localities[localities["county_id"].notna()]["county_id"].unique()
        print(f"\n   Unique county_ids: {len(county_ids)}")

        # Get sample of county_id to name mapping
        print("\n   Sample county_id to name mapping:")
        sample_ids = list(county_ids)[:20]
        for cid in sample_ids:
            sample_rows = localities[localities["county_id"] == cid]
            name = sample_rows["name"].iloc[0] if len(sample_rows) > 0 else "Unknown"
            print(f"      county_id {cid}: {name[:40]}")
    else:
        print("   No county_id column in WOF data")

    # =========================================================
    # 12. WOF REGION_ID DISTRIBUTION
    # =========================================================
    print("\n" + "="*100)
    print("📊 12. WOF REGION_ID DISTRIBUTION")
    print("="*100)

    if "region_id" in localities.columns:
        region_ids = localities[localities["region_id"].notna()]["region_id"].unique()
        print(f"\n   Unique region_ids: {len(region_ids)}")

        print("\n   Sample region_id to name mapping:")
        sample_ids = list(region_ids)[:10]
        for rid in sample_ids:
            sample_rows = localities[localities["region_id"] == rid]
            name = sample_rows["name"].iloc[0] if len(sample_rows) > 0 else "Unknown"
            print(f"      region_id {rid}: {name[:40]}")
    else:
        print("   No region_id column in WOF data")

    # =========================================================
    # 13. SUMMARY AND RECOMMENDATIONS
    # =========================================================
    print("\n" + "="*100)
    print("💡 13. SUMMARY AND RECOMMENDATIONS")
    print("="*100)

    print(f"""
    DATA SUMMARY:
    =============
    Config Departments:        {len(config_depts)}
    ADM2 Departments:          {len(adm2_depts) if not adm2.empty else 0}
    Department matches:        {len(exact_matches)}

    Config Arrondissements:    {len(config_arr_set)}
    ADM3 Arrondissements:      {len(adm3_arr_set) if not adm3.empty else 0}
    Arrondissement matches:    {len(exact_arr_matches)}

    WOF Villages:              {len(wof_villages):,}
    WOF Unique county_ids:     {len(county_ids) if 'county_id' in locals() else 0}
    WOF Unique region_ids:     {len(region_ids) if 'region_id' in locals() else 0}

    RECOMMENDATIONS:
    ================
    1. The column 'Department_WOF' doesn't exist - need to create it from spatial matching
    2. Use ADM2 centroids to assign villages to departments spatially
    3. Use ADM3 centroids to assign villages to arrondissements spatially
    4. Create mapping: Department_WOF = closest ADM2 department name
    5. Create mapping: Arrondissement_WOF = closest ADM3 arrondissement name
    """)

    print("\n" + "="*100)
    print("✅ DIAGNOSTIC COMPLETE")
    print("="*100)


if __name__ == "__main__":
    run_diagnostic()