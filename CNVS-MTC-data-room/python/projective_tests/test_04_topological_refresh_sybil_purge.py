# ==============================================================================
# CNVS FRAMEWORK - EXECUTION ENVIRONMENT
# Copyright (c) 2026 Massimo Comitato.
#
# This file is part of the CNVS MTC Data Room.
# Licensed under the PolyForm Noncommercial License 1.0.0.
#
# Commercial use is prohibited without prior written authorization.
# Academic review and technical due diligence use are permitted under the license.
#
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# ==============================================================================

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ==============================================================================
# CNVS REMARK 11.1 / LEMMA 10 CONDITIONAL PROJECTION:
# TOPOLOGICAL REFRESH, FAULT-INJECTION, AND AUTHENTICATED IDENTITY EXCLUSION
#
# Test Name: Test 4 - Monte Carlo Stress Projection of Topological Refresh under Repeated Fault-Injection and Stochastic Authenticated Identity Exclusion.
# filename = "test_04_topological_refresh_sybil_purge.py"
#
# PURPOSE:
# This script performs a Monte Carlo stress projection of metadata usability
# across repeated rejected fault-injection cycles.
#
# It compares four implementation-level scenarios:
#
#   1. STATIC_NO_EXCLUSION
#      No refresh and no identity exclusion. Metadata remains fully transferable
#      across cycles.
#
#   2. PERFECT_REFRESH_ONLY
#      CNVS-style perfect topological refresh after every rejected transition,
#      but no identity exclusion.
#
#   3. PERFECT_REFRESH_WITH_EXCLUSION
#      Perfect refresh plus stochastic exclusion of authenticated malicious
#      identities whose fraudulent participation is assumed to be identifiable.
#
#   4. IMPERFECT_REFRESH_WITH_EXCLUSION
#      A stress scenario in which a fraction of currently usable metadata remains
#      transferable after refresh, together with stochastic identity exclusion.
#
# FORMAL / THEORETICAL SCOPE:
# The script ASSUMES the formal CNVS refresh mechanism described after rejection:
# decomposition, task structure, and assignments are regenerated for the next
# transition attempt.
#
# It does NOT instantiate the full typed universe 𝓢, execute V_L or V_G, or
# calculate the mutual information I(X_S; M_S).
#
# FORCED-REJECTION STRESS SCHEDULE:
# Every evaluation window represents one adversarial fault-injection attempt that
# is assumed to be rejected by the Global-Veto mechanism. Therefore, the code
# models the consequences of repeated rejection; it does not compute V_G itself.
#
# METADATA INTERPRETATION:
# "Usable metadata" is an operational proxy for metadata that remains relevant to
# the CURRENT topology. Refresh does not erase the attacker's physical historical
# archive. It reduces cross-cycle transferability to the newly randomized topology.
#
# The operational limit L_meta is NOT the formal mutual-information parameter
# gamma_top from Lemma 10. It is a normalized implementation-level risk threshold.
#
# IDENTITY-EXCLUSION INTERPRETATION:
# Identity exclusion is an implementation-layer assumption, not a theorem-level
# guarantee. Each active malicious authenticated identity has a configurable
# probability of being identified and excluded after a rejected transition.
# New identities may also be regenerated between cycles.
#
# STATISTICAL OUTPUTS:
#   - probability that usable metadata exceeds L_meta at least once;
#   - 95% Wilson confidence interval for that probability;
#   - cycle of first threshold exceedance;
#   - distribution of cycle peaks;
#   - final malicious-identity population;
#   - probability of complete population exhaustion within the simulated horizon.
#
# The Monte Carlo process deliberately includes scenarios in which refresh fails
# to keep metadata below the operational threshold.
# ==============================================================================


SCENARIOS = {
    "STATIC_NO_EXCLUSION": {
        "label": "Static topology, no exclusion",
        "refresh_retention": 1.0,
        "identity_exclusion": False,
    },
    "PERFECT_REFRESH_ONLY": {
        "label": "Perfect refresh only",
        "refresh_retention": 0.0,
        "identity_exclusion": False,
    },
    "PERFECT_REFRESH_WITH_EXCLUSION": {
        "label": "Perfect refresh + identity exclusion",
        "refresh_retention": 0.0,
        "identity_exclusion": True,
    },
    "IMPERFECT_REFRESH_WITH_EXCLUSION": {
        "label": "Imperfect refresh + identity exclusion",
        "refresh_retention": 0.35,
        "identity_exclusion": True,
    },
}


def validate_probability(name, value):
    """Validate and return a finite probability in [0, 1]."""
    value = float(value)
    if not math.isfinite(value) or not (0.0 <= value <= 1.0):
        raise ValueError(f"{name} must satisfy 0 <= {name} <= 1.")
    return value


def validate_non_negative_real(name, value):
    """Validate and return a finite non-negative real value."""
    value = float(value)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be a finite non-negative real number.")
    return value


def validate_positive_integer(name, value):
    """Validate and return a positive integer."""
    if not isinstance(value, (int, np.integer)) or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")
    return int(value)


def wilson_interval(successes, trials, z=1.959963984540054):
    """
    Wilson score confidence interval for a binomial proportion.
    """
    successes = int(successes)
    trials = validate_positive_integer("trials", trials)

    if not (0 <= successes <= trials):
        raise ValueError("successes must satisfy 0 <= successes <= trials.")

    p_hat = successes / trials
    denominator = 1.0 + (z * z / trials)
    center = (
        p_hat
        + (z * z) / (2.0 * trials)
    ) / denominator

    half_width = (
        z
        * math.sqrt(
            (p_hat * (1.0 - p_hat) / trials)
            + (z * z) / (4.0 * trials * trials)
        )
        / denominator
    )

    return max(0.0, center - half_width), min(1.0, center + half_width)


def sample_gamma_with_mean_and_cv(rng, mean_values, coefficient_of_variation):
    """
    Sample non-negative cycle-level leakage increments from Gamma distributions.

    For each positive mean μ and coefficient of variation CV:
        shape = 1 / CV^2
        scale = μ * CV^2

    This is a heuristic implementation-level stress distribution, not a CNVS law.
    """
    coefficient_of_variation = validate_non_negative_real(
        "coefficient_of_variation",
        coefficient_of_variation
    )

    mean_values = np.asarray(mean_values, dtype=float)

    if np.any(~np.isfinite(mean_values)) or np.any(mean_values < 0.0):
        raise ValueError("mean_values must be finite and non-negative.")

    if coefficient_of_variation == 0.0:
        return mean_values.copy()

    samples = np.zeros_like(mean_values)
    positive_mask = mean_values > 0.0

    if np.any(positive_mask):
        shape = 1.0 / (coefficient_of_variation ** 2)
        scales = (
            mean_values[positive_mask]
            * (coefficient_of_variation ** 2)
        )
        samples[positive_mask] = rng.gamma(
            shape=shape,
            scale=scales
        )

    return samples


def simulate_scenario(
    rng,
    scenario_name,
    num_runs,
    num_cycles,
    t_eval,
    operational_metadata_risk_limit,
    initial_sybils,
    base_accumulation_rate,
    cycle_leakage_cv,
    detection_probability,
    identity_regeneration_mean
):
    """
    Simulate one scenario over many independent Monte Carlo trajectories.

    State variables
    ---------------
    active_sybils:
        Active malicious authenticated identities at the start of each cycle.

    usable_carryover:
        Metadata still relevant to the current topology after the preceding
        refresh event. Perfect refresh sets this to zero. Static topology retains
        it fully. Imperfect refresh retains a configured fraction.

    historical_archive:
        Total metadata physically acquired by the attacker. It is not erased by
        refresh, but only the retained fraction of current usable metadata can be
        transferred to the next topology in this proxy model.
    """
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    scenario = SCENARIOS[scenario_name]
    refresh_retention = validate_probability(
        "refresh_retention",
        scenario["refresh_retention"]
    )
    identity_exclusion = bool(scenario["identity_exclusion"])

    num_runs = validate_positive_integer("num_runs", num_runs)
    num_cycles = validate_positive_integer("num_cycles", num_cycles)
    t_eval = validate_positive_integer("t_eval", t_eval)

    operational_metadata_risk_limit = validate_non_negative_real(
        "operational_metadata_risk_limit",
        operational_metadata_risk_limit
    )

    initial_sybils = validate_positive_integer(
        "initial_sybils",
        initial_sybils
    )

    base_accumulation_rate = validate_non_negative_real(
        "base_accumulation_rate",
        base_accumulation_rate
    )

    cycle_leakage_cv = validate_non_negative_real(
        "cycle_leakage_cv",
        cycle_leakage_cv
    )

    detection_probability = validate_probability(
        "detection_probability",
        detection_probability
    )

    identity_regeneration_mean = validate_non_negative_real(
        "identity_regeneration_mean",
        identity_regeneration_mean
    )

    active_sybils = np.full(
        num_runs,
        initial_sybils,
        dtype=np.int64
    )

    usable_carryover = np.zeros(num_runs, dtype=float)
    historical_archive = np.zeros(num_runs, dtype=float)

    cycle_peaks = np.zeros((num_runs, num_cycles), dtype=float)
    sybil_history = np.zeros((num_runs, num_cycles + 1), dtype=np.int64)
    excluded_history = np.zeros((num_runs, num_cycles), dtype=np.int64)
    regenerated_history = np.zeros((num_runs, num_cycles), dtype=np.int64)

    sybil_history[:, 0] = active_sybils

    first_breach_cycle = np.full(num_runs, -1, dtype=np.int32)
    ever_breached = np.zeros(num_runs, dtype=bool)

    for cycle_index in range(num_cycles):
        # 1. STOCHASTIC METADATA ACCUMULATION DURING THE EVALUATION WINDOW
        #
        # The expected cycle leakage scales with the current malicious-identity
        # pressure. If active identities exceed the initial population because of
        # regeneration, the pressure ratio may exceed one.
        pressure_ratio = active_sybils / initial_sybils

        expected_new_metadata = (
            base_accumulation_rate
            * t_eval
            * pressure_ratio
        )

        new_metadata = sample_gamma_with_mean_and_cv(
            rng=rng,
            mean_values=expected_new_metadata,
            coefficient_of_variation=cycle_leakage_cv
        )

        historical_archive += new_metadata

        # Peak usable metadata before the forced rejection and refresh.
        current_peak = usable_carryover + new_metadata
        cycle_peaks[:, cycle_index] = current_peak

        breaches_this_cycle = (
            current_peak > operational_metadata_risk_limit
        )

        new_first_breach = breaches_this_cycle & (~ever_breached)
        first_breach_cycle[new_first_breach] = cycle_index + 1
        ever_breached |= breaches_this_cycle

        # 2. FORCED GLOBAL-VETO REJECTION + TOPOLOGICAL REFRESH PROXY
        #
        # The attacker keeps a historical archive, but only refresh_retention of
        # the currently usable metadata is assumed transferable to the next
        # randomized topology.
        usable_carryover = refresh_retention * current_peak

        # 3. STOCHASTIC AUTHENTICATED IDENTITY EXCLUSION
        #
        # This is an implementation-layer assumption. It is performed only in
        # scenarios explicitly configured with identity exclusion.
        if identity_exclusion:
            excluded = rng.binomial(
                n=active_sybils,
                p=detection_probability
            ).astype(np.int64)

            regenerated = rng.poisson(
                lam=identity_regeneration_mean,
                size=num_runs
            ).astype(np.int64)

            active_sybils = np.maximum(
                0,
                active_sybils - excluded + regenerated
            )
        else:
            excluded = np.zeros(num_runs, dtype=np.int64)
            regenerated = np.zeros(num_runs, dtype=np.int64)

        excluded_history[:, cycle_index] = excluded
        regenerated_history[:, cycle_index] = regenerated
        sybil_history[:, cycle_index + 1] = active_sybils

    breach_count = int(np.sum(ever_breached))
    breach_probability = breach_count / num_runs
    breach_ci_low, breach_ci_high = wilson_interval(
        successes=breach_count,
        trials=num_runs
    )

    purged = active_sybils == 0
    purge_count = int(np.sum(purged))
    purge_probability = purge_count / num_runs
    purge_ci_low, purge_ci_high = wilson_interval(
        successes=purge_count,
        trials=num_runs
    )

    breached_cycles = first_breach_cycle[first_breach_cycle > 0]

    mean_first_breach_cycle = (
        float(np.mean(breached_cycles))
        if breached_cycles.size > 0
        else math.nan
    )

    return {
        "scenario_name": scenario_name,
        "scenario_label": scenario["label"],
        "refresh_retention": refresh_retention,
        "identity_exclusion": identity_exclusion,
        "cycle_peaks": cycle_peaks,
        "sybil_history": sybil_history,
        "excluded_history": excluded_history,
        "regenerated_history": regenerated_history,
        "historical_archive": historical_archive,
        "first_breach_cycle": first_breach_cycle,
        "breach_probability": breach_probability,
        "breach_ci": (breach_ci_low, breach_ci_high),
        "mean_first_breach_cycle": mean_first_breach_cycle,
        "purge_probability": purge_probability,
        "purge_ci": (purge_ci_low, purge_ci_high),
        "final_active_sybils": active_sybils,
    }


def summarize_scenario(result):
    """Return summary statistics for a completed scenario."""
    peaks = result["cycle_peaks"]
    final_sybils = result["final_active_sybils"]
    archive = result["historical_archive"]

    return {
        "peak_median": np.median(peaks, axis=0),
        "peak_q05": np.quantile(peaks, 0.05, axis=0),
        "peak_q95": np.quantile(peaks, 0.95, axis=0),
        "sybil_median": np.median(result["sybil_history"], axis=0),
        "sybil_q05": np.quantile(result["sybil_history"], 0.05, axis=0),
        "sybil_q95": np.quantile(result["sybil_history"], 0.95, axis=0),
        "mean_max_peak": float(np.mean(np.max(peaks, axis=1))),
        "median_max_peak": float(np.median(np.max(peaks, axis=1))),
        "median_final_sybils": float(np.median(final_sybils)),
        "mean_final_sybils": float(np.mean(final_sybils)),
        "median_historical_archive": float(np.median(archive)),
    }


def run_projection():
    # ==========================================================================
    # GLOBAL PARAMETERS
    # ==========================================================================

    NUM_RUNS = 100_000
    MAX_TICKS = 600
    T_EVAL = 100

    if MAX_TICKS % T_EVAL != 0:
        raise ValueError(
            "MAX_TICKS must be an integer multiple of T_EVAL "
            "for this fixed-window projection."
        )

    NUM_CYCLES = MAX_TICKS // T_EVAL

    # Operational proxy threshold. This is not the formal gamma_top quantity.
    OPERATIONAL_METADATA_RISK_LIMIT = 50.0

    INITIAL_SYBILS = 1_200

    # Expected first-cycle metadata without population reduction:
    # 0.35 * 100 = 35 operational units.
    BASE_ACCUMULATION_RATE = 0.35

    # Cycle-level heuristic variability of leakage increments.
    CYCLE_LEAKAGE_CV = 0.35

    # Implementation-layer identity-exclusion assumptions.
    DETECTION_PROBABILITY = 0.25
    IDENTITY_REGENERATION_MEAN = 20.0

    # Reproducible independent random streams for each scenario.
    SEED = 42

    # ==========================================================================
    # VALIDATION
    # ==========================================================================

    validate_positive_integer("NUM_RUNS", NUM_RUNS)
    validate_positive_integer("MAX_TICKS", MAX_TICKS)
    validate_positive_integer("T_EVAL", T_EVAL)
    validate_positive_integer("INITIAL_SYBILS", INITIAL_SYBILS)

    validate_non_negative_real(
        "OPERATIONAL_METADATA_RISK_LIMIT",
        OPERATIONAL_METADATA_RISK_LIMIT
    )
    validate_non_negative_real(
        "BASE_ACCUMULATION_RATE",
        BASE_ACCUMULATION_RATE
    )
    validate_non_negative_real(
        "CYCLE_LEAKAGE_CV",
        CYCLE_LEAKAGE_CV
    )
    validate_probability(
        "DETECTION_PROBABILITY",
        DETECTION_PROBABILITY
    )
    validate_non_negative_real(
        "IDENTITY_REGENERATION_MEAN",
        IDENTITY_REGENERATION_MEAN
    )

    scenario_names = list(SCENARIOS.keys())
    master_seed_sequence = np.random.SeedSequence(SEED)
    child_seed_sequences = master_seed_sequence.spawn(len(scenario_names))

    results = {}
    summaries = {}

    print(
        "CNVS Monte Carlo Projection: Topological Refresh, "
        "Fault-Injection, and Authenticated Identity Exclusion"
    )
    print(f"Monte Carlo trajectories per scenario: {NUM_RUNS:,}")
    print(f"Evaluation windows: {NUM_CYCLES}")
    print(f"Ticks per evaluation window: {T_EVAL}")
    print(
        "Operational metadata risk limit L_meta: "
        f"{OPERATIONAL_METADATA_RISK_LIMIT:.2f}"
    )
    print(f"Initial malicious authenticated identities: {INITIAL_SYBILS:,}")
    print(
        "Expected first-cycle leakage before stochastic variation: "
        f"{BASE_ACCUMULATION_RATE * T_EVAL:.2f}"
    )
    print(f"Cycle-level leakage CV: {CYCLE_LEAKAGE_CV:.2f}")
    print(f"Detection probability per active identity: {DETECTION_PROBABILITY:.2%}")
    print(
        "Mean regenerated identities per rejected cycle: "
        f"{IDENTITY_REGENERATION_MEAN:.2f}"
    )
    print(f"Master random seed: {SEED}\n")

    for scenario_name, child_seed_sequence in zip(
        scenario_names,
        child_seed_sequences
    ):
        rng = np.random.default_rng(child_seed_sequence)

        result = simulate_scenario(
            rng=rng,
            scenario_name=scenario_name,
            num_runs=NUM_RUNS,
            num_cycles=NUM_CYCLES,
            t_eval=T_EVAL,
            operational_metadata_risk_limit=OPERATIONAL_METADATA_RISK_LIMIT,
            initial_sybils=INITIAL_SYBILS,
            base_accumulation_rate=BASE_ACCUMULATION_RATE,
            cycle_leakage_cv=CYCLE_LEAKAGE_CV,
            detection_probability=DETECTION_PROBABILITY,
            identity_regeneration_mean=IDENTITY_REGENERATION_MEAN
        )

        summary = summarize_scenario(result)

        results[scenario_name] = result
        summaries[scenario_name] = summary

        breach_low, breach_high = result["breach_ci"]
        purge_low, purge_high = result["purge_ci"]

        first_breach_text = (
            f"{result['mean_first_breach_cycle']:.2f}"
            if math.isfinite(result["mean_first_breach_cycle"])
            else "not observed"
        )

        print(result["scenario_label"])
        print(
            "  Refresh retention: "
            f"{result['refresh_retention']:.2f}"
        )
        print(
            "  Identity exclusion enabled: "
            f"{result['identity_exclusion']}"
        )
        print(
            "  P(any L_meta exceedance): "
            f"{result['breach_probability']:.4%} "
            f"[95% CI {breach_low:.4%}, {breach_high:.4%}]"
        )
        print(
            "  Mean first exceedance cycle, conditional on exceedance: "
            f"{first_breach_text}"
        )
        print(
            "  Median maximum usable metadata: "
            f"{summary['median_max_peak']:.2f}"
        )
        print(
            "  Mean maximum usable metadata: "
            f"{summary['mean_max_peak']:.2f}"
        )
        print(
            "  Median final active identities: "
            f"{summary['median_final_sybils']:.0f}"
        )
        print(
            "  P(complete identity-population exhaustion): "
            f"{result['purge_probability']:.4%} "
            f"[95% CI {purge_low:.4%}, {purge_high:.4%}]"
        )
        print(
            "  Median historical external archive: "
            f"{summary['median_historical_archive']:.2f}\n"
        )

    # ==========================================================================
    # INTERNAL CONSISTENCY CHECKS
    # ==========================================================================

    static_peaks = results["STATIC_NO_EXCLUSION"]["cycle_peaks"]
    static_differences = np.diff(static_peaks, axis=1)

    if np.any(static_differences < -1e-12):
        raise RuntimeError(
            "Static-topology usable metadata decreased unexpectedly."
        )

    perfect_refresh = results["PERFECT_REFRESH_ONLY"]
    perfect_refresh_exclusion = results[
        "PERFECT_REFRESH_WITH_EXCLUSION"
    ]

    if perfect_refresh["refresh_retention"] != 0.0:
        raise RuntimeError("Perfect-refresh scenario retention must equal zero.")

    if perfect_refresh_exclusion["refresh_retention"] != 0.0:
        raise RuntimeError(
            "Perfect-refresh-with-exclusion retention must equal zero."
        )

    if np.any(
        results["STATIC_NO_EXCLUSION"]["final_active_sybils"]
        != INITIAL_SYBILS
    ):
        raise RuntimeError(
            "Static no-exclusion scenario changed the identity population."
        )

    if np.any(
        results["PERFECT_REFRESH_ONLY"]["final_active_sybils"]
        != INITIAL_SYBILS
    ):
        raise RuntimeError(
            "Refresh-only scenario changed the identity population."
        )

    # ==========================================================================
    # PLOTTING
    # ==========================================================================

    cycle_axis = np.arange(1, NUM_CYCLES + 1)
    population_cycle_axis = np.arange(0, NUM_CYCLES + 1)

    fig, axes = plt.subplots(3, 1, figsize=(13, 15))
    ax1, ax2, ax3 = axes

    # --------------------------------------------------------------------------
    # Plot 1: Distribution of usable metadata peaks by cycle.
    # --------------------------------------------------------------------------
    for scenario_name in scenario_names:
        summary = summaries[scenario_name]
        label = results[scenario_name]["scenario_label"]

        line = ax1.plot(
            cycle_axis,
            summary["peak_median"],
            marker="o",
            linewidth=2.2,
            label=label
        )[0]

        ax1.fill_between(
            cycle_axis,
            summary["peak_q05"],
            summary["peak_q95"],
            alpha=0.13,
            color=line.get_color()
        )

    ax1.axhline(
        OPERATIONAL_METADATA_RISK_LIMIT,
        linestyle="--",
        linewidth=2.0,
        label=r"Operational risk limit $L_{\mathrm{meta}}$"
    )

    ax1.set_title(
        "1. Usable Metadata Peaks after Repeated Fault-Injection",
        fontsize=14,
        fontweight="bold"
    )
    ax1.set_xlabel("Rejected transition cycle")
    ax1.set_ylabel("Usable metadata proxy")
    ax1.set_xticks(cycle_axis)
    ax1.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    ax1.legend(loc="upper left", fontsize=9)

    # --------------------------------------------------------------------------
    # Plot 2: Probability of at least one operational-limit exceedance.
    # --------------------------------------------------------------------------
    breach_probabilities = np.array([
        results[name]["breach_probability"]
        for name in scenario_names
    ])

    lower_errors = np.array([
        results[name]["breach_probability"]
        - results[name]["breach_ci"][0]
        for name in scenario_names
    ])

    upper_errors = np.array([
        results[name]["breach_ci"][1]
        - results[name]["breach_probability"]
        for name in scenario_names
    ])

    x_positions = np.arange(len(scenario_names))

    ax2.bar(
        x_positions,
        breach_probabilities * 100.0,
        yerr=np.vstack([
            lower_errors * 100.0,
            upper_errors * 100.0
        ]),
        capsize=5
    )

    ax2.set_title(
        "2. Probability of at Least One Operational-Limit Exceedance",
        fontsize=14,
        fontweight="bold"
    )
    ax2.set_ylabel("Probability [%]")
    ax2.set_xticks(x_positions)
    ax2.set_xticklabels(
        [SCENARIOS[name]["label"] for name in scenario_names],
        rotation=12,
        ha="right"
    )
    ax2.set_ylim(0.0, 105.0)
    ax2.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.65)

    # --------------------------------------------------------------------------
    # Plot 3: Malicious authenticated identity population.
    # --------------------------------------------------------------------------
    exclusion_scenarios = [
        "PERFECT_REFRESH_WITH_EXCLUSION",
        "IMPERFECT_REFRESH_WITH_EXCLUSION",
    ]

    for scenario_name in exclusion_scenarios:
        summary = summaries[scenario_name]
        label = results[scenario_name]["scenario_label"]

        line = ax3.plot(
            population_cycle_axis,
            summary["sybil_median"],
            marker="o",
            linewidth=2.4,
            label=label
        )[0]

        ax3.fill_between(
            population_cycle_axis,
            summary["sybil_q05"],
            summary["sybil_q95"],
            alpha=0.14,
            color=line.get_color()
        )

    ax3.axhline(
        INITIAL_SYBILS,
        linestyle=":",
        linewidth=1.6,
        label="Initial identity population"
    )

    ax3.set_title(
        "3. Stochastic Authenticated Identity Exclusion and Regeneration",
        fontsize=14,
        fontweight="bold"
    )
    ax3.set_xlabel("Rejected transition cycle")
    ax3.set_ylabel("Active malicious authenticated identities")
    ax3.set_xticks(population_cycle_axis)
    ax3.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    ax3.legend(loc="upper right", fontsize=9)
    ax3.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda value, _: f"{int(value):,}")
    )

    fig.suptitle(
        "CNVS Conditional Monte Carlo Projection: "
        "Topological Refresh and Identity-Exclusion Stress Test",
        fontsize=15,
        fontweight="bold"
    )

    fig.text(
        0.5,
        0.012,
        "Shaded regions show the 5th–95th percentile range. "
        "L_meta is an operational proxy, not the formal mutual-information "
        "quantity gamma_top. Refresh limits transferability; it does not erase "
        "the adversary's historical archive.",
        ha="center",
        fontsize=9
    )

    plt.tight_layout(rect=(0.0, 0.035, 1.0, 0.965))
    plt.show()


if __name__ == "__main__":
    run_projection()
