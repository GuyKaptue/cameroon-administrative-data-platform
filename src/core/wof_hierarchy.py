#!/usr/bin/env python3
"""
cameroon_population_pipeline/src/core/wof_hierarchy.py

Build administrative hierarchy directly from WOF data.
WOF contains all levels: region (placetype=region), department (county), and locality/village.
"""

import pandas as pd
import geopandas as gpd
from typing import Dict
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WOFHierarchyBuilder:
    """
    Build administrative hierarchy directly from Who's On First data.
    WOF already contains region, department, and locality information.
    """

    def __init__(self, wof_shp_path: Path):
        self.wof_path = wof_shp_path
        self.wof_gdf = None
        self.hierarchy = {}

    def load_wof_data(self) -> pd.DataFrame:
        """Load WOF shapefile and prepare for hierarchy extraction"""
        print("\n" + "="*60)
        print("📍 LOADING WOF HIERARCHY DATA")
        print("="*60)

        if not self.wof_path.exists():
            print(f"❌ WOF file not found: {self.wof_path}")
            return pd.DataFrame()

        self.wof_gdf = gpd.read_file(self.wof_path)

        # Normalize column names
        self.wof_gdf.columns = [c.lower().replace(":", "_") for c in self.wof_gdf.columns]

        print(f"✅ Loaded {len(self.wof_gdf)} features from WOF")
        print(f"\n📋 Available columns: {list(self.wof_gdf.columns)}")

        # Show placetype distribution
        if "placetype" in self.wof_gdf.columns:
            print("\n📊 Placetype distribution:")
            placetype_counts = self.wof_gdf["placetype"].value_counts()
            for pt, count in placetype_counts.items():
                print(f"   {pt:15}: {count:5,} features")

        return self.wof_gdf

    def extract_regions(self) -> pd.DataFrame:
        """Extract regions from WOF data (placetype='region')"""
        print("\n" + "-"*60)
        print("🏛️ Extracting Regions from WOF")
        print("-"*60)

        if self.wof_gdf is None:
            return pd.DataFrame()

        # Filter for regions
        regions = self.wof_gdf[self.wof_gdf["placetype"] == "region"].copy()

        if len(regions) == 0:
            # Try alternative: look for features with region_id but no county_id
            regions = self.wof_gdf[self.wof_gdf["region_id"].notna() & self.wof_gdf["county_id"].isna()].copy()

        if len(regions) > 0:
            regions["Region"] = regions["name"].str.upper().str.strip()
            regions["Lat_Region"] = regions["lat"]
            regions["Lon_Region"] = regions["lon"]

            print(f"✅ Found {len(regions)} regions:")
            for _, row in regions.iterrows():
                print(f"   • {row['Region']} (ID: {row.get('region_id', 'N/A')})")

            return regions[["Region", "Lat_Region", "Lon_Region", "region_id"]]
        else:
            print("⚠️ No regions found in WOF data")
            return pd.DataFrame()

    def extract_departments(self) -> pd.DataFrame:
        """Extract departments from WOF data (using county_id or placetype='county')"""
        print("\n" + "-"*60)
        print("📁 Extracting Departments from WOF")
        print("-"*60)

        if self.wof_gdf is None:
            return pd.DataFrame()

        # Filter for departments (county level)
        departments = self.wof_gdf[self.wof_gdf["county_id"].notna()].copy()

        # Remove duplicates by county_id (take first occurrence)
        if len(departments) > 0 and "county_id" in departments.columns:
            departments = departments.drop_duplicates(subset=["county_id"])
            departments["Department"] = departments["name"].str.upper().str.strip()
            departments["Lat_Department"] = departments["lat"]
            departments["Lon_Department"] = departments["lon"]

            print(f"✅ Found {len(departments)} departments")
            print(f"   Sample departments: {list(departments['Department'].head(10).values)}")

            return departments[["Department", "Lat_Department", "Lon_Department", "county_id", "region_id"]]
        else:
            print("⚠️ No departments found in WOF data")
            return pd.DataFrame()

    def extract_localities(self) -> pd.DataFrame:
        """Extract villages/localities from WOF data"""
        print("\n" + "-"*60)
        print("🏘️ Extracting Villages/Localities from WOF")
        print("-"*60)

        if self.wof_gdf is None:
            return pd.DataFrame()

        # Filter for localities, villages, towns
        locality_types = ["locality", "village", "town", "city", "hamlet"]
        localities = self.wof_gdf[self.wof_gdf["placetype"].isin(locality_types)].copy()

        if len(localities) == 0:
            # Fallback: take all features with coordinates
            localities = self.wof_gdf[self.wof_gdf["lat"].notna() & self.wof_gdf["lon"].notna()].copy()

        localities["Village"] = localities["name"].str.upper().str.strip()
        localities["Lat_Village"] = localities["lat"]
        localities["Lon_Village"] = localities["lon"]

        # Map to region and department using IDs
        localities["region_id"] = localities.get("region_id", None)
        localities["county_id"] = localities.get("county_id", None)

        print(f"✅ Found {len(localities)} villages/localities")

        return localities[["Village", "Lat_Village", "Lon_Village", "region_id", "county_id", "placetype"]]

    def build_complete_hierarchy(self) -> pd.DataFrame:
        """Build complete hierarchy by joining regions, departments, and localities"""
        print("\n" + "="*60)
        print("🔗 BUILDING COMPLETE HIERARCHY")
        print("="*60)

        # Extract each level
        regions_df = self.extract_regions()
        departments_df = self.extract_departments()
        localities_df = self.extract_localities()

        if regions_df.empty or departments_df.empty or localities_df.empty:
            print("❌ Missing required data for hierarchy")
            return pd.DataFrame()

        # Join localities with departments using county_id
        print("\n📍 Joining localities to departments...")
        df = localities_df.merge(
            departments_df[["Department", "Lat_Department", "Lon_Department", "county_id", "region_id"]],
            on="county_id",
            how="left"
        )

        # Join with regions using region_id
        print("📍 Joining to regions...")
        df = df.merge(
            regions_df[["Region", "Lat_Region", "Lon_Region", "region_id"]],
            on="region_id",
            how="left"
        )

        # Fill missing arrondissement (use department name as fallback)
        df["Arrondissement_WOF"] = df.get("Arrondissement_WOF", df["Department"])
        df["Lat_Arrondissement"] = df["Lat_Department"]
        df["Lon_Arrondissement"] = df["Lon_Department"]

        # Clean up
        df = df.dropna(subset=["Region", "Department", "Lat_Village", "Lon_Village"])

        print(f"\n✅ Built hierarchy with {len(df)} villages")
        print(f"   • Regions: {df['Region'].nunique()}")
        print(f"   • Departments: {df['Department'].nunique()}")

        # Show distribution
        print("\n📊 Region distribution:")
        region_counts = df["Region"].value_counts()
        for region, count in region_counts.items():
            print(f"   {region:20}: {count:5,} villages")

        return df


def get_department_mapping_from_wof(wof_gdf: pd.DataFrame) -> Dict[str, str]:
    """
    Create mapping from WOF county_id to department name
    """
    mapping = {}

    if wof_gdf is not None and "county_id" in wof_gdf.columns:
        depts = wof_gdf[wof_gdf["county_id"].notna()].drop_duplicates(subset=["county_id"])
        for _, row in depts.iterrows():
            county_id = row["county_id"]
            dept_name = row["name"].upper().strip() if row["name"] else None
            if dept_name:
                mapping[county_id] = dept_name

    return mapping


def get_region_mapping_from_wof(wof_gdf: pd.DataFrame) -> Dict[str, str]:
    """
    Create mapping from WOF region_id to region name
    """
    mapping = {}

    if wof_gdf is not None and "region_id" in wof_gdf.columns:
        regions = wof_gdf[wof_gdf["region_id"].notna()].drop_duplicates(subset=["region_id"])
        for _, row in regions.iterrows():
            region_id = row["region_id"]
            region_name = row["name"].upper().strip() if row["name"] else None
            if region_name:
                mapping[region_id] = region_name

    return mapping