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
# CRITICAL-SET COMPROMISE, GLOBAL-VETO PROXY, AND ECONOMIC DETERRENCE
#
# Test Name: Test 3 - Statistical Projection of Critical-Set Compromise Decay and Attack Payoff under High Collusion and Slashing.
# filename = "test_03_slashing_expected_value.py"
#
# PURPOSE:
# This script is a conditional Monte Carlo stress test built on the formal CNVS
# Theorem 4 reconstruction bound.
#
# It projects:
#   1. the probability that all m critical terminal fragments become compromised;
#   2. the corresponding worst-case proxy for unauthorized reconstruction;
#   3. the expected attacker payoff under two implementation-layer slashing levels.
#
# THEORETICAL SCOPE:
# The script ASSUMES the formal CNVS bounds and does not attempt to re-prove them.
# It does NOT instantiate the full typed universe 𝓢, execute V_L, or explicitly
# evaluate Cons_R, Inv_C, or the complete global verification function V_G.
#
# FORMAL ASSUMPTIONS:
#   1. Terminal fragments are assigned through randomized injective matching.
#   2. The m critical fragments are selected through hidden random binding.
#   3. Residual conditional min-entropy satisfies:
#
#          H∞(d_miss_i | View_adv^(i)) >= h_min_residual
#
#   4. The corresponding inference probability satisfies:
#
#          p_inf <= 2^(-h_min_residual)
#
#   5. WORST-CASE SATURATION:
#      The simulation deliberately sets:
#
#          p_inf = 2^(-h_min_residual)
#
#      granting the attacker the strongest inference capability admitted by the
#      assumed residual min-entropy margin.
#
#   6. Theorem 4 gives the upper bound:
#
#          P(Rec*) <= p_comp^m
#
#      with:
#
#          p_comp = q + (1 - q) p_inf
#
#   7. WORST-CASE SUFFICIENCY PROXY:
#      Theorem 4 makes compromise of all m critical fragments a necessary
#      condition for unauthorized reconstruction. This simulator pessimistically
#      treats complete critical-set compromise as sufficient for Rec*. Therefore,
#      "reconstruction" in this file is a worst-case reconstruction proxy.
#
# ECONOMIC IMPLEMENTATION ASSUMPTION:
# A directly compromised critical verifier is assumed to have actively submitted
# a fraudulent observation and to be identifiable by authenticated system evidence
# when the attempted malicious transition is rejected.
#
# Slashing is applied ONLY to directly compromised critical submitters.
# The code does not assume oracle-level knowledge of the entire coalition.
#
# ECONOMIC INTERPRETATION:
# The plotted quantity is "expected attack payoff per attempted cycle":
#
#      successful attack reward minus slashing applied after a rejected attack.
#
# It is NOT a complete net-profit model because it does not include bribery,
# coordination, capital, opportunity, or operational costs.
#
# DEPENDENCE SCOPE:
# Dependence is introduced by injective assignment without replacement.
# Residual inference trials use a fixed worst-case p_inf within each cycle and do
# not model adaptive within-cycle entropy erosion.
# ==============================================================================


def validate_non_negative_real(name, value):
    """Validate and return a finite non-negative real value."""
    value = float(value)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be a finite non-negative real number.")
    return value


def validate_probability(name, value):
    """Validate and return a probability in [0, 1]."""
    value = float(value)
    if not math.isfinite(value) or not (0.0 <= value <= 1.0):
        raise ValueError(f"{name} must satisfy 0 <= {name} <= 1.")
    return value


def min_entropy_to_inference_bound(h_min_residual):
    """
    Convert a residual conditional min-entropy margin into the corresponding
    adversarial inference upper bound.

    The Monte Carlo model deliberately saturates this upper bound.
    """
    h_min_residual = validate_non_negative_real(
        "h_min_residual",
        h_min_residual
    )
    return 2.0 ** (-h_min_residual)


def hypergeometric_probability_honest_hits(
    Q_verifiers,
    r_malicious,
    m_critical,
    honest_hits
):
    """
    Probability that exactly 'honest_hits' of the m critical fragments are
    assigned to honest verifiers under uniform injective assignment.
    """
    honest_verifiers = Q_verifiers - r_malicious

    if honest_hits < 0 or honest_hits > m_critical:
        return 0.0
    if honest_hits > honest_verifiers:
        return 0.0
    if (m_critical - honest_hits) > r_malicious:
        return 0.0

    numerator = (
        math.comb(honest_verifiers, honest_hits)
        * math.comb(r_malicious, m_critical - honest_hits)
    )
    denominator = math.comb(Q_verifiers, m_critical)

    return numerator / denominator


def exact_injective_reconstruction_probability(
    Q_verifiers,
    r_malicious,
    m_critical,
    p_inf_bound
):
    """
    Exact worst-case reconstruction-proxy probability under uniform injective
    assignment.

    If h critical fragments are assigned to honest verifiers, all h missing
    fragments must be inferred. Under the fixed within-cycle inference model,
    this occurs with probability p_inf_bound ** h.
    """
    p_inf_bound = validate_probability("p_inf_bound", p_inf_bound)

    honest_verifiers = Q_verifiers - r_malicious
    min_honest_hits = max(0, m_critical - r_malicious)
    max_honest_hits = min(m_critical, honest_verifiers)

    exact_probability = 0.0

    for h in range(min_honest_hits, max_honest_hits + 1):
        probability_h = hypergeometric_probability_honest_hits(
            Q_verifiers=Q_verifiers,
            r_malicious=r_malicious,
            m_critical=m_critical,
            honest_hits=h
        )
        exact_probability += probability_h * (p_inf_bound ** h)

    return exact_probability


def exact_expected_attack_payoff(
    Q_verifiers,
    r_malicious,
    m_critical,
    p_inf_bound,
    reward_success,
    penalty_per_caught_node
):
    """
    Exact expected attack payoff under the implemented slashing rule.

    Let h be the number of critical fragments assigned to honest verifiers.
    Then:
      - directly compromised critical submitters = m_critical - h;
      - attack success probability conditional on h = p_inf_bound ** h;
      - failed attack payoff = caught_nodes * penalty_per_caught_node.

    Therefore:
      E[payoff | h]
        = p_inf^h * reward_success
          + (1 - p_inf^h) * (m_critical - h) * penalty_per_caught_node.
    """
    p_inf_bound = validate_probability("p_inf_bound", p_inf_bound)
    reward_success = validate_non_negative_real("reward_success", reward_success)

    penalty_per_caught_node = float(penalty_per_caught_node)
    if not math.isfinite(penalty_per_caught_node) or penalty_per_caught_node > 0.0:
        raise ValueError(
            "penalty_per_caught_node must be finite and non-positive."
        )

    honest_verifiers = Q_verifiers - r_malicious
    min_honest_hits = max(0, m_critical - r_malicious)
    max_honest_hits = min(m_critical, honest_verifiers)

    expected_payoff = 0.0

    for h in range(min_honest_hits, max_honest_hits + 1):
        probability_h = hypergeometric_probability_honest_hits(
            Q_verifiers=Q_verifiers,
            r_malicious=r_malicious,
            m_critical=m_critical,
            honest_hits=h
        )

        success_probability_given_h = p_inf_bound ** h
        caught_nodes_if_veto = m_critical - h

        conditional_payoff = (
            success_probability_given_h * reward_success
            + (1.0 - success_probability_given_h)
            * caught_nodes_if_veto
            * penalty_per_caught_node
        )

        expected_payoff += probability_h * conditional_payoff

    return expected_payoff


def simulate_single_m(
    rng,
    Q_verifiers,
    r_malicious,
    k_fragments,
    m_critical,
    p_inf_bound,
    reward_success,
    penalty_mild,
    penalty_strict,
    num_runs
):
    """
    Monte Carlo simulation for a fixed critical-fragment count m.

    Slashing scope:
      Only directly compromised CRITICAL submitters are penalized when the
      worst-case reconstruction proxy fails and the Global-Veto proxy rejects
      the malicious transition.

    The simulator does not slash honest verifiers, inferred fragments, unrelated
    terminal assignments, or coalition members that produced no identifiable
    fraudulent critical submission.
    """
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng must be an instance of numpy.random.Generator.")

    malicious_verifiers = set(range(r_malicious))

    successful_reconstructions = 0
    total_payoff_mild = 0.0
    total_payoff_strict = 0.0

    for _ in range(num_runs):

        # 1. RANDOMIZED INJECTIVE ASSIGNMENT
        # Each terminal fragment is assigned to a distinct verifier.
        assigned_verifiers = rng.choice(
            Q_verifiers,
            size=k_fragments,
            replace=False
        )

        # 2. HIDDEN CRITICAL BINDING
        # The critical subset is selected randomly and is not pre-disclosed to
        # the adversarial coalition.
        critical_fragments = rng.choice(
            k_fragments,
            size=m_critical,
            replace=False
        )

        directly_compromised = np.fromiter(
            (
                assigned_verifiers[f] in malicious_verifiers
                for f in critical_fragments
            ),
            dtype=bool,
            count=m_critical
        )

        m_direct = int(np.sum(directly_compromised))
        m_missing = m_critical - m_direct

        # 3. RESIDUAL INFERENCE TRIALS AT THE FIXED WORST-CASE BOUND
        # p_inf is held constant within a cycle. The loop does not model
        # adaptive within-cycle entropy erosion.
        if m_missing == 0:
            all_missing_inferred = True
        else:
            inference_draws = rng.random(m_missing)
            all_missing_inferred = bool(
                np.all(inference_draws < p_inf_bound)
            )

        # 4. WORST-CASE RECONSTRUCTION PROXY + GLOBAL-VETO PROXY
        # Complete compromise of all m critical fragments is pessimistically
        # treated as sufficient for unauthorized reconstruction.
        reconstruction_proxy_success = all_missing_inferred

        if reconstruction_proxy_success:
            successful_reconstructions += 1
            total_payoff_mild += reward_success
            total_payoff_strict += reward_success
        else:
            # Only directly compromised critical submitters are assumed to be
            # identifiable and slashable after rejection.
            caught_nodes = m_direct

            total_payoff_mild += caught_nodes * penalty_mild
            total_payoff_strict += caught_nodes * penalty_strict

    simulated_probability = successful_reconstructions / num_runs
    average_payoff_mild = total_payoff_mild / num_runs
    average_payoff_strict = total_payoff_strict / num_runs

    return (
        simulated_probability,
        average_payoff_mild,
        average_payoff_strict
    )


def validate_model_parameters(
    num_runs,
    Q_verifiers,
    r_malicious,
    k_fragments,
    m_values,
    h_min_residual,
    reward_success,
    penalty_mild,
    penalty_strict
):
    """Validate all simulation parameters."""
    if not isinstance(num_runs, (int, np.integer)) or num_runs <= 0:
        raise ValueError("NUM_RUNS must be a positive integer.")

    if not isinstance(Q_verifiers, (int, np.integer)) or Q_verifiers <= 0:
        raise ValueError("Q_VERIFIERS must be a positive integer.")

    if (
        not isinstance(r_malicious, (int, np.integer))
        or not (0 <= r_malicious <= Q_verifiers)
    ):
        raise ValueError(
            "R_MALICIOUS must satisfy 0 <= R_MALICIOUS <= Q_VERIFIERS."
        )

    if (
        not isinstance(k_fragments, (int, np.integer))
        or not (0 < k_fragments <= Q_verifiers)
    ):
        raise ValueError(
            "K_FRAGMENTS must satisfy 0 < K_FRAGMENTS <= Q_VERIFIERS."
        )

    m_values = np.asarray(m_values)

    if m_values.size == 0:
        raise ValueError("M_VALUES must contain at least one value.")

    if not np.issubdtype(m_values.dtype, np.integer):
        raise ValueError("All M_VALUES must be integers.")

    if np.any(m_values <= 0):
        raise ValueError("All M_VALUES must be strictly positive.")

    if np.any(m_values > k_fragments):
        raise ValueError("All M_VALUES must satisfy m <= K_FRAGMENTS.")

    if np.any(m_values > Q_verifiers):
        raise ValueError("All M_VALUES must satisfy m <= Q_VERIFIERS.")

    validate_non_negative_real("H_MIN_RESIDUAL", h_min_residual)
    validate_non_negative_real("REWARD_SUCCESS", reward_success)

    penalty_mild = float(penalty_mild)
    penalty_strict = float(penalty_strict)

    if not math.isfinite(penalty_mild) or penalty_mild > 0.0:
        raise ValueError("PENALTY_MILD must be finite and non-positive.")

    if not math.isfinite(penalty_strict) or penalty_strict > 0.0:
        raise ValueError("PENALTY_STRICT must be finite and non-positive.")

    if penalty_strict > penalty_mild:
        raise ValueError(
            "PENALTY_STRICT must be at least as severe as PENALTY_MILD."
        )


def simulate_economic_model():
    # ==========================================================================
    # SYSTEM PARAMETERS
    # ==========================================================================

    NUM_RUNS = 100_000

    Q_VERIFIERS = 100
    R_MALICIOUS = 80

    K_FRAGMENTS = 50
    M_VALUES = np.arange(1, 16, dtype=int)

    # Residual min-entropy:
    # h_min = 1.0 implies the worst-case saturated inference probability p_inf=0.5.
    H_MIN_RESIDUAL = 1.0

    # Implementation-layer economic parameters.
    REWARD_SUCCESS = 10_000.0
    PENALTY_MILD = -500.0
    PENALTY_STRICT = -1_500.0

    # Reproducible master seed.
    # Independent child streams are generated for each m so that changing the
    # order or number of M_VALUES does not reuse one continuous RNG trajectory.
    SEED = 42

    # ==========================================================================
    # VALIDATION
    # ==========================================================================

    validate_model_parameters(
        num_runs=NUM_RUNS,
        Q_verifiers=Q_VERIFIERS,
        r_malicious=R_MALICIOUS,
        k_fragments=K_FRAGMENTS,
        m_values=M_VALUES,
        h_min_residual=H_MIN_RESIDUAL,
        reward_success=REWARD_SUCCESS,
        penalty_mild=PENALTY_MILD,
        penalty_strict=PENALTY_STRICT
    )

    q = R_MALICIOUS / Q_VERIFIERS
    p_inf_bound = min_entropy_to_inference_bound(H_MIN_RESIDUAL)
    p_comp_bound = q + (1.0 - q) * p_inf_bound

    master_seed_sequence = np.random.SeedSequence(SEED)
    child_seed_sequences = master_seed_sequence.spawn(len(M_VALUES))

    simulated_probs = []
    exact_probs = []
    theorem_bounds = []

    simulated_payoffs_mild = []
    simulated_payoffs_strict = []

    exact_payoffs_mild = []
    exact_payoffs_strict = []

    print(
        "Executing CNVS Statistical Projection: "
        "Critical-Set Compromise and Economic Deterrence"
    )
    print(f"Verifier pool size Q_v: {Q_VERIFIERS}")
    print(f"Colluding verifiers r: {R_MALICIOUS}")
    print(f"Adversarial fraction q = r/Q_v: {q:.2%}")
    print(f"Terminal fragments k: {K_FRAGMENTS}")
    print(f"Residual min-entropy margin h_min: {H_MIN_RESIDUAL:.3f}")
    print(
        "Worst-case saturated inference probability "
        f"p_inf = 2^(-h_min): {p_inf_bound:.3f}"
    )
    print(f"Composite compromise bound p_comp: {p_comp_bound:.3f}")
    print("Slashing scope: directly compromised critical submitters only")
    print(f"Master random seed: {SEED}\n")

    for m, child_seed_sequence in zip(M_VALUES, child_seed_sequences):
        rng = np.random.default_rng(child_seed_sequence)

        (
            simulated_rec,
            simulated_payoff_mild,
            simulated_payoff_strict
        ) = simulate_single_m(
            rng=rng,
            Q_verifiers=Q_VERIFIERS,
            r_malicious=R_MALICIOUS,
            k_fragments=K_FRAGMENTS,
            m_critical=int(m),
            p_inf_bound=p_inf_bound,
            reward_success=REWARD_SUCCESS,
            penalty_mild=PENALTY_MILD,
            penalty_strict=PENALTY_STRICT,
            num_runs=NUM_RUNS
        )

        exact_rec = exact_injective_reconstruction_probability(
            Q_verifiers=Q_VERIFIERS,
            r_malicious=R_MALICIOUS,
            m_critical=int(m),
            p_inf_bound=p_inf_bound
        )

        theorem_bound = p_comp_bound ** int(m)

        exact_payoff_mild = exact_expected_attack_payoff(
            Q_verifiers=Q_VERIFIERS,
            r_malicious=R_MALICIOUS,
            m_critical=int(m),
            p_inf_bound=p_inf_bound,
            reward_success=REWARD_SUCCESS,
            penalty_per_caught_node=PENALTY_MILD
        )

        exact_payoff_strict = exact_expected_attack_payoff(
            Q_verifiers=Q_VERIFIERS,
            r_malicious=R_MALICIOUS,
            m_critical=int(m),
            p_inf_bound=p_inf_bound,
            reward_success=REWARD_SUCCESS,
            penalty_per_caught_node=PENALTY_STRICT
        )

        simulated_probs.append(simulated_rec * 100.0)
        exact_probs.append(exact_rec * 100.0)
        theorem_bounds.append(theorem_bound * 100.0)

        simulated_payoffs_mild.append(simulated_payoff_mild)
        simulated_payoffs_strict.append(simulated_payoff_strict)

        exact_payoffs_mild.append(exact_payoff_mild)
        exact_payoffs_strict.append(exact_payoff_strict)

        print(
            f"m={m:2d} | "
            f"Sim. proxy = {simulated_rec * 100:7.3f}% | "
            f"Exact inj. = {exact_rec * 100:7.3f}% | "
            f"T4 bound = {theorem_bound * 100:7.3f}% | "
            f"Sim mild = {simulated_payoff_mild:10,.1f} | "
            f"Exact mild = {exact_payoff_mild:10,.1f} | "
            f"Sim strict = {simulated_payoff_strict:10,.1f} | "
            f"Exact strict = {exact_payoff_strict:10,.1f}"
        )

    simulated_probs = np.asarray(simulated_probs)
    exact_probs = np.asarray(exact_probs)
    theorem_bounds = np.asarray(theorem_bounds)

    simulated_payoffs_mild = np.asarray(simulated_payoffs_mild)
    simulated_payoffs_strict = np.asarray(simulated_payoffs_strict)
    exact_payoffs_mild = np.asarray(exact_payoffs_mild)
    exact_payoffs_strict = np.asarray(exact_payoffs_strict)

    # ==========================================================================
    # FULL-COLLUSION CONTROL SCENARIO: q = 1
    # ==========================================================================

    full_collusion_probability = 1.0
    full_collusion_payoff = REWARD_SUCCESS

    print("\nFull-collusion control scenario:")
    print("q = 1.000")
    print(
        "All critical fragments are directly assigned to colluding verifiers; "
        "the worst-case reconstruction proxy succeeds with probability 1."
    )
    print(
        "No veto-triggered slashing occurs in this control scenario, so expected "
        f"attack payoff remains {full_collusion_payoff:,.1f} credits for every m."
    )

    # ==========================================================================
    # NUMERICAL CONSISTENCY CHECKS
    # ==========================================================================

    tolerance = 1e-12

    if np.any(exact_probs - theorem_bounds > tolerance):
        raise RuntimeError(
            "Exact injective probability exceeded the Theorem 4 bound."
        )

    max_probability_error = np.max(
        np.abs(simulated_probs - exact_probs)
    )

    max_payoff_error_mild = np.max(
        np.abs(simulated_payoffs_mild - exact_payoffs_mild)
    )

    max_payoff_error_strict = np.max(
        np.abs(simulated_payoffs_strict - exact_payoffs_strict)
    )

    print("\nMonte Carlo consistency summary:")
    print(
        "Maximum absolute probability deviation "
        f"(simulation vs exact): {max_probability_error:.4f} percentage points"
    )
    print(
        "Maximum absolute mild-payoff deviation "
        f"(simulation vs exact): {max_payoff_error_mild:,.2f} credits"
    )
    print(
        "Maximum absolute strict-payoff deviation "
        f"(simulation vs exact): {max_payoff_error_strict:,.2f} credits"
    )

    # ==========================================================================
    # PLOTTING
    # ==========================================================================

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(19, 7))

    # Plot 1: Worst-case reconstruction-proxy decay.
    ax1.plot(
        M_VALUES,
        simulated_probs,
        marker="o",
        linewidth=2.3,
        label=r"Monte Carlo worst-case reconstruction proxy"
    )

    ax1.plot(
        M_VALUES,
        exact_probs,
        marker="s",
        linestyle=":",
        linewidth=2.3,
        label="Exact injective-assignment probability"
    )

    ax1.plot(
        M_VALUES,
        theorem_bounds,
        linestyle="--",
        linewidth=2.3,
        label=r"Theorem 4 upper bound $(p_{\mathrm{comp}})^m$"
    )

    ax1.set_title(
        rf"Critical-Set Compromise Decay "
        rf"($q={q:.2f}$, $h_{{min}}={H_MIN_RESIDUAL}$)"
    )

    ax1.set_xlabel(r"Number of Critical Terminal Fragments ($m$)")
    ax1.set_ylabel("Worst-Case Reconstruction-Proxy Probability [%]")
    ax1.set_xticks(M_VALUES)
    ax1.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
    ax1.legend()

    # Plot 2: Expected attack payoff.
    bar_width = 0.34
    x = np.arange(len(M_VALUES))

    ax2.bar(
        x - bar_width / 2,
        simulated_payoffs_mild,
        width=bar_width,
        alpha=0.55,
        label=f"Monte Carlo mild slashing ({PENALTY_MILD:,.0f})"
    )

    ax2.bar(
        x + bar_width / 2,
        simulated_payoffs_strict,
        width=bar_width,
        alpha=0.55,
        label=f"Monte Carlo strict slashing ({PENALTY_STRICT:,.0f})"
    )

    ax2.plot(
        x,
        exact_payoffs_mild,
        marker="o",
        linestyle="-",
        linewidth=2.0,
        label="Exact expected payoff: mild"
    )

    ax2.plot(
        x,
        exact_payoffs_strict,
        marker="s",
        linestyle="-",
        linewidth=2.0,
        label="Exact expected payoff: strict"
    )

    ax2.axhline(
        0.0,
        linewidth=1.5,
        linestyle="--",
        label="Break-even"
    )

    ax2.axhline(
        full_collusion_payoff,
        linewidth=1.2,
        linestyle=":",
        label=r"Full-collusion control payoff ($q=1$)"
    )

    ax2.set_title(
        r"Expected Attack Payoff per Attempted Cycle"
        "\n"
        r"(successful-attack reward minus veto-triggered slashing)"
    )

    ax2.set_xlabel(r"Number of Critical Terminal Fragments ($m$)")
    ax2.set_ylabel("Expected Attack Payoff [credits]")
    ax2.set_xticks(x)
    ax2.set_xticklabels(M_VALUES)
    ax2.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
    ax2.legend()
    ax2.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda value, _: f"{int(value):,}")
    )

    fig.suptitle(
        "CNVS Statistical Projection: "
        "High-Collusion Critical-Set Compromise and Economic Deterrence",
        fontsize=14
    )

    fig.text(
        0.5,
        0.01,
        "Economic values exclude bribery, coordination, capital, opportunity, "
        "and operating costs; they are attack payoffs, not complete net profits.",
        ha="center",
        fontsize=9
    )

    plt.tight_layout(rect=(0.0, 0.04, 1.0, 0.96))
    plt.show()


if __name__ == "__main__":
    simulate_economic_model()
