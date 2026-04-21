"""
cameroon-administrative-data-platform/src/core/postal_codes.py

Generate hierarchical 5-digit postal codes based on administrative divisions.
"""

import pandas as pd # type: ignore
from typing import Dict, Tuple, List
from sklearn.cluster import KMeans # type: ignore
import logging

logger = logging.getLogger(__name__)


class PostalCodeGenerator:
    """Generate hierarchical 5-digit postal codes."""

    def __init__(self):
        self.region_codes: Dict[str, int] = {}
        self.dept_codes: Dict[Tuple[str, str], int] = {}
        self.arr_codes: Dict[Tuple[str, str, str], int] = {}

    def generate_geo_codes(self, df: pd.DataFrame, group_cols: List[str], lat_col: str, lon_col: str) -> Dict:
        """Generate geospatial codes (1-9) using clustering."""
        codes = {}

        # Group by the specified columns
        grouped = df.groupby(group_cols)

        for key, sub in grouped:
            coords = sub[[lat_col, lon_col]].dropna().to_numpy()

            if len(coords) == 0:
                codes[key] = 1
            elif len(coords) == 1:
                codes[key] = 1
            else:
                # Number of clusters = min(9, number of items)
                k = min(9, len(coords))
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(coords)
                codes[key] = (kmeans.labels_[0] % 9) + 1

        return codes

    def generate_postal_codes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate 5-digit postal codes for each arrondissement.
        Format: R D A X Y (all digits 1-9, no zeros)
        """
        logger.info("Generating postal codes...")

        df = df.copy()

        # Generate region codes
        regions = sorted(df["Region"].unique())
        region_codes = {region: (i % 9) + 1 for i, region in enumerate(regions)}
        df["RegionCode"] = df["Region"].map(region_codes)

        # Generate department codes (unique within region)
        dept_codes = {}
        for region in regions:
            region_df = df[df["Region"] == region]
            depts = sorted(region_df["Department_WOF"].unique())
            for i, dept in enumerate(depts):
                dept_codes[(region, dept)] = (i % 9) + 1
        df["DeptCode"] = df.apply(lambda r: dept_codes.get((r["Region"], r["Department_WOF"]), 1), axis=1)

        # Generate arrondissement codes (unique within department)
        arr_codes = {}
        unique_arrs = df[["Region", "Department_WOF", "Arrondissement_WOF"]].drop_duplicates()
        for _, row in unique_arrs.iterrows():
            key = (row["Region"], row["Department_WOF"])
            if key not in arr_codes:
                arr_codes[key] = {}
            dept_arrs = df[(df["Region"] == row["Region"]) & (df["Department_WOF"] == row["Department_WOF"])]
            arrs = sorted(dept_arrs["Arrondissement_WOF"].unique())
            for i, arr in enumerate(arrs):
                arr_codes[key][arr] = (i % 9) + 1

        df["ArrCode"] = df.apply(
            lambda r: arr_codes.get((r["Region"], r["Department_WOF"]), {}).get(r["Arrondissement_WOF"], 1),
            axis=1
        )

        # Generate checksum digits from arrondissement centroid
        df["X"] = ((df["Lat_Arrondissement"].fillna(df["Lat_Region"]).fillna(0) * 100) % 9 + 1).astype(int)
        df["Y"] = ((df["Lon_Arrondissement"].fillna(df["Lon_Region"]).fillna(0) * 100) % 9 + 1).astype(int)

        # Ensure X and Y are in 1-9 range
        df["X"] = df["X"].clip(1, 9)
        df["Y"] = df["Y"].clip(1, 9)

        # Generate final 5-digit postal code
        df["postal_code"] = (
            df["RegionCode"].astype(str) +
            df["DeptCode"].astype(str) +
            df["ArrCode"].astype(str) +
            df["X"].astype(str) +
            df["Y"].astype(str)
        )

        # Verify no zeros in postal codes
        if any("0" in code for code in df["postal_code"]):
            logger.warning("Some postal codes contain zeros - fixing...")
            df["postal_code"] = df["postal_code"].str.replace("0", "9")

        # Verify uniqueness at arrondissement level
        unique_codes = df.groupby(["Region", "Department_WOF", "Arrondissement_WOF"])["postal_code"].nunique()
        if (unique_codes > 1).any():
            logger.warning("Some arrondissements have multiple postal codes - fixing...")
            for (region, dept, arr), group in df.groupby(["Region", "Department_WOF", "Arrondissement_WOF"]):
                first_code = group["postal_code"].iloc[0]
                mask = (df["Region"] == region) & (df["Department_WOF"] == dept) & (df["Arrondissement_WOF"] == arr)
                df.loc[mask, "postal_code"] = first_code

        logger.info(f"Generated {df['postal_code'].nunique()} unique postal codes")

        return df