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
# q-DEPENDENT RESIDUAL MIN-ENTROPY EROSION STRESS TEST
#
# Test Name: Test 2 - Statistical Projection under q-Dependent Erosion of Residual Conditional Min-Entropy.
# filename = "test_02_dynamic_entropy_erosion.py"
#
# PURPOSE:
# This simulator is a conditional Monte Carlo stress test for the CNVS
# reconstruction layer. It assumes the formal validity of Theorem 4 and explores
# how systemic reconstruction risk changes when the residual conditional
# min-entropy is deliberately eroded as a function of the colluding fraction q.
#
# IMPORTANT SCOPE CLARIFICATION:
# The word "erosion" here is parametric, not temporal within a single Monte Carlo
# run. For each externally selected value of q, the script computes one fixed
# residual entropy level h_res(q), and that value remains constant throughout
# all inference attempts in that run.
#
# Therefore, this test does NOT simulate:
#   - a time variable t;
#   - cumulative adversarial knowledge W(t);
#   - adaptive within-run entropy loss after earlier compromises;
#   - an evolving p_inf,i conditioned on the exact previous compromise history.
#
# It DOES simulate:
#   1. Randomized injective assignment of terminal fragments.
#   2. Hidden random selection of m critical fragments.
#   3. Direct compromise according to the malicious verifier fraction q.
#   4. Residual inference trials at a q-dependent worst-case upper bound.
#   5. Systemic reconstruction only when all m critical fragments are controlled.
#
# FORMAL ASSUMPTIONS:
#   H_inf(d_miss_i | View_adv^(i)) >= h_res(q)
#   p_inf(q) <= 2^(-h_res(q))
#   p_comp(q) = q + (1 - q) p_inf(q)
#   P(Rec*) <= p_comp(q)^m
#
# WORST-CASE SATURATION:
# The simulation deliberately sets:
#   p_inf(q) = 2^(-h_res(q))
# thereby saturating the CNVS min-entropy inference upper bound. Each erosion
# profile therefore represents the strongest admissible inference capability
# under the assumed residual entropy margin.
#
# The linear, quadratic, and quartic profiles are heuristic stress-test models.
# They are not claimed to be universal physical laws or consequences uniquely
# derived from the CNVS formal theory.
# ==============================================================================


def min_entropy_to_inference_bound(h_residual):
    """
    Convert a non-negative residual conditional min-entropy margin into the
    corresponding worst-case adversarial inference-probability upper bound.

    The simulator deliberately saturates the bound by using the returned value
    as the actual Bernoulli inference probability in the stress test.
    """
    h_residual = float(h_residual)

    if not np.isfinite(h_residual):
        raise ValueError("h_residual must be finite.")

    if h_residual < 0.0:
        raise ValueError("h_residual must be non-negative.")

    return 2.0 ** (-h_residual)


def q_dependent_residual_entropy(h_max, q, erosion_profile):
    """
    Compute the residual min-entropy margin h_res(q) for a selected heuristic
    erosion profile.

    Profiles
    --------
    linear:
        h_res(q) = h_max * (1 - q)

    quadratic:
        h_res(q) = h_max * (1 - q)^2

    quartic:
        h_res(q) = h_max * (1 - q)^4
        This is the most aggressive profile among the three because, for
        0 < (1 - q) < 1, the fourth power is smaller than the first and second
        powers.
    """
    h_max = float(h_max)
    q = float(q)

    if not np.isfinite(h_max) or h_max < 0.0:
        raise ValueError("h_max must be finite and non-negative.")

    if not np.isfinite(q) or not (0.0 <= q <= 1.0):
        raise ValueError("q must satisfy 0 <= q <= 1.")

    if erosion_profile == "linear":
        return h_max * (1.0 - q)

    if erosion_profile == "quadratic":
        return h_max * ((1.0 - q) ** 2)

    if erosion_profile == "quartic":
        return h_max * ((1.0 - q) ** 4)

    raise ValueError(
        "Unknown erosion profile. Use 'linear', 'quadratic', or 'quartic'."
    )


def simulate_cnvs_q_dependent_entropy_erosion(
    Q_verifiers,
    r_malicious,
    k_fragments,
    m_critical,
    h_max,
    erosion_profile,
    iterations=100000,
    seed=None,
):
    """
    Monte Carlo projection of Theorem 4 under q-dependent residual
    min-entropy erosion.

    The simulator preserves m_critical as the decisive systemic-security
    quantity: reconstruction succeeds only if all m critical fragments are
    directly compromised or successfully inferred.
    """
    integer_parameters = {
        "Q_verifiers": Q_verifiers,
        "r_malicious": r_malicious,
        "k_fragments": k_fragments,
        "m_critical": m_critical,
        "iterations": iterations,
    }

    for name, value in integer_parameters.items():
        if not isinstance(value, (int, np.integer)):
            raise TypeError(f"{name} must be an integer.")

    if Q_verifiers <= 0:
        raise ValueError("Q_verifiers must be positive.")

    if not (0 <= r_malicious <= Q_verifiers):
        raise ValueError(
            "r_malicious must satisfy 0 <= r_malicious <= Q_verifiers."
        )

    if not (0 < k_fragments <= Q_verifiers):
        raise ValueError(
            "k_fragments must satisfy 0 < k_fragments <= Q_verifiers."
        )

    if not (0 < m_critical <= k_fragments):
        raise ValueError(
            "m_critical must satisfy 0 < m_critical <= k_fragments."
        )

    if iterations <= 0:
        raise ValueError("iterations must be positive.")

    h_max = float(h_max)
    if not np.isfinite(h_max) or h_max < 0.0:
        raise ValueError("h_max must be finite and non-negative.")

    rng = np.random.default_rng(seed)

    q = r_malicious / Q_verifiers

    # q-dependent erosion of the residual conditional min-entropy.
    # This value is fixed throughout each Monte Carlo run at the selected q.
    h_res_q = q_dependent_residual_entropy(
        h_max=h_max,
        q=q,
        erosion_profile=erosion_profile,
    )

    # Worst-case saturation of the formal CNVS inference upper bound:
    # p_inf(q) is deliberately set equal to 2^(-h_res(q)).
    p_inf_bound = min_entropy_to_inference_bound(h_res_q)

    p_comp_bound = q + (1.0 - q) * p_inf_bound
    theorem4_upper_bound = p_comp_bound ** m_critical

    successful_reconstructions = 0
    global_vetoes = 0

    # Fixed adversarial coalition for the selected value of r_malicious.
    malicious_verifiers = set(range(r_malicious))

    for _ in range(iterations):
        # 1. RANDOMIZED INJECTIVE ASSIGNMENT
        # Each selected verifier receives at most one terminal fragment in the
        # current assignment cycle.
        assigned_verifiers = rng.choice(
            Q_verifiers,
            size=k_fragments,
            replace=False,
        )

        # 2. HIDDEN CRITICAL BINDING
        # The m critical fragments are selected randomly inside the larger set
        # of k terminal fragments. The simulator therefore does not privilege a
        # deterministic critical configuration.
        critical_fragments = rng.choice(
            k_fragments,
            size=m_critical,
            replace=False,
        )

        directly_compromised = np.fromiter(
            (
                assigned_verifiers[fragment_index] in malicious_verifiers
                for fragment_index in critical_fragments
            ),
            dtype=bool,
            count=m_critical,
        )

        m_direct = int(np.sum(directly_compromised))
        m_missing = m_critical - m_direct

        # 3. RESIDUAL INFERENCE AT THE q-DEPENDENT WORST-CASE BOUND
        # Within a single Monte Carlo run, all missing critical fragments use
        # the same fixed p_inf(q). The test does not model adaptive within-run
        # entropy erosion after earlier compromises.
        all_missing_inferred = True

        for _ in range(m_missing):
            inferred = rng.random() < p_inf_bound

            if not inferred:
                all_missing_inferred = False
                break

        # 4. SYSTEMIC RECONSTRUCTION / GLOBAL-VETO PROXY
        # Reconstruction succeeds only if all m critical fragments are under
        # adversarial control. Otherwise at least one critical fragment remains
        # uncompromised and the systemic reconstruction attempt is vetoed.
        if m_missing == 0 or all_missing_inferred:
            successful_reconstructions += 1
        else:
            global_vetoes += 1

    simulated_rec = successful_reconstructions / iterations
    simulated_veto = global_vetoes / iterations

    return {
        "q": q,
        "h_res_q": h_res_q,
        "p_inf_bound": p_inf_bound,
        "p_comp_bound": p_comp_bound,
        "theorem4_upper_bound": theorem4_upper_bound,
        "simulated_rec": simulated_rec,
        "simulated_veto": simulated_veto,
        "successful_reconstructions": successful_reconstructions,
        "global_vetoes": global_vetoes,
        "iterations": iterations,
    }


# ==============================================================================
# SYSTEM PARAMETERS & EXECUTION
# ==============================================================================

Q_VERIFIERS = 1000
K_FRAGMENTS = 100
M_CRITICAL = 50
ITERATIONS = 100000
H_MAX_START = 10.0
SEED = 42

scenarios = {
    "Linear erosion": {
        "profile": "linear",
        "color": "#2ca02c",
    },
    "Quadratic erosion": {
        "profile": "quadratic",
        "color": "#ff7f0e",
    },
    "Quartic accelerated erosion": {
        "profile": "quartic",
        "color": "#d62728",
    },
}

# Include q = 1 explicitly as the total-collusion breaking point.
malicious_counts = np.unique(
    np.append(
        np.linspace(0, Q_VERIFIERS - 1, 40, dtype=int),
        Q_VERIFIERS,
    )
)

# Reproducible but non-identical random streams:
# SEED = 42 initializes one master sequence, from which a distinct child seed is
# generated for every scenario/q pair. Thus, the complete experiment is exactly
# reproducible without reusing the same pseudorandom stream for each curve.
master_seed_sequence = np.random.SeedSequence(SEED)
child_seed_iterator = iter(
    master_seed_sequence.spawn(
        len(scenarios) * len(malicious_counts)
    )
)

MONTE_CARLO_RESOLUTION = 1.0 / ITERATIONS

plt.figure(figsize=(12, 8))
plt.rcParams.update({"font.size": 11, "font.family": "serif"})

for label, params in scenarios.items():
    profile = params["profile"]
    color = params["color"]

    q_values = []
    simulated_results = []
    theorem_results = []

    for r_malicious in malicious_counts:
        child_seed = next(child_seed_iterator)

        result = simulate_cnvs_q_dependent_entropy_erosion(
            Q_verifiers=Q_VERIFIERS,
            r_malicious=int(r_malicious),
            k_fragments=K_FRAGMENTS,
            m_critical=M_CRITICAL,
            h_max=H_MAX_START,
            erosion_profile=profile,
            iterations=ITERATIONS,
            seed=child_seed,
        )

        q_values.append(result["q"])
        simulated_results.append(result["simulated_rec"])
        theorem_results.append(result["theorem4_upper_bound"])

    q_values = np.asarray(q_values, dtype=float)
    simulated_results = np.asarray(simulated_results, dtype=float)
    theorem_results = np.asarray(theorem_results, dtype=float)

    zero_event_mask = simulated_results == 0.0

    # Logarithmic plots cannot display zero. Zero-event observations are placed
    # at the Monte Carlo resolution floor 1/N only for visualization and are
    # marked separately with downward triangles. They must be interpreted as
    # "no reconstruction observed in N iterations", not as measured P = 1/N.
    simulated_plot = np.where(
        zero_event_mask,
        MONTE_CARLO_RESOLUTION,
        simulated_results,
    )

    plt.plot(
        q_values,
        simulated_plot,
        marker="o",
        linestyle="-",
        color=color,
        alpha=0.75,
        label=f"Simulated projection: {label}",
    )

    if np.any(zero_event_mask):
        plt.scatter(
            q_values[zero_event_mask],
            np.full(np.sum(zero_event_mask), MONTE_CARLO_RESOLUTION),
            marker="v",
            color=color,
            s=55,
            zorder=4,
            label=f"Zero observed events (< resolution): {label}",
        )

    plt.plot(
        q_values,
        theorem_results,
        linestyle="--",
        color=color,
        linewidth=2.5,
        label=f"Theorem 4 upper bound: {label}",
    )

plt.axvline(
    x=1.0,
    color="black",
    linestyle=":",
    linewidth=2.0,
    label="Total collusion breaking point (q = 1)",
)

plt.title(
    "CNVS Stress Test: q-Dependent Erosion of Residual Min-Entropy\n"
    f"Worst-Case Bound Saturation, h_max={H_MAX_START} log2-units "
    f"(Q_v={Q_VERIFIERS}, k={K_FRAGMENTS}, m={M_CRITICAL})",
    pad=15,
)

plt.xlabel(r"Fraction of Colluding Verifiers ($q = r/Q_v$)")
plt.ylabel(r"Systemic Reconstruction Probability $\mathbb{P}(Rec^*)$")
plt.yscale("log")
plt.ylim(MONTE_CARLO_RESOLUTION, 1.5)
plt.xlim(0.0, 1.02)
plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0.0)

plt.figtext(
    0.5,
    0.01,
    "Downward triangles at 1/N indicate zero observed reconstruction events; "
    "they are censored by Monte Carlo resolution and do not represent P = 1/N.",
    ha="center",
    fontsize=9,
)

plt.tight_layout(rect=(0.0, 0.04, 1.0, 1.0))

# plt.savefig(
#     "cnvs_q_dependent_residual_entropy_stress_test.pdf",
#     format="pdf",
#     dpi=300,
#     bbox_inches="tight",
# )

plt.show()
