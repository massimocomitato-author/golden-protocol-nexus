# ==============================================================================
# CNVS FRAMEWORK - ENGINEERING-HARDENED EXECUTION ENVIRONMENT
# Copyright (c) 2026 Massimo Comitato.
#
# This file is part of the CNVS MTC Data Room.
# Licensed under the PolyForm Noncommercial License 1.0.0.
#
# Commercial use is prohibited without prior written authorization.
# Academic review and technical due diligence use are permitted non-commercial uses.
#
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# ==============================================================================


#
#
# Test Name: CNVS Test 12 - Engineering-Hardened 256-bit Fragmentation Sensitivity Test under Hidden Invariant Binding.
# filname:  test_12_engineering_hardened_256bit_fragmentation
#
#



"""
CNVS Test 12:
Engineering-Hardened 256-bit Fragmentation Sensitivity Test
under Hidden Invariant Binding.

This script preserves the executable Test 11 logic:

    V_L -> Cons_R -> Inv_C -> V_G

but addresses the engineering limitations identified in the academic PoC:

    1. no NumPy finite-field state;
    2. arbitrary-precision Python integers;
    3. 256-bit prime finite field;
    4. cryptographic randomness via secrets;
    5. no deterministic seed;
    6. randomized/adaptive malicious verifier subset per trial.

This is an engineering-hardening test, not a production CNVS node and not a
formal proof of unconditional security.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import csv
import math
import secrets
import time
from typing import Dict, List, Sequence, Set, Tuple


# ==============================================================================
# 256-BIT FINITE FIELD
# ==============================================================================

# secp256k1 field prime: p = 2^256 - 2^32 - 977.
# Used here as a standard 256-bit prime modulus. This script does not implement
# elliptic-curve cryptography.
FIELD_PRIME = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F


# ==============================================================================
# PARAMETERS
# ==============================================================================

Q_VERIFIERS = 2500

# CSPRNG + 256-bit arithmetic is slower than NumPy int64.
# Raise to 20_000 when you want Test 11-like Monte Carlo resolution.
ITERATIONS_PER_POINT = 100000

# Residual inference bound: p_inf <= 2^(-H_MIN_BITS).
# Integer exponent keeps inference sampling exact via secrets.randbits().
H_MIN_BITS = 1

Q_SCENARIOS = [0.33, 0.45, 0.5, 0.6, 0.7, 0.75, 0.80, 0.85, 0.90, 0.95, 0.97, 0.98, 0.99]
M_VALUES = [1, 2, 3, 5, 8, 12, 16, 24, 32, 48, 64, 96, 128, 256, 512, 1024]

TOPOLOGY_MULTIPLIER = 2
MIN_TERMINAL_FRAGMENTS = 50
M_MAX_SEMANTIC_WARNING = 1024

# If True, malicious verifiers are resampled at every trial, approximating
# adaptive Sybil relocation / shifting peripheral compromise.
ADAPTIVE_MALICIOUS_SET = True

OUTPUT_DIR = Path("outputs/test_12_engineering_hardened_256bit")
FIGURE_DIR = Path("figures/test_12_engineering_hardened_256bit")


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass(frozen=True)
class CNVSState256:
    k: int
    m: int
    true_values: List[int]
    critical_indices: Tuple[int, ...]
    a: Dict[int, int]
    b: Dict[int, int]
    tag: Dict[int, int]
    pair_constraints: List[Tuple[int, int, int, int]]
    run_nonce: str


@dataclass(frozen=True)
class VGReport:
    accepted: bool
    local_layer_ok: bool
    relational_consistency_ok: bool
    invariant_binding_ok: bool


@dataclass(frozen=True)
class SimulationResult:
    q: float
    r: int
    k: int
    m: int
    h_min_bits: int
    p_inf: float
    vg_accept_ordinary: float
    vg_veto_ordinary: float
    local_pass_global_veto: float
    cint_leak_accepts: bool
    exact_injective_reference: float
    theorem_reference: float
    avg_direct: float
    avg_inferred: float
    avg_failed: float


# ==============================================================================
# CSPRNG HELPERS
# ==============================================================================

def rand_field_element() -> int:
    return secrets.randbelow(FIELD_PRIME)


def rand_nonzero_field_element() -> int:
    return secrets.randbelow(FIELD_PRIME - 1) + 1


def secure_sample_without_replacement(population_size: int, sample_size: int) -> List[int]:
    """CSPRNG-based sampling without replacement."""
    if sample_size < 0 or sample_size > population_size:
        raise ValueError("sample_size must satisfy 0 <= sample_size <= population_size.")
    selected: Set[int] = set()
    while len(selected) < sample_size:
        selected.add(secrets.randbelow(population_size))
    return list(selected)


def residual_inference_success(h_min_bits: int) -> bool:
    """Sample an event with exact probability 2^(-h_min_bits)."""
    if h_min_bits <= 0:
        return True
    return secrets.randbits(h_min_bits) == 0


# ==============================================================================
# FINITE-FIELD AND REFERENCE HELPERS
# ==============================================================================

def inv_mod(x: int, p: int = FIELD_PRIME) -> int:
    return pow(x, -1, p)


def p_inf_from_h_bits(h_min_bits: int) -> float:
    if h_min_bits <= 0:
        return 1.0
    return float(Fraction(1, 2 ** h_min_bits))


def wrong_field_value(true_value: int) -> int:
    delta = secrets.randbelow(FIELD_PRIME - 1) + 1
    return (true_value + delta) % FIELD_PRIME


def log_comb(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("-inf")
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def hypergeom_pmf(x: int, Q: int, r: int, m: int) -> float:
    if x < 0 or x > r or x > m or (m - x) > (Q - r):
        return 0.0
    return math.exp(log_comb(r, x) + log_comb(Q - r, m - x) - log_comb(Q, m))


def exact_injective_reference(Q: int, r: int, m: int, p_inf: float) -> float:
    """Reference only. It is not used by V_G."""
    total = 0.0
    for x in range(max(0, m - (Q - r)), min(m, r) + 1):
        total += hypergeom_pmf(x, Q, r, m) * (p_inf ** (m - x))
    return total


# ==============================================================================
# CNVS-LIKE STATE CONSTRUCTION
# ==============================================================================

def build_state_256(k: int, m: int) -> CNVSState256:
    if not (0 < m <= k):
        raise ValueError("m must satisfy 0 < m <= k.")

    true_values = [rand_field_element() for _ in range(k)]
    critical_indices = tuple(sorted(secure_sample_without_replacement(k, m)))

    a: Dict[int, int] = {}
    b: Dict[int, int] = {}
    tag: Dict[int, int] = {}

    for i in critical_indices:
        ai = rand_nonzero_field_element()
        bi = rand_field_element()
        ti = (ai * true_values[i] + bi) % FIELD_PRIME
        a[i] = ai
        b[i] = bi
        tag[i] = ti

    pair_constraints: List[Tuple[int, int, int, int]] = []
    for x, y in zip(critical_indices[:-1], critical_indices[1:]):
        c = rand_nonzero_field_element()
        target = (true_values[x] + c * true_values[y] + true_values[x] * true_values[y]) % FIELD_PRIME
        pair_constraints.append((x, y, c, target))

    return CNVSState256(
        k=k,
        m=m,
        true_values=true_values,
        critical_indices=critical_indices,
        a=a,
        b=b,
        tag=tag,
        pair_constraints=pair_constraints,
        run_nonce=secrets.token_hex(16),
    )


# ==============================================================================
# V_L, Cons_R, Inv_C, V_G
# ==============================================================================

def V_L(values: Sequence[int]) -> List[bool]:
    """Local admissibility only: integer field element. No global truth check."""
    return [isinstance(v, int) and 0 <= v < FIELD_PRIME for v in values]


def Cons_R(state: CNVSState256, values: Sequence[int], local_ok: Sequence[bool]) -> bool:
    """Minimal topological consistency proxy matching Test 11."""
    return len(values) == state.k and len(local_ok) == state.k and all(local_ok)


def Inv_C(state: CNVSState256, values: Sequence[int]) -> bool:
    """Hidden invariant binding over a 256-bit prime field."""
    for i in state.critical_indices:
        if (state.a[i] * values[i] + state.b[i]) % FIELD_PRIME != state.tag[i]:
            return False
    for x, y, c, target in state.pair_constraints:
        if (values[x] + c * values[y] + values[x] * values[y]) % FIELD_PRIME != target:
            return False
    return True


def V_G(state: CNVSState256, values: Sequence[int]) -> VGReport:
    local_ok = V_L(values)
    if not all(local_ok):
        return VGReport(False, False, False, False)
    relational_ok = Cons_R(state, values, local_ok)
    if not relational_ok:
        return VGReport(False, True, False, False)
    invariant_ok = Inv_C(state, values)
    if not invariant_ok:
        return VGReport(False, True, True, False)
    return VGReport(True, True, True, True)


# ==============================================================================
# ADVERSARIAL MODEL
# ==============================================================================

def solve_from_cint_leak(state: CNVSState256, i: int) -> int:
    return ((state.tag[i] - state.b[i]) * inv_mod(state.a[i])) % FIELD_PRIME


def make_adversarial_values(
    state: CNVSState256,
    assigned_verifiers: Sequence[int],
    malicious_set: Set[int],
    h_min_bits: int,
    mode: str,
) -> Tuple[List[int], int, int, int]:
    values = list(state.true_values)
    direct = 0
    inferred = 0
    failed = 0

    for i in state.critical_indices:
        if mode == "cint_leak":
            values[i] = solve_from_cint_leak(state, i)
            inferred += 1
            continue
        if mode != "ordinary":
            raise ValueError("mode must be 'ordinary' or 'cint_leak'.")

        if assigned_verifiers[i] in malicious_set:
            values[i] = state.true_values[i]
            direct += 1
        elif residual_inference_success(h_min_bits):
            values[i] = state.true_values[i]
            inferred += 1
        else:
            values[i] = wrong_field_value(state.true_values[i])
            failed += 1

    return values, direct, inferred, failed


# ==============================================================================
# SIMULATION
# ==============================================================================

def simulate_one_m_256(
    Q: int,
    q: float,
    m: int,
    h_min_bits: int,
    iterations: int,
    adaptive_malicious_set: bool,
) -> SimulationResult:
    if not (0 <= q < 1):
        raise ValueError("q must satisfy 0 <= q < 1.")

    r = min(max(int(round(q * Q)), 0), Q - 1)
    k = max(MIN_TERMINAL_FRAGMENTS, TOPOLOGY_MULTIPLIER * m)
    if k > Q:
        raise ValueError("k exceeds Q; reduce m or increase Q.")

    p_inf = p_inf_from_h_bits(h_min_bits)
    p_comp = q + (1.0 - q) * p_inf
    state = build_state_256(k, m)

    if not V_G(state, state.true_values).accepted:
        raise RuntimeError("Honest state rejected: invalid test construction.")

    fixed_malicious_set: Set[int] = set()
    if not adaptive_malicious_set:
        fixed_malicious_set = set(secure_sample_without_replacement(Q, r))

    accepted = 0
    veto = 0
    local_pass_global_veto = 0
    direct_total = 0
    inferred_total = 0
    failed_total = 0

    for _ in range(iterations):
        assigned_verifiers = secure_sample_without_replacement(Q, k)
        malicious_set = set(secure_sample_without_replacement(Q, r)) if adaptive_malicious_set else fixed_malicious_set

        candidate, direct, inferred, failed = make_adversarial_values(
            state, assigned_verifiers, malicious_set, h_min_bits, mode="ordinary"
        )
        report = V_G(state, candidate)

        direct_total += direct
        inferred_total += inferred
        failed_total += failed

        if report.accepted:
            accepted += 1
        else:
            veto += 1
            if report.local_layer_ok and report.relational_consistency_ok:
                local_pass_global_veto += 1

    # C_int leak control. If C_int is exposed, forged values should be accepted.
    leak_accepts_all = True
    for _ in range(5):
        assigned_verifiers = secure_sample_without_replacement(Q, k)
        malicious_set = set(secure_sample_without_replacement(Q, r)) if adaptive_malicious_set else fixed_malicious_set
        leaked_candidate, _, _, _ = make_adversarial_values(
            state, assigned_verifiers, malicious_set, h_min_bits, mode="cint_leak"
        )
        if not V_G(state, leaked_candidate).accepted:
            leak_accepts_all = False
            break

    return SimulationResult(
        q=q,
        r=r,
        k=k,
        m=m,
        h_min_bits=h_min_bits,
        p_inf=p_inf,
        vg_accept_ordinary=accepted / iterations,
        vg_veto_ordinary=veto / iterations,
        local_pass_global_veto=local_pass_global_veto / iterations,
        cint_leak_accepts=leak_accepts_all,
        exact_injective_reference=exact_injective_reference(Q, r, m, p_inf),
        theorem_reference=p_comp ** m,
        avg_direct=direct_total / iterations,
        avg_inferred=inferred_total / iterations,
        avg_failed=failed_total / iterations,
    )


def write_results_csv(results: Dict[float, List[SimulationResult]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(SimulationResult.__dataclass_fields__.keys()))
        writer.writeheader()
        for rows in results.values():
            for row in rows:
                writer.writerow(row.__dict__)


def plot_results(results: Dict[float, List[SimulationResult]], iterations: int) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("[plot] matplotlib not available; skipping figure generation.")
        return

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    floor = 1.0 / iterations

    plt.figure(figsize=(12, 7))
    for q, rows in results.items():
        m_axis = [r.m for r in rows]
        empirical = [max(r.vg_accept_ordinary, floor) for r in rows]
        exact_ref = [max(r.exact_injective_reference, floor) for r in rows]
        plt.plot(m_axis, empirical, marker="o", label=f"Executable V_G acceptance, q={q:.2f}")
        plt.plot(m_axis, exact_ref, linestyle="--", label=f"Exact injective reference, q={q:.2f}")
    plt.axvline(M_MAX_SEMANTIC_WARNING, linestyle=":", linewidth=2, label=f"semantic warning m_max = {M_MAX_SEMANTIC_WARNING}")
    plt.yscale("log")
    plt.xlabel("Critical fragmentation cardinality m")
    plt.ylabel("Unauthorized reconstruction / V_G acceptance probability")
    plt.title("CNVS Test 12: 256-bit CSPRNG Engineering-Hardened Fragmentation Test")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend(fontsize=9)
    plt.tight_layout()
    out1 = FIGURE_DIR / "test_12_256bit_vg_acceptance.png"
    plt.savefig(out1, dpi=300)
    plt.close()

    plt.figure(figsize=(12, 7))
    for q, rows in results.items():
        m_axis = [r.m for r in rows]
        veto_signal = [r.local_pass_global_veto for r in rows]
        plt.plot(m_axis, veto_signal, marker="s", label=f"Local-pass / Global-Veto rate, q={q:.2f}")
    plt.axvline(M_MAX_SEMANTIC_WARNING, linestyle=":", linewidth=2, label=f"semantic warning m_max = {M_MAX_SEMANTIC_WARNING}")
    plt.xlabel("Critical fragmentation cardinality m")
    plt.ylabel("Rate where V_L and Cons_R pass but V_G vetoes")
    plt.title("CNVS Test 12: Non-Reducibility Signal under 256-bit CSPRNG Execution")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend(fontsize=9)
    plt.tight_layout()
    out2 = FIGURE_DIR / "test_12_256bit_local_pass_global_veto.png"
    plt.savefig(out2, dpi=300)
    plt.close()

    print(f"[plot] saved {out1}")
    print(f"[plot] saved {out2}")


def run_test_12() -> Dict[float, List[SimulationResult]]:
    run_id = secrets.token_hex(12)
    start = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nCNVS Test 12: Engineering-Hardened 256-bit Fragmentation Sensitivity")
    print("--------------------------------------------------------------------")
    print(f"run_id = {run_id}")
    print(f"field_prime_bits = {FIELD_PRIME.bit_length()}")
    print(f"Q_verifiers = {Q_VERIFIERS}")
    print(f"h_min_bits = {H_MIN_BITS}")
    print(f"iterations per point = {ITERATIONS_PER_POINT}")
    print(f"adaptive malicious set = {ADAPTIVE_MALICIOUS_SET}")
    print(f"m values = {M_VALUES}")
    print("V_G acceptance is computed by executing V_L -> Cons_R -> Inv_C -> V_G.")
    print("The analytical formula is shown only as a reference.\n")

    results: Dict[float, List[SimulationResult]] = {}

    for q in Q_SCENARIOS:
        rows: List[SimulationResult] = []
        print(f"\n=== q = {q:.2f} ===")
        print("m | k | VG_accept | local-pass/VG-veto | exact_ref | theorem_ref | C_int_leak")
        for m in M_VALUES:
            out = simulate_one_m_256(Q_VERIFIERS, q, m, H_MIN_BITS, ITERATIONS_PER_POINT, ADAPTIVE_MALICIOUS_SET)
            rows.append(out)
            print(
                f"{out.m:3d} | {out.k:3d} | {out.vg_accept_ordinary:.8f} | "
                f"{out.local_pass_global_veto:.8f} | {out.exact_injective_reference:.8f} | "
                f"{out.theorem_reference:.8f} | {out.cint_leak_accepts}"
            )
        results[q] = rows

    csv_path = OUTPUT_DIR / f"test_12_results_{run_id}.csv"
    write_results_csv(results, csv_path)
    plot_results(results, ITERATIONS_PER_POINT)

    print("\nCompleted.")
    print(f"run_id = {run_id}")
    print(f"elapsed_seconds = {time.time() - start:.2f}")
    print(f"results_csv = {csv_path}")
    return results


if __name__ == "__main__":
    run_test_12()
