"""
cameroon-administrative-data-platform/src/core/population_simulator.py

Hierarchical Population Simulation for Cameroon (2005 → 2025)
Mathematical model: Village → Arrondissement → Department → Region → National

Based on:
- config.py: NATIONAL_POPULATION, DEPT_POPULATION_2005, GROWTH_RATES
- optimized_parameters.py: Regional multipliers, urbanization targets, city constraints
- Actual 2005 and 2010 arrondissement census data
"""

import pandas as pd
from .optimized_parameters import (
    REGIONAL_MULTIPLIERS_OPTIMIZED,
    REGIONAL_TARGETS_2026,
    MAJOR_CITIES_2025,
    CITY_DEPARTMENT_MAP,
    UN_POPULATION_TARGETS,
    PERIOD_GROWTH_RATES,
    URBANIZATION_TARGETS,
    VALIDATION_THRESHOLDS,
    MODEL_PARAMETERS,
    REGIONAL_URBANIZATION_2005,
    REGIONAL_FERTILITY_INDICES,
    REGIONAL_MORTALITY_INDICES,
    get_arrondissement_population_2005,
    get_arrondissement_population_2010,
    calculate_arrondissement_growth_rates,
)
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


class HierarchicalPopulationSimulator:
    """
    Hierarchical population simulation with BOTTOM-UP approach:
    Village → Arrondissement → Department → Region → National

    Levels:
    L4: Villages (13,436+ villages) - base unit with rural/urban classification
    L3: Arrondissements (360) - aggregate from villages, calibrated with 2005-2010 census
    L2: Departments (58) - aggregate from arrondissements
    L1: Regions (10) - aggregate from departments
    L0: Country (Cameroon) - aggregate from regions, constrained by UN targets
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize simulator with village-level data.

        Args:
            df: DataFrame with columns:
                - Village, Region, Department_WOF, Arrondissement_WOF
                - Lat/Lon coordinates
                - population_2005 (to be distributed)
        """
        self.df = df.copy()
        self.years = [2005, 2010, 2015, 2020, 2025]

        # National constraints
        self.national_pop = UN_POPULATION_TARGETS
        self.growth_rates = PERIOD_GROWTH_RATES

        # Regional parameters
        self.regional_multipliers = REGIONAL_MULTIPLIERS_OPTIMIZED
        self.regional_targets = REGIONAL_TARGETS_2026
        self.regional_urbanization_2005 = REGIONAL_URBANIZATION_2005
        self.fertility_indices = REGIONAL_FERTILITY_INDICES
        self.mortality_indices = REGIONAL_MORTALITY_INDICES

        # City constraints
        self.major_cities = MAJOR_CITIES_2025
        self.city_department_map = CITY_DEPARTMENT_MAP

        # Urbanization targets
        self.urbanization_targets = URBANIZATION_TARGETS

        # Model parameters
        self.model_params = MODEL_PARAMETERS

        # Validation thresholds
        self.thresholds = VALIDATION_THRESHOLDS

        # Census data for calibration
        self.arr_pop_2005 = get_arrondissement_population_2005()
        self.arr_pop_2010 = get_arrondissement_population_2010()
        self.arr_growth_rates = calculate_arrondissement_growth_rates()

        # Will be populated during simulation
        self.village_urban_frac = {}
        self.arr_urban_frac = {}

        # Pre-compute village characteristics
        self._initialize_village_characteristics()

    def _initialize_village_characteristics(self):
        """Initialize village-level urban/rural classification and weights."""
        print("\n   🌾 Initializing village characteristics...")

        # Calculate initial village weights based on population distribution
        for idx in self.df.index:
            village = self.df.loc[idx, "Village"]  # noqa: F841
            arr_name = self.df.loc[idx, "Arrondissement_WOF"]

            # Get arrondissement population if available
            arr_pop_2005 = self.arr_pop_2005.get(arr_name.upper(), 0)  # noqa: F841

            # Initial weight: equal distribution within arrondissement
            # Will be refined during simulation
            self.village_urban_frac[idx] = 0.3  # Default rural

        # Calculate arrondissement urbanization fractions
        for arr in self.df["Arrondissement_WOF"].unique():
            arr_mask = self.df["Arrondissement_WOF"] == arr
            dept = self.df.loc[arr_mask, "Department_WOF"].iloc[0] if arr_mask.sum() > 0 else None

            # Check if arrondissement contains a major city
            if dept and dept in self.city_department_map.values():
                self.arr_urban_frac[arr] = 0.8  # Urban arrondissement
            else:
                # Rural arrondissement
                self.arr_urban_frac[arr] = 0.2

    # =========================================================
    # BOTTOM-UP: Village Level Distribution
    # =========================================================

    def distribute_population_to_villages_2005(self) -> pd.DataFrame:
        """
        Distribute 2005 population from arrondissement totals to villages.

        This is the FOUNDATION of the simulation. All subsequent calculations
        aggregate up from this village-level distribution.
        """
        print("\n" + "="*60)
        print("👥 DISTRIBUTING 2005 POPULATION TO VILLAGES")
        print("="*60)

        df = self.df.copy()
        df["population_2005"] = 0

        matched_arrs = 0
        total_arr_pop = 0

        # Distribute population for each arrondissement
        for arr_name, arr_pop_2005 in tqdm(self.arr_pop_2005.items(), desc="   Distributing by arrondissement", unit="arr"):
            # Find villages in this arrondissement
            arr_mask = df["Arrondissement_WOF"].str.upper().str.strip() == arr_name.upper().strip()
            n_villages = arr_mask.sum()

            if n_villages > 0 and arr_pop_2005 > 0:
                matched_arrs += 1
                total_arr_pop += arr_pop_2005

                # Calculate weights for villages in this arrondissement
                # Weighted by: urban/rural classification + population capacity
                weights = []
                for idx in df[arr_mask].index:
                    # Base weight: 1 for all villages
                    weight = 1.0

                    # Adjust for urban/rural preference
                    # Urban centers get higher weight (more population density)
                    if self.arr_urban_frac.get(arr_name, 0.2) > 0.5:
                        # Urban arrondissement - favor larger settlements
                        village_name = df.loc[idx, "Village"]
                        if any(city in village_name.upper() for city in ["YAOUNDE", "DOUALA", "GAROUA", "MAROUA"]):
                            weight = 3.0  # Major city
                        elif len(village_name) < 15:  # Shorter names often indicate towns
                            weight = 1.5
                    else:
                        # Rural arrondissement - more equal distribution
                        weight = 1.0

                    weights.append(weight)

                # Normalize weights
                total_weight = sum(weights)
                if total_weight > 0:
                    weights = [w / total_weight for w in weights]

                    # Distribute population
                    for idx, weight in zip(df[arr_mask].index, weights):
                        df.loc[idx, "population_2005"] = int(round(arr_pop_2005 * weight))

        print(f"\n   ✅ Matched {matched_arrs} / {len(self.arr_pop_2005)} arrondissements")
        print(f"   📊 TOTAL 2005 POPULATION: {df['population_2005'].sum():,.0f}")

        # Scale to match UN target if needed
        un_target_2005 = self.national_pop[2005]
        total_sim = df["population_2005"].sum()

        if total_sim > 0 and abs(total_sim - un_target_2005) / un_target_2005 > 0.01:
            scaling = un_target_2005 / total_sim
            print(f"\n   Scaling to match UN target (factor: {scaling:.3f})")
            df["population_2005"] = (df["population_2005"] * scaling).round(0).astype(int)

        return df

    # =========================================================
    # BOTTOM-UP: Aggregation Functions
    # =========================================================

    def aggregate_to_arrondissements(self, df: pd.DataFrame, year: int) -> dict:
        """Aggregate village populations to arrondissement level."""
        arr_pop = {}
        for arr in df["Arrondissement_WOF"].unique():
            mask = df["Arrondissement_WOF"] == arr
            arr_pop[arr] = df.loc[mask, f"population_{year}"].sum()
        return arr_pop

    def aggregate_to_departments(self, df: pd.DataFrame, year: int) -> dict:
        """Aggregate village populations to department level."""
        dept_pop = {}
        for dept in df["Department_WOF"].unique():
            mask = df["Department_WOF"] == dept
            dept_pop[dept] = df.loc[mask, f"population_{year}"].sum()
        return dept_pop

    def aggregate_to_regions(self, df: pd.DataFrame, year: int) -> dict:
        """Aggregate village populations to region level."""
        region_pop = {}
        for region in df["Region"].unique():
            mask = df["Region"] == region
            region_pop[region] = df.loc[mask, f"population_{year}"].sum()
        return region_pop

    # =========================================================
    # BOTTOM-UP: Village Growth Simulation
    # =========================================================

    def get_village_growth_factor(self, village_pop: float, arr_avg_pop: float,
                                   village_name: str, t: int, t_next: int) -> float:
        """
        Calculate growth factor for an individual village.

        Factors:
        - Rural areas grow slower (out-migration)
        - Urban centers grow faster (in-migration)
        - Major cities get additional boost
        """
        # Base growth (national rate)
        G_base = self.national_pop[t_next] / self.national_pop[t]

        # Rural-urban migration factor
        if village_pop > arr_avg_pop * 2:
            # Large settlement - likely urban
            migration_factor = 1.05  # 5% higher growth
        elif village_pop < arr_avg_pop * 0.5:
            # Small settlement - likely rural
            migration_factor = 0.95  # 5% lower growth
        else:
            migration_factor = 1.0

        # Major city boost
        city_boost = 1.0
        major_cities = ["YAOUNDE", "DOUALA", "GAROUA", "MAROUA", "BAMENDA", "NGAOUNDERE"]
        if any(city in village_name.upper() for city in major_cities):
            city_boost = 1.03  # 3% additional growth for major cities

        return G_base * migration_factor * city_boost

    def simulate_villages_bottom_up(self, df: pd.DataFrame, t: int, t_next: int) -> pd.DataFrame:
        """
        Simulate village population growth BOTTOM-UP.

        Each village grows independently based on its characteristics,
        then we aggregate up for validation.
        """
        df = df.copy()

        # Calculate average village population per arrondissement at time t
        arr_avg_pops = {}
        for arr in df["Arrondissement_WOF"].unique():
            mask = df["Arrondissement_WOF"] == arr
            arr_avg_pops[arr] = df.loc[mask, f"population_{t}"].mean()

        # Simulate each village
        for idx in df.index:
            current_pop = df.loc[idx, f"population_{t}"]
            if current_pop > 0:
                arr = df.loc[idx, "Arrondissement_WOF"]
                arr_avg = arr_avg_pops.get(arr, current_pop)
                village_name = df.loc[idx, "Village"]

                G_v = self.get_village_growth_factor(current_pop, arr_avg, village_name, t, t_next)
                df.loc[idx, f"population_{t_next}"] = int(round(current_pop * G_v))
            else:
                df.loc[idx, f"population_{t_next}"] = 0

        return df

    # =========================================================
    # TOP-DOWN: Constraint Application
    # =========================================================

    def apply_national_constraint(self, df: pd.DataFrame, t_next: int) -> pd.DataFrame:
        """
        Apply national constraint by scaling all villages uniformly.
        This ensures the total matches UN targets.
        """
        total_sim = df[f"population_{t_next}"].sum()
        total_target = self.national_pop[t_next]

        if total_sim > 0 and abs(total_sim - total_target) / total_target > 0.001:
            scaling = total_target / total_sim
            df[f"population_{t_next}"] = (df[f"population_{t_next}"] * scaling).round(0).astype(int)

        return df

    def apply_regional_constraint(self, df: pd.DataFrame, t: int, t_next: int) -> pd.DataFrame:
        """
        Apply regional growth factors to constrain regional totals.
        """
        df = df.copy()

        # Calculate regional populations at time t
        region_pops_t = self.aggregate_to_regions(df, t)

        for region in df["Region"].unique():
            region_mask = df["Region"] == region
            current_region_pop = region_pops_t.get(region, 0)

            if current_region_pop > 0:
                # Calculate regional growth factor
                G_region = self.compute_regional_growth_factor(region, t, t_next)
                target_region_pop = current_region_pop * G_region

                # Scale villages in this region
                current_sim = df.loc[region_mask, f"population_{t_next}"].sum()
                if current_sim > 0:
                    scaling = target_region_pop / current_sim
                    df.loc[region_mask, f"population_{t_next}"] = (
                        df.loc[region_mask, f"population_{t_next}"] * scaling
                    ).round(0).astype(int)

        return df

    def compute_regional_growth_factor(self, region: str, t: int, t_next: int) -> float:
        """Compute regional growth factor with demographic factors."""
        G_c = self.national_pop[t_next] / self.national_pop[t]

        # Fertility factor
        fert_idx = self.fertility_indices.get(region, 1.0)
        F_fert = 1 + self.model_params["alpha_fert"] * (fert_idx - 1)

        # Mortality factor
        mort_idx = self.mortality_indices.get(region, 1.0)
        F_mort = 1 - self.model_params["alpha_mort"] * (mort_idx - 1)

        # Urbanization factor
        U_r_t = self.get_regional_urbanization(region, t)
        U_c_t = self.get_national_urbanization(t)
        F_urban = 1 + self.model_params["alpha_urban"] * (U_r_t - U_c_t)

        # Regional multiplier
        m_r = self.regional_multipliers.get(region, 1.0)

        return G_c * F_fert * F_mort * F_urban * m_r

    def get_regional_urbanization(self, region: str, t: int) -> float:
        """Calculate regional urbanization rate."""
        U_r_2005 = self.regional_urbanization_2005.get(region, 0.3)
        multiplier = self.regional_multipliers.get(region, 1.0)
        trend = (multiplier - 1.0) * 0.05
        U_r_t = U_r_2005 + trend * (t - 2005) / 20
        return max(0.0, min(1.0, U_r_t))

    def get_national_urbanization(self, t: int) -> float:
        """Get national urbanization target."""
        return self.urbanization_targets.get(t, 0.5)

    # =========================================================
    # 2010 Calibration (Critical for accuracy)
    # =========================================================

    def calibrate_with_2010_census(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calibrate 2010 populations using actual arrondissement census data.
        This is applied AFTER bottom-up simulation but BEFORE constraint application.
        """
        print("\n   📊 Calibrating with 2010 census data...")
        print(f"      Using {len(self.arr_pop_2010)} arrondissement records")

        df = df.copy()
        calibrated = 0

        for arr_name, pop_2010_census in tqdm(self.arr_pop_2010.items(), desc="   Applying 2010 data", unit="arr"):
            arr_mask = df["Arrondissement_WOF"].str.upper().str.strip() == arr_name.upper().strip()

            if arr_mask.sum() > 0:
                calibrated += 1
                current_sum = df.loc[arr_mask, "population_2010"].sum()

                if current_sum > 0:
                    factor = pop_2010_census / current_sum
                    factor = max(0.5, min(2.0, factor))  # Limit extreme adjustments
                    df.loc[arr_mask, "population_2010"] = (
                        df.loc[arr_mask, "population_2010"] * factor
                    ).round(0).astype(int)

        print(f"      ✅ Calibrated {calibrated} / {len(self.arr_pop_2010)} arrondissements")

        # Apply national constraint after calibration
        df = self.apply_national_constraint(df, 2010)

        return df

    # =========================================================
    # City Constraints (2025)
    # =========================================================

    def apply_city_constraints(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply major city population targets for 2025."""
        print("\n   🏙️ Applying city constraints...")
        df = df.copy()

        for city_name, target_pop in self.major_cities.items():
            # Find villages belonging to this city
            city_mask = df["Village"].str.contains(city_name, case=False, na=False)

            # Fallback to department mapping
            if city_mask.sum() == 0 and city_name in self.city_department_map:
                dept = self.city_department_map[city_name]
                city_mask = df["Department_WOF"] == dept

            if city_mask.sum() > 0:
                current_pop = df.loc[city_mask, "population_2025"].sum()
                if current_pop > 0 and current_pop < target_pop * 0.8:
                    lambda_m = min(1.5, target_pop / current_pop)
                    df.loc[city_mask, "population_2025"] = (
                        df.loc[city_mask, "population_2025"] * lambda_m
                    ).round(0).astype(int)
                    print(f"      {city_name}: {current_pop:,.0f} → {df.loc[city_mask, 'population_2025'].sum():,.0f} (λ={lambda_m:.3f})")

        return df

    # =========================================================
    # Validation
    # =========================================================

    def validate_simulation(self, df: pd.DataFrame):
        """Validate simulation results at all hierarchical levels."""
        print("\n" + "="*60)
        print("✅ VALIDATION RESULTS")
        print("="*60)

        all_valid = True

        # 1. National level validation
        print("\n   📊 National Population Validation:")
        for year in self.years:
            simulated = df[f"population_{year}"].sum()
            target = self.national_pop.get(year, 0)
            if target > 0:
                diff_pct = abs(simulated - target) / target * 100
                status = "✅" if diff_pct < self.thresholds["national_diff_percent"] else "⚠️"
                if status == "⚠️":
                    all_valid = False
                print(f"      {status} {year}: {simulated:12,.0f} vs UN {target:12,.0f} (diff: {diff_pct:.1f}%)")

        # 2. Regional level validation (2025)
        print("\n   📊 Regional Validation (2025):")
        region_pops = self.aggregate_to_regions(df, 2025)
        for region, target in self.regional_targets.items():
            sim_pop = region_pops.get(region, 0)
            if target > 0:
                diff_pct = abs(sim_pop - target) / target * 100
                status = "✅" if diff_pct < self.thresholds["regional_diff_percent"] else "⚠️"
                if status == "⚠️":
                    all_valid = False
                print(f"      {status} {region:15}: {sim_pop:12,.0f} vs {target:12,.0f} (diff: {diff_pct:.1f}%)")

        # 3. Urbanization validation
        print("\n   🏙️ Urbanization Validation:")
        for year in [2005, 2010, 2015, 2020, 2025]:
            if year in self.urbanization_targets:
                urban_pop = 0
                total_pop = 0
                for arr in df["Arrondissement_WOF"].unique():
                    arr_mask = df["Arrondissement_WOF"] == arr
                    arr_pop = df.loc[arr_mask, f"population_{year}"].sum()
                    urban_frac = self.arr_urban_frac.get(arr, 0.2)
                    urban_pop += arr_pop * urban_frac
                    total_pop += arr_pop

                sim_urban = urban_pop / total_pop if total_pop > 0 else 0
                target_urban = self.urbanization_targets[year]
                diff_pct = abs(sim_urban - target_urban) / target_urban * 100
                status = "✅" if diff_pct < self.thresholds["urbanization_diff_percent"] else "⚠️"
                if status == "⚠️":
                    all_valid = False
                print(f"      {status} {year}: {sim_urban*100:.1f}% vs {target_urban*100:.1f}% (diff: {diff_pct:.1f}%)")

        return all_valid

    # =========================================================
    # Main Simulation Pipeline (BOTTOM-UP)
    # =========================================================

    def simulate(self) -> pd.DataFrame:
        """
        Complete BOTTOM-UP hierarchical simulation from 2005 to 2025.

        Pipeline:
        1. Distribute 2005 population to villages (from arrondissement census)
        2. For each period (2005-2010, 2010-2015, 2015-2020, 2020-2025):
           a. Simulate village growth (bottom-up)
           b. Apply regional constraints (top-down)
           c. Apply national constraint (top-down)
        3. Calibrate 2010 with actual census data
        4. Apply city constraints for 2025
        5. Validate results
        """
        print("\n" + "="*80)
        print("🏛️ BOTTOM-UP HIERARCHICAL POPULATION SIMULATION")
        print("="*80)
        print("\n   Mathematical Framework:")
        print("   • Level 4: Village model (rural decline + urban growth)")
        print("   • Level 3: Arrondissement (aggregation + 2010 census calibration)")
        print("   • Level 2: Department (aggregation)")
        print("   • Level 1: Region (demographic factors × multiplier)")
        print("   • Level 0: National (UN target constraint)")

        # STEP 1: Distribute 2005 population to villages
        df = self.distribute_population_to_villages_2005()

        # Initialize other year columns
        for year in self.years[1:]:
            df[f"population_{year}"] = df["population_2005"]

        # STEP 2: Simulate each period
        periods = [(2005, 2010), (2010, 2015), (2015, 2020), (2020, 2025)]

        print("\n📈 Running bottom-up hierarchical simulation:")

        with tqdm(total=len(periods), desc="   Simulating", unit="period", ncols=80) as pbar:
            for t, t_next in periods:
                # Bottom-up: Simulate village growth
                df = self.simulate_villages_bottom_up(df, t, t_next)

                # Top-down: Apply regional constraints
                df = self.apply_regional_constraint(df, t, t_next)

                # Top-down: Apply national constraint
                df = self.apply_national_constraint(df, t_next)

                # Special calibration for 2010
                if t_next == 2010:
                    df = self.calibrate_with_2010_census(df)

                pbar.set_postfix_str(f"{t}→{t_next}")
                pbar.update(1)

        # STEP 3: Apply city constraints for 2025
        df = self.apply_city_constraints(df)

        # STEP 4: Final national constraint for 2025
        df = self.apply_national_constraint(df, 2025)

        # STEP 5: Validate
        all_valid = self.validate_simulation(df)

        if all_valid:
            print("\n   🎉 All validation checks passed!")
        else:
            print("\n   ⚠️ Some validation checks exceeded thresholds.")

        return df