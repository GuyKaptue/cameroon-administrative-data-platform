"""
cameroon-administrative-data-platform/src/core/population_distributor.py

Distribute department-level population to individual villages.
"""

import pandas as pd # type: ignore
import numpy as np # type: ignore
from .config import config
import logging

logger = logging.getLogger(__name__)


def distribute_population(df: pd.DataFrame) -> pd.DataFrame:
    """
    Distribute 2005 population from department totals to individual villages.
    Population is distributed with realistic variation.
    """
    logger.info("Distributing 2005 population to villages...")

    df = df.copy()
    df["population_2005"] = 0

    # Set random seed for reproducibility
    np.random.seed(42)

    # For each department, distribute population to its villages
    for dept, total_pop in config.DEPT_POPULATION_2005.items():
        dept_mask = df["Department_WOF"] == dept
        num_villages = dept_mask.sum()

        if num_villages > 0:
            # Distribute with some variation (not perfectly equal)
            base_pop = total_pop // num_villages
            remainder = total_pop % num_villages

            # Assign populations with variation
            for i, idx in enumerate(df[dept_mask].index):
                variation = np.random.uniform(0.8, 1.2)
                village_pop = int(base_pop * variation)
                if i < remainder:
                    village_pop += 1
                df.loc[idx, "population_2005"] = max(village_pop, 50)  # Minimum 50 people

    logger.info(f"Distributed {df['population_2005'].sum():,.0f} people across {len(df)} villages")

    # Validate against department totals
    logger.info("Department population validation:")
    for dept in list(config.DEPT_POPULATION_2005.keys())[:5]:
        dept_sum = df[df["Department_WOF"] == dept]["population_2005"].sum()
        expected = config.DEPT_POPULATION_2005[dept]
        diff_pct = abs(dept_sum - expected) / expected * 100
        status = "✓" if diff_pct < 5 else "⚠"
        logger.info(f"  {status} {dept}: {dept_sum:,} vs {expected:,} ({diff_pct:.1f}% diff)")

    return df