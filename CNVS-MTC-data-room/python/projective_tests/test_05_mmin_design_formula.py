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
# CNVS EQUATION 42 DETERMINISTIC EXPLORATORY TEST:
# MINIMUM CRITICAL FRAGMENTATION UNDER ASYMMETRIC TOPOLOGICAL EXPOSURE
#
# Test Name: Test 5 - Deterministic Exploratory Test of the Minimum Critical Fragmentation Design Formula under Asymmetric Topological Exposure.
# filename = "test_05_mmin_design_formula.py"
#
# PURPOSE:
# This program is a deterministic design-space exploration.
#
# It is NOT:
#   - a Monte Carlo reconstruction test;
#   - an empirical validation of CNVS;
#   - a simulation of V_L, V_G, Cons_R, Inv_C, or adversarial state recovery;
#   - an independent proof of Equation 42.
#
# It ASSUMES the formal CNVS design relation:
#
#       P(Rec*) <= p_comp^m
#
# and computes the minimum integer critical-fragment cardinality required to
# satisfy a selected target reconstruction-risk limit eta:
#
#       m_min = ceil( ln(eta) / ln(p_comp) )
#
# with:
#
#       p_comp = q + (1 - q) p_inf
#
# and the worst-case saturation:
#
#       p_inf = 2^(-h_res)
#
# where the formal entropy bound is p_inf <= 2^(-h_res).
#
# TOPOLOGY-TO-ENTROPY EXPLORATION:
# The mapping:
#
#       h_res = h_max * (1 - w_top)^erosion_power
#
# is a heuristic topology-to-entropy transfer profile used only to explore
# sensitivity. It is NOT asserted as a universal CNVS law.
#
# DETERMINISTIC ASYMMETRIC TOPOLOGY:
# A fixed rank-weighted topology is constructed without random sampling:
#
#       raw_weight_j = 1 / rank_j^topology_skew_exponent
#
# and normalized to sum to one.
#
# For each number r of colluding verifier slots, the program computes exactly:
#
#   1. MINIMUM EXPOSURE:
#      sum of the r smallest topological weights;
#
#   2. EXACT MEAN EXPOSURE:
#      r / Q_v, which is the exact expected captured weight over all uniformly
#      selected r-subsets, regardless of the fixed weight asymmetry;
#
#   3. MAXIMUM ADVERSARIAL EXPOSURE:
#      sum of the r largest topological weights.
#
# These are deterministic exposure scenarios. No random coalition or Dirichlet
# topology is sampled.
#
# FEASIBILITY LIMIT:
# ASSUMED_MAX_CRITICAL_FRAGMENTS is an implementation-level design assumption,
# not a constant derived from CNVS theory.
#
# q = 1 CONTROL:
# At total collusion, p_comp = 1 and no finite m can satisfy eta < 1.
# The program records m_min = infinity and never discards infinite results.
# ==============================================================================


def validate_probability_open(name, value):
    """Validate a finite probability strictly between zero and one."""
    value = float(value)
    if not math.isfinite(value) or not (0.0 < value < 1.0):
        raise ValueError(f"{name} must satisfy 0 < {name} < 1.")
    return value


def validate_non_negative_real(name, value):
    """Validate a finite non-negative real number."""
    value = float(value)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be a finite non-negative real number.")
    return value


def validate_positive_integer(name, value):
    """Validate a positive integer."""
    if not isinstance(value, (int, np.integer)) or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")
    return int(value)


def min_entropy_to_inference_bound(h_residual):
    """
    Convert residual conditional min-entropy into the corresponding inference
    upper bound.

    This deterministic exploration deliberately saturates the formal limit:
        p_inf = 2^(-h_residual).
    """
    h_residual = validate_non_negative_real("h_residual", h_residual)
    return 2.0 ** (-h_residual)


def m_min_for_security(p_comp, eta):
    """
    Compute the minimum positive integer m satisfying:
        p_comp^m <= eta.

    Boundary cases:
      - p_comp = 1  -> no finite m exists, return infinity;
      - p_comp = 0  -> m = 1 is sufficient.
    """
    eta = validate_probability_open("eta", eta)
    p_comp = float(p_comp)

    if not math.isfinite(p_comp) or not (0.0 <= p_comp <= 1.0):
        raise ValueError("p_comp must satisfy 0 <= p_comp <= 1.")

    if p_comp == 1.0:
        return math.inf

    if p_comp == 0.0:
        return 1

    log_eta = math.log(eta)
    log_p_comp = math.log(p_comp)

    return int(math.ceil(log_eta / log_p_comp))


def verify_m_min_minimality(p_comp, eta, m_required):
    """
    Verify the implementation of Equation 42 in logarithmic space.

    For finite m_required, this checks:
        p_comp^m_required <= eta
    and, when m_required > 1:
        p_comp^(m_required - 1) > eta.

    This validates the numerical implementation of the design formula. It does
    not independently validate the CNVS theorem from which the formula follows.
    """
    eta = validate_probability_open("eta", eta)
    p_comp = float(p_comp)

    if math.isinf(m_required):
        if p_comp != 1.0:
            raise RuntimeError(
                "Infinite m_min is only expected when p_comp equals one."
            )
        return True

    if p_comp == 0.0:
        if m_required != 1:
            raise RuntimeError("p_comp=0 must produce m_min=1.")
        return True

    log_eta = math.log(eta)
    log_p_comp = math.log(p_comp)

    log_bound_at_m = m_required * log_p_comp

    # Small numerical tolerance in logarithmic space.
    tolerance = 1e-12

    if log_bound_at_m > log_eta + tolerance:
        raise RuntimeError(
            "Computed m_min does not satisfy the target eta."
        )

    if m_required > 1:
        log_bound_at_previous_m = (m_required - 1) * log_p_comp

        if log_bound_at_previous_m <= log_eta + tolerance:
            raise RuntimeError(
                "Computed m_min is not minimal; m_min - 1 also satisfies eta."
            )

    return True


def residual_entropy_from_topological_exposure(
    h_max,
    w_top,
    erosion_power
):
    """
    Apply the heuristic deterministic topology-to-entropy transfer profile:
        h_res = h_max * (1 - w_top)^erosion_power.
    """
    h_max = validate_non_negative_real("h_max", h_max)
    erosion_power = validate_non_negative_real(
        "erosion_power",
        erosion_power
    )

    w_top = float(w_top)
    if not math.isfinite(w_top) or not (0.0 <= w_top <= 1.0):
        raise ValueError("w_top must satisfy 0 <= w_top <= 1.")

    return h_max * ((1.0 - w_top) ** erosion_power)


def construct_rank_weighted_topology(
    topology_components,
    topology_skew_exponent
):
    """
    Construct a fixed deterministic asymmetric topology.

    The weight of rank j is proportional to:
        1 / j^topology_skew_exponent.

    exponent = 0 produces a uniform topology.
    larger exponents produce stronger concentration.
    """
    topology_components = validate_positive_integer(
        "topology_components",
        topology_components
    )
    topology_skew_exponent = validate_non_negative_real(
        "topology_skew_exponent",
        topology_skew_exponent
    )

    ranks = np.arange(
        1,
        topology_components + 1,
        dtype=float
    )

    raw_weights = 1.0 / np.power(
        ranks,
        topology_skew_exponent
    )

    topology_weights = raw_weights / np.sum(raw_weights)

    if not np.isclose(np.sum(topology_weights), 1.0):
        raise RuntimeError("Topology weights do not sum to one.")

    if np.any(topology_weights <= 0.0):
        raise RuntimeError("All topology weights must be strictly positive.")

    return topology_weights


def deterministic_exposure_bounds(topology_weights, corrupted_slots):
    """
    Compute exact deterministic exposure values for a fixed topology.

    Returns:
      minimum_exposure:
          sum of the corrupted_slots smallest weights;

      exact_mean_exposure:
          corrupted_slots / Q_v, equal to the exact expected captured weight
          over all uniformly selected subsets of that cardinality;

      maximum_exposure:
          sum of the corrupted_slots largest weights.
    """
    topology_weights = np.asarray(topology_weights, dtype=float)

    if topology_weights.ndim != 1 or topology_weights.size == 0:
        raise ValueError(
            "topology_weights must be a non-empty one-dimensional array."
        )

    if np.any(~np.isfinite(topology_weights)):
        raise ValueError("topology_weights must be finite.")

    if np.any(topology_weights < 0.0):
        raise ValueError("topology_weights must be non-negative.")

    if not np.isclose(np.sum(topology_weights), 1.0):
        raise ValueError("topology_weights must sum to one.")

    Q_verifiers = topology_weights.size

    if (
        not isinstance(corrupted_slots, (int, np.integer))
        or not (0 <= corrupted_slots <= Q_verifiers)
    ):
        raise ValueError(
            "corrupted_slots must satisfy 0 <= corrupted_slots <= Q_verifiers."
        )

    if corrupted_slots == 0:
        return 0.0, 0.0, 0.0

    if corrupted_slots == Q_verifiers:
        return 1.0, 1.0, 1.0

    sorted_weights = np.sort(topology_weights)

    minimum_exposure = float(
        np.sum(sorted_weights[:corrupted_slots])
    )

    maximum_exposure = float(
        np.sum(sorted_weights[-corrupted_slots:])
    )

    exact_mean_exposure = corrupted_slots / Q_verifiers

    if not (
        minimum_exposure
        <= exact_mean_exposure + 1e-12
        <= maximum_exposure + 1e-12
    ):
        raise RuntimeError(
            "Deterministic exposure ordering is inconsistent."
        )

    return (
        minimum_exposure,
        exact_mean_exposure,
        maximum_exposure
    )


def design_point(
    q_direct,
    w_top,
    h_max,
    erosion_power,
    eta
):
    """
    Deterministically propagate one exposure assumption through the complete
    design chain:
        w_top -> h_res -> p_inf -> p_comp -> m_min.
    """
    q_direct = float(q_direct)

    if not math.isfinite(q_direct) or not (0.0 <= q_direct <= 1.0):
        raise ValueError("q_direct must satisfy 0 <= q_direct <= 1.")

    h_res = residual_entropy_from_topological_exposure(
        h_max=h_max,
        w_top=w_top,
        erosion_power=erosion_power
    )

    p_inf = min_entropy_to_inference_bound(h_res)

    p_comp = q_direct + (1.0 - q_direct) * p_inf

    # Guard only against floating-point overshoot.
    p_comp = min(max(p_comp, 0.0), 1.0)

    m_required = m_min_for_security(
        p_comp=p_comp,
        eta=eta
    )

    verify_m_min_minimality(
        p_comp=p_comp,
        eta=eta,
        m_required=m_required
    )

    return {
        "w_top": w_top,
        "h_res": h_res,
        "p_inf": p_inf,
        "p_comp": p_comp,
        "m_min": m_required,
    }


def maximum_feasible_q(q_values, m_values, feasibility_limit):
    """
    Return the largest q whose deterministic m_min is finite and does not exceed
    the assumed implementation feasibility limit.
    """
    q_values = np.asarray(q_values, dtype=float)
    m_values = np.asarray(m_values, dtype=float)

    feasible = np.isfinite(m_values) & (
        m_values <= feasibility_limit
    )

    if not np.any(feasible):
        return math.nan

    return float(np.max(q_values[feasible]))


def plot_finite_curve_with_infinity_markers(
    ax,
    x_values,
    y_values,
    infinity_display_level,
    label,
    marker,
    linestyle
):
    """
    Plot finite m_min values and explicitly mark infinite values at a designated
    display level. Infinite points are not silently removed or converted into a
    finite design requirement.
    """
    x_values = np.asarray(x_values, dtype=float)
    y_values = np.asarray(y_values, dtype=float)

    finite_mask = np.isfinite(y_values)
    infinite_mask = ~finite_mask

    ax.plot(
        x_values[finite_mask],
        y_values[finite_mask],
        marker=marker,
        markersize=3.0,
        linewidth=2.0,
        linestyle=linestyle,
        label=label
    )

    if np.any(infinite_mask):
        ax.scatter(
            x_values[infinite_mask],
            np.full(
                np.sum(infinite_mask),
                infinity_display_level
            ),
            marker="X",
            s=70,
            label=f"{label}: no finite $m$"
        )


def explore_m_min_design_space():
    # ==========================================================================
    # DESIGN PARAMETERS
    # ==========================================================================

    H_MAX = 10.0
    ETA = 1e-6

    Q_VERIFIERS = 200
    TOPOLOGY_COMPONENTS = Q_VERIFIERS

    # Fixed deterministic topology concentration.
    # This value is an exploratory design assumption, not a CNVS constant.
    TOPOLOGY_SKEW_EXPONENT = 0.75

    # Heuristic topology-to-entropy transfer exponent.
    EROSION_POWER = 2.0

    # Assumed implementation-level feasibility boundary.
    ASSUMED_MAX_CRITICAL_FRAGMENTS = 3_000

    # Deterministic sweep over exact verifier-slot counts.
    # Includes q = 1 as the total-collusion control.
    selected_r_values = np.unique(
        np.concatenate([
            np.rint(
                np.linspace(
                    1,
                    Q_VERIFIERS - 1,
                    80
                )
            ).astype(int),
            np.array([Q_VERIFIERS], dtype=int)
        ])
    )

    # ==========================================================================
    # VALIDATION AND TOPOLOGY CONSTRUCTION
    # ==========================================================================

    validate_non_negative_real("H_MAX", H_MAX)
    validate_probability_open("ETA", ETA)
    validate_positive_integer("Q_VERIFIERS", Q_VERIFIERS)
    validate_positive_integer(
        "TOPOLOGY_COMPONENTS",
        TOPOLOGY_COMPONENTS
    )
    validate_non_negative_real(
        "TOPOLOGY_SKEW_EXPONENT",
        TOPOLOGY_SKEW_EXPONENT
    )
    validate_non_negative_real(
        "EROSION_POWER",
        EROSION_POWER
    )
    validate_positive_integer(
        "ASSUMED_MAX_CRITICAL_FRAGMENTS",
        ASSUMED_MAX_CRITICAL_FRAGMENTS
    )

    if TOPOLOGY_COMPONENTS != Q_VERIFIERS:
        raise ValueError(
            "This exploration requires one topology component per verifier slot."
        )

    topology_weights = construct_rank_weighted_topology(
        topology_components=TOPOLOGY_COMPONENTS,
        topology_skew_exponent=TOPOLOGY_SKEW_EXPONENT
    )

    sorted_descending = np.sort(topology_weights)[::-1]

    topology_hhi = float(np.sum(topology_weights ** 2))
    top_10_share = float(
        np.sum(
            sorted_descending[
                :max(1, int(round(0.10 * TOPOLOGY_COMPONENTS)))
            ]
        )
    )

    # ==========================================================================
    # DETERMINISTIC EXPLORATION
    # ==========================================================================

    q_values = []

    exposures = {
        "minimum": [],
        "mean": [],
        "maximum": [],
    }

    results = {
        "minimum": {
            "h_res": [],
            "p_inf": [],
            "p_comp": [],
            "m_min": [],
        },
        "mean": {
            "h_res": [],
            "p_inf": [],
            "p_comp": [],
            "m_min": [],
        },
        "maximum": {
            "h_res": [],
            "p_inf": [],
            "p_comp": [],
            "m_min": [],
        },
    }

    print(
        "CNVS Test 5: Deterministic Exploratory Test of the "
        "Minimum Critical Fragmentation Design Formula"
    )
    print(f"Target reconstruction-risk limit eta: {ETA:.1e}")
    print(f"Initial residual min-entropy h_max: {H_MAX:.3f}")
    print(f"Verifier/topology components Q_v: {Q_VERIFIERS}")
    print(
        "Fixed topology skew exponent: "
        f"{TOPOLOGY_SKEW_EXPONENT:.3f}"
    )
    print(f"Topology concentration HHI: {topology_hhi:.6f}")
    print(f"Top 10% topology-weight share: {top_10_share:.4%}")
    print(
        "Heuristic topology-to-entropy erosion power: "
        f"{EROSION_POWER:.3f}"
    )
    print(
        "Assumed implementation feasibility limit: "
        f"{ASSUMED_MAX_CRITICAL_FRAGMENTS:,} critical fragments"
    )
    print(
        "No Monte Carlo sampling is performed. All exposure values are "
        "deterministic and exact for the fixed topology.\n"
    )

    for corrupted_slots in selected_r_values:
        q_direct = corrupted_slots / Q_VERIFIERS

        (
            minimum_exposure,
            exact_mean_exposure,
            maximum_exposure
        ) = deterministic_exposure_bounds(
            topology_weights=topology_weights,
            corrupted_slots=int(corrupted_slots)
        )

        scenario_exposures = {
            "minimum": minimum_exposure,
            "mean": exact_mean_exposure,
            "maximum": maximum_exposure,
        }

        q_values.append(q_direct)

        for scenario_name, w_top in scenario_exposures.items():
            point = design_point(
                q_direct=q_direct,
                w_top=w_top,
                h_max=H_MAX,
                erosion_power=EROSION_POWER,
                eta=ETA
            )

            exposures[scenario_name].append(point["w_top"])
            results[scenario_name]["h_res"].append(point["h_res"])
            results[scenario_name]["p_inf"].append(point["p_inf"])
            results[scenario_name]["p_comp"].append(point["p_comp"])
            results[scenario_name]["m_min"].append(point["m_min"])

        def format_m(value):
            return "infinity" if math.isinf(value) else f"{int(value):,}"

        print(
            f"q={q_direct:5.3f} | "
            f"W_min={minimum_exposure:8.5f} | "
            f"W_mean={exact_mean_exposure:8.5f} | "
            f"W_max={maximum_exposure:8.5f} | "
            f"m_min(min/mean/max)="
            f"{format_m(results['minimum']['m_min'][-1])} / "
            f"{format_m(results['mean']['m_min'][-1])} / "
            f"{format_m(results['maximum']['m_min'][-1])}"
        )

    q_values = np.asarray(q_values, dtype=float)

    for scenario_name in results:
        for variable_name in results[scenario_name]:
            results[scenario_name][variable_name] = np.asarray(
                results[scenario_name][variable_name],
                dtype=float
            )

        exposures[scenario_name] = np.asarray(
            exposures[scenario_name],
            dtype=float
        )

    # ==========================================================================
    # FEASIBILITY SUMMARY
    # ==========================================================================

    feasibility_labels = {
        "minimum": "Minimum-exposure coalition",
        "mean": "Exact mean exposure",
        "maximum": "Maximum adversarial exposure",
    }

    print("\nDeterministic feasibility summary:")

    for scenario_name in ["minimum", "mean", "maximum"]:
        max_q = maximum_feasible_q(
            q_values=q_values,
            m_values=results[scenario_name]["m_min"],
            feasibility_limit=ASSUMED_MAX_CRITICAL_FRAGMENTS
        )

        if math.isnan(max_q):
            print(
                f"  {feasibility_labels[scenario_name]}: "
                "no explored q value is feasible."
            )
        else:
            print(
                f"  {feasibility_labels[scenario_name]}: "
                f"feasible up to q={max_q:.3f} on the explored grid."
            )

    total_collusion_index = np.where(
        np.isclose(q_values, 1.0)
    )[0]

    if total_collusion_index.size != 1:
        raise RuntimeError(
            "The deterministic q=1 control must occur exactly once."
        )

    total_collusion_index = int(total_collusion_index[0])

    for scenario_name in results:
        if not math.isinf(
            results[scenario_name]["m_min"][total_collusion_index]
        ):
            raise RuntimeError(
                "q=1 must produce an infinite m_min in every scenario."
            )

    print(
        "\nTotal-collusion control q=1: "
        "p_comp=1 and no finite critical fragmentation can satisfy eta."
    )

    # ==========================================================================
    # PLOTTING
    # ==========================================================================

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(13, 12),
        sharex=True
    )

    # Plot 1: Deterministic topological exposure scenarios.
    ax1.plot(
        q_values,
        exposures["minimum"],
        marker="o",
        markersize=3.0,
        linewidth=2.0,
        label="Minimum possible exposure"
    )

    ax1.plot(
        q_values,
        exposures["mean"],
        marker="s",
        markersize=3.0,
        linewidth=2.0,
        linestyle="--",
        label="Exact mean exposure over all equal-cardinality subsets"
    )

    ax1.plot(
        q_values,
        exposures["maximum"],
        marker="^",
        markersize=3.0,
        linewidth=2.0,
        linestyle=":",
        label="Maximum adversarial exposure"
    )

    ax1.set_title(
        "1. Exact Deterministic Exposure Bounds on the Fixed Asymmetric Topology",
        fontsize=13,
        fontweight="bold"
    )
    ax1.set_ylabel(r"Captured topology-weight fraction $w_{\mathrm{top}}$")
    ax1.set_ylim(0.0, 1.03)
    ax1.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    ax1.legend(loc="upper left", fontsize=9)

    # Plot 2: Deterministic m_min design requirements.
    all_finite_m = np.concatenate([
        results[name]["m_min"][
            np.isfinite(results[name]["m_min"])
        ]
        for name in results
    ])

    if all_finite_m.size == 0:
        raise RuntimeError("No finite m_min values are available for plotting.")

    maximum_finite_m = float(np.max(all_finite_m))

    infinity_display_level = max(
        maximum_finite_m * 1.35,
        ASSUMED_MAX_CRITICAL_FRAGMENTS * 2.0
    )

    plot_finite_curve_with_infinity_markers(
        ax=ax2,
        x_values=q_values,
        y_values=results["minimum"]["m_min"],
        infinity_display_level=infinity_display_level,
        label="Minimum-exposure requirement",
        marker="o",
        linestyle="-"
    )

    plot_finite_curve_with_infinity_markers(
        ax=ax2,
        x_values=q_values,
        y_values=results["mean"]["m_min"],
        infinity_display_level=infinity_display_level,
        label="Exact-mean-exposure requirement",
        marker="s",
        linestyle="--"
    )

    plot_finite_curve_with_infinity_markers(
        ax=ax2,
        x_values=q_values,
        y_values=results["maximum"]["m_min"],
        infinity_display_level=infinity_display_level,
        label="Maximum-adversarial-exposure requirement",
        marker="^",
        linestyle=":"
    )

    ax2.axhline(
        ASSUMED_MAX_CRITICAL_FRAGMENTS,
        linestyle="-.",
        linewidth=2.0,
        label=(
            "Assumed implementation feasibility limit "
            f"({ASSUMED_MAX_CRITICAL_FRAGMENTS:,})"
        )
    )

    ax2.set_yscale("log")
    ax2.set_xlim(float(np.min(q_values)), 1.0)
    ax2.set_ylim(1.0, infinity_display_level * 1.15)

    ax2.set_title(
        "2. Deterministic Minimum Critical-Fragment Requirements",
        fontsize=13,
        fontweight="bold"
    )

    ax2.set_xlabel(r"Fraction of colluding verifier slots ($q=r/Q_v$)")
    ax2.set_ylabel(r"Required critical fragments $m_{\min}$")
    ax2.grid(
        True,
        which="both",
        linestyle="--",
        linewidth=0.5,
        alpha=0.65
    )
    ax2.legend(loc="upper left", fontsize=8.5)

    ax2.yaxis.set_major_formatter(
        mticker.FuncFormatter(
            lambda value, _: f"{value:,.0f}"
            if value >= 1.0
            else f"{value:g}"
        )
    )

    fig.suptitle(
        "CNVS Test 5 — Deterministic Exploratory Test of Equation 42\n"
        rf"$\eta={ETA:.0e}$, $h_{{max}}={H_MAX}$, "
        rf"fixed topology skew exponent={TOPOLOGY_SKEW_EXPONENT}",
        fontsize=15,
        fontweight="bold"
    )

    fig.text(
        0.5,
        0.012,
        "The topology-to-entropy mapping and feasibility limit are exploratory "
        "design assumptions. Infinite markers mean that no finite m can satisfy "
        "the selected eta; they are not omitted from the analysis.",
        ha="center",
        fontsize=9
    )

    plt.tight_layout(rect=(0.0, 0.04, 1.0, 0.95))
    plt.show()


if __name__ == "__main__":
    explore_m_min_design_space()
