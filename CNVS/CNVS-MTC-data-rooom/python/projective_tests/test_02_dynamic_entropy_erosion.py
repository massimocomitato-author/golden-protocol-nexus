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



import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# CNVS THEOREM 4 STATISTICAL PROJECTION:
# DYNAMIC RESIDUAL MIN-ENTROPY EROSION STRESS TEST
#
#
#   Test Name: Test 2: Statistical Projection (Stress Test) under Dynamic Erosion of the Residual Min-Entropy.
#
# PURPOSE:
# This simulator acts as a formal stress test for the CNVS reconstruction layer.
# Unlike Test 1, which assumes a static min-entropy margin, this script models 
# the dynamic erosion of the residual conditional min-entropy as the adversarial 
# fraction q increases.
#
# FORMAL ASSUMPTION (Erosion Profiles):
#   H∞(d_miss_i | View_adv^(i)) >= h_res(q)
#   p_inf(q) <= 2^(-h_res(q))
#   p_comp(q) = q + (1 - q) p_inf(q)
#   P(Rec*) <= p_comp(q)^m
#
# The profiles (linear, quadratic, radical) are heuristic stress-test models, 
# not universal physical laws. They strictly test the resilience of Theorem 4 
# under accelerated adversarial inference.
# ==============================================================================

def min_entropy_to_inference_bound(h_residual):
    """
    Converts a residual conditional min-entropy margin into an adversarial
    inference probability upper bound.
    """
    h_residual = max(float(h_residual), 0.0)
    return 2.0 ** (-h_residual)

def dynamic_residual_entropy(h_max, q, erosion_profile):
    """
    Computes the eroded min-entropy margin based on selected heuristic profiles.
    h_res(q) = h_max * phi(q)
    """
    if erosion_profile == "linear":
        return h_max * (1.0 - q)
    if erosion_profile == "quadratic":
        return h_max * ((1.0 - q) ** 2)
    if erosion_profile == "radical":
        return h_max * ((1.0 - q) ** 4)
    if erosion_profile == "static":
        return h_max

    raise ValueError("Unknown erosion profile.")

def simulate_cnvs_dynamic_erosion(
    Q_verifiers,
    r_malicious,
    k_fragments,
    m_critical,
    h_max,
    erosion_profile,
    iterations=100000,
    seed=None
):
    """
    Monte Carlo simulation of Theorem 4 under dynamic entropy erosion.
    """
    rng = np.random.default_rng(seed)

    if Q_verifiers <= 0 or not (0 <= r_malicious < Q_verifiers):
        raise ValueError("Invalid verifier count or malicious fraction.")
    if not (0 < k_fragments <= Q_verifiers) or not (0 < m_critical <= k_fragments):
        raise ValueError("Invalid fragment distribution parameters.")

    q = r_malicious / Q_verifiers

    # Dynamic erosion of residual conditional min-entropy
    h_res_dynamic = dynamic_residual_entropy(h_max, q, erosion_profile)
    
    p_inf_bound = min_entropy_to_inference_bound(h_res_dynamic)
    p_comp_bound = q + (1.0 - q) * p_inf_bound
    theorem4_upper_bound = p_comp_bound ** m_critical

    successful_reconstructions = 0
    global_vetoes = 0
    malicious_verifiers = set(range(r_malicious))

    for _ in range(iterations):
        # 1. Randomized injective assignment
        assigned_verifiers = rng.choice(Q_verifiers, size=k_fragments, replace=False)

        # 2. Hidden critical binding
        critical_fragments = rng.choice(k_fragments, size=m_critical, replace=False)

        directly_compromised = np.array([
            assigned_verifiers[f] in malicious_verifiers
            for f in critical_fragments
        ])

        m_direct = int(np.sum(directly_compromised))
        m_missing = m_critical - m_direct

        # 3. Sequential residual inference under dynamic bounding
        all_missing_inferred = True
        for _ in range(m_missing):
            inferred = rng.random() < p_inf_bound
            if not inferred:
                all_missing_inferred = False
                break

        # 4. Global Veto Condition
        if m_missing == 0 or all_missing_inferred:
            successful_reconstructions += 1
        else:
            global_vetoes += 1

    # CORRETTO DA EMPIRICAL A SIMULATED
    simulated_rec = successful_reconstructions / iterations
    simulated_veto = global_vetoes / iterations

    return {
        "q": q,
        "h_res_dynamic": h_res_dynamic,
        "p_inf_bound": p_inf_bound,
        "p_comp_bound": p_comp_bound,
        "theorem4_upper_bound": theorem4_upper_bound,
        "simulated_rec": simulated_rec,
        "simulated_veto": simulated_veto
    }

# ==============================================================================
# SYSTEM PARAMETERS & EXECUTION
# ==============================================================================

Q_VERIFIERS = 1000
K_FRAGMENTS = 100
M_CRITICAL = 50
ITERATIONS = 100000
H_MAX_START = 10.0

scenarios = {
    "Linear erosion": {"profile": "linear", "color": "#2ca02c"},
    "Quadratic erosion": {"profile": "quadratic", "color": "#ff7f0e"},
    "Radical erosion": {"profile": "radical", "color": "#d62728"}
}

malicious_counts = np.unique(np.linspace(0, Q_VERIFIERS - 1, 40, dtype=int))

plt.figure(figsize=(12, 8))
plt.rcParams.update({"font.size": 11, "font.family": "serif"})

for label, params in scenarios.items():
    profile = params["profile"]
    color = params["color"]

    q_values, simulated_results, theorem_results = [], [], []

    for r_malicious in malicious_counts:
        result = simulate_cnvs_dynamic_erosion(
            Q_verifiers=Q_VERIFIERS,
            r_malicious=int(r_malicious),
            k_fragments=K_FRAGMENTS,
            m_critical=M_CRITICAL,
            h_max=H_MAX_START,
            erosion_profile=profile,
            iterations=ITERATIONS
        )

        q_values.append(result["q"])
        simulated_results.append(result["simulated_rec"])
        theorem_results.append(result["theorem4_upper_bound"])

    # Floor limit for logarithmic plotting visibility
    simulated_plot = np.maximum(simulated_results, 1.0 / ITERATIONS)

    # CORRETTO DA EMPIRICAL A SIMULATED PROJECTION
    plt.plot(
        q_values, simulated_plot,
        marker="o", linestyle="-", color=color, alpha=0.75,
        label=f"Simulated Projection: {label}"
    )

    plt.plot(
        q_values, theorem_results,
        linestyle="--", color=color, linewidth=2.5,
        label=f"Theorem 4 bound: {label}"
    )

plt.title(
    "CNVS Stress Test: Dynamic Erosion of Residual Min-Entropy\n"
    f"Initial Baseline $h_{{max}}={H_MAX_START}$ log2-units "
    f"($Q_v={Q_VERIFIERS}, k={K_FRAGMENTS}, m={M_CRITICAL}$)",
    pad=15
)

plt.xlabel(r"Fraction of Colluding Verifiers ($q = r/Q_v$)")
plt.ylabel(r"Systemic Reconstruction Probability $\mathbb{P}(Rec^*)$")
plt.yscale("log")
plt.ylim(1.0 / ITERATIONS, 1.5)
plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0.0)
plt.tight_layout()

# plt.savefig("cnvs_dynamic_residual_entropy_stress_test.pdf", format="pdf", dpi=300)
plt.show()
