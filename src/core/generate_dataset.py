#!/usr/bin/env python3
"""
cameroon_population_pipeline/src/core/generate_dataset.py

Complete professional pipeline to generate Cameroon population dataset.
Uses spatial matching to assign villages to departments and arrondissements.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import config
from core.geospatial_loader import load_geospatial_data, get_department_region_mapping
from core.population_simulator import HierarchicalPopulationSimulator
from core.postal_codes import PostalCodeGenerator
from core.hierarchy_builder import build_hierarchy
from core.data_exporter import DataExporter
from core.validator import DataValidator
from core.optimized_parameters import UN_POPULATION_TARGETS, URBANIZATION_TARGETS, save_optimized_parameters
import logging
import pandas as pd
import numpy as np
from tqdm import tqdm
import geopandas as gpd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_demographic_context():
    """Print UN demographic context for the dataset."""
    print("\n" + "="*80)
    print("📊 DEMOGRAPHIC CONTEXT (UN World Population Prospects 2024)")
    print("="*80)
    print(f"\n   🇨🇲 Cameroon Population 2026: {UN_POPULATION_TARGETS.get(2026, 30_640_817):,}")
    print(f"   📈 Growth 2005-2025: {(UN_POPULATION_TARGETS[2025]/UN_POPULATION_TARGETS[2005]-1)*100:.1f}%")
    print(f"   👶 Fertility rate: 4.18 children/woman (2025)")  # noqa: F541
    print(f"   📊 Median age: 18.0 years (2025)")  # noqa: F541
    print(f"   🏙️ Urban population: {URBANIZATION_TARGETS.get(2025, 0.594)*100:.1f}%")
    print(f"   🏥 Life expectancy: 64.5 years (2026)")  # noqa: F541
    print("="*80)


def load_wof_localities() -> pd.DataFrame:
    """Load WOF localities and extract village information."""
    print("\n" + "="*60)
    print("📍 LOADING WOF LOCALITIES")
    print("="*60)

    wof_path = config.WOF_LOCALITY_SHP

    if not wof_path.exists():
        print(f"❌ WOF file not found: {wof_path}")
        return pd.DataFrame()

    wof_gdf = gpd.read_file(wof_path)
    wof_gdf.columns = [c.lower().replace(":", "_") for c in wof_gdf.columns]

    localities = wof_gdf[wof_gdf["lat"].notna() & wof_gdf["lon"].notna()].copy()
    localities["Village"] = localities["name"].str.upper().str.strip()
    localities["Lat_Village"] = localities["lat"]
    localities["Lon_Village"] = localities["lon"]

    print(f"✅ Loaded {len(localities):,} villages from WOF")
    return localities[["Village", "Lat_Village", "Lon_Village"]]


def assign_villages_to_departments_spatial(villages_df: pd.DataFrame, adm2: pd.DataFrame) -> pd.DataFrame:
    """Assign each village to the nearest department using spatial matching."""
    print("\n" + "="*60)
    print("📍 SPATIAL ASSIGNMENT: VILLAGES → DEPARTMENTS")
    print("="*60)

    if villages_df.empty or adm2.empty:
        return pd.DataFrame()

    df = villages_df.copy()
    df["Department"] = None
    df["Lat_Department"] = None
    df["Lon_Department"] = None

    depts = []
    for _, row in adm2.iterrows():
        depts.append({
            "name": row["Department"],
            "lat": row["Lat_Department"],
            "lon": row["Lon_Department"]
        })

    print(f"   Matching {len(df):,} villages to {len(depts)} departments...")

    with tqdm(total=len(df), desc="   Spatial matching", unit="villages", ncols=80) as pbar:
        for idx, row in df.iterrows():
            if pd.notna(row["Lat_Village"]) and pd.notna(row["Lon_Village"]):
                min_dist = float('inf')
                closest_dept = None
                closest_lat = None
                closest_lon = None

                for dept in depts:
                    dist = ((row["Lat_Village"] - dept["lat"])**2 +
                            (row["Lon_Village"] - dept["lon"])**2)**0.5
                    if dist < min_dist:
                        min_dist = dist
                        closest_dept = dept["name"]
                        closest_lat = dept["lat"]
                        closest_lon = dept["lon"]

                if closest_dept:
                    df.loc[idx, "Department"] = closest_dept
                    df.loc[idx, "Lat_Department"] = closest_lat
                    df.loc[idx, "Lon_Department"] = closest_lon
            pbar.update(1)

    matched = df["Department"].notna().sum()
    print(f"\n   ✅ Matched {matched:,} / {len(df):,} villages ({matched/len(df)*100:.1f}%)")
    return df


def assign_villages_to_arrondissements_spatial(df: pd.DataFrame, adm3: pd.DataFrame) -> pd.DataFrame:
    """Assign each village to the nearest arrondissement using spatial matching."""
    print("\n" + "="*60)
    print("📍 SPATIAL ASSIGNMENT: VILLAGES → ARRONDISSEMENTS")
    print("="*60)

    if df.empty or adm3.empty:
        print("   No ADM3 data available, using department as arrondissement")
        df["Arrondissement_WOF"] = df["Department"]
        df["Lat_Arrondissement"] = df["Lat_Department"]
        df["Lon_Arrondissement"] = df["Lon_Department"]
        return df

    arrs = []
    for _, row in adm3.iterrows():
        arrs.append({
            "name": row["Arrondissement"],
            "lat": row["Lat_Arrondissement"],
            "lon": row["Lon_Arrondissement"]
        })

    print(f"   Matching {len(df):,} villages to {len(arrs)} arrondissements...")

    df["Arrondissement_WOF"] = None
    df["Lat_Arrondissement"] = None
    df["Lon_Arrondissement"] = None

    with tqdm(total=len(df), desc="   Spatial matching", unit="villages", ncols=80) as pbar:
        for idx, row in df.iterrows():
            if pd.notna(row["Lat_Village"]) and pd.notna(row["Lon_Village"]):
                min_dist = float('inf')
                closest_arr = None
                closest_lat = None
                closest_lon = None

                for arr in arrs:
                    dist = ((row["Lat_Village"] - arr["lat"])**2 +
                            (row["Lon_Village"] - arr["lon"])**2)**0.5
                    if dist < min_dist:
                        min_dist = dist
                        closest_arr = arr["name"]
                        closest_lat = arr["lat"]
                        closest_lon = arr["lon"]

                if closest_arr:
                    df.loc[idx, "Arrondissement_WOF"] = closest_arr
                    df.loc[idx, "Lat_Arrondissement"] = closest_lat
                    df.loc[idx, "Lon_Arrondissement"] = closest_lon
            pbar.update(1)

    matched = df["Arrondissement_WOF"].notna().sum()
    print(f"\n   ✅ Matched {matched:,} / {len(df):,} villages ({matched/len(df)*100:.1f}%)")

    df["Arrondissement_WOF"] = df["Arrondissement_WOF"].fillna(df["Department"])
    df["Lat_Arrondissement"] = df["Lat_Arrondissement"].fillna(df["Lat_Department"])
    df["Lon_Arrondissement"] = df["Lon_Arrondissement"].fillna(df["Lon_Department"])

    return df


def assign_regions_to_villages(df: pd.DataFrame, adm1: pd.DataFrame, adm2: pd.DataFrame) -> pd.DataFrame:
    """Assign regions to villages using department-region mapping."""
    print("\n" + "="*60)
    print("📍 ASSIGNING REGIONS TO VILLAGES")
    print("="*60)

    if df.empty or adm2.empty or adm1.empty:
        return df

    region_coords = {}
    for _, row in adm1.iterrows():
        region_coords[row["Region"]] = {"lat": row["Lat_Region"], "lon": row["Lon_Region"]}

    dept_to_region = {}
    for _, row in adm2.iterrows():
        dept_name = row["Department"]
        dept_lat = row["Lat_Department"]
        dept_lon = row["Lon_Department"]

        if pd.notna(dept_lat) and pd.notna(dept_lon):
            min_dist = float('inf')
            closest_region = None
            for region, coords in region_coords.items():
                dist = ((dept_lat - coords["lat"])**2 + (dept_lon - coords["lon"])**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_region = region
            if closest_region:
                dept_to_region[dept_name] = closest_region

    config_mapping = get_department_region_mapping()
    for region, depts in config_mapping.items():
        for dept in depts:
            dept_to_region[dept] = region
            dept_to_region[dept.replace("-", " ")] = region
            dept_to_region[dept.replace(" ", "-")] = region

    df["Region"] = df["Department"].map(dept_to_region)
    df["Lat_Region"] = df["Region"].map(lambda x: region_coords.get(x, {}).get("lat"))
    df["Lon_Region"] = df["Region"].map(lambda x: region_coords.get(x, {}).get("lon"))

    before = len(df)
    df = df.dropna(subset=["Region"])
    after = len(df)

    print(f"\n   ✅ Assigned regions to {after:,} / {before:,} villages ({after/before*100:.1f}%)")
    return df


def distribute_population_to_arrondissements(df: pd.DataFrame) -> pd.DataFrame:
    """Distribute 2005 population using arrondissement-level census data."""
    print("\n" + "="*60)
    print("👥 DISTRIBUTING 2005 POPULATION (Arrondissement Level)")
    print("="*60)

    df = df.copy()
    df["population_2005"] = 0
    np.random.seed(42)

    total_population = 0
    matched_arr = 0
    arr_populations = config.ARRONDISSEMENT_POPULATION_2005
    df_arr_names = df["Arrondissement_WOF"].unique()

    with tqdm(total=len(arr_populations), desc="   Distributing by arrondissement", unit="arr", ncols=80) as pbar:
        for arr_name, total_pop in arr_populations.items():
            arr_name_upper = arr_name.upper().strip()
            arr_mask = df["Arrondissement_WOF"].str.upper().str.strip() == arr_name_upper
            num_villages = arr_mask.sum()

            if num_villages == 0:
                for df_arr in df_arr_names:
                    if pd.notna(df_arr) and (arr_name_upper in str(df_arr).upper() or str(df_arr).upper() in arr_name_upper):
                        arr_mask = df["Arrondissement_WOF"] == df_arr
                        num_villages = arr_mask.sum()
                        if num_villages > 0:
                            break

            if num_villages > 0:
                matched_arr += 1
                base_pop = total_pop // num_villages
                variations = np.random.lognormal(mean=0, sigma=0.5, size=num_villages)
                variations = variations / variations.sum() * num_villages
                village_pops = (base_pop * variations).astype(int)
                village_pops = np.maximum(village_pops, 50)

                diff = total_pop - village_pops.sum()
                if diff != 0:
                    indices = np.argsort(village_pops)[::-1]
                    for i in range(abs(diff)):
                        village_pops[indices[i % len(indices)]] += 1 if diff > 0 else -1

                arr_indices = df[arr_mask].index
                for i, idx in enumerate(arr_indices):
                    df.loc[idx, "population_2005"] = village_pops[i]

                total_population += village_pops.sum()
                pbar.set_postfix_str(f"✓ {arr_name[:25]}: {num_villages} villages")
            else:
                pbar.set_postfix_str(f"⚠️ {arr_name[:25]}: no villages")
            pbar.update(1)

    print(f"\n   ✅ Matched {matched_arr} / {len(arr_populations)} arrondissements")
    print(f"\n📊 TOTAL 2005 POPULATION: {total_population:,.0f}")
    print(f"   Expected (UN 2005): {UN_POPULATION_TARGETS[2005]:,.0f}")

    if total_population > 0 and abs(total_population - UN_POPULATION_TARGETS[2005]) / UN_POPULATION_TARGETS[2005] > 0.02:
        scaling_factor = UN_POPULATION_TARGETS[2005] / total_population
        print(f"\n   Scaling to match UN target (factor: {scaling_factor:.3f})")
        df["population_2005"] = (df["population_2005"] * scaling_factor).round(0).astype(int)

    return df


def main():
    """Main pipeline to generate complete dataset."""
    print("\n" + "="*80)
    print("🇨🇲 CAMEROON COMPLETE DATASET GENERATOR")
    print("="*80)
    print_demographic_context()

    # STEP 1: Load GeoBoundaries
    print("\n" + "-"*60)
    print("📁 STEP 1: Loading GeoBoundaries")
    print("-"*60)
    adm1, adm2, adm3, _ = load_geospatial_data()

    if adm1.empty or adm2.empty:
        logger.error("Missing required GeoBoundaries data")
        return None, None, None

    # STEP 2: Load WOF villages
    print("\n" + "-"*60)
    print("📍 STEP 2: Loading WOF Villages")
    print("-"*60)
    villages = load_wof_localities()
    if villages.empty:
        logger.error("No villages loaded from WOF")
        return None, None, None

    # STEP 3: Assign to departments
    print("\n" + "-"*60)
    print("📍 STEP 3: Spatial Assignment to Departments")
    print("-"*60)
    df = assign_villages_to_departments_spatial(villages, adm2)
    if df.empty:
        logger.error("No villages assigned to departments")
        return None, None, None

    # STEP 4: Assign to arrondissements
    print("\n" + "-"*60)
    print("📍 STEP 4: Spatial Assignment to Arrondissements")
    print("-"*60)
    df = assign_villages_to_arrondissements_spatial(df, adm3)

    # STEP 5: Assign regions
    print("\n" + "-"*60)
    print("📍 STEP 5: Assigning Regions")
    print("-"*60)
    df = assign_regions_to_villages(df, adm1, adm2)
    if df.empty:
        logger.error("No regions assigned")
        return None, None, None

    # STEP 6: Create Department_WOF column
    df["Department_WOF"] = df["Department"]

    # STEP 7: Distribute 2005 population
    print("\n" + "-"*60)
    print("👥 STEP 6: Population Distribution (2005 Census)")
    print("-"*60)
    df = distribute_population_to_arrondissements(df)

    # STEP 8: Hierarchical population simulation
    print("\n" + "-"*60)
    print("📈 STEP 7: Hierarchical Population Simulation (2005-2025)")
    print("-"*60)
    simulator = HierarchicalPopulationSimulator(df)
    df = simulator.simulate()

    # STEP 9: Generate postal codes
    print("\n" + "-"*60)
    print("📮 STEP 8: Generating Postal Codes")
    print("-"*60)
    postal_gen = PostalCodeGenerator()
    df = postal_gen.generate_postal_codes(df)

    # STEP 10: Build hierarchy
    print("\n" + "-"*60)
    print("🏗️ STEP 9: Building Hierarchy")
    print("-"*60)
    hierarchy = build_hierarchy(df)

    # STEP 11: Validate
    print("\n" + "-"*60)
    print("✅ STEP 10: Validation")
    print("-"*60)
    validator = DataValidator(df, hierarchy)
    validation = validator.validate_all()

    # STEP 12: Export
    print("\n" + "-"*60)
    print("💾 STEP 11: Exporting Data")
    print("-"*60)
    exporter = DataExporter()

    export_tasks = [
        ("CSV dataset", lambda: exporter.export_csv(df, "cameroon_complete_dataset.csv")),
        ("JSON hierarchy", lambda: exporter.export_json(hierarchy, "cameroon_hierarchy.json")),
        ("Year-specific files", lambda: exporter.export_by_year(df)),
        ("Summary statistics", lambda: exporter.export_summary(df, hierarchy)),
        ("Report generation", lambda: exporter.generate_report(df)),
    ]

    with tqdm(total=len(export_tasks), desc="   Exporting", unit="task", ncols=80) as pbar:
        for task_name, task_func in export_tasks:
            try:
                task_func()
                pbar.set_postfix_str(f"✓ {task_name}")
            except Exception as e:
                pbar.set_postfix_str(f"⚠️ {task_name}: {str(e)[:30]}")
            pbar.update(1)

    # Export additional summaries
    print("\n   📊 Generating additional summaries...")

    summary_by_region = df.groupby("Region").agg({
        "population_2005": "sum", "population_2010": "sum", "population_2015": "sum",
        "population_2020": "sum", "population_2025": "sum", "Village": "count"
    }).reset_index()
    summary_by_region.to_csv(config.OUTPUT_DIR / "summary_by_region.csv", index=False)

    summary_by_dept = df.groupby(["Region", "Department_WOF"]).agg({
        "population_2005": "sum", "population_2010": "sum", "population_2015": "sum",
        "population_2020": "sum", "population_2025": "sum", "Village": "count"
    }).reset_index()
    summary_by_dept.to_csv(config.OUTPUT_DIR / "summary_by_department.csv", index=False)

    summary_by_arr = df.groupby(["Region", "Department_WOF", "Arrondissement_WOF"]).agg({
        "population_2005": "sum", "population_2010": "sum", "population_2015": "sum",
        "population_2020": "sum", "population_2025": "sum", "Village": "count"
    }).reset_index()
    summary_by_arr.to_csv(config.OUTPUT_DIR / "summary_by_arrondissement.csv", index=False)

    # Save optimized parameters
    save_optimized_parameters(config.OUTPUT_DIR)

    # FINAL SUMMARY
    print("\n" + "="*80)
    print("🎉 GENERATION COMPLETE!")
    print("="*80)
    print(f"\n📁 OUTPUT DIRECTORY: {config.OUTPUT_DIR}")
    print("\n📄 FILES GENERATED:")
    for f in [
        "   • cameroon_complete_dataset.csv",
        "   • cameroon_hierarchy.json",
        "   • population_2005.csv, population_2010.csv, population_2015.csv, population_2020.csv, population_2025.csv",
        "   • population_report.csv",
        "   • summary.json",
        "   • summary_by_region.csv",
        "   • summary_by_department.csv",
        "   • summary_by_arrondissement.csv",
        "   • optimized_parameters.json",
    ]:
        print(f)

    print(f"\n📊 DATASET STATISTICS:")  # noqa: F541
    print(f"   • Villages: {len(df):,}")
    print(f"   • Regions: {len(hierarchy)}")
    print(f"   • Departments: {df['Department_WOF'].nunique()}")
    print(f"   • Arrondissements: {df['Arrondissement_WOF'].nunique()}")
    print(f"   • Unique postal codes: {df['postal_code'].nunique()}")
    print(f"   • Population 2005: {df['population_2005'].sum():,.0f} (UN: {UN_POPULATION_TARGETS[2005]:,.0f})")
    print(f"   • Population 2025: {df['population_2025'].sum():,.0f} (UN: {UN_POPULATION_TARGETS[2025]:,.0f})")
    print(f"   • Growth 2005-2025: {(df['population_2025'].sum()/df['population_2005'].sum()-1)*100:.1f}%")

    return df, hierarchy, validation


def console_main():
    """Entry point for console script."""
    try:
        df, hierarchy, validation = main()
        if df is not None and not df.empty:
            print("\n🎉 Pipeline executed successfully!")
            return 0
        else:
            print("\n❌ Pipeline failed to generate data.")
            return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(console_main())