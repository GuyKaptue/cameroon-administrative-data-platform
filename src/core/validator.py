"""
cameroon-administrative-data-platform/src/core/validator.py

Data Validator for ensuring data integrity and consistency.
"""

import pandas as pd # type: ignore
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate data integrity and consistency."""

    def __init__(self, df: pd.DataFrame, hierarchy: Dict = None):
        self.df = df
        self.hierarchy = hierarchy

    def validate_all(self) -> Dict[str, Any]:
        """Run all validations."""
        results = {
            "total_records": len(self.df),
            "villages_with_coords": self.df[self.df["Lat_Village"].notna()].shape[0],
            "villages_with_postal_code": self.df[self.df["postal_code"].notna()].shape[0],
            "unique_postal_codes": self.df["postal_code"].nunique(),
            "postal_code_format_valid": all(len(str(c)) == 5 and "0" not in str(c)
                                             for c in self.df["postal_code"]),
            "no_zeros_in_postal_codes": all("0" not in str(c) for c in self.df["postal_code"]),
            "population_positive": (self.df["population_2005"] > 0).all(),
            "population_growth_positive": (self.df["population_2025"] > self.df["population_2005"]).all(),
            "issues": []
        }

        # Check for missing values
        missing = self.df.isnull().sum()
        if missing.any():
            results["issues"].append(f"Missing values found: {missing[missing > 0].to_dict()}")

        # Check for negative populations
        for col in self.df.columns:
            if col.startswith("population_"):
                if (self.df[col] < 0).any():
                    results["issues"].append(f"Negative population values in {col}")

        # Check hierarchy consistency if hierarchy is provided
        if self.hierarchy:
            total_villages_in_hierarchy = sum(
                len(arr["villages"])
                for region in self.hierarchy.values()
                for dept in region["departments"].values()
                for arr in dept["arrondissements"].values()
            )

            if total_villages_in_hierarchy != len(self.df):
                results["issues"].append(f"Hierarchy village count mismatch: {total_villages_in_hierarchy} vs {len(self.df)}")

        # Check postal code uniqueness at arrondissement level
        postal_by_arr = self.df.groupby(["Region", "Department_WOF", "Arrondissement_WOF"])["postal_code"].nunique()
        if (postal_by_arr > 1).any():
            results["issues"].append("Some arrondissements have multiple postal codes")

        # Print validation results
        logger.info(f"Total records: {results['total_records']:,}")
        logger.info(f"Villages with coordinates: {results['villages_with_coords']:,} ({results['villages_with_coords']/len(self.df)*100:.1f}%)")
        logger.info(f"Unique postal codes: {results['unique_postal_codes']}")
        logger.info(f"Postal code format valid: {results['postal_code_format_valid']}")

        if results["issues"]:
            logger.warning(f"Issues found: {results['issues']}")
        else:
            logger.info("All validation checks passed!")

        return results