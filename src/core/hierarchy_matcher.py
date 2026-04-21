"""
cameroon-administrative-data-platform/src/core/hierarchy_matcher.py

Match WOF villages to administrative hierarchy.
"""

import pandas as pd # type: ignore
from .config import config
from .geospatial_loader import get_department_region_mapping
import logging

logger = logging.getLogger(__name__)


def match_hierarchy(wof: pd.DataFrame, adm1: pd.DataFrame, adm2: pd.DataFrame, adm3: pd.DataFrame) -> pd.DataFrame:
    """
    Match WOF villages to the administrative hierarchy.
    Uses exact matching and fallback to department-based assignment.
    """
    logger.info("Matching villages to administrative hierarchy...")

    # Create a copy
    df = wof.copy()

    # First attempt: exact matching by name
    df = df.merge(adm1, left_on="Region_WOF", right_on="Region", how="left")
    df = df.merge(adm2, left_on="Department_WOF", right_on="Department", how="left")
    df = df.merge(adm3, left_on="Arrondissement_WOF", right_on="Arrondissement", how="left")

    # For unmatched records, try to match by department name pattern
    unmatched = df[df["Region"].isna()]
    logger.info(f"Matched {len(df) - len(unmatched)} villages directly")

    if len(unmatched) > 0:
        logger.warning(f"{len(unmatched)} villages require hierarchical assignment")

        # Assign based on department mapping
        region_mapping = get_department_region_mapping()

        for idx, row in unmatched.iterrows():
            dept_name = row["Department_WOF"]
            if dept_name and dept_name in config.DEPT_POPULATION_2005:
                # Find region for this department
                for region, depts in region_mapping.items():
                    if dept_name in depts:
                        # Get region centroid
                        region_match = adm1[adm1["Region"] == region]
                        if len(region_match) > 0:
                            df.loc[idx, "Region"] = region
                            df.loc[idx, "Lat_Region"] = region_match.iloc[0]["Lat_Region"]
                            df.loc[idx, "Lon_Region"] = region_match.iloc[0]["Lon_Region"]
                        break

    # Final cleanup
    df = df.dropna(subset=["Region"])
    logger.info(f"Final dataset: {len(df)} villages with valid hierarchy")

    return df