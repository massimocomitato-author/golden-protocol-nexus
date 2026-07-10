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
from pathlib import Path
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt


# ==============================================================================
# Test Name: Test 11 - Executable Fragmentation Sensitivity under Hidden Invariant Binding
# filename = "test_11_fragmentation_sensitivity_100k_2048_with_plots.py"
#
# Purpose:
#   This test extends the logic of CNVS Test 10.
#
#   Test 10 checks that peripheral verifier compromise does not imply global
#   falsification while C_int remains hidden.
#
#   Test 11 varies the critical fragmentation cardinality m inside an executable
#   CNVS-like model and measures how the observed V_G acceptance probability
#   changes as m increases.
#
# Core idea:
#
#   The test does NOT decide success using:
#
#       P(Rec*) <= [q + (1 - q) 2^(-h_min)]^m
#
#   Instead, every adversarial candidate is executed through:
#
#       V_L -> Cons_R -> Inv_C -> V_G
#
#   The analytical formula is shown only as a comparison reference.
#
# What is simulated:
#   1. terminal fragments;
#   2. hidden critical subset;
#   3. local syntactic verification V_L;
#   4. structural consistency Cons_R;
#   5. hidden finite-field invariant binding Inv_C;
#   6. global validation V_G;
#   7. ordinary adversary with peripheral verifier compromise;
#   8. C_int leak upper-bound control.
#
# This is not a formal proof and not a full CNVS implementation.
# It is an executable structural sensitivity test under explicit assumptions.
# ==============================================================================


PRIME = 1_000_003


@dataclass
class State:
    k: int
    m: int
    true: np.ndarray
    crit: np.ndarray
    a: np.ndarray
    b: np.ndarray
    tag: np.ndarray
    pairs: list


# ==============================================================================
# BASIC UTILITIES
# ==============================================================================

def inv_mod(a, p=PRIME):
    return pow(int(a), p - 2, p)


def p_inf_from_h(h_min):
    """
    Residual min-entropy interpretation:

        H_inf(d_miss_i | View_adv_i) >= h_min

    Therefore:

        p_inf <= 2^(-h_min)
    """
    return 1.0 if h_min <= 0 else 2.0 ** (-float(h_min))


def make_point_rng(seed_base: int, q_index: int, m_value: int, stream: int = 0):
    """
    Deterministic but separated seed construction.

    Each (q, m) point receives an independent pseudo-random stream while remaining
    reproducible for academic review.
    """
    seed_sequence = np.random.SeedSequence([seed_base, q_index, int(m_value), stream])
    return np.random.default_rng(seed_sequence)


# ==============================================================================
# STATE CONSTRUCTION
# ==============================================================================

def build_state(k, m, rng):
    """
    Build a finite CNVS-like candidate state.

    The state contains:
      - k terminal fragments;
      - m hidden critical fragments;
      - one hidden algebraic C_int tag per critical fragment;
      - hidden pairwise finite-field constraints among critical fragments.

    Local verifiers do not know:
      - critical subset;
      - a, b, tag;
      - pair constraints;
      - global invariant binding.
    """

    if m > k:
        raise ValueError("m must be <= k. Critical fragments cannot exceed terminal fragments.")

    true = rng.integers(0, PRIME, size=k, dtype=np.int64)

    crit = np.sort(
        rng.choice(k, size=m, replace=False)
    ).astype(int)

    a = np.zeros(k, dtype=np.int64)
    b = np.zeros(k, dtype=np.int64)
    tag = np.zeros(k, dtype=np.int64)

    # Hidden per-fragment invariant tag:
    #
    #     tag_i = a_i * value_i + b_i mod PRIME
    #
    # This is a finite-field proxy for hidden invariant binding.
    for i in crit:
        a[i] = rng.integers(1, PRIME)
        b[i] = rng.integers(0, PRIME)
        tag[i] = (a[i] * true[i] + b[i]) % PRIME

    # Hidden pairwise relational constraints:
    #
    #     target = x_i + c*x_j + x_i*x_j mod PRIME
    #
    # These constraints make V_G non-reducible to local syntactic validity.
    pairs = []

    for x, y in zip(crit[:-1], crit[1:]):
        c = int(rng.integers(1, PRIME))
        target = (
            int(true[x])
            + c * int(true[y])
            + int(true[x]) * int(true[y])
        ) % PRIME

        pairs.append((int(x), int(y), c, target))

    return State(
        k=k,
        m=m,
        true=true,
        crit=crit,
        a=a,
        b=b,
        tag=tag,
        pairs=pairs
    )


# ==============================================================================
# V_L, Cons_R, Inv_C, V_G
# ==============================================================================

def V_L(values):
    """
    Local Verification V_L.

    V_L checks only local admissibility:
      - value is inside the accepted finite-field domain.

    It does not check truth.
    It does not know hidden invariants.
    It does not know global binding.

    Therefore, wrong but well-formed values can pass V_L.
    """
    return (values >= 0) & (values < PRIME)


def Cons_R(state, values, local_ok):
    """
    Relational/topological consistency proxy.

    In this finite test, Cons_R checks:
      - the candidate has exactly k terminal values;
      - all values passed V_L.

    A full CNVS implementation would also check the complete typed topology R(t).
    """
    if len(values) != state.k:
        return False

    if len(local_ok) != state.k:
        return False

    if not bool(np.all(local_ok)):
        return False

    return True


def Inv_C(state, values):
    """
    Hidden invariant binding Inv_C.

    This is the global hidden layer.

    It checks:
      1. hidden algebraic tag for every critical fragment;
      2. hidden pairwise relational constraints among critical fragments.

    If a missing critical fragment is guessed incorrectly, it may pass V_L
    but should fail Inv_C with overwhelming probability.
    """

    for i in state.crit:
        if (
            int(state.a[i]) * int(values[i])
            + int(state.b[i])
        ) % PRIME != int(state.tag[i]):
            return False

    for x, y, c, target in state.pairs:
        if (
            int(values[x])
            + c * int(values[y])
            + int(values[x]) * int(values[y])
        ) % PRIME != target:
            return False

    return True


def V_G(state, values):
    """
    Global Verification V_G.

    V_G accepts only if:
      - all terminal values pass V_L;
      - Cons_R is satisfied;
      - Inv_C is satisfied.

    Otherwise, Global Veto is triggered.
    """

    local_ok = V_L(values)
    local_layer_ok = bool(np.all(local_ok))

    if not local_layer_ok:
        return False, local_layer_ok, False, False

    rel_ok = Cons_R(state, values, local_ok)

    if not rel_ok:
        return False, True, False, False

    inv_ok = Inv_C(state, values)

    if not inv_ok:
        return False, True, True, False

    return True, True, True, True


# ==============================================================================
# ADVERSARIAL MODEL
# ==============================================================================

def wrong_value(v, rng):
    """
    Wrong but locally admissible value.

    It passes V_L, but should fail V_G if the fragment is critical.
    """
    return (int(v) + int(rng.integers(1, PRIME))) % PRIME


def solve_from_Cint_leak(state, i):
    """
    Upper-bound C_int leak model.

    If C_int is fully leaked, the adversary can invert:

        tag_i = a_i * value_i + b_i mod PRIME

    and reconstruct the critical value.
    """
    return (
        (int(state.tag[i]) - int(state.b[i]))
        * inv_mod(state.a[i])
    ) % PRIME


def make_adversarial_values(
    state,
    assigned,
    malicious_set,
    p_inf,
    rng,
    mode="ordinary"
):
    """
    Construct adversarial candidate evidence.

    ordinary mode:
      - directly compromised critical fragments are known;
      - missing critical fragments are inferred with probability p_inf;
      - failed missing fragments receive wrong but locally admissible values.

    cint_leak mode:
      - C_int is fully exfiltrated;
      - the attacker reconstructs all critical values from hidden parameters.

    The candidate is then evaluated by V_G.
    """

    values = np.array(state.true, copy=True)

    direct = 0
    inferred = 0
    failed = 0

    for i in state.crit:
        i = int(i)

        if mode == "cint_leak":
            values[i] = solve_from_Cint_leak(state, i)
            inferred += 1
            continue

        if mode != "ordinary":
            raise ValueError("mode must be 'ordinary' or 'cint_leak'.")

        directly_compromised = int(assigned[i]) in malicious_set

        if directly_compromised:
            values[i] = state.true[i]
            direct += 1

        else:
            if rng.random() < p_inf:
                values[i] = state.true[i]
                inferred += 1
            else:
                values[i] = wrong_value(state.true[i], rng)
                failed += 1

    return values, direct, inferred, failed


# ==============================================================================
# EXACT AND THEOREM REFERENCES
# ==============================================================================

def log_comb(n, k):
    if k < 0 or k > n:
        return float("-inf")

    return (
        math.lgamma(n + 1)
        - math.lgamma(k + 1)
        - math.lgamma(n - k + 1)
    )


def hypergeom_pmf(x, Q, r, m):
    """
    X = number of critical fragments directly assigned to malicious verifiers.

    Since assignment is injective, X follows a hypergeometric law.
    """
    if x < 0 or x > r or x > m or (m - x) > (Q - r):
        return 0.0

    return math.exp(
        log_comb(r, x)
        + log_comb(Q - r, m - x)
        - log_comb(Q, m)
    )


def exact_injective_reference(Q, r, m, p_inf):
    """
    Exact injective-assignment reference.

    This is not used to decide V_G acceptance.
    It is plotted only to compare the executable result with the expected
    injective-assignment reconstruction probability:

        sum_x Hypergeom(Q, r, m; x) * p_inf^(m-x)
    """
    total = 0.0

    for x in range(max(0, m - (Q - r)), min(m, r) + 1):
        total += hypergeom_pmf(x, Q, r, m) * (p_inf ** (m - x))

    return total


def theorem_reference(q, m, p_inf):
    """
    Compact CNVS theorem-style reference:

        p_comp = q + (1 - q) * p_inf

        theorem_ref = p_comp^m

    This curve is not used to decide V_G acceptance.
    """
    p_comp = q + (1.0 - q) * p_inf
    return p_comp ** m


# ==============================================================================
# SIMULATION
# ==============================================================================

def simulate_one_m(
    Q,
    q,
    m,
    h_min,
    iterations,
    rng,
    terminal_fragments,
):
    """
    Simulate one fragmentation level m.

    In this high-resolution variant, the total number of terminal fragments is
    fixed at terminal_fragments = 2048, while m varies up to 2048.
    """

    if not (0 <= q < 1):
        raise ValueError("q must satisfy 0 <= q < 1.")

    r = min(max(int(round(q * Q)), 0), Q - 1)
    k = int(terminal_fragments)

    if k > Q:
        raise ValueError(
            f"Injective assignment requires k <= Q, but k={k} and Q={Q}. "
            "Increase Q or reduce terminal_fragments."
        )

    if m > k:
        raise ValueError(
            f"Critical fragments m={m} cannot exceed terminal fragments k={k}."
        )

    p_inf = p_inf_from_h(h_min)
    state = build_state(k, m, rng)

    honest_accept, _, _, _ = V_G(state, state.true)

    if not honest_accept:
        raise RuntimeError("Honest state rejected: invalid test construction.")

    malicious = set(range(r))

    accepted = 0
    veto = 0
    local_pass_global_veto = 0

    direct_total = 0
    inferred_total = 0
    failed_total = 0

    for _ in range(iterations):

        # Injective assignment: one fragment, one verifier.
        assigned = rng.choice(Q, size=k, replace=False)

        candidate, d, inf, fail = make_adversarial_values(
            state=state,
            assigned=assigned,
            malicious_set=malicious,
            p_inf=p_inf,
            rng=rng,
            mode="ordinary"
        )

        acc, local_ok, rel_ok, inv_ok = V_G(state, candidate)

        direct_total += d
        inferred_total += inf
        failed_total += fail

        if acc:
            accepted += 1
        else:
            veto += 1

            if local_ok and rel_ok:
                local_pass_global_veto += 1

    # C_int leak control.
    assigned = rng.choice(Q, size=k, replace=False)

    leaked_candidate, _, _, _ = make_adversarial_values(
        state=state,
        assigned=assigned,
        malicious_set=malicious,
        p_inf=p_inf,
        rng=rng,
        mode="cint_leak"
    )

    leak_accept, _, _, _ = V_G(state, leaked_candidate)

    exact_ref = exact_injective_reference(Q, r, m, p_inf)
    theorem_ref = theorem_reference(q, m, p_inf)

    return {
        "q": q,
        "r": r,
        "k": k,
        "m": m,
        "h_min": h_min,
        "p_inf": p_inf,
        "VG_accept_ordinary": accepted / iterations,
        "VG_veto_ordinary": veto / iterations,
        "local_pass_global_veto": local_pass_global_veto / iterations,
        "Cint_leak_accepts": bool(leak_accept),
        "exact_injective_reference": exact_ref,
        "theorem_reference": theorem_ref,
        "avg_direct": direct_total / iterations,
        "avg_inferred": inferred_total / iterations,
        "avg_failed": failed_total / iterations,
    }


# ==============================================================================
# PLOTTING
# ==============================================================================

def plot_test11_comparisons(
    results,
    iterations,
    out_dir,
    selected_q_for_curves,
    show_plots=True
):
    """
    Generates and displays Test 11 comparison plots.

    Output:
      - test_11_selected_q_vg_acceptance_vs_references.png
      - test_11_all_points_empirical_vs_references.png
      - test_11_local_pass_global_veto_heatmap.png
      - test_11_max_fragmentation_vs_q.png

    If show_plots=True, the figures are displayed in notebook / Colab output.
    """

    out_dir.mkdir(parents=True, exist_ok=True)
    floor = 1.0 / max(1, iterations)

    # --------------------------------------------------------------------------
    # Plot 1: selected q curves, empirical vs exact vs theorem.
    # --------------------------------------------------------------------------

    plt.figure(figsize=(13, 8))

    for q in selected_q_for_curves:
        if q not in results:
            continue

        rows = results[q]

        m_axis = np.array([r["m"] for r in rows])
        empirical = np.array([r["VG_accept_ordinary"] for r in rows])
        exact_ref = np.array([r["exact_injective_reference"] for r in rows])
        theorem_ref = np.array([r["theorem_reference"] for r in rows])

        plt.plot(
            m_axis,
            np.maximum(empirical, floor),
            marker="o",
            label=f"Executable V_G, q={q:.2f}"
        )

        plt.plot(
            m_axis,
            np.maximum(exact_ref, floor),
            linestyle="--",
            label=f"Exact injective, q={q:.2f}"
        )

        plt.plot(
            m_axis,
            np.maximum(theorem_ref, floor),
            linestyle=":",
            label=f"Theorem ref, q={q:.2f}"
        )

    plt.xscale("log", base=2)
    plt.yscale("log")
    plt.xlabel("Critical fragmentation cardinality m")
    plt.ylabel(f"Unauthorized reconstruction / V_G acceptance probability; floor = 1 / {iterations}")
    plt.title("CNVS Test 11: Executable V_G Acceptance vs Exact and Theorem References")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend(fontsize=8, ncol=2)
    plt.tight_layout()

    output_1 = out_dir / "test_11_selected_q_vg_acceptance_vs_references.png"
    plt.savefig(output_1, dpi=300)

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 2: all empirical points against exact and theorem references.
    # --------------------------------------------------------------------------

    empirical_all = []
    exact_all = []
    theorem_all = []

    for _, rows in results.items():
        for r in rows:
            empirical_all.append(max(r["VG_accept_ordinary"], floor))
            exact_all.append(max(r["exact_injective_reference"], floor))
            theorem_all.append(max(r["theorem_reference"], floor))

    empirical_all = np.array(empirical_all)
    exact_all = np.array(exact_all)
    theorem_all = np.array(theorem_all)

    min_axis = floor
    max_axis = 1.0

    plt.figure(figsize=(9, 9))

    plt.scatter(
        exact_all,
        empirical_all,
        marker="o",
        label="Empirical vs exact injective reference"
    )

    plt.scatter(
        theorem_all,
        empirical_all,
        marker="^",
        label="Empirical vs theorem reference"
    )

    plt.plot(
        [min_axis, max_axis],
        [min_axis, max_axis],
        linestyle="--",
        label="Ideal alignment y = x"
    )

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Reference probability")
    plt.ylabel("Observed executable V_G acceptance")
    plt.title("CNVS Test 11: Empirical Acceptance vs Reference Curves")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    plt.tight_layout()

    output_2 = out_dir / "test_11_all_points_empirical_vs_references.png"
    plt.savefig(output_2, dpi=300)

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 3: Local-pass / Global-Veto heatmap.
    # --------------------------------------------------------------------------

    q_values = list(results.keys())
    m_values = [r["m"] for r in next(iter(results.values()))]

    heatmap = np.array([
        [r["local_pass_global_veto"] for r in results[q]]
        for q in q_values
    ])

    plt.figure(figsize=(13, 8))

    im = plt.imshow(
        heatmap,
        aspect="auto",
        origin="lower"
    )

    plt.colorbar(im, label="Local-pass / Global-Veto rate")
    plt.xticks(
        ticks=np.arange(len(m_values)),
        labels=[str(m) for m in m_values],
        rotation=45,
        ha="right"
    )
    plt.yticks(
        ticks=np.arange(len(q_values)),
        labels=[f"{q:.2f}" for q in q_values]
    )
    plt.xlabel("Critical fragmentation cardinality m")
    plt.ylabel("Peripheral compromise q")
    plt.title("CNVS Test 11: Non-Reducibility Heatmap")
    plt.tight_layout()

    output_3 = out_dir / "test_11_local_pass_global_veto_heatmap.png"
    plt.savefig(output_3, dpi=300)

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 4: max fragmentation vs q.
    # --------------------------------------------------------------------------

    max_m = max(m_values)

    q_axis = []
    empirical_final = []
    exact_final = []
    theorem_final = []

    for q, rows in results.items():
        row = next(r for r in rows if r["m"] == max_m)

        q_axis.append(q)
        empirical_final.append(max(row["VG_accept_ordinary"], floor))
        exact_final.append(max(row["exact_injective_reference"], floor))
        theorem_final.append(max(row["theorem_reference"], floor))

    plt.figure(figsize=(12, 7))

    plt.semilogy(
        q_axis,
        empirical_final,
        marker="o",
        label=f"Executable V_G acceptance at m={max_m}"
    )

    plt.semilogy(
        q_axis,
        exact_final,
        linestyle="--",
        marker="s",
        label=f"Exact injective reference at m={max_m}"
    )

    plt.semilogy(
        q_axis,
        theorem_final,
        linestyle=":",
        marker="^",
        label=f"Theorem reference at m={max_m}"
    )

    plt.xlabel("Peripheral verifier compromise q")
    plt.ylabel(f"Probability, log scale; floor = 1 / {iterations}")
    plt.title(f"CNVS Test 11: Max Fragmentation m={max_m} vs q")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    plt.tight_layout()

    output_4 = out_dir / "test_11_max_fragmentation_vs_q.png"
    plt.savefig(output_4, dpi=300)

    if show_plots:
        plt.show()

    plt.close()

    print("\n[Plot Output]")
    print(f"Saved: {output_1}")
    print(f"Saved: {output_2}")
    print(f"Saved: {output_3}")
    print(f"Saved: {output_4}")
    print(f"Absolute folder: {out_dir.resolve()}")


# ==============================================================================
# MAIN TEST RUN
# ==============================================================================

def run_test_11():

    # ==========================================================================
    # PARAMETERS
    # ==========================================================================

    # Requested setup:
    #
    #   requested Q = 2000
    #   terminal fragments = 2048
    #
    # Strict injective assignment requires:
    #
    #   Q >= k >= m
    #
    # Therefore, the effective Q is automatically raised to 2048 in order to
    # preserve the one-fragment / one-verifier assumption instead of silently
    # breaking the model.
    Q_REQUESTED = 2000
    TERMINAL_FRAGMENTS = 2048
    Q = max(Q_REQUESTED, TERMINAL_FRAGMENTS)

    H_MIN = 1.0
    ITERATIONS = 100_000
    SEED_BASE = 42

    Q_SCENARIOS = [
        0.33, 0.40, 0.45, 0.50,
        0.55, 0.60, 0.65, 0.70,
        0.75, 0.80, 0.85, 0.90,
        0.95, 0.97, 0.98, 0.99
    ]

    M_VALUES = [
        1, 2, 4, 8, 16, 32,
        64, 128, 256, 512, 1024, 2048
    ]

    SELECTED_Q_FOR_CURVES = [0.50, 0.70, 0.90, 0.99]

    OUT_DIR = Path("figures/test_11")

    results = {}

    print("\nCNVS Test 11: Executable Fragmentation Sensitivity Test")
    print("-------------------------------------------------------")
    print(f"Q_requested = {Q_REQUESTED}")
    print(f"Q_effective = {Q}")
    print(f"terminal_fragments k = {TERMINAL_FRAGMENTS}")
    print(f"h_min = {H_MIN}")
    print(f"iterations per point = {ITERATIONS}")
    print(f"seed base = {SEED_BASE}")
    print(f"q scenarios = {Q_SCENARIOS}")
    print(f"m values = {M_VALUES}")
    print("V_G acceptance is computed by executing V_L -> Cons_R -> Inv_C -> V_G.")
    print("Exact and theorem references are shown only as comparison curves.")
    print("Formula: theorem_ref = [q + (1 - q) * 2^(-h_min)]^m\n")

    if Q != Q_REQUESTED:
        print("[Injective Assignment Notice]")
        print(
            f"Requested Q={Q_REQUESTED} is smaller than terminal_fragments={TERMINAL_FRAGMENTS}. "
            f"Effective Q has been raised to {Q} to preserve injective assignment.\n"
        )

    for q_index, q in enumerate(Q_SCENARIOS):

        rows = []

        print(f"\n=== q = {q:.2f} ===")
        print(
            "m | k | VG_accept | local-pass/VG-veto | "
            "exact_ref | theorem_ref | C_int_leak"
        )

        for m in M_VALUES:

            rng = make_point_rng(SEED_BASE, q_index, m)

            out = simulate_one_m(
                Q=Q,
                q=q,
                m=m,
                h_min=H_MIN,
                iterations=ITERATIONS,
                rng=rng,
                terminal_fragments=TERMINAL_FRAGMENTS,
            )

            rows.append(out)

            print(
                f"{m:4d} | {out['k']:4d} | "
                f"{out['VG_accept_ordinary']:.8f} | "
                f"{out['local_pass_global_veto']:.8f} | "
                f"{out['exact_injective_reference']:.8f} | "
                f"{out['theorem_reference']:.8f} | "
                f"{out['Cint_leak_accepts']}"
            )

        results[q] = rows

    plot_test11_comparisons(
        results=results,
        iterations=ITERATIONS,
        out_dir=OUT_DIR,
        selected_q_for_curves=SELECTED_Q_FOR_CURVES,
        show_plots=True,
    )

    print("\n================ FINAL INTERPRETATION ================\n")
    print("- Test 11 was executed through V_L -> Cons_R -> Inv_C -> V_G.")
    print("- Exact injective and theorem references were used only as comparison curves.")
    print("- The theorem reference is [q + (1 - q) * 2^(-h_min)]^m.")
    print("- The exact reference uses the hypergeometric injective-assignment law.")
    print("- The local-pass / Global-Veto signal measures CNVS non-reducibility.")
    print("- The C_int leak control confirms the expected upper-bound collapse scenario.")

    return results


if __name__ == "__main__":
    run_test_11()
