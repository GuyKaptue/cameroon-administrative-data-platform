"""
cameroon_population_pipeline/src/core/geospatial_loader.py

Load geospatial data from GeoBoundaries and WOF shapefiles.
"""

import geopandas as gpd
import pandas as pd
from typing import Tuple, Dict
import logging
import warnings
import sys
from pathlib import Path

# Suppress geopandas warnings
warnings.filterwarnings('ignore', category=UserWarning)

logger = logging.getLogger(__name__)


def get_config_for_testing():
    """Create a config object for testing when running directly"""
    # Add the parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    try:
        from core.config import config
        return config
    except ImportError:
        # Fallback config for direct testing
        from dataclasses import dataclass

        @dataclass
        class TestConfig:
            BASE_DIR = Path("/Volumes/Intenso/my_work_spaces/cameroon-administrative-data-platform")
            DATA_DIR = BASE_DIR / "data"
            EXTERNAL_DIR = DATA_DIR / "external"
            RAW_DIR = DATA_DIR / "raw"
            PROCESSED_DIR = DATA_DIR / "processed"
            OUTPUT_DIR = DATA_DIR / "output"
            ADM1_FILE = EXTERNAL_DIR / "geoBoundaries-CMR-ADM1.geojson"
            ADM2_FILE = EXTERNAL_DIR / "geoBoundaries-CMR-ADM2.geojson"
            ADM3_FILE = EXTERNAL_DIR / "geoBoundaries-CMR-ADM3.geojson"
            WOF_DIR = EXTERNAL_DIR / "whosonfirst-data-admin-cm-latest"
            WOF_LOCALITY_SHP = WOF_DIR / "whosonfirst-data-admin-cm-locality-point.shp"

        return TestConfig()


# Try to import config, fallback to test config
try:
    from .config import config
    print("✅ Using config from module import")
except ImportError:
    try:
        from core.config import config
        print("✅ Using config from core.config")
    except ImportError:
        config = get_config_for_testing()
        print("⚠️ Using fallback test config")


def load_geospatial_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all geospatial data:
    - ADM1 (Regions) with centroids
    - ADM2 (Departments) with centroids
    - ADM3 (Arrondissements) with centroids (if available)
    - WOF localities (villages)

    Returns empty DataFrames if files are not found.
    """
    print("\n" + "="*80)
    print("📍 LOADING GEOSPATIAL DATA")
    print("="*80)

    logger.info("Loading geospatial data...")

    # Initialize empty DataFrames as fallbacks
    empty_adm1 = pd.DataFrame(columns=["Region", "Lat_Region", "Lon_Region"])
    empty_adm2 = pd.DataFrame(columns=["Department", "Lat_Department", "Lon_Department"])
    empty_adm3 = pd.DataFrame(columns=["Arrondissement", "Lat_Arrondissement", "Lon_Arrondissement"])
    empty_wof = pd.DataFrame(columns=["Village", "Lat_Village", "Lon_Village",
                                       "Region_WOF", "Department_WOF", "Arrondissement_WOF"])

    # =========================================================
    # 1. LOAD ADM1 (REGIONS)
    # =========================================================
    print("\n" + "-"*60)
    print("📁 STEP 1: Loading ADM1 - Regions")
    print("-"*60)

    adm1 = empty_adm1.copy()
    print(f"🔍 Looking for ADM1 file at: {config.ADM1_FILE}")

    if config.ADM1_FILE.exists():
        print(f"✅ ADM1 file found!")  # noqa: F541
        print(f"📏 File size: {config.ADM1_FILE.stat().st_size / 1024:.2f} KB")

        try:
            adm1_gdf = gpd.read_file(config.ADM1_FILE)
            print(f"📊 Raw ADM1 GeoJSON loaded with {len(adm1_gdf)} features")

            # Show column names
            print(f"\n📋 Raw ADM1 columns: {list(adm1_gdf.columns)}")

            # Show first few shapeName values
            if "shapeName" in adm1_gdf.columns:
                print(f"\n🏷️ Raw shapeName values:")  # noqa: F541
                for i, name in enumerate(adm1_gdf["shapeName"].head(10).values):
                    print(f"   {i+1}. '{name}'")
                if len(adm1_gdf) > 10:
                    print(f"   ... and {len(adm1_gdf) - 10} more")

            # Extract region names from shapeName field
            adm1_gdf["Lat_Region"] = adm1_gdf.geometry.centroid.y
            adm1_gdf["Lon_Region"] = adm1_gdf.geometry.centroid.x
            adm1_gdf["Region"] = adm1_gdf["shapeName"].str.upper().str.strip()
            adm1 = adm1_gdf[["Region", "Lat_Region", "Lon_Region"]].copy()

            print(f"\n✅ Processed ADM1: {len(adm1)} regions")
            print(f"\n📍 REGIONS with centroids:")  # noqa: F541
            for i, row in adm1.iterrows():
                print(f"   {i+1}. {row['Region']:20} | Lat: {row['Lat_Region']:.4f}, Lon: {row['Lon_Region']:.4f}")

            logger.info(f"Loaded {len(adm1)} regions from {config.ADM1_FILE}")

        except Exception as e:
            print(f"❌ ERROR loading ADM1 file: {e}")
            logger.warning(f"Could not load ADM1 file: {e}")
    else:
        print(f"❌ ADM1 file NOT FOUND!")  # noqa: F541
        print(f"   Please ensure the file exists at: {config.ADM1_FILE}")

    # =========================================================
    # 2. LOAD ADM2 (DEPARTMENTS)
    # =========================================================
    print("\n" + "-"*60)
    print("📁 STEP 2: Loading ADM2 - Departments")
    print("-"*60)

    adm2 = empty_adm2.copy()
    print(f"🔍 Looking for ADM2 file at: {config.ADM2_FILE}")

    if config.ADM2_FILE.exists():
        print(f"✅ ADM2 file found!")  # noqa: F541
        print(f"📏 File size: {config.ADM2_FILE.stat().st_size / 1024:.2f} KB")

        try:
            adm2_gdf = gpd.read_file(config.ADM2_FILE)
            print(f"📊 Raw ADM2 GeoJSON loaded with {len(adm2_gdf)} features")

            # Show column names
            print(f"\n📋 Raw ADM2 columns: {list(adm2_gdf.columns)}")

            # Show first few shapeName values
            if "shapeName" in adm2_gdf.columns:
                print(f"\n🏷️ Raw shapeName values (first 15):")  # noqa: F541
                for i, name in enumerate(adm2_gdf["shapeName"].head(15).values):
                    print(f"   {i+1}. '{name}'")
                if len(adm2_gdf) > 15:
                    print(f"   ... and {len(adm2_gdf) - 15} more")

            # Extract department names from shapeName field
            adm2_gdf["Lat_Department"] = adm2_gdf.geometry.centroid.y
            adm2_gdf["Lon_Department"] = adm2_gdf.geometry.centroid.x
            adm2_gdf["Department"] = adm2_gdf["shapeName"].str.upper().str.strip()
            adm2 = adm2_gdf[["Department", "Lat_Department", "Lon_Department"]].copy()

            print(f"\n✅ Processed ADM2: {len(adm2)} departments")
            print(f"\n📍 DEPARTMENTS with centroids (first 20):")  # noqa: F541
            for i, row in adm2.head(20).iterrows():
                print(f"   {i+1}. {row['Department']:35} | Lat: {row['Lat_Department']:.4f}, Lon: {row['Lon_Department']:.4f}")
            if len(adm2) > 20:
                print(f"   ... and {len(adm2) - 20} more departments")

            logger.info(f"Loaded {len(adm2)} departments from {config.ADM2_FILE}")

        except Exception as e:
            print(f"❌ ERROR loading ADM2 file: {e}")
            logger.warning(f"Could not load ADM2 file: {e}")
    else:
        print(f"❌ ADM2 file NOT FOUND!")  # noqa: F541

    # =========================================================
    # 3. LOAD ADM3 (ARRONDISSEMENTS)
    # =========================================================
    print("\n" + "-"*60)
    print("📁 STEP 3: Loading ADM3 - Arrondissements")
    print("-"*60)

    adm3 = empty_adm3.copy()
    print(f"🔍 Looking for ADM3 file at: {config.ADM3_FILE}")

    if config.ADM3_FILE and config.ADM3_FILE.exists():
        print(f"✅ ADM3 file found!")  # noqa: F541
        print(f"📏 File size: {config.ADM3_FILE.stat().st_size / 1024:.2f} KB")

        try:
            adm3_gdf = gpd.read_file(config.ADM3_FILE)
            print(f"📊 Raw ADM3 GeoJSON loaded with {len(adm3_gdf)} features")

            # Show column names
            print(f"\n📋 Raw ADM3 columns: {list(adm3_gdf.columns)}")

            # Show first few shapeName values
            if "shapeName" in adm3_gdf.columns:
                print(f"\n🏷️ Raw shapeName values (first 15):")  # noqa: F541
                for i, name in enumerate(adm3_gdf["shapeName"].head(15).values):
                    print(f"   {i+1}. '{name}'")
                if len(adm3_gdf) > 15:
                    print(f"   ... and {len(adm3_gdf) - 15} more")

            adm3_gdf["Lat_Arrondissement"] = adm3_gdf.geometry.centroid.y
            adm3_gdf["Lon_Arrondissement"] = adm3_gdf.geometry.centroid.x
            adm3_gdf["Arrondissement"] = adm3_gdf["shapeName"].str.upper().str.strip()
            adm3 = adm3_gdf[["Arrondissement", "Lat_Arrondissement", "Lon_Arrondissement"]].copy()

            print(f"\n✅ Processed ADM3: {len(adm3)} arrondissements")
            print(f"\n📍 ARRONDISSEMENTS with centroids (first 20):")  # noqa: F541
            for i, row in adm3.head(20).iterrows():
                print(f"   {i+1}. {row['Arrondissement'][:40]:40} | Lat: {row['Lat_Arrondissement']:.4f}, Lon: {row['Lon_Arrondissement']:.4f}")
            if len(adm3) > 20:
                print(f"   ... and {len(adm3) - 20} more arrondissements")

            logger.info(f"Loaded {len(adm3)} arrondissements from {config.ADM3_FILE}")

        except Exception as e:
            print(f"❌ ERROR loading ADM3 file: {e}")
            logger.warning(f"Could not load ADM3 file: {e}")
    else:
        print(f"⚠️ ADM3 file not found: {config.ADM3_FILE}")

    # =========================================================
    # 4. LOAD WOF LOCALITIES (VILLAGES)
    # =========================================================
    print("\n" + "-"*60)
    print("📁 STEP 4: Loading WOF - Localities/Villages")
    print("-"*60)

    wof = empty_wof.copy()
    print(f"🔍 Looking for WOF shapefile at: {config.WOF_LOCALITY_SHP}")

    if config.WOF_LOCALITY_SHP.exists():
        print(f"✅ WOF shapefile found!")  # noqa: F541
        print(f"📏 File size: {config.WOF_LOCALITY_SHP.stat().st_size / 1024:.2f} KB")

        try:
            wof_gdf = gpd.read_file(config.WOF_LOCALITY_SHP)
            print(f"📊 Raw WOF shapefile loaded with {len(wof_gdf)} features")

            # Show original column names
            print(f"\n📋 Raw WOF columns: {list(wof_gdf.columns)}")

            # Map WOF fields to our schema based on actual column names
            wof = pd.DataFrame()

            # Map village name - use 'name' column
            if "name" in wof_gdf.columns:
                wof["Village"] = wof_gdf["name"].str.upper().str.strip()
                print(f"   ✅ Using 'name' column for village names")  # noqa: F541
            elif "wof_name" in wof_gdf.columns:
                wof["Village"] = wof_gdf["wof_name"].str.upper().str.strip()
                print(f"   ✅ Using 'wof_name' column for village names")  # noqa: F541
            else:
                wof["Village"] = None
                print(f"   ⚠️ No name column found")  # noqa: F541

            # Map coordinates - use 'lat' and 'lon' columns
            if "lat" in wof_gdf.columns and "lon" in wof_gdf.columns:
                wof["Lat_Village"] = wof_gdf["lat"]
                wof["Lon_Village"] = wof_gdf["lon"]
                print(f"   ✅ Using 'lat' and 'lon' columns for coordinates")  # noqa: F541
            elif "geom_latitude" in wof_gdf.columns and "geom_longitude" in wof_gdf.columns:
                wof["Lat_Village"] = wof_gdf["geom_latitude"]
                wof["Lon_Village"] = wof_gdf["geom_longitude"]
                print(f"   ✅ Using 'geom_latitude' and 'geom_longitude' columns for coordinates")  # noqa: F541
            else:
                wof["Lat_Village"] = None
                wof["Lon_Village"] = None
                print(f"   ⚠️ No coordinate columns found")  # noqa: F541

            # Extract administrative hierarchy from WOF fields
            # Try different possible column names
            if "region_id" in wof_gdf.columns:
                wof["Region_WOF"] = wof_gdf["region_id"]
                print(f"   ✅ Using 'region_id' for region mapping")  # noqa: F541
            elif "qs_a1" in wof_gdf.columns:
                wof["Region_WOF"] = wof_gdf["qs_a1"].str.upper().str.strip()
                print(f"   ✅ Using 'qs_a1' for region mapping")  # noqa: F541
            else:
                wof["Region_WOF"] = None
                print(f"   ⚠️ No region mapping column found")  # noqa: F541

            if "county_id" in wof_gdf.columns:
                wof["Department_WOF"] = wof_gdf["county_id"]
                print(f"   ✅ Using 'county_id' for department mapping")  # noqa: F541
            elif "qs_a2" in wof_gdf.columns:
                wof["Department_WOF"] = wof_gdf["qs_a2"].str.upper().str.strip()
                print(f"   ✅ Using 'qs_a2' for department mapping")  # noqa: F541
            else:
                wof["Department_WOF"] = None
                print(f"   ⚠️ No department mapping column found")  # noqa: F541

            # For arrondissement, use placetype or try to infer
            if "placetype" in wof_gdf.columns:
                # Filter for villages/localities
                wof["Arrondissement_WOF"] = wof_gdf["placetype"]
                print(f"   ✅ Using 'placetype' for administrative level")  # noqa: F541
            elif "qs_a3" in wof_gdf.columns:
                wof["Arrondissement_WOF"] = wof_gdf["qs_a3"].str.upper().str.strip()
                print(f"   ✅ Using 'qs_a3' for arrondissement mapping")  # noqa: F541
            else:
                wof["Arrondissement_WOF"] = None
                print(f"   ⚠️ No arrondissement mapping column found")  # noqa: F541

            # Print sample of what we loaded
            print(f"\n📊 WOF data structure:")  # noqa: F541
            print(f"   - Village names present: {wof['Village'].notna().sum():,} / {len(wof)}")
            print(f"   - Coordinates present: {wof['Lat_Village'].notna().sum():,} / {len(wof)}")
            print(f"   - Region_WOF present: {wof['Region_WOF'].notna().sum():,}")
            print(f"   - Department_WOF present: {wof['Department_WOF'].notna().sum():,}")
            print(f"   - Arrondissement_WOF present: {wof['Arrondissement_WOF'].notna().sum():,}")

            # Show sample of WOF data
            print(f"\n📝 Sample WOF records (first 10):")  # noqa: F541
            for i, row in wof.head(10).iterrows():
                village = row.get("Village", "N/A")[:50] if pd.notna(row.get("Village")) else "N/A"
                region = row.get("Region_WOF", "N/A") if pd.notna(row.get("Region_WOF")) else "N/A"
                dept = row.get("Department_WOF", "N/A") if pd.notna(row.get("Department_WOF")) else "N/A"
                arr = row.get("Arrondissement_WOF", "N/A") if pd.notna(row.get("Arrondissement_WOF")) else "N/A"
                lat = row.get("Lat_Village", "N/A") if pd.notna(row.get("Lat_Village")) else "N/A"
                lon = row.get("Lon_Village", "N/A") if pd.notna(row.get("Lon_Village")) else "N/A"
                print(f"   {i+1}. Village: {village}")
                print(f"      Region ID: {region}, Dept ID: {dept}, Type: {arr}")
                if lat != "N/A" and lon != "N/A":
                    print(f"      Coords: ({lat:.4f}, {lon:.4f})")
                print()

            # Drop records without coordinates
            before_drop = len(wof)
            wof = wof.dropna(subset=["Lat_Village", "Lon_Village"])
            after_drop = len(wof)

            print(f"\n🗑️ Dropped {before_drop - after_drop} records without coordinates")
            print(f"✅ Final WOF dataset: {len(wof)} villages/localities with coordinates")

            logger.info(f"Loaded {len(wof)} villages/localities from WOF")

        except Exception as e:
            print(f"❌ ERROR loading WOF file: {e}")
            import traceback
            traceback.print_exc()
            logger.warning(f"Could not load WOF file: {e}")
    else:
        print(f"❌ WOF shapefile NOT FOUND!")  # noqa: F541

    # =========================================================
    # 5. SUMMARY
    # =========================================================
    print("\n" + "="*80)
    print("📊 GEOSPATIAL DATA LOADING SUMMARY")
    print("="*80)
    print(f"✅ ADM1 (Regions):        {len(adm1):>6,} features")
    print(f"✅ ADM2 (Departments):    {len(adm2):>6,} features")
    print(f"✅ ADM3 (Arrondissements):{len(adm3):>6,} features")
    print(f"✅ WOF (Villages):        {len(wof):>6,} features")
    print("="*80)

    # Create mapping from ADM3 arrondissements to departments
    if not adm2.empty and not adm3.empty:
        print("\n🔍 CREATING ARRONDISSEMENT-DEPARTMENT MAPPING:")
        print("-"*50)
        print(f"📋 Need to map {len(adm3)} arrondissements to {len(adm2)} departments")
        print("   (This requires spatial join or manual mapping)")

    # Verify department-region mapping
    print("\n🔍 VERIFYING DEPARTMENT-REGION MAPPING:")
    print("-"*40)
    dept_mapping = get_department_region_mapping()
    total_depts_in_mapping = sum(len(depts) for depts in dept_mapping.values())
    print(f"📋 Department-region mapping has {total_depts_in_mapping} departments across {len(dept_mapping)} regions")

    # Check if ADM2 departments match mapping
    if not adm2.empty:
        adm2_depts = set(adm2["Department"].values)
        mapped_depts = set()
        for depts in dept_mapping.values():
            mapped_depts.update(depts)

        missing_in_mapping = adm2_depts - mapped_depts
        extra_in_mapping = mapped_depts - adm2_depts

        if missing_in_mapping:
            print(f"\n⚠️ Departments in ADM2 but NOT in mapping ({len(missing_in_mapping)}):")
            for dept in sorted(missing_in_mapping)[:10]:
                print(f"   - {dept}")
            if len(missing_in_mapping) > 10:
                print(f"   ... and {len(missing_in_mapping) - 10} more")
        else:
            print(f"\n✅ All {len(adm2_depts)} ADM2 departments found in mapping")

        if extra_in_mapping:
            print(f"\n⚠️ Departments in mapping but NOT in ADM2 ({len(extra_in_mapping)}):")
            for dept in sorted(extra_in_mapping)[:10]:
                print(f"   - {dept}")
            if len(extra_in_mapping) > 10:
                print(f"   ... and {len(extra_in_mapping) - 10} more")

    print("\n" + "="*80)
    print("✅ GEOSPATIAL DATA LOADING COMPLETE")
    print("="*80 + "\n")

    return adm1, adm2, adm3, wof


def get_department_region_mapping() -> Dict[str, list]:
    """
    Get mapping of regions to their departments.
    This matches the ADM1 shapeName values to ADM2 departments.
    """
    mapping = {
        "ADAMAOUA": ["DJEREM", "FARO-ET-DEO", "MAYO-BANYO", "MBERE", "VINA"],
        "CENTRE": ["HAUTE-SANAGA", "LEKIE", "MBAM-ET-INOUBOU", "MBAM-ET-KIM",
                   "MEFOU-ET-AFAMBA", "MEFOU-ET-AKONO", "MFOUNDI", "NYONG-ET-KELLE",
                   "NYONG-ET-MFOUMOU", "NYONG-ET-SO"],
        "EST": ["BOUMBA-ET-NGOKO", "HAUT-NYONG", "KADEI", "LOM-ET-DJEREM"],
        "EXTREME-NORD": ["DIAMARE", "LOGONE-ET-CHARI", "MAYO-DANAY", "MAYO-KANI",
                         "MAYO-SAVA", "MAYO-TSANAGA"],
        "LITTORAL": ["MOUNGO", "NKAM", "SANAGA-MARITIME", "WOURI"],
        "NORD": ["BENOUE", "FARO", "MAYO-LOUTI", "MAYO-REY"],
        "NORD-OUEST": ["BOYO", "BUI", "DONGA-MANTUNG", "MENCHUM", "MEZAM", "MOMO", "NGO-KETUNJIA"],
        "OUEST": ["BAMBOUTOS", "HAUT-NKAM", "HAUTS-PLATEAUX", "KOUNG-KHI",
                  "MENOUA", "MIFI", "NDE", "NOUN"],
        "SUD": ["DJA-ET-LOBO", "MVILA", "OCEAN", "VALLEE-DU-NTEM"],
        "SUD-OUEST": ["FAKO", "KUPE-MANENGUBA", "LEBIALEM", "MANYU", "MEME", "NDIAN"]
    }

    print("\n📋 DEPARTMENT-REGION MAPPING SUMMARY:")
    print("-"*40)
    for region, depts in mapping.items():
        print(f"   {region:15} : {len(depts)} departments")

    return mapping


def get_region_from_department(dept_name: str, adm2: pd.DataFrame = None, adm1: pd.DataFrame = None) -> str:
    """
    Infer region from department name using spatial join or mapping.

    Args:
        dept_name: Department name to find region for
        adm2: DataFrame with department geometries (optional)
        adm1: DataFrame with region geometries (optional)

    Returns:
        Region name or None if not found
    """
    if dept_name is None:
        return None

    # Try exact match from mapping first
    region_mapping = get_department_region_mapping()
    for region, depts in region_mapping.items():
        if dept_name.upper().strip() in depts:
            return region

    return None


def create_arrondissement_mapping(adm3: pd.DataFrame, adm2: pd.DataFrame) -> Dict[str, str]:
    """
    Create mapping from arrondissement names to department names.
    This requires spatial matching since ADM3 doesn't have direct department reference.

    Args:
        adm3: DataFrame with arrondissement geometries
        adm2: DataFrame with department geometries

    Returns:
        Dictionary mapping arrondissement name to department name
    """
    print("\n🔍 CREATING ARRONDISSEMENT TO DEPARTMENT MAPPING")
    print("-"*50)

    if adm3.empty or adm2.empty:
        print("⚠️ Cannot create mapping: ADM2 or ADM3 data is empty")
        return {}

    # Perform spatial join to find which department contains each arrondissement
    # Convert to GeoDataFrames
    adm3_gdf = gpd.GeoDataFrame(adm3, geometry=gpd.points_from_xy(adm3["Lon_Arrondissement"], adm3["Lat_Arrondissement"]))  # noqa: F841
    adm2_gdf = gpd.GeoDataFrame(adm2, geometry=gpd.points_from_xy(adm2["Lon_Department"], adm2["Lat_Department"]))  # noqa: F841

    # Spatial join - find department for each arrondissement
    # Since we only have centroids, we need to use actual geometries
    # For now, return empty mapping
    print("⚠️ Spatial join requires polygon geometries, not just centroids")
    print("   Will need to load ADM3 and ADM2 with full geometries for accurate mapping")

    return {}


# For direct testing
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 TESTING GEOSPATIAL LOADER")
    print("="*80)

    # Load all data
    adm1, adm2, adm3, wof = load_geospatial_data()

    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)

    # Print final stats
    print("\n📊 FINAL STATISTICS:")
    print(f"   Regions: {len(adm1)}")
    print(f"   Departments: {len(adm2)}")
    print(f"   Arrondissements: {len(adm3)}")
    print(f"   Villages: {len(wof)}")

    # Show arrondissements by department (sample)
    if not adm3.empty:
        print(f"\n📋 Sample Arrondissements (first 10):")  # noqa: F541
        for i, row in adm3.head(10).iterrows():
            print(f"   {i+1}. {row['Arrondissement']}")