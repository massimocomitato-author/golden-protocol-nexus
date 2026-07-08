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
from dataclasses import dataclass


# ==============================================================================
# CNVS TEST 11:
# EXECUTABLE FRAGMENTATION SENSITIVITY TEST
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
#   The analytical formula is shown only as a reference curve.
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
    #     target = x_i + c * x_j + x_i*x_j mod PRIME
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

    # Individual hidden C_int tags.
    for i in state.crit:
        if (
            int(state.a[i]) * int(values[i])
            + int(state.b[i])
        ) % PRIME != int(state.tag[i]):
            return False

    # Pairwise hidden constraints.
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
# EXACT REFERENCE CURVE FOR INJECTIVE ASSIGNMENT
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
    Reference probability only.

    This is not used to decide V_G acceptance.
    It is plotted only to compare the executable result with the expected
    injective-assignment reconstruction probability.
    """

    total = 0.0

    for x in range(max(0, m - (Q - r)), min(m, r) + 1):
        total += hypergeom_pmf(x, Q, r, m) * (p_inf ** (m - x))

    return total


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
    topology_multiplier=2
):
    """
    Simulate one fragmentation level m.

    k grows with m to represent deeper fragmentation.
    """

    if not (0 <= q < 1):
        raise ValueError("q must satisfy 0 <= q < 1.")

    r = min(max(int(round(q * Q)), 0), Q - 1)
    k = max(50, topology_multiplier * m)

    if k > Q:
        raise ValueError("k exceeds Q; reduce m or increase Q.")

    p_inf = p_inf_from_h(h_min)

    state = build_state(k, m, rng)

    # Honest sanity check.
    honest_accept, _, _, _ = V_G(state, state.true)

    if not honest_accept:
        raise RuntimeError("Honest state rejected: invalid test construction.")

    malicious = set(range(r))

    accepted = 0
    veto = 0
    local_pass_global_veto = 0

    direct_counts = []
    inferred_counts = []
    failed_counts = []

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

        direct_counts.append(d)
        inferred_counts.append(inf)
        failed_counts.append(fail)

        if acc:
            accepted += 1
        else:
            veto += 1

            # This is the key CNVS signal:
            # local admissibility and Cons_R pass, but V_G rejects through Inv_C.
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

    p_comp = q + (1 - q) * p_inf

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
        "exact_injective_reference": exact_injective_reference(Q, r, m, p_inf),
        "theorem_reference": p_comp ** m,
        "avg_direct": float(np.mean(direct_counts)),
        "avg_inferred": float(np.mean(inferred_counts)),
        "avg_failed": float(np.mean(failed_counts)),
    }


def run_test_11():

    # ==========================================================================
    # PARAMETERS
    # ==========================================================================

    Q = 1000
    H_MIN = 1.0
    ITERATIONS = 20_000
    SEED = 42

    Q_SCENARIOS = [0.60, 0.80, 0.90]

    M_VALUES = [
        1, 2, 3, 5, 8, 12, 16,
        24, 32, 48, 64, 96, 128
    ]

    # Semantic feasibility warning only.
    # It does not affect V_G.
    M_MAX_SEMANTIC = 150

    rng = np.random.default_rng(SEED)

    results = {}

    print("\nCNVS Test 11: Executable Fragmentation Sensitivity Test")
    print("-------------------------------------------------------")
    print(f"Q_verifiers = {Q}")
    print(f"h_min = {H_MIN}")
    print(f"iterations per point = {ITERATIONS}")
    print(f"m values = {M_VALUES}")
    print("V_G acceptance is computed by executing V_L -> Cons_R -> Inv_C -> V_G.")
    print("The analytical formula is shown only as a reference.\n")

    for q in Q_SCENARIOS:

        rows = []

        print(f"\n=== q = {q:.2f} ===")
        print(
            "m | k | VG_accept | local-pass/VG-veto | "
            "exact_ref | theorem_ref | C_int_leak"
        )

        for m in M_VALUES:

            out = simulate_one_m(
                Q=Q,
                q=q,
                m=m,
                h_min=H_MIN,
                iterations=ITERATIONS,
                rng=rng
            )

            rows.append(out)

            print(
                f"{m:3d} | {out['k']:3d} | "
                f"{out['VG_accept_ordinary']:.8f} | "
                f"{out['local_pass_global_veto']:.8f} | "
                f"{out['exact_injective_reference']:.8f} | "
                f"{out['theorem_reference']:.8f} | "
                f"{out['Cint_leak_accepts']}"
            )

        results[q] = rows

    # ==========================================================================
    # PLOT 1: EXECUTABLE V_G ACCEPTANCE
    # ==========================================================================

    floor = 1.0 / ITERATIONS

    plt.figure(figsize=(12, 7))

    for q, rows in results.items():

        m_axis = np.array([r["m"] for r in rows])
        empirical = np.array([r["VG_accept_ordinary"] for r in rows])
        exact_ref = np.array([r["exact_injective_reference"] for r in rows])

        plt.plot(
            m_axis,
            np.maximum(empirical, floor),
            marker="o",
            label=f"Executable V_G acceptance, q={q:.2f}"
        )

        plt.plot(
            m_axis,
            np.maximum(exact_ref, floor),
            linestyle="--",
            label=f"Exact injective reference, q={q:.2f}"
        )

    plt.axvline(
        M_MAX_SEMANTIC,
        linestyle=":",
        linewidth=2,
        label=f"semantic warning m_max = {M_MAX_SEMANTIC}"
    )

    plt.yscale("log")
    plt.xlabel("Critical fragmentation cardinality m")
    plt.ylabel("Unauthorized reconstruction / V_G acceptance probability")
    plt.title(
        f"CNVS Test 11: Fragmentation Depth vs Executable V_G Acceptance "
        f"(h_min={H_MIN})"
    )
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend(fontsize=9)
    plt.tight_layout()

    # Uncomment for publication export.
    # plt.savefig(
    #     "cnvs_test11_fragmentation_sensitivity_vg_acceptance.pdf",
    #     format="pdf",
    #     dpi=300
    # )

    plt.show()

    # ==========================================================================
    # PLOT 2: LOCAL VALIDITY BUT GLOBAL VETO
    # ==========================================================================

    plt.figure(figsize=(12, 7))

    for q, rows in results.items():

        m_axis = np.array([r["m"] for r in rows])
        veto_signal = np.array([r["local_pass_global_veto"] for r in rows])

        plt.plot(
            m_axis,
            veto_signal,
            marker="s",
            label=f"Local-pass / Global-Veto rate, q={q:.2f}"
        )

    plt.axvline(
        M_MAX_SEMANTIC,
        linestyle=":",
        linewidth=2,
        label=f"semantic warning m_max = {M_MAX_SEMANTIC}"
    )

    plt.xlabel("Critical fragmentation cardinality m")
    plt.ylabel("Rate of cases where V_L and Cons_R pass but V_G vetoes")
    plt.title(
        "CNVS Test 11: Non-Reducibility Signal\n"
        "Local admissibility passes while hidden C_int binding triggers Global Veto"
    )
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend(fontsize=9)
    plt.tight_layout()

    # Uncomment for publication export.
    # plt.savefig(
    #     "cnvs_test11_local_pass_global_veto_rate.pdf",
    #     format="pdf",
    #     dpi=300
    # )

    plt.show()

    return results


if __name__ == "__main__":
    run_test_11()
