"""
cameroon-administrative-data-platform/src/core/data_exporter.py

Data Exporter for handling various data export formats and structures.
"""

import json
import pandas as pd # type: ignore
from pathlib import Path
from typing import Dict
from datetime import datetime
from .config import config
import logging

logger = logging.getLogger(__name__)


class DataExporter:
    """Export data to various formats."""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_csv(self, df: pd.DataFrame, filename: str = "cameroon_complete_dataset.csv") -> Path:
        """Export flattened dataset to CSV."""
        filepath = self.output_dir / filename

        # Select columns for export
        export_cols = ["Region", "Department_WOF", "Arrondissement_WOF", "Village",
                       "postal_code", "Lat_Village", "Lon_Village",
                       "Lat_Arrondissement", "Lon_Arrondissement",
                       "Lat_Department", "Lon_Department", "Lat_Region", "Lon_Region"]

        # Add population columns
        for year in config.YEARS:
            export_cols.append(f"population_{year}")

        export_df = df[export_cols].copy()
        export_df = export_df.rename(columns={
            "Department_WOF": "Department",
            "Arrondissement_WOF": "Arrondissement"
        })

        export_df.to_csv(filepath, index=False, encoding="utf-8")
        logger.info(f"Exported CSV to {filepath}")
        return filepath

    def export_json(self, hierarchy: Dict, filename: str = "cameroon_hierarchy.json") -> Path:
        """Export hierarchical structure to JSON."""
        filepath = self.output_dir / filename

        output = {
            "metadata": {
                "source": "Cameroon RGPH 2005, WOF Localities, GeoBoundaries",
                "generated_date": datetime.now().isoformat(),
                "years": config.YEARS,
                "total_regions": len(hierarchy),
                "postal_code_format": "5 digits (1-9 only)",
                "postal_code_structure": "R D A X Y (Region, Dept, Arrondissement, Checksum)"
            },
            "hierarchy": hierarchy
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"Exported JSON to {filepath}")
        return filepath

    def export_by_year(self, df: pd.DataFrame) -> None:
        """Export separate CSV files for each year."""
        for year in config.YEARS:
            year_df = df[["Village", "Department_WOF", "Arrondissement_WOF", "Region",
                          "postal_code", f"population_{year}", "Lat_Village", "Lon_Village"]].copy()
            year_df = year_df.rename(columns={
                f"population_{year}": "population",
                "Department_WOF": "Department",
                "Arrondissement_WOF": "Arrondissement"
            })
            year_df["year"] = year

            filepath = self.output_dir / f"population_{year}.csv"
            year_df.to_csv(filepath, index=False, encoding="utf-8")

        logger.info(f"Exported {len(config.YEARS)} year-specific files")

    def export_summary(self, df: pd.DataFrame, hierarchy: Dict) -> Path:
        """Export summary statistics."""
        summary = {
            "total_villages": len(df),
            "total_regions": len(hierarchy),
            "total_departments": sum(len(region["departments"]) for region in hierarchy.values()),
            "total_arrondissements": sum(
                len(dept["arrondissements"])
                for region in hierarchy.values()
                for dept in region["departments"].values()
            ),
            "unique_postal_codes": df["postal_code"].nunique(),
            "population_by_year": {},
            "population_by_region": {}
        }

        # Population by year
        for year in config.YEARS:
            summary["population_by_year"][str(year)] = int(df[f"population_{year}"].sum())

        # Population by region for 2025
        for region in df["Region"].unique():
            region_pop = df[df["Region"] == region]["population_2025"].sum()
            summary["population_by_region"][region] = int(region_pop)

        filepath = self.output_dir / "summary.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Exported summary to {filepath}")
        return filepath

    def generate_report(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate a comprehensive report."""
        report = []

        for region in df["Region"].unique():
            region_df = df[df["Region"] == region]

            for year in config.YEARS:
                report.append({
                    "region": region,
                    "year": int(year),
                    "population": int(region_df[f"population_{year}"].sum()),
                    "num_departments": region_df["Department_WOF"].nunique(),
                    "num_arrondissements": region_df["Arrondissement_WOF"].nunique(),
                    "num_villages": len(region_df),
                })

        report_df = pd.DataFrame(report)
        report_path = self.output_dir / "population_report.csv"
        report_df.to_csv(report_path, index=False)

        return report_df