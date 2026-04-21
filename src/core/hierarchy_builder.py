"""
cameroon-administrative-data-platform/src/core/hierarchy_builder.py

Build nested administrative hierarchy from flattened dataframe.
"""

import pandas as pd # type: ignore
from typing import Dict, Any
from .config import config
import logging

logger = logging.getLogger(__name__)


def build_hierarchy(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Build nested hierarchical structure:
    Region → Department → Arrondissement → Villages

    Returns:
        Nested dictionary with complete hierarchy and population data
    """
    logger.info("Building hierarchical structure...")

    hierarchy = {}
    years = config.YEARS

    for _, row in df.iterrows():
        region = row["Region"]
        dept = row["Department_WOF"]
        arr = row["Arrondissement_WOF"] if pd.notna(row["Arrondissement_WOF"]) else "CENTRAL"

        if region not in hierarchy:
            hierarchy[region] = {
                "lat": float(row["Lat_Region"]) if pd.notna(row["Lat_Region"]) else None,
                "lon": float(row["Lon_Region"]) if pd.notna(row["Lon_Region"]) else None,
                "departments": {}
            }

        if dept not in hierarchy[region]["departments"]:
            hierarchy[region]["departments"][dept] = {
                "lat": float(row["Lat_Department"]) if pd.notna(row["Lat_Department"]) else None,
                "lon": float(row["Lon_Department"]) if pd.notna(row["Lon_Department"]) else None,
                "arrondissements": {}
            }

        if arr not in hierarchy[region]["departments"][dept]["arrondissements"]:
            hierarchy[region]["departments"][dept]["arrondissements"][arr] = {
                "lat": float(row["Lat_Arrondissement"]) if pd.notna(row["Lat_Arrondissement"]) else None,
                "lon": float(row["Lon_Arrondissement"]) if pd.notna(row["Lon_Arrondissement"]) else None,
                "postal_code": row["postal_code"],
                "villages": []
            }

        # Add village data
        village_data = {
            "name": row["Village"],
            "lat": float(row["Lat_Village"]) if pd.notna(row["Lat_Village"]) else None,
            "lon": float(row["Lon_Village"]) if pd.notna(row["Lon_Village"]) else None,
            "population": {
                str(year): int(row[f"population_{year}"]) for year in years
            }
        }

        hierarchy[region]["departments"][dept]["arrondissements"][arr]["villages"].append(village_data)

    logger.info(f"Built hierarchy with {len(hierarchy)} regions")

    return hierarchy


def flatten_hierarchy(hierarchy: Dict) -> pd.DataFrame:
    """Convert hierarchy back to flattened dataframe."""
    rows = []
    years = config.YEARS

    for region, region_data in hierarchy.items():
        for dept, dept_data in region_data["departments"].items():
            for arr, arr_data in dept_data["arrondissements"].items():
                for village in arr_data["villages"]:
                    row = {
                        "Region": region,
                        "Department": dept,
                        "Arrondissement": arr,
                        "Village": village["name"],
                        "postal_code": arr_data["postal_code"],
                        "Lat_Region": region_data["lat"],
                        "Lon_Region": region_data["lon"],
                        "Lat_Department": dept_data["lat"],
                        "Lon_Department": dept_data["lon"],
                        "Lat_Arrondissement": arr_data["lat"],
                        "Lon_Arrondissement": arr_data["lon"],
                        "Lat_Village": village["lat"],
                        "Lon_Village": village["lon"],
                    }

                    for year in years:
                        row[f"population_{year}"] = village["population"].get(str(year), 0)

                    rows.append(row)

    return pd.DataFrame(rows)