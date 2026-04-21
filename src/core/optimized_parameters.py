"""
cameroon-administrative-data-platform/src/core/optimized_parameters.py

Optimized parameters for Cameroon population simulation.
These parameters were calibrated to match UN targets and 2026 regional estimates.
Includes actual 2005 and 2010 arrondissement census data and mathematical calibration.
"""

# =========================================================
# OPTIMIZED REGIONAL GROWTH MULTIPLIERS
# Calibrated to match 2026 regional targets
# =========================================================

import numpy as np
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

# Try to import tqdm for progress bars
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("⚠️ tqdm not available. Install with: pip install tqdm")


@dataclass
class OptimizationHistory:
    """Track optimization history"""
    iterations: List[int] = field(default_factory=list)
    losses: List[float] = field(default_factory=list)
    best_losses: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    best_params: Dict[str, Any] = field(default_factory=dict)

    def add(self, iteration: int, loss: float, best_loss: float, params: Optional[Dict] = None):
        self.iterations.append(iteration)
        self.losses.append(loss)
        self.best_losses.append(best_loss)
        self.timestamps.append(datetime.now())
        if params and (not self.best_params or loss < min(self.best_losses)):
            self.best_params = params.copy()

    def get_summary(self) -> Dict:
        """Get optimization summary statistics"""
        if not self.losses:
            return {"error": "No data"}

        return {
            "total_iterations": len(self.losses),
            "initial_loss": self.losses[0],
            "final_loss": self.losses[-1],
            "best_loss": min(self.best_losses),
            "improvement": ((self.losses[0] - min(self.best_losses)) / max(self.losses[0], 1e-6)) * 100,
            "best_iteration": self.iterations[self.best_losses.index(min(self.best_losses))],
        }

    def print_summary(self):
        """Print optimization summary"""
        summary = self.get_summary()
        if "error" in summary:
            print("   No optimization data available")
            return

        print("\n   📊 OPTIMIZATION SUMMARY:")
        print(f"      Total iterations: {summary['total_iterations']}")
        print(f"      Initial loss: {summary['initial_loss']:.6f}")
        print(f"      Final loss: {summary['final_loss']:.6f}")
        print(f"      Best loss: {summary['best_loss']:.6f}")
        print(f"      Improvement: {summary['improvement']:.1f}%")
        print(f"      Best at iteration: {summary['best_iteration']}")


REGIONAL_MULTIPLIERS_OPTIMIZED = {
    "EXTREME-NORD": 1.08,
    "NORD": 1.06,
    "ADAMAOUA": 1.04,
    "OUEST": 1.02,
    "SUD": 1.00,
    "EST": 1.00,
    "SUD-OUEST": 0.98,
    "NORD-OUEST": 0.96,
    "CENTRE": 0.94,
    "LITTORAL": 0.92,
}

# =========================================================
# REGIONAL TARGETS (2026 estimates from INS/BUCREP)
# =========================================================

REGIONAL_TARGETS_2026 = {
    "CENTRE": 5_500_000,
    "LITTORAL": 4_300_000,
    "EXTREME-NORD": 4_500_000,
    "NORD": 3_100_000,
    "NORD-OUEST": 2_200_000,
    "OUEST": 2_100_000,
    "SUD-OUEST": 1_800_000,
    "ADAMAOUA": 1_400_000,
    "EST": 1_100_000,
    "SUD": 900_000,
}

# Regional weights for optimization (higher weight = more important to match)
REGIONAL_OPTIMIZATION_WEIGHTS = {
    "EXTREME-NORD": 1.2,
    "NORD": 1.0,
    "ADAMAOUA": 0.8,
    "OUEST": 1.0,
    "SUD": 0.7,
    "EST": 0.6,
    "SUD-OUEST": 0.9,
    "NORD-OUEST": 0.8,
    "CENTRE": 2.0,         # Increased weight
    "LITTORAL": 2.0,       # Increased weight
}

# =========================================================
# MAJOR CITIES 2025 POPULATION
# =========================================================

MAJOR_CITIES_2025 = {
    "YAOUNDE": 5_106_087,
    "DOUALA": 4_104_516,
    "GAROUA": 678_769,
    "MAROUA": 526_702,
    "BAMENDA": 394_155,
    "NGAOUNDERE": 345_148,
    "KUMBA": 329_340,
    "BAFOUSSAM": 321_489,
    "KOUSSERI": 244_247,
    "BERTOUA": 235_399,
    "LIMBE": 233_212,
    "BUEA": 222_996,
    "MOKOLO": 190_418,
    "GUIDER": 187_887,
    "FOUMBAN": 182_273,
}

CITY_OPTIMIZATION_WEIGHTS = {
    "YAOUNDE": 2.0,
    "DOUALA": 2.0,
    "GAROUA": 1.0,
    "MAROUA": 1.0,
    "BAMENDA": 1.0,
    "NGAOUNDERE": 0.8,
    "KUMBA": 0.8,
    "BAFOUSSAM": 0.8,
}

CITY_DEPARTMENT_MAP = {
    "DOUALA": "WOURI",
    "YAOUNDE": "MFOUNDI",
    "GAROUA": "BENOUE",
    "MAROUA": "DIAMARE",
    "BAMENDA": "MEZAM",
    "NGAOUNDERE": "VINA",
    "KUMBA": "MEME",
    "BAFOUSSAM": "MIFI",
    "KOUSSERI": "LOGONE-ET-CHARI",
    "BERTOUA": "LOM-ET-DJEREM",
    "LIMBE": "FAKO",
    "BUEA": "FAKO",
    "MOKOLO": "MAYO-TSANAGA",
    "GUIDER": "MAYO-LOUTI",
    "FOUMBAN": "NOUN",
}

# =========================================================
# UN POPULATION TARGETS
# =========================================================

UN_POPULATION_TARGETS = {
    2005: 17_074_594,
    2010: 19_668_066,
    2015: 22_763_414,
    2020: 26_210_558,
    2025: 29_879_337,
    2026: 30_640_817,
    2030: 33_777_190,
    2035: 37_893_818,
    2040: 42_208_003,
    2045: 46_629_039,
    2050: 51_096_317,
}

PERIOD_GROWTH_RATES = {
    "2005-2010": 0.0287,
    "2010-2015": 0.0297,
    "2015-2020": 0.0286,
    "2020-2025": 0.0268,
}

ANNUAL_GROWTH_RATES = {
    2005: 0.0274, 2006: 0.0274, 2007: 0.0274, 2008: 0.0274, 2009: 0.0274,
    2010: 0.0287, 2011: 0.0287, 2012: 0.0287, 2013: 0.0287, 2014: 0.0287,
    2015: 0.0297, 2016: 0.0297, 2017: 0.0297, 2018: 0.0297, 2019: 0.0297,
    2020: 0.0286, 2021: 0.0286, 2022: 0.0286, 2023: 0.0286, 2024: 0.0286,
    2025: 0.0268,
}

URBANIZATION_TARGETS = {
    2005: 0.495,
    2010: 0.524,
    2015: 0.547,
    2020: 0.570,
    2025: 0.594,
    2026: 0.598,
    2030: 0.617,
}

REGIONAL_URBANIZATION_2005 = {
    "LITTORAL": 0.85, "CENTRE": 0.75, "OUEST": 0.45,
    "SUD-OUEST": 0.40, "NORD-OUEST": 0.35, "NORD": 0.30,
    "EXTREME-NORD": 0.25, "SUD": 0.25, "ADAMAOUA": 0.20, "EST": 0.18,
}

REGIONAL_URBANIZATION_TRENDS = {
    "LITTORAL": 0.006, "CENTRE": 0.008, "OUEST": 0.010,
    "SUD-OUEST": 0.008, "NORD-OUEST": 0.006, "NORD": 0.005,
    "EXTREME-NORD": 0.004, "SUD": 0.004, "ADAMAOUA": 0.003, "EST": 0.003,
}

REGIONAL_FERTILITY_INDICES = {
    "EXTREME-NORD": 1.15, "NORD": 1.12, "ADAMAOUA": 1.10,
    "NORD-OUEST": 1.05, "OUEST": 1.03, "EST": 1.02,
    "SUD": 1.00, "CENTRE": 0.95, "LITTORAL": 0.93, "SUD-OUEST": 0.98,
}

REGIONAL_MORTALITY_INDICES = {
    "EXTREME-NORD": 1.12, "NORD": 1.10, "ADAMAOUA": 1.08,
    "NORD-OUEST": 1.05, "SUD-OUEST": 1.05, "OUEST": 1.02,
    "EST": 1.02, "SUD": 1.00, "CENTRE": 0.95, "LITTORAL": 0.93,
}

MODEL_PARAMETERS = {
    "alpha_fert": 0.5,
    "alpha_mort": 0.3,
    "alpha_urban": 0.2,
    "gamma_urban": 0.10,
    "delta_rural": 0.05,
    "delta_increase": 0.001,
    "city_factor_max": 3.0,
    "city_factor_min": 0.5,
}

PARAMETER_BOUNDS = {
    "alpha_fert": (0.1, 1.0),
    "alpha_mort": (0.05, 1.0),
    "alpha_urban": (0.01, 0.8),
    "gamma_urban": (0.01, 0.5),
    "delta_rural": (0.0, 0.2),
    "delta_increase": (0.0, 0.01),
}

REGIONAL_MULTIPLIER_BOUNDS = (0.7, 1.3)

VALIDATION_THRESHOLDS = {
    "national_diff_percent": 2.0,
    "regional_diff_percent": 20.0,
    "urbanization_diff_percent": 10.0,
    "arrondissement_growth_diff": 0.02,
}

DEMOGRAPHIC_INDICATORS_2026 = {
    "median_age": 18.2,
    "fertility_rate": 4.12,
    "life_expectancy": 64.5,
    "infant_mortality": 43.6,
    "under_5_mortality": 62.3,
    "population_density": 65.0,
}


# =========================================================
# IMPROVED LOSS FUNCTION WITH CORRECT METRICS
# =========================================================

def _simulate_regional_trajectory(params, cfg, include_regional_multipliers=False):
    """Simulate regional populations 2005-2026."""

    alpha_fert = params["alpha_fert"]
    alpha_mort = params["alpha_mort"]
    alpha_urban = params["alpha_urban"]

    national_targets = cfg.NATIONAL_POPULATION
    years = [2005, 2010, 2015, 2020, 2025, 2026]

    regions = list(REGIONAL_TARGETS_2026.keys())

    # Get regional multipliers
    if include_regional_multipliers and "regional_multipliers" in params:
        reg_mult = params["regional_multipliers"]
    else:
        reg_mult = REGIONAL_MULTIPLIERS_OPTIMIZED

    # Initialize 2005 regional populations
    total_2005 = national_targets[2005]
    total_2026_targets = sum(REGIONAL_TARGETS_2026.values())
    regional_pops = {year: {} for year in years}
    for r in regions:
        weight = REGIONAL_TARGETS_2026[r] / total_2026_targets
        regional_pops[2005][r] = total_2005 * weight

    fert_idx = REGIONAL_FERTILITY_INDICES
    mort_idx = REGIONAL_MORTALITY_INDICES
    urb_2005 = REGIONAL_URBANIZATION_2005
    urb_targets = URBANIZATION_TARGETS

    # Urbanization trends
    beta_r = {}
    target_year_for_urban = 2025
    Uc_2025 = urb_targets[target_year_for_urban]

    def compute_weighted_urban(year):
        num, den = 0.0, 0.0
        for r in regions:
            Ur = urb_2005[r]
            Pr = regional_pops[2005][r]
            num += Ur * Pr
            den += Pr
        return num / den if den > 0 else 0.0

    current_U_2025 = compute_weighted_urban(target_year_for_urban)
    delta_U = Uc_2025 - current_U_2025
    for r in regions:
        beta_r[r] = delta_U / (target_year_for_urban - 2005)

    for i in range(len(years) - 1):
        t = years[i]
        t_next = years[i + 1]

        Pc_t = national_targets[t]
        Pc_next = national_targets[t_next]
        Gc = Pc_next / Pc_t

        raw_next = {}
        for r in regions:
            Pr_t = regional_pops[t][r]
            fr = fert_idx.get(r, 1.0)
            mr = mort_idx.get(r, 1.0)
            Ur_t = urb_2005[r] + beta_r[r] * (t - 2005)
            Uc_t = urb_targets.get(t, Ur_t)

            F_fert = 1.0 + alpha_fert * (fr - 1.0)
            F_mort = 1.0 - alpha_mort * (mr - 1.0)
            F_urban = 1.0 + alpha_urban * (Ur_t - Uc_t)
            F_reg_mult = reg_mult.get(r, 1.0)

            Gr_raw = Gc * F_fert * F_mort * F_urban * F_reg_mult
            raw_next[r] = Pr_t * Gr_raw

        sum_raw = sum(raw_next.values())
        if sum_raw <= 0:
            for r in regions:
                regional_pops[t_next][r] = Pc_next / len(regions)
        else:
            scale = Pc_next / sum_raw
            for r in regions:
                regional_pops[t_next][r] = raw_next[r] * scale

    national_pops = {year: sum(regional_pops[year].values()) for year in years}
    urban_share = {}
    for year in years:
        num, den = 0.0, 0.0
        for r in regions:
            Ur = urb_2005[r] + beta_r[r] * (year - 2005)
            Pr = regional_pops[year][r]
            num += Ur * Pr
            den += Pr
        urban_share[year] = num / den if den > 0 else 0.0

    return regional_pops, national_pops, urban_share


def _compute_loss(params, cfg, include_regional_multipliers=False):
    """
    IMPROVED LOSS FUNCTION with proper weighting and penalties.

    This loss function correctly penalizes:
    1. National population deviations (weighted)
    2. Regional population deviations with asymmetric penalties
    3. Urbanization trajectory deviations
    4. Large errors (>50%) get exponential penalty
    """

    regional_pops, national_pops, urban_share = _simulate_regional_trajectory(
        params, cfg, include_regional_multipliers
    )

    nat_targets = cfg.NATIONAL_POPULATION
    years = [2005, 2010, 2015, 2020, 2025, 2026]

    # =========================================================
    # 1. NATIONAL LOSS (with exponential penalty for large errors)
    # =========================================================
    L_nat = 0.0
    for t in years:
        Pt_sim = national_pops[t]
        Pt_true = nat_targets[t]
        rel_error = (Pt_sim - Pt_true) / Pt_true

        # Exponential penalty for errors > 2%
        if abs(rel_error) > 0.02:
            penalty = np.exp(abs(rel_error) * 10) - 1
        else:
            penalty = 0

        L_nat += rel_error ** 2 + penalty * 0.1

    # =========================================================
    # 2. REGIONAL LOSS (with asymmetric penalties for underestimation)
    # =========================================================
    L_reg = 0.0
    region_errors = {}

    for r, target in REGIONAL_TARGETS_2026.items():
        Pr_sim = regional_pops[2026].get(r, target)
        weight = REGIONAL_OPTIMIZATION_WEIGHTS.get(r, 1.0)
        rel_error = (Pr_sim - target) / target
        region_errors[r] = rel_error

        # Asymmetric penalty: underestimation worse than overestimation
        if rel_error < 0:  # Underestimation
            penalty = abs(rel_error) ** 2 * 2.0
        elif rel_error > 0.5:  # Overestimation > 50%
            penalty = (rel_error - 0.5) ** 2 * 5.0
        else:
            penalty = 0

        L_reg += weight * (rel_error ** 2 + penalty)

    # =========================================================
    # 3. URBANIZATION LOSS
    # =========================================================
    L_urb = 0.0
    for t, U_target in URBANIZATION_TARGETS.items():
        if t in urban_share:
            U_sim = urban_share[t]
            diff = U_sim - U_target
            # Stronger penalty for large urbanization deviations
            if abs(diff) > 0.1:
                penalty = np.exp(abs(diff) * 5) - 1
            else:
                penalty = 0
            L_urb += diff ** 2 + penalty * 0.05

        # =========================================================
    # 4. REGIONAL BALANCE PENALTY (prevents extreme disparities)
    # =========================================================
    L_balance = 0.0

    # Check for extreme disparities (like Littoral being 4x too large)
    for r, rel_error in region_errors.items():
        if abs(rel_error) > 0.5:  # More than 50% error
            L_balance += (abs(rel_error) - 0.5) ** 2 * 10.0

    # Special penalty for key regions (Littoral and Centre)
    for r in ["LITTORAL", "CENTRE"]:
        if r in region_errors:
            rel_error = abs(region_errors[r])
            if rel_error > 0.3:  # More than 30% error
                L_balance += rel_error ** 2 * 5.0

    # =========================================================
    # 5. PARAMETER REGULARIZATION (prevents extreme parameter values)
    # =========================================================
    L_reg_param = 0.0

    # Penalize extreme fertility/mortality parameters
    if params["alpha_fert"] > 0.9:
        L_reg_param += (params["alpha_fert"] - 0.9) ** 2 * 2.0
    if params["alpha_mort"] < 0.1:
        L_reg_param += (0.1 - params["alpha_mort"]) ** 2 * 2.0

    # Penalize unrealistic urbanization parameters
    if params["alpha_urban"] > 0.6:
        L_reg_param += (params["alpha_urban"] - 0.6) ** 2 * 1.0

    # =========================================================
    # COMBINE LOSSES WITH ADAPTIVE WEIGHTS
    # =========================================================

    # Dynamic weights based on current errors
    max_regional_error = max([abs(e) for e in region_errors.values()]) if region_errors else 0

    if max_regional_error > 0.5:
        # Increase regional weight when errors are large
        w_reg = 5.0
        w_balance = 3.0
    elif max_regional_error > 0.2:
        w_reg = 3.0
        w_balance = 1.5
    else:
        w_reg = 2.0
        w_balance = 0.5

    w_nat = 10.0
    w_urb = 1.0
    w_reg_param = 0.5

    total_loss = (w_nat * L_nat +
                  w_reg * L_reg +
                  w_urb * L_urb +
                  w_balance * L_balance +
                  w_reg_param * L_reg_param)

    return total_loss


def _params_to_vector(params, include_regional_multipliers=False):
    """Convert parameters dictionary to optimization vector."""
    vec = [
        params["alpha_fert"],
        params["alpha_mort"],
        params["alpha_urban"],
        params["gamma_urban"],
        params["delta_rural"],
        params["delta_increase"],
    ]
    if include_regional_multipliers and "regional_multipliers" in params:
        regions = sorted(REGIONAL_TARGETS_2026.keys())
        for r in regions:
            vec.append(params["regional_multipliers"][r])
    return vec


def _vector_to_params(vec, include_regional_multipliers=False):
    """Convert optimization vector back to parameters dictionary."""
    params = {
        "alpha_fert": float(vec[0]),
        "alpha_mort": float(vec[1]),
        "alpha_urban": float(vec[2]),
        "gamma_urban": float(vec[3]),
        "delta_rural": float(vec[4]),
        "delta_increase": float(vec[5]),
        "city_factor_max": 3.0,
        "city_factor_min": 0.5,
    }

    if include_regional_multipliers:
        regions = sorted(REGIONAL_TARGETS_2026.keys())
        regional_multipliers = {}
        for i, r in enumerate(regions):
            regional_multipliers[r] = float(vec[6 + i])
        params["regional_multipliers"] = regional_multipliers

    return params


def get_parameter_bounds(include_regional_multipliers=False):
    """Get bounds for optimization parameters."""
    lower = [PARAMETER_BOUNDS[k][0] for k in ["alpha_fert", "alpha_mort", "alpha_urban", "gamma_urban", "delta_rural", "delta_increase"]]
    upper = [PARAMETER_BOUNDS[k][1] for k in ["alpha_fert", "alpha_mort", "alpha_urban", "gamma_urban", "delta_rural", "delta_increase"]]

    if include_regional_multipliers:
        n_regions = len(REGIONAL_TARGETS_2026)
        lower.extend([REGIONAL_MULTIPLIER_BOUNDS[0]] * n_regions)
        upper.extend([REGIONAL_MULTIPLIER_BOUNDS[1]] * n_regions)

    return lower, upper


# =========================================================
# OPTION A — CMA-ES OPTIMIZATION
# =========================================================

def optimize_cma_es(
    n_iterations: int = 200,
    sigma0: float = 0.1,
    include_regional_multipliers: bool = False,
    verbose: bool = True,
    show_progress: bool = True,
    history: Optional[OptimizationHistory] = None,
):
    """CMA-ES optimization with improved loss function."""
    try:
        import cma
    except ImportError:
        print("⚠️ CMA-ES requires 'cma'. Install with: pip install cma")
        return None

    from .config import config as cfg

    if history is None:
        history = OptimizationHistory()

    base_params = MODEL_PARAMETERS.copy()
    if include_regional_multipliers:
        base_params["regional_multipliers"] = REGIONAL_MULTIPLIERS_OPTIMIZED.copy()

    x0 = _params_to_vector(base_params, include_regional_multipliers)
    lower, upper = get_parameter_bounds(include_regional_multipliers)

    best_loss = float('inf')
    best_params = None

    def objective(x):
        nonlocal best_loss, best_params
        x_clipped = np.clip(x, lower, upper)
        params = _vector_to_params(x_clipped, include_regional_multipliers)
        loss = _compute_loss(params, cfg, include_regional_multipliers)

        if loss < best_loss:
            best_loss = loss
            best_params = params.copy()

        return loss

    pbar = None
    if show_progress and TQDM_AVAILABLE and verbose:
        pbar = tqdm(total=n_iterations, desc="🔍 CMA-ES optimization",
                    unit="iter", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")

    es = cma.CMAEvolutionStrategy(
        x0, sigma0,
        {"bounds": [lower, upper], "verb_disp": 0}
    )

    for i in range(n_iterations):
        xs = es.ask()
        losses = [objective(x) for x in xs]
        es.tell(xs, losses)

        current_loss = min(losses)
        history.add(i, current_loss, best_loss, best_params)

        if pbar:
            pbar.update(1)
            pbar.set_postfix({'best': f'{best_loss:.4f}'})

        if es.stop():
            break

    if pbar:
        pbar.close()

    best_x = es.result.xbest
    best_x = np.clip(best_x, lower, upper)
    best_params = _vector_to_params(best_x, include_regional_multipliers)
    loss = _compute_loss(best_params, cfg, include_regional_multipliers)

    if verbose:
        print("\n🎯 CMA-ES finished")
        print(f"   Best loss: {loss:.6f}")
        history.print_summary()

    # Update global parameters
    for k in ["alpha_fert", "alpha_mort", "alpha_urban", "gamma_urban", "delta_rural", "delta_increase"]:
        if k in best_params:
            MODEL_PARAMETERS[k] = best_params[k]
    if include_regional_multipliers and "regional_multipliers" in best_params:
        REGIONAL_MULTIPLIERS_OPTIMIZED.update(best_params["regional_multipliers"])

    return {"best_loss": loss, "best_params": best_params, "history": history}


# =========================================================
# OPTION B — OPTUNA OPTIMIZATION
# =========================================================

def optimize_optuna(
    n_trials: int = 200,
    include_regional_multipliers: bool = False,
    study_name: str = "cameroon_optimization",
    verbose: bool = True,
    show_progress: bool = True,
    history: Optional[OptimizationHistory] = None,
):
    """Bayesian optimization using Optuna with improved loss."""
    try:
        import optuna
    except ImportError:
        print("⚠️ Optuna requires 'optuna'. Install with: pip install optuna")
        return None

    from .config import config as cfg

    if history is None:
        history = OptimizationHistory()

    best_loss = float('inf')
    best_params = None
    trial_count = 0

    def objective(trial):
        nonlocal best_loss, best_params, trial_count
        trial_count += 1

        alpha_fert = trial.suggest_float("alpha_fert", 0.1, 1.0)
        alpha_mort = trial.suggest_float("alpha_mort", 0.05, 1.0)
        alpha_urban = trial.suggest_float("alpha_urban", 0.01, 0.8)
        gamma_urban = trial.suggest_float("gamma_urban", 0.01, 0.5)
        delta_rural = trial.suggest_float("delta_rural", 0.0, 0.2)
        delta_increase = trial.suggest_float("delta_increase", 0.0, 0.01)

        params = {
            "alpha_fert": alpha_fert,
            "alpha_mort": alpha_mort,
            "alpha_urban": alpha_urban,
            "gamma_urban": gamma_urban,
            "delta_rural": delta_rural,
            "delta_increase": delta_increase,
            "city_factor_max": 3.0,
            "city_factor_min": 0.5,
        }

        if include_regional_multipliers:
            regional_multipliers = {}
            for r in REGIONAL_TARGETS_2026.keys():
                regional_multipliers[r] = trial.suggest_float(f"mult_{r}", 0.7, 1.3)
            params["regional_multipliers"] = regional_multipliers

        loss = _compute_loss(params, cfg, include_regional_multipliers)

        if loss < best_loss:
            best_loss = loss
            best_params = params.copy()

        history.add(trial_count, loss, best_loss, best_params)

        return loss

    class ProgressCallback:
        def __init__(self, total_trials):
            self.pbar = None
            self.total_trials = total_trials

        def __call__(self, study, trial):
            if self.pbar is None and show_progress and TQDM_AVAILABLE and verbose:
                self.pbar = tqdm(total=self.total_trials, desc="🔍 Optuna optimization",
                                unit="trial", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")
            if self.pbar:
                self.pbar.update(1)
                self.pbar.set_postfix({'best': f'{best_loss:.4f}'})

            if self.pbar and trial.number >= self.total_trials - 1:
                self.pbar.close()

    sampler = optuna.samplers.TPESampler()
    study = optuna.create_study(direction="minimize", sampler=sampler, study_name=study_name)

    callback = ProgressCallback(n_trials)
    study.optimize(objective, n_trials=n_trials, callbacks=[callback], show_progress_bar=False)

    loss = study.best_value

    if verbose:
        print("\n🎯 Optuna finished")
        print(f"   Best loss: {loss:.6f}")
        history.print_summary()

    return {"best_loss": loss, "best_params": best_params, "study": study, "history": history}


# =========================================================
# OPTION C — SIMULATED ANNEALING
# =========================================================

def optimize_simulated_annealing(
    n_iterations: int = 2000,
    T_start: float = 1.0,
    T_end: float = 0.01,
    include_regional_multipliers: bool = False,
    verbose: bool = True,
    show_progress: bool = True,
    history: Optional[OptimizationHistory] = None,
):
    """Simulated annealing with improved loss function."""
    from .config import config as cfg
    import math

    if history is None:
        history = OptimizationHistory()

    current = MODEL_PARAMETERS.copy()
    if include_regional_multipliers:
        current["regional_multipliers"] = REGIONAL_MULTIPLIERS_OPTIMIZED.copy()

    current_loss = _compute_loss(current, cfg, include_regional_multipliers)
    best = current.copy()
    best_loss = current_loss

    history.add(0, current_loss, best_loss, best)

    lower, upper = get_parameter_bounds(include_regional_multipliers)

    def propose(p, T):
        q = {}
        for k in p.keys():
            if k in ["city_factor_max", "city_factor_min"]:
                q[k] = p[k]
                continue

            if k == "regional_multipliers":
                q[k] = {}
                for r, v in p[k].items():
                    scale = 0.05 * T
                    q[k][r] = float(np.clip(v + np.random.normal(0, scale), 0.7, 1.3))
            else:
                if k in PARAMETER_BOUNDS:
                    bounds = PARAMETER_BOUNDS[k]
                    scale = 0.1 * T
                    q[k] = float(np.clip(p[k] + np.random.normal(0, scale), bounds[0], bounds[1]))
                else:
                    q[k] = p[k]
        return q

    pbar = None
    if show_progress and TQDM_AVAILABLE and verbose:
        pbar = tqdm(total=n_iterations, desc="🔍 Simulated annealing",
                    unit="iter", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")

    for i in range(n_iterations):
        t = i / max(1, n_iterations - 1)
        T = T_start * (T_end / T_start) ** t

        candidate = propose(current, T)
        cand_loss = _compute_loss(candidate, cfg, include_regional_multipliers)

        delta = cand_loss - current_loss
        if delta < 0 or np.random.rand() < math.exp(-delta / max(T, 1e-6)):
            current = candidate
            current_loss = cand_loss

        if cand_loss < best_loss:
            best = candidate
            best_loss = cand_loss
            if verbose and (i + 1) % 100 == 0:
                print(f"   ✅ SA iter {i+1}/{n_iterations} - best_loss={best_loss:.6f}")

        history.add(i + 1, current_loss, best_loss, best)

        if pbar:
            pbar.update(1)
            pbar.set_postfix({
                'best': f'{best_loss:.4f}',
                'T': f'{T:.3f}'
            })

    if pbar:
        pbar.close()

    if verbose:
        print("\n🎯 Simulated annealing finished")
        print(f"   Best loss: {best_loss:.6f}")
        history.print_summary()

    # Update global parameters
    for k in ["alpha_fert", "alpha_mort", "alpha_urban", "gamma_urban", "delta_rural", "delta_increase"]:
        if k in best:
            MODEL_PARAMETERS[k] = best[k]
    if include_regional_multipliers and "regional_multipliers" in best:
        REGIONAL_MULTIPLIERS_OPTIMIZED.update(best["regional_multipliers"])

    return {"best_loss": best_loss, "best_params": best, "history": history}


# =========================================================
# OPTION D — HYBRID OPTIMIZATION
# =========================================================

def optimize_hybrid(
    random_trials: int = 200,
    cma_iterations: int = 150,
    sa_iterations: int = 1000,
    include_regional_multipliers: bool = False,
    verbose: bool = True,
    show_progress: bool = True,
):
    """
    Hybrid optimization with improved loss function.
    """
    from .config import config as cfg

    history = OptimizationHistory()

    best = MODEL_PARAMETERS.copy()
    if include_regional_multipliers:
        best["regional_multipliers"] = REGIONAL_MULTIPLIERS_OPTIMIZED.copy()

    best_loss = _compute_loss(best, cfg, include_regional_multipliers)
    history.add(0, best_loss, best_loss, best)

    if verbose:
        print("\n🔧 Hybrid optimization: Random search phase...")

    # 1) Random search
    pbar = None
    if show_progress and TQDM_AVAILABLE and verbose:
        pbar = tqdm(total=random_trials, desc="   Random search",
                    unit="trial", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]")

    for i in range(random_trials):
        candidate = {
            "alpha_fert": float(np.random.uniform(0.1, 1.0)),
            "alpha_mort": float(np.random.uniform(0.05, 1.0)),
            "alpha_urban": float(np.random.uniform(0.01, 0.8)),
            "gamma_urban": float(np.random.uniform(0.01, 0.5)),
            "delta_rural": float(np.random.uniform(0.0, 0.2)),
            "delta_increase": float(np.random.uniform(0.0, 0.01)),
            "city_factor_max": 3.0,
            "city_factor_min": 0.5,
        }

        if include_regional_multipliers:
            regional_multipliers = {}
            for r in REGIONAL_TARGETS_2026.keys():
                regional_multipliers[r] = float(np.random.uniform(0.7, 1.3))
            candidate["regional_multipliers"] = regional_multipliers

        loss = _compute_loss(candidate, cfg, include_regional_multipliers)

        if loss < best_loss:
            best = candidate
            best_loss = loss
            if verbose and (i + 1) % 20 == 0:
                print(f"   ✅ New best: {best_loss:.6f}")

        history.add(i + 1, loss, best_loss, best if loss < best_loss else None)

        if pbar:
            pbar.update(1)
            pbar.set_postfix({'best': f'{best_loss:.4f}'})

    if pbar:
        pbar.close()

    # Update global parameters
    for k in ["alpha_fert", "alpha_mort", "alpha_urban", "gamma_urban", "delta_rural", "delta_increase"]:
        if k in best:
            MODEL_PARAMETERS[k] = best[k]
    if include_regional_multipliers and "regional_multipliers" in best:
        REGIONAL_MULTIPLIERS_OPTIMIZED.update(best["regional_multipliers"])

    # 2) CMA-ES refinement
    try:
        if verbose:
            print("\n🔧 Hybrid optimization: CMA-ES phase...")
        cma_result = optimize_cma_es(
            n_iterations=cma_iterations,
            include_regional_multipliers=include_regional_multipliers,
            verbose=verbose,
            show_progress=show_progress,
            history=history,
        )
        if cma_result:
            best_loss = cma_result["best_loss"]
    except ImportError:
        if verbose:
            print("⚠️ CMA-ES not available, skipping.")

    # 3) Simulated annealing refinement
    if verbose:
        print("\n🔧 Hybrid optimization: Simulated annealing phase...")
    sa_result = optimize_simulated_annealing(
        n_iterations=sa_iterations,
        include_regional_multipliers=include_regional_multipliers,
        verbose=verbose,
        show_progress=show_progress,
        history=history,
    )
    best_loss = sa_result["best_loss"]

    if verbose:
        print("\n🎯 Hybrid optimization finished")
        print(f"   Final best loss: {best_loss:.6f}")
        history.print_summary()

    return {"best_loss": best_loss, "best_params": MODEL_PARAMETERS.copy(), "history": history}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_optimized_config():
    """Return all optimized parameters as a dictionary."""
    return {
        "regional_multipliers": REGIONAL_MULTIPLIERS_OPTIMIZED,
        "regional_targets_2026": REGIONAL_TARGETS_2026,
        "regional_optimization_weights": REGIONAL_OPTIMIZATION_WEIGHTS,
        "major_cities_2025": MAJOR_CITIES_2025,
        "city_optimization_weights": CITY_OPTIMIZATION_WEIGHTS,
        "city_department_map": CITY_DEPARTMENT_MAP,
        "un_population_targets": UN_POPULATION_TARGETS,
        "period_growth_rates": PERIOD_GROWTH_RATES,
        "annual_growth_rates": ANNUAL_GROWTH_RATES,
        "urbanization_targets": URBANIZATION_TARGETS,
        "regional_urbanization_2005": REGIONAL_URBANIZATION_2005,
        "regional_urbanization_trends": REGIONAL_URBANIZATION_TRENDS,
        "regional_fertility_indices": REGIONAL_FERTILITY_INDICES,
        "regional_mortality_indices": REGIONAL_MORTALITY_INDICES,
        "model_parameters": MODEL_PARAMETERS,
        "parameter_bounds": PARAMETER_BOUNDS,
        "regional_multiplier_bounds": REGIONAL_MULTIPLIER_BOUNDS,
        "validation_thresholds": VALIDATION_THRESHOLDS,
        "demographic_indicators_2026": DEMOGRAPHIC_INDICATORS_2026,
    }


def save_optimized_parameters(output_dir):
    """Save optimized parameters to JSON file."""
    import json
    from pathlib import Path

    params = get_optimized_config()
    output_path = Path(output_dir) / "optimized_parameters.json"

    def convert(obj):
        if isinstance(obj, dict):
            return {str(k): convert(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert(item) for item in obj]
        return obj

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(convert(params), f, indent=2)

    print(f"\n   ✅ Optimized parameters saved to {output_path}")
    return output_path


def load_optimized_parameters(input_dir):
    """Load optimized parameters from JSON file."""
    import json
    from pathlib import Path

    input_path = Path(input_dir) / "optimized_parameters.json"

    if input_path.exists():
        with open(input_path, "r", encoding="utf-8") as f:
            params = json.load(f)

        if "un_population_targets" in params:
            params["un_population_targets"] = {int(k): v for k, v in params["un_population_targets"].items()}
        if "urbanization_targets" in params:
            params["urbanization_targets"] = {int(k): v for k, v in params["urbanization_targets"].items()}
        if "annual_growth_rates" in params:
            params["annual_growth_rates"] = {int(k): v for k, v in params["annual_growth_rates"].items()}

        print(f"✅ Loaded optimized parameters from {input_path}")
        return params
    else:
        print(f"⚠️ No saved parameters found at {input_path}")
        return None


def print_config_summary():
    """Print a summary of all optimized parameters."""
    print("\n" + "="*80)
    print("📊 OPTIMIZED PARAMETERS SUMMARY")
    print("="*80)

    print("\n📍 REGIONAL MULTIPLIERS:")
    for region, mult in REGIONAL_MULTIPLIERS_OPTIMIZED.items():
        print(f"   {region:15}: {mult:.3f}")

    print("\n🎯 REGIONAL TARGETS (2026):")
    for region, target in REGIONAL_TARGETS_2026.items():
        print(f"   {region:15}: {target:,}")

    print("\n⚖️ REGIONAL OPTIMIZATION WEIGHTS:")
    for region, weight in REGIONAL_OPTIMIZATION_WEIGHTS.items():
        print(f"   {region:15}: {weight:.1f}")

    print("\n⚙️ MODEL PARAMETERS:")
    for param, value in MODEL_PARAMETERS.items():
        print(f"   {param}: {value}")

    print("\n📈 PERIOD GROWTH RATES:")
    for period, rate in PERIOD_GROWTH_RATES.items():
        print(f"   {period}: {rate*100:.2f}% annual")

    print("\n🏙️ URBANIZATION TARGETS:")
    for year, urban in URBANIZATION_TARGETS.items():
        print(f"   {year}: {urban*100:.1f}%")

    print("="*80)
def get_arrondissement_population_2005():
    """Get 2005 arrondissement population data from config."""
    try:
        from .config import config
        return config.ARRONDISSEMENT_POPULATION_2005
    except (ImportError, AttributeError):
        print("⚠️ Could not load arrondissement population 2005 from config")
        return {}


def get_arrondissement_population_2010():
    """Get 2010 arrondissement population data from config."""
    try:
        from .config import config
        return config.ARRONDISSEMENT_POPULATION_2010
    except (ImportError, AttributeError):
        print("⚠️ Could not load arrondissement population 2010 from config")
        return {}


def get_department_population_2005():
    """Get 2005 department population data from config."""
    try:
        from .config import config
        return config.DEPT_POPULATION_2005
    except (ImportError, AttributeError):
        print("⚠️ Could not load department population 2005 from config")
        return {}


def calculate_arrondissement_growth_rates():
    """Calculate actual growth rates between 2005 and 2010 for each arrondissement."""
    arr_pop_2005 = get_arrondissement_population_2005()
    arr_pop_2010 = get_arrondissement_population_2010()

    growth_rates = {}
    for arr_name, pop_2005 in arr_pop_2005.items():
        pop_2010 = arr_pop_2010.get(arr_name, 0)
        if pop_2005 > 0 and pop_2010 > 0:
            annual_rate = (pop_2010 / pop_2005) ** (1/5) - 1
            growth_rates[arr_name.upper()] = annual_rate

    return growth_rates

if __name__ == "__main__":
    print_config_summary()