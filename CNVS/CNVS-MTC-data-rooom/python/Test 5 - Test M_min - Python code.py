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

# ==============================================================================
# CNVS THEOREM 4 STATISTICAL PROJECTION:
# SYSTEMIC DESIGN FORMULA & MINIMUM CRITICAL FRAGMENTATION
#
# Test Name: Test 5: Statistical Projection of Minimum Critical Fragmentation (mmin) under Asymmetric Topological Exposure.
#
#
# PURPOSE:
# This script projects the minimum number of critical low-inference fragments 
# (m_min) required to satisfy a target systemic security threshold (eta), 
# ASSUMING the formal validity of the CNVS design formula (Eq. 42):
#
#       P(Rec*) <= eta
#       m_min = ceil( ln(eta) / ln(p_comp) )
#
# FORMAL ASSUMPTIONS:
#   1. p_comp = q + (1 - q) * p_inf
#   2. p_inf <= 2^(-h_res)
#   3. Target Security Boundary (eta): The maximum acceptable probability of 
#      unauthorized reconstruction (e.g., 1e-6).
#   4. Asymmetric Topological Exposure: The adversary captures non-uniform 
#      topological components (modeled via Dirichlet distribution), which 
#      dynamically erodes the residual min-entropy margin (h_res). 
#   5. Semantic Feasibility Limit (m_max): A systemic boundary representing 
#      the maximum number of critical fragments practically permissible.
# ==============================================================================

def min_entropy_to_inference_bound(h_residual):
    """
    Converts residual conditional min-entropy into an inference probability bound.
    """
    h_residual = max(float(h_residual), 0.0)
    return 2.0 ** (-h_residual)

def m_min_for_security(p_comp, eta):
    """
    Computes the minimum critical-fragment cardinality required by Eq. 42.
    """
    if not (0.0 < eta < 1.0):
        raise ValueError("eta must satisfy 0 < eta < 1.")
    if p_comp >= 1.0:
        return math.inf
    if p_comp <= 0.0:
        return 1

    return math.ceil(math.log(eta) / math.log(p_comp))

def dynamic_residual_entropy_from_topology(h_max, w_top, erosion_power=2.0):
    """
    Heuristic dynamic erosion profile based on asymmetric topological exposure.
    w_top represents the fraction of observable topological exposure acquired.
    """
    w_top = min(max(float(w_top), 0.0), 1.0)
    return h_max * ((1.0 - w_top) ** erosion_power)

def simulate_m_min_projection(seed=42):
    # ==========================================================================
    # SYSTEM PARAMETERS
    # ==========================================================================
    H_MAX = 10.0
    ETA = 1e-6

    Q_VERIFIERS = 200
    TOPOLOGY_COMPONENTS = Q_VERIFIERS
    ITERATIONS = 50000
    EROSION_POWER = 2.0
    M_MAX_SEMANTIC = 3000

    q_axis = np.linspace(0.01, 0.99, 80)
    rng = np.random.default_rng(seed)

    # Fixed asymmetric topology via Dirichlet distribution
    DIRICHLET_ALPHA = 1.0
    topology_weights = rng.dirichlet(np.ones(TOPOLOGY_COMPONENTS) * DIRICHLET_ALPHA)

    q_effective_values = []
    m_min_mean = []
    m_min_median = []
    m_min_95th = []
    m_min_worst_sampled = []
    p_comp_mean = []
    h_res_mean = []
    w_top_mean = []

    print("Executing CNVS Statistical Projection: Systemic Design Formula (m_min)...")
    print(f"Target security eta: {ETA:.1e}")
    print(f"Initial residual min-entropy h_max: {H_MAX}")
    print(f"Verifier pool Q_v: {Q_VERIFIERS}")
    print(f"Semantic feasibility boundary m_max: {M_MAX_SEMANTIC}")
    print(f"q range projected: 0.01 to 0.99\n")

    for q_target in q_axis:
        corrupted_slots = int(round(q_target * Q_VERIFIERS))
        corrupted_slots = min(max(corrupted_slots, 1), Q_VERIFIERS - 1)
        q_direct = corrupted_slots / Q_VERIFIERS

        m_samples, p_comp_samples, h_res_samples, w_top_samples = [], [], [], []

        for _ in range(ITERATIONS):
            # 1. Asymmetric topological exposure
            captured_components = rng.choice(
                TOPOLOGY_COMPONENTS, size=corrupted_slots, replace=False
            )
            w_top = float(np.sum(topology_weights[captured_components]))

            # 2. Dynamic residual min-entropy erosion
            h_res = dynamic_residual_entropy_from_topology(
                h_max=H_MAX, w_top=w_top, erosion_power=EROSION_POWER
            )
            p_inf = min_entropy_to_inference_bound(h_res)

            # 3. Composite compromise probability
            p_comp = q_direct + (1.0 - q_direct) * p_inf

            # 4. Minimum critical fragmentation (Eq. 42)
            m_required = m_min_for_security(p_comp, ETA)

            m_samples.append(m_required)
            p_comp_samples.append(p_comp)
            h_res_samples.append(h_res)
            w_top_samples.append(w_top)

        m_array = np.array(m_samples, dtype=float)
        finite_m = m_array[np.isfinite(m_array)]

        if finite_m.size == 0:
            mean_m = median_m = p95_m = worst_m = math.inf
        else:
            mean_m = float(np.mean(finite_m))
            median_m = float(np.median(finite_m))
            p95_m = float(np.percentile(finite_m, 95))
            worst_m = float(np.max(finite_m))

        q_effective_values.append(q_direct)
        m_min_mean.append(mean_m)
        m_min_median.append(median_m)
        m_min_95th.append(p95_m)
        m_min_worst_sampled.append(worst_m)
        p_comp_mean.append(float(np.mean(p_comp_samples)))
        h_res_mean.append(float(np.mean(h_res_samples)))
        w_top_mean.append(float(np.mean(w_top_samples)))

        print(
            f"q={q_direct:5.2f} | E[W_top]={w_top_mean[-1]:7.4f} | "
            f"E[h_res]={h_res_mean[-1]:8.4f} | E[p_comp]={p_comp_mean[-1]:10.7f} | "
            f"E[m_min]={mean_m:8.2f} | m_min(95%)={p95_m:8.2f}"
        )

    q_effective_values = np.array(q_effective_values, dtype=float)
    m_min_mean = np.array(m_min_mean, dtype=float)
    m_min_95th = np.array(m_min_95th, dtype=float)
    m_min_worst_sampled = np.array(m_min_worst_sampled, dtype=float)

    feasible_95 = m_min_95th <= M_MAX_SEMANTIC

    if np.any(feasible_95):
        max_q_feasible_95 = float(np.max(q_effective_values[feasible_95]))
        print(f"\n95% design criterion: feasible up to approximately q = {max_q_feasible_95:.2f}")
    else:
        print("\n95% design criterion: no q value is feasible under current parameters.")

    # ==========================================================================
    # PLOTTING
    # ==========================================================================
    fig, ax = plt.subplots(figsize=(13, 7))

    finite_values = np.concatenate([
        m_min_mean[np.isfinite(m_min_mean)],
        m_min_95th[np.isfinite(m_min_95th)],
        m_min_worst_sampled[np.isfinite(m_min_worst_sampled)]
    ])

    Y_AXIS_MIN = 1
    Y_AXIS_MAX = max(3500, float(np.percentile(finite_values, 99)) * 1.15)

    ax.plot(
        q_effective_values, m_min_mean,
        marker="o", markersize=2.6, markeredgewidth=0.4, linewidth=2.2,
        label=r"Expected $\mathbb{E}[m_{min}]$"
    )

    ax.plot(
        q_effective_values, m_min_95th,
        marker="s", markersize=2.6, markeredgewidth=0.4, linestyle="--", linewidth=2.2,
        label=r"Risk-margin design $m_{min}^{95\%}$"
    )

    ax.plot(
        q_effective_values, m_min_worst_sampled,
        marker="^", markersize=2.6, markeredgewidth=0.4, linestyle=":", linewidth=1.8,
        label=r"Worst sampled $m_{min}$"
    )

    ax.axhline(
        M_MAX_SEMANTIC,
        linestyle="-.", linewidth=2.3,
        label=rf"Semantic feasibility limit $m_{{max}}={M_MAX_SEMANTIC}$"
    )

    reference_fragment_levels = [50, 150, 250, 350, 450]
    for level in reference_fragment_levels:
        ax.axhline(level, linestyle="--", linewidth=1.35, alpha=0.65)
        ax.text(
            1.006, level, f"{level} fragments",
            transform=ax.get_yaxis_transform(), va="center", ha="left",
            fontsize=8.5, fontweight="bold", alpha=0.9, clip_on=False
        )

    ax.fill_between(
        q_effective_values, Y_AXIS_MIN, M_MAX_SEMANTIC,
        where=feasible_95, alpha=0.12, label=r"Feasible under 95% criterion"
    )

    ax.fill_between(
        q_effective_values, M_MAX_SEMANTIC, Y_AXIS_MAX,
        where=~feasible_95, alpha=0.12, label=r"Infeasible under 95% criterion"
    )

    ax.set_yscale("log")
    ax.set_xlim(0.01, 0.99)
    ax.set_ylim(Y_AXIS_MIN, Y_AXIS_MAX)

    ax.set_title(
        "CNVS Systemic Design Formula: Minimum Critical Fragmentation\n"
        rf"Target $\eta={ETA:.0e}$, asymmetric topological exposure, "
        rf"$h_{{max}}={H_MAX}$, curve shown up to $q=0.99$",
        pad=15
    )

    ax.set_xlabel(r"Fraction of colluding verifiers ($q=r/Q_v$)")
    ax.set_ylabel(r"Minimum critical fragments required ($m_{min}$)")

    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.65)
    ax.legend(loc="upper left", fontsize=10)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    simulate_m_min_projection()