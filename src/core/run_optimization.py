"""
cameroon_population_pipeline/src/core/run_optimization.py

Run optimization of model parameters and then generate realistic simulation.
"""

import sys
import argparse
import time
from pathlib import Path

# Check for tqdm
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Create dummy tqdm for when not available
    class tqdm:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def update(self, *args, **kwargs):
            pass
        def set_description(self, *args, **kwargs):
            pass
        def set_postfix(self, *args, **kwargs):
            pass
        def close(self, *args, **kwargs):
            pass

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.optimized_parameters import (
    optimize_hybrid,
    optimize_cma_es,
    optimize_optuna,
    optimize_simulated_annealing,
    save_optimized_parameters,
    print_config_summary,
    MODEL_PARAMETERS,
    REGIONAL_MULTIPLIERS_OPTIMIZED,
)
from core.generate_dataset import main as generate_main
from core.config import config


def print_optimization_summary(result, include_regional):
    """Print detailed optimization summary with history."""
    print("\n" + "="*80)
    print("✅ OPTIMIZATION COMPLETE")
    print("="*80)

    print("\n📊 Final optimized parameters:")
    print(f"   alpha_fert: {MODEL_PARAMETERS['alpha_fert']:.6f}")
    print(f"   alpha_mort: {MODEL_PARAMETERS['alpha_mort']:.6f}")
    print(f"   alpha_urban: {MODEL_PARAMETERS['alpha_urban']:.6f}")
    print(f"   gamma_urban: {MODEL_PARAMETERS['gamma_urban']:.6f}")
    print(f"   delta_rural: {MODEL_PARAMETERS['delta_rural']:.6f}")
    print(f"   delta_increase: {MODEL_PARAMETERS['delta_increase']:.8f}")

    if include_regional:
        print("\n   📍 Optimized Regional Multipliers:")
        for region, mult in REGIONAL_MULTIPLIERS_OPTIMIZED.items():
            print(f"      {region:15}: {mult:.4f}")

    # Print optimization history if available
    if result and "history" in result and result["history"]:
        print("\n" + "="*80)
        result["history"].print_summary()

        # Plot loss convergence if matplotlib is available
        try:
            import matplotlib.pyplot as plt
            history = result["history"]

            if len(history.iterations) > 10:
                print("\n   📈 Generating loss convergence plot...")

                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

                # Loss over iterations
                ax1.plot(history.iterations, history.losses, 'b-', alpha=0.5, label='Current loss')
                ax1.plot(history.iterations, history.best_losses, 'r-', linewidth=2, label='Best loss')
                ax1.set_xlabel('Iteration')
                ax1.set_ylabel('Loss')
                ax1.set_title('Loss Convergence')
                ax1.legend()
                ax1.grid(True, alpha=0.3)

                # Best loss on log scale
                ax2.semilogy(history.iterations, history.best_losses, 'g-', linewidth=2)
                ax2.set_xlabel('Iteration')
                ax2.set_ylabel('Best Loss (log scale)')
                ax2.set_title('Best Loss Convergence')
                ax2.grid(True, alpha=0.3)

                plt.tight_layout()
                plot_path = Path(config.OUTPUT_DIR) / "optimization_convergence.png"
                plt.savefig(plot_path, dpi=150, bbox_inches='tight')
                print(f"   💾 Convergence plot saved to: {plot_path}")
                plt.close()
        except ImportError:
            pass  # matplotlib not available
        except Exception as e:
            print(f"   ⚠️ Could not generate plot: {e}")


def run_optimization_with_progress(method: str = "hybrid", include_regional: bool = False, n_trials: int = 200):
    """
    Run optimization with full progress bars and history tracking.
    """
    print("\n" + "="*80)
    print("🔧 CAMEROON POPULATION MODEL OPTIMIZATION")
    print("="*80)
    print(f"\n   Method: {method}")
    print(f"   Include regional multipliers: {include_regional}")
    print(f"   Number of trials: {n_trials}")
    print("")

    if not TQDM_AVAILABLE:
        print("   ⚠️ tqdm not available. Install with: pip install tqdm")
        print("   Continuing without progress bars...")

    try:
        if method == "hybrid":
            random_trials = n_trials // 2
            cma_iterations = n_trials // 3
            sa_iterations = n_trials

            print(f"   📊 Hybrid breakdown:")  # noqa: F541
            print(f"      • Random search: {random_trials} trials")
            print(f"      • CMA-ES: {cma_iterations} iterations")
            print(f"      • Simulated annealing: {sa_iterations} iterations")
            print("")

            # Run hybrid optimization with built-in progress bars
            result = optimize_hybrid(
                random_trials=random_trials,
                cma_iterations=cma_iterations,
                sa_iterations=sa_iterations,
                include_regional_multipliers=include_regional,
                verbose=True,
                show_progress=True,
            )

        elif method == "cmaes":
            result = optimize_cma_es(
                n_iterations=n_trials,
                include_regional_multipliers=include_regional,
                verbose=True,
                show_progress=True,
            )

        elif method == "optuna":
            print("   📊 Running Optuna optimization...")
            result = optimize_optuna(
                n_trials=n_trials,
                include_regional_multipliers=include_regional,
                verbose=True,
                show_progress=True,
            )

        elif method == "sa":
            result = optimize_simulated_annealing(
                n_iterations=n_trials,
                include_regional_multipliers=include_regional,
                verbose=True,
                show_progress=True,
            )
        else:
            print(f"❌ Unknown method: {method}")
            return None

        if result is None:
            print("\n❌ Optimization returned no result")
            return None

        # Print detailed summary with history
        print_optimization_summary(result, include_regional)

        return result

    except Exception as e:
        print(f"\n❌ Optimization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def run_optimization_simple(method: str = "hybrid", include_regional: bool = False, n_trials: int = 200):
    """
    Simple wrapper without progress bars (backward compatible).
    """
    print("\n" + "="*80)
    print("🔧 CAMEROON POPULATION MODEL OPTIMIZATION")
    print("="*80)
    print(f"\n   Method: {method}")
    print(f"   Include regional multipliers: {include_regional}")
    print(f"   Number of trials: {n_trials}")

    try:
        if method == "hybrid":
            random_trials = n_trials // 2
            cma_iterations = n_trials // 3
            sa_iterations = n_trials

            print(f"\n   📊 Hybrid breakdown:")  # noqa: F541
            print(f"      • Random search: {random_trials} trials")
            print(f"      • CMA-ES: {cma_iterations} iterations")
            print(f"      • Simulated annealing: {sa_iterations} iterations")
            print("")

            result = optimize_hybrid(
                random_trials=random_trials,
                cma_iterations=cma_iterations,
                sa_iterations=sa_iterations,
                include_regional_multipliers=include_regional,
                verbose=True,
                show_progress=False,
            )
        elif method == "cmaes":
            result = optimize_cma_es(
                n_iterations=n_trials,
                include_regional_multipliers=include_regional,
                verbose=True,
                show_progress=False,
            )
        elif method == "optuna":
            result = optimize_optuna(
                n_trials=n_trials,
                include_regional_multipliers=include_regional,
                verbose=True,
                show_progress=False,
            )
        elif method == "sa":
            result = optimize_simulated_annealing(
                n_iterations=n_trials,
                include_regional_multipliers=include_regional,
                verbose=True,
                show_progress=False,
            )
        else:
            print(f"❌ Unknown method: {method}")
            return None

        if result is None:
            print("\n❌ Optimization returned no result")
            return None

        print_optimization_summary(result, include_regional)

        return result

    except Exception as e:
        print(f"\n❌ Optimization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def save_optimization_results():
    """Save optimization results with error handling."""
    try:
        print("\n💾 Saving optimization results...")
        save_optimized_parameters(config.OUTPUT_DIR)
        print_config_summary()
        return True
    except Exception as e:
        print(f"❌ Failed to save optimization results: {str(e)}")
        return False


def run_simulation_with_progress():
    """Run simulation with a nice progress indicator."""
    print("\n" + "="*80)
    print("🏃 RUNNING FULL POPULATION SIMULATION")
    print("="*80)
    print("")

    stages = [
        "📂 Loading geospatial data",
        "🗺️ Processing boundaries",
        "👥 Distributing population",
        "📈 Running simulation",
        "🏙️ Applying city constraints",
        "📮 Generating postal codes",
        "🏗️ Building hierarchy",
        "✅ Validating data",
        "💾 Exporting results"
    ]

    try:
        if TQDM_AVAILABLE:
            with tqdm(total=len(stages), desc="🚀 Simulation progress",
                      unit="stage", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]") as pbar:

                for stage in stages:
                    pbar.set_description(stage)
                    pbar.update(1)

                    # Run the actual simulation (only once)
                    if stage == stages[0]:
                        start_time = time.time()
                        df, hierarchy, validation = generate_main()
                        elapsed = time.time() - start_time

                pbar.set_description("✅ Complete")
        else:
            print("📂 Loading and processing data...")
            start_time = time.time()
            df, hierarchy, validation = generate_main()
            elapsed = time.time() - start_time

        print(f"\n⏱️  Simulation completed in {elapsed:.1f} seconds")

        if df is not None and not df.empty:
            print("\n🎉 Full simulation completed successfully!")

            # Display quick validation summary
            if validation and isinstance(validation, dict):
                print("\n📊 Quick Validation Summary:")

                # National validation
                if 'national' in validation:
                    print("\n   📈 National Population:")
                    for year, data in validation['national'].items():
                        if isinstance(data, dict) and 'diff_percent' in data:
                            diff = abs(data['diff_percent'])
                            if diff < 2:
                                status = "✅✅"
                            elif diff < 5:
                                status = "✅"
                            elif diff < 15:
                                status = "⚠️"
                            else:
                                status = "❌"
                            print(f"      {status} {year}: {data.get('population_sim', 0):,.0f} vs {data.get('population_un', 0):,.0f} (diff: {diff:.1f}%)")

                # Regional validation highlights
                if 'regional' in validation:
                    print("\n   🗺️ Regional (worst deviations):")
                    regions_data = []
                    for region, data in validation['regional'].items():
                        if isinstance(data, dict) and 'diff_percent' in data:
                            regions_data.append((abs(data['diff_percent']), region, data))

                    regions_data.sort(reverse=True)
                    for diff_pct, region, data in regions_data[:5]:  # Top 5 worst
                        if diff_pct < 10:
                            status = "✅"
                        elif diff_pct < 30:
                            status = "⚠️"
                        else:
                            status = "❌"
                        print(f"      {status} {region:15}: {data.get('population_sim', 0):,.0f} vs {data.get('population_target', 0):,.0f} (diff: {diff_pct:.1f}%)")

            return df, hierarchy, validation
        else:
            print("\n❌ Simulation failed to generate data.")
            return None, None, None

    except Exception as e:
        print(f"\n❌ Simulation failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None


def main():
    parser = argparse.ArgumentParser(
        description="Run Cameroon population optimization and simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run hybrid optimization with progress bars
  python -m src.core.run_optimization --optimize --method hybrid --trials 1000 --progress

  # Run CMA-ES without progress bars (faster)
  python -m src.core.run_optimization --optimize --method cmaes --trials 500

  # Run optimization with regional multipliers
  python -m src.core.run_optimization --optimize --method hybrid --include-regional --trials 2000 --progress

  # Skip optimization, just run simulation
  python -m src.core.run_optimization
        """
    )
    parser.add_argument("--optimize", action="store_true",
                        help="Run optimization before simulation")
    parser.add_argument("--method", type=str, default="hybrid",
                        choices=["hybrid", "cmaes", "optuna", "sa"],
                        help="Optimization method to use (default: hybrid)")
    parser.add_argument("--include-regional", action="store_true",
                        help="Include regional multipliers in optimization")
    parser.add_argument("--trials", type=int, default=200,
                        help="Number of optimization trials (default: 200)")
    parser.add_argument("--progress", action="store_true",
                        help="Show detailed progress bars")
    parser.add_argument("--verbose", action="store_true",
                        help="Show verbose optimization output")
    parser.add_argument("--skip-simulation", action="store_true",
                        help="Skip running the full simulation after optimization")
    parser.add_argument("--plot", action="store_true",
                        help="Generate convergence plots (requires matplotlib)")

    args = parser.parse_args()

    # Warn if progress requested but tqdm not available
    if args.progress and not TQDM_AVAILABLE:
        print("⚠️  --progress requires tqdm. Install with: pip install tqdm")
        print("   Continuing without progress bars...")
        args.progress = False

    # Run optimization if requested
    if args.optimize:
        if args.progress:
            result = run_optimization_with_progress(
                method=args.method,
                include_regional=args.include_regional,
                n_trials=args.trials
            )
        else:
            result = run_optimization_simple(
                method=args.method,
                include_regional=args.include_regional,
                n_trials=args.trials
            )

        if result:
            if not save_optimization_results():
                print("⚠️  Warning: Failed to save optimization results, continuing with simulation...")
        else:
            print("⚠️  Optimization failed, using existing parameters...")

    # Run the full simulation (unless skipped)
    if not args.skip_simulation:
        df, hierarchy, validation = run_simulation_with_progress()

        if df is not None and not df.empty:
            return 0
        else:
            return 1
    else:
        print("\n✅ Optimization complete (simulation skipped)")
        return 0


if __name__ == "__main__":
    sys.exit(main())