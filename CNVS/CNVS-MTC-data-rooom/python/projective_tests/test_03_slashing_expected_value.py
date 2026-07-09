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
# DEPENDENT COLLUSION, GLOBAL VETO, AND ECONOMIC PENALTY MODEL
#
#  Test Name: Test 3: Statistical Projection of Reconstruction Decay and Economic Penalty (Slashing) Model under Extreme Dependent Collusion.
#  filename = "test_03_slashing_expected_value.py"
#
# PURPOSE:
# This script simulates an implementation-layer economic model built upon the 
# CNVS Theorem 4 reconstruction bound. It projects the statistical behavior of 
# the system under dependent collusion and economic truth-forcing, ASSUMING the 
# formal validity of the theoretical bounds.
#
# It does NOT construct the full typed universe 𝓢, execute the local verification 
# function V_L, or explicitly evaluate the topological constraints Cons_R or Inv_C.
#
# FORMAL ASSUMPTIONS:
#   1. Randomized injective assignment of terminal fragments to verifiers.
#   2. Hidden binding of m critical fragments to the invariant family.
#   3. Residual conditional min-entropy bound: H∞(d_miss_i | View_adv^(i)) ≥ h_min_residual.
#   4. Sequential inference probability bounded by: p_inf <= 2^(-h_min_residual).
#   5. Global Veto Condition: Unauthorized reconstruction succeeds ONLY if all m 
#      critical fragments are either directly compromised or successfully inferred.
#   6. Economic Penalty (Slashing): A financial penalty is applied to compromised 
#      nodes when the Global Veto rejects a malicious state transition.
# ==============================================================================

def min_entropy_to_inference_bound(h_min_residual):
    """
    Converts a residual conditional min-entropy margin into an adversarial
    inference probability upper bound.
    """
    h_min_residual = max(float(h_min_residual), 0.0)
    return 2.0 ** (-h_min_residual)

def exact_injective_reconstruction_probability(
    Q_verifiers,
    r_malicious,
    m_critical,
    p_inf_bound
):
    """
    Exact analytical reconstruction probability under uniform injective assignment.
    Computes the expected probability using a hypergeometric distribution for the 
    number of critical fragments assigned to honest verifiers.
    """
    honest_verifiers = Q_verifiers - r_malicious
    denominator = math.comb(Q_verifiers, m_critical)

    exact_probability = 0.0

    min_honest_hits = max(0, m_critical - r_malicious)
    max_honest_hits = min(m_critical, honest_verifiers)

    for h in range(min_honest_hits, max_honest_hits + 1):
        probability_h = (
            math.comb(honest_verifiers, h)
            * math.comb(r_malicious, m_critical - h)
            / denominator
        )

        exact_probability += probability_h * (p_inf_bound ** h)

    return exact_probability

def simulate_single_m(
    rng,
    Q_verifiers,
    r_malicious,
    k_fragments,
    m_critical,
    p_inf_bound,
    reward_win,
    penalty_mild,
    penalty_strict,
    num_runs,
    slashing_mode="critical_only"
):
    """
    Monte Carlo simulation for a fixed number of critical fragments (m).
    
    slashing_mode assumptions:
      - "critical_only": Penalty applied only to directly compromised critical fragments.
      - "all_assigned_malicious": Penalty applied to all malicious verifiers assigned 
        to any terminal fragment in the failed cycle.
    """
    malicious_verifiers = set(range(r_malicious))

    successful_reconstructions = 0
    total_profit_mild = 0.0
    total_profit_strict = 0.0

    for _ in range(num_runs):

        # 1. Randomized injective assignment
        assigned_verifiers = rng.choice(
            Q_verifiers,
            size=k_fragments,
            replace=False
        )

        # 2. Hidden critical binding
        critical_fragments = rng.choice(
            k_fragments,
            size=m_critical,
            replace=False
        )

        directly_compromised = np.array([
            assigned_verifiers[f] in malicious_verifiers
            for f in critical_fragments
        ])

        m_direct = int(np.sum(directly_compromised))
        m_missing = m_critical - m_direct

        # 3. Sequential residual inference
        all_missing_inferred = True
        for _ in range(m_missing):
            inferred = rng.random() < p_inf_bound
            if not inferred:
                all_missing_inferred = False
                break

        # 4. Global Veto Condition + Economic Truth-Forcing
        reconstruction_success = (m_missing == 0) or all_missing_inferred

        if reconstruction_success:
            successful_reconstructions += 1
            total_profit_mild += reward_win
            total_profit_strict += reward_win
        else:
            if slashing_mode == "critical_only":
                caught_nodes = m_direct
            elif slashing_mode == "all_assigned_malicious":
                caught_nodes = int(np.sum([
                    v in malicious_verifiers for v in assigned_verifiers
                ]))
            else:
                raise ValueError("Unknown slashing_mode.")

            total_profit_mild += caught_nodes * penalty_mild
            total_profit_strict += caught_nodes * penalty_strict

    simulated_probability = successful_reconstructions / num_runs
    average_profit_mild = total_profit_mild / num_runs
    average_profit_strict = total_profit_strict / num_runs

    return simulated_probability, average_profit_mild, average_profit_strict

def simulate_economic_model():
    # ==========================================================================
    # SYSTEM PARAMETERS
    # ==========================================================================

    NUM_RUNS = 100000

    Q_VERIFIERS = 100
    R_MALICIOUS = 80

    K_FRAGMENTS = 50
    M_VALUES = np.arange(1, 16)

    # Residual min-entropy (h_min = 1.0 implies p_inf <= 0.5)
    H_MIN_RESIDUAL = 1.0

    # Economic implementation parameters
    REWARD_WIN = 10000
    PENALTY_MILD = -500
    PENALTY_STRICT = -1500

    SLASHING_MODE = "critical_only"

    SEED = 42
    rng = np.random.default_rng(SEED)

    # ==========================================================================
    # VALIDATION & EXECUTION
    # ==========================================================================

    if not (0 <= R_MALICIOUS < Q_VERIFIERS):
        raise ValueError("R_MALICIOUS must satisfy 0 <= R_MALICIOUS < Q_VERIFIERS.")
    if not (0 < K_FRAGMENTS <= Q_VERIFIERS):
        raise ValueError("K_FRAGMENTS must satisfy 0 < K_FRAGMENTS <= Q_VERIFIERS.")
    if np.max(M_VALUES) > K_FRAGMENTS:
        raise ValueError("All M_VALUES must satisfy m <= K_FRAGMENTS.")

    q = R_MALICIOUS / Q_VERIFIERS
    p_inf_bound = min_entropy_to_inference_bound(H_MIN_RESIDUAL)
    p_comp_bound = q + (1.0 - q) * p_inf_bound

    simulated_probs = []
    exact_probs = []
    theorem_bounds = []
    attacker_profits_mild = []
    attacker_profits_strict = []

    print("Executing CNVS Statistical Projection: Economic Penalty Model...")
    print(f"Verifier pool size Q_v: {Q_VERIFIERS}")
    print(f"Colluding verifiers r: {R_MALICIOUS}")
    print(f"Adversarial fraction q = r/Q_v: {q:.2%}")
    print(f"Terminal fragments k: {K_FRAGMENTS}")
    print(f"Residual min-entropy margin h_min: {H_MIN_RESIDUAL:.3f}")
    print(f"Inference bound p_inf <= 2^(-h_min): {p_inf_bound:.3f}")
    print(f"Composite compromise bound p_comp: {p_comp_bound:.3f}")
    print(f"Slashing mode: {SLASHING_MODE}\n")

    for m in M_VALUES:
        simulated_rec, avg_profit_mild, avg_profit_strict = simulate_single_m(
            rng=rng,
            Q_verifiers=Q_VERIFIERS,
            r_malicious=R_MALICIOUS,
            k_fragments=K_FRAGMENTS,
            m_critical=int(m),
            p_inf_bound=p_inf_bound,
            reward_win=REWARD_WIN,
            penalty_mild=PENALTY_MILD,
            penalty_strict=PENALTY_STRICT,
            num_runs=NUM_RUNS,
            slashing_mode=SLASHING_MODE
        )

        exact_rec = exact_injective_reconstruction_probability(
            Q_verifiers=Q_VERIFIERS,
            r_malicious=R_MALICIOUS,
            m_critical=int(m),
            p_inf_bound=p_inf_bound
        )

        theorem_bound = p_comp_bound ** int(m)

        simulated_probs.append(simulated_rec * 100.0)
        exact_probs.append(exact_rec * 100.0)
        theorem_bounds.append(theorem_bound * 100.0)
        attacker_profits_mild.append(avg_profit_mild)
        attacker_profits_strict.append(avg_profit_strict)

        print(
            f"m={m:2d} | "
            f"Sim. Rec = {simulated_rec * 100:7.3f}% | "
            f"Exact Inj. = {exact_rec * 100:7.3f}% | "
            f"Theorem 4 Bound = {theorem_bound * 100:7.3f}% | "
            f"Mild Profit = {avg_profit_mild:10,.0f} | "
            f"Strict Profit = {avg_profit_strict:10,.0f}"
        )

    # ==========================================================================
    # PLOTTING
    # ==========================================================================

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))

    # Plot 1: Reconstruction probability decay
    ax1.plot(
        M_VALUES,
        simulated_probs,
        marker="o",
        linewidth=2.5,
        label=r"Simulated $\mathbb{P}(Rec^*)$"
    )

    ax1.plot(
        M_VALUES,
        exact_probs,
        marker="s",
        linestyle=":",
        linewidth=2.5,
        label="Exact injective-assignment probability"
    )

    ax1.plot(
        M_VALUES,
        theorem_bounds,
        linestyle="--",
        linewidth=2.5,
        label=r"Theorem 4 upper bound $(p_{comp})^m$"
    )

    ax1.set_title(
        rf"Dependent-Collusion Reconstruction Decay "
        rf"($q={q:.2f}$, $h_{{min}}={H_MIN_RESIDUAL}$)"
    )

    ax1.set_xlabel(r"Number of Critical Terminal Fragments ($m$)")
    ax1.set_ylabel("Reconstruction Probability [%]")
    ax1.set_xticks(M_VALUES)
    ax1.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
    ax1.legend()

    # Plot 2: Expected attacker profit
    bar_width = 0.4
    x1 = np.arange(len(M_VALUES))
    x2 = x1 + bar_width

    ax2.bar(
        x1,
        attacker_profits_mild,
        width=bar_width,
        edgecolor="grey",
        label=f"Mild penalty ({PENALTY_MILD})"
    )

    ax2.bar(
        x2,
        attacker_profits_strict,
        width=bar_width,
        edgecolor="grey",
        label=f"Strict penalty ({PENALTY_STRICT})"
    )

    ax2.axhline(0, linewidth=1.5, linestyle="-", label="Break-even")

    ax2.set_title(
        rf"Expected Attacker Net Profit per Cycle "
        rf"($V_G$ Veto + Economic Penalty)"
    )

    ax2.set_xlabel(r"Number of Critical Terminal Fragments ($m$)")
    ax2.set_ylabel("Expected Profit [credits]")
    ax2.set_xticks(x1 + bar_width / 2)
    ax2.set_xticklabels(M_VALUES)
    ax2.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
    ax2.legend()
    ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))

    fig.suptitle(
        "CNVS Statistical Projection: Dependent Collusion & Economic Penalty Model",
        fontsize=14
    )

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    simulate_economic_model()
