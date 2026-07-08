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
# DEPENDENT COLLUSION AND RESIDUAL MIN-ENTROPY
#
#  Test Name: Test 1: Statistical Projection of Systemic Reconstruction under Dependent Collusion (Min-Entropy Variation).
#
#
#
# PURPOSE:
# This script is a statistical demonstrator. It projects the probabilistic 
# behavior of the CNVS adversarial reconstruction layer, ASSUMING the formal 
# validity of Theorem 4 and its underlying equations.
#
# It does NOT instantiate the physical typed universe 𝓢, the decomposition 
# operator 𝔇, or the geometric validation logic of V_L and V_G.
#
# It strictly models the mathematical implications of:
#   1. Randomized injective assignment of terminal fragments.
#   2. Hidden selection of m critical fragments.
#   3. Direct semantic exposure based on the malicious fraction (q).
#   4. Residual inference attempts bounded by min-entropy (h_min).
#   5. The systemic requirement that all m critical fragments must be controlled 
#      to bypass the Global Veto.
#
# FORMAL ASSUMPTION:
#   H∞(d_miss_i | View_adv^(i)) ≥ h_min
#   p_inf_i ≤ 2^(-h_min)
#   p_comp = q + (1 - q) p_inf
#   P(Rec*) ≤ p_comp^m
# ==============================================================================


def min_entropy_to_inference_bound(h_min_residual):
    """
    Converts a residual conditional min-entropy margin into an adversarial
    guessing/inference probability upper bound.

    CONTEXT:
    h_min_residual represents the uniform lower bound on the adversary's 
    remaining uncertainty for each missing critical fragment, after conditioning 
    on the full adversarial view (View_adv).
    """
    if h_min_residual < 0:
        raise ValueError("h_min_residual must be non-negative.")

    return 2.0 ** (-h_min_residual)


def simulate_cnvs_dependent_collusion(
    Q_verifiers,
    r_malicious,
    k_fragments,
    m_critical,
    h_min_residual,
    iterations=100000,
    seed=None
):
    """
    Monte Carlo simulation mapping the theoretical bounds of Theorem 4.

    Parameters
    ----------
    Q_verifiers : int
        Total verifier pool size Q_v = |𝒱|.
    r_malicious : int
        Number of colluding verifiers r = |𝒱_adv|.
    k_fragments : int
        Number of active terminal fragments k = |Ter(t)|.
    m_critical : int
        Number of critical fragments bound to the hidden invariant family.
    h_min_residual : float
        Uniform residual conditional min-entropy margin.
    iterations : int
        Number of stochastic trials.
    seed : int or None
        Optional random seed for reproducibility.

    Returns
    -------
    dict
        Simulated reconstruction probability, simulated Global Veto probability,
        and Theorem 4 theoretical upper bound.
    """

    if Q_verifiers <= 0:
        raise ValueError("Q_verifiers must be positive.")

    if not (0 <= r_malicious <= Q_verifiers):
        raise ValueError("r_malicious must satisfy 0 ≤ r_malicious ≤ Q_verifiers.")

    if not (0 < k_fragments <= Q_verifiers):
        raise ValueError("k_fragments must satisfy 0 < k_fragments ≤ Q_verifiers.")

    if not (0 < m_critical <= k_fragments):
        raise ValueError("m_critical must satisfy 0 < m_critical ≤ k_fragments.")

    rng = np.random.default_rng(seed)

    # Theoretical parameters based on CNVS Axioms
    q = r_malicious / Q_verifiers
    p_inf_bound = min_entropy_to_inference_bound(h_min_residual)
    p_comp_bound = q + (1.0 - q) * p_inf_bound
    theorem4_upper_bound = p_comp_bound ** m_critical

    successful_reconstructions = 0
    global_vetoes = 0

    # Fixed malicious verifier set representing the adversarial coalition.
    malicious_verifiers = set(range(r_malicious))

    for _ in range(iterations):

        # 1. RANDOMIZED INJECTIVE ASSIGNMENT
        assigned_verifiers = rng.choice(
            Q_verifiers,
            size=k_fragments,
            replace=False
        )

        # 2. HIDDEN CRITICAL BINDING
        critical_fragments = rng.choice(
            k_fragments,
            size=m_critical,
            replace=False
        )

        # Boolean array: True if the critical fragment is assigned to a malicious node
        directly_compromised = np.array([
            assigned_verifiers[f] in malicious_verifiers
            for f in critical_fragments
        ])

        m_direct = int(np.sum(directly_compromised))
        m_missing = m_critical - m_direct

        # 3. RESIDUAL STRUCTURAL INFERENCE
        # Simulating sequential inference attempts bounded by p_inf_bound
        all_missing_inferred = True

        for _ in range(m_missing):
            inferred = rng.random() < p_inf_bound
            if not inferred:
                all_missing_inferred = False
                break

        # 4. GLOBAL VETO CONDITION
        # Systemic failure occurs only if ALL critical fragments are controlled.
        if m_missing == 0 or all_missing_inferred:
            successful_reconstructions += 1
        else:
            global_vetoes += 1

    # Statistical outcomes over n iterations (CORRETTO DA EMPIRICAL A SIMULATED)
    simulated_rec = successful_reconstructions / iterations
    simulated_veto = global_vetoes / iterations

    return {
        "q": q,
        "p_inf_bound": p_inf_bound,
        "p_comp_bound": p_comp_bound,
        "theorem4_upper_bound": theorem4_upper_bound,
        "simulated_rec": simulated_rec,
        "simulated_veto": simulated_veto,
        "iterations": iterations
    }


# ==============================================================================
# SYSTEM PARAMETERS & EXECUTION
# ==============================================================================

Q_VERIFIERS = 1000
K_FRAGMENTS = 100
M_CRITICAL = 50
ITERATIONS = 100000
SEED = 42

# Objective parameterization of Min-Entropy scenarios
scenarios = {
    "Near-Deterministic Residual Inference ($h_{min}=0.5$)": {
        "h_min": 0.5,
        "color": "#d62728"
    },
    "Moderate Residual Non-Inferability ($h_{min}=2.0$)": {
        "h_min": 2.0,
        "color": "#ff7f0e"
    },
    "Strong Residual Non-Inferability ($h_{min}=10.0$)": {
        "h_min": 10.0,
        "color": "#2ca02c"
    }
}

malicious_counts = np.unique(
    np.linspace(0, Q_VERIFIERS - 1, 40, dtype=int)
)

plt.figure(figsize=(12, 8))
plt.rcParams.update({"font.size": 11, "font.family": "serif"})

for label, params in scenarios.items():
    h_val = params["h_min"]
    c_val = params["color"]

    q_values = []
    simulated_results = []
    theorem_results = []

    for r_malicious in malicious_counts:
        result = simulate_cnvs_dependent_collusion(
            Q_verifiers=Q_VERIFIERS,
            r_malicious=int(r_malicious),
            k_fragments=K_FRAGMENTS,
            m_critical=M_CRITICAL,
            h_min_residual=h_val,
            iterations=ITERATIONS,
            seed=None
        )

        q_values.append(result["q"])
        simulated_results.append(result["simulated_rec"])
        theorem_results.append(result["theorem4_upper_bound"])

    # Floor limit for logarithmic plotting visibility
    simulated_plot = np.maximum(simulated_results, 1.0 / ITERATIONS)

    # CORRETTO DA "Empirical CNVS reconstruction" a "Simulated Projection"
    plt.plot(
        q_values,
        simulated_plot,
        marker="o",
        linestyle="-",
        color=c_val,
        alpha=0.75,
        label=f"Simulated Projection: {label}"
    )

    plt.plot(
        q_values,
        theorem_results,
        linestyle="--",
        color=c_val,
        linewidth=2.5,
        label=f"Theorem 4 upper bound ($h_{{min}}={h_val}$)"
    )

# Illustrative reference line for classical BFT tolerance limits
plt.axvline(
    x=0.33,
    color="black",
    linestyle=":",
    linewidth=2,
    label="Classical BFT 33% limit (Reference)"
)

plt.title(
    "CNVS Dependent-Collusion Reconstruction Bound\n"
    f"Statistical Projection over 100k Iterations "
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

# plt.savefig("cnvs_theorem4_statistical_projection.pdf", format="pdf", dpi=300)
plt.show()