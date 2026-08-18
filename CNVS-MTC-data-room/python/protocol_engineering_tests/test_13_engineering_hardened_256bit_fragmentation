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

from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from random import SystemRandom
import secrets
import time
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import matplotlib.pyplot as plt


# ==============================================================================
# TEST 13 — ENGINEERING-HARDENED 256-BIT FRAGMENTATION SENSITIVITY
#
# Test Name:
# CNVS Test 13 - Engineering-Hardened 256-bit Fragmentation Sensitivity
#                under Hidden Full-State Invariant Binding
#
# filename = "test_13_engineering_hardened_256bit_fragmentation.py"
#
# CLASSIFICATION:
# This program is a CSPRNG-driven Monte Carlo sensitivity experiment with
# arbitrary-precision Python integers and a 256-bit prime field.
#
# It is NOT:
#   - a formal proof of CNVS;
#   - a production CNVS node;
#   - an empirical validation of a deployed system;
#   - a false-state-acceptance experiment;
#   - a complete authentication, consensus, or network implementation.
#
# PRIMARY QUESTION:
# How does the probability of reconstructing every hidden critical fragment
# change as critical fragmentation cardinality m increases?
#
# IMPORTANT SEMANTIC DISTINCTION:
# The ordinary measured event is:
#
#   "the adversary reconstructs all hidden critical values, after which the
#    authentic reconstructed state is accepted by V_G."
#
# It is NOT:
#
#   "V_G accepts an arbitrary semantically false state."
#
# A separate false-state control mutates an already reconstructed state and
# verifies that the hidden invariant binding vetoes it.
#
# ENGINEERING-HARDENING PROPERTIES:
#   1. arbitrary-precision Python integers;
#   2. secp256k1's 256-bit field prime as modulus;
#   3. cryptographic randomness from secrets/SystemRandom;
#   4. no deterministic test seed;
#   5. 128-bit run identifiers;
#   6. exact injective-assignment sampling through integer hypergeometric weights;
#   7. exact 2^(-h) inference sampling;
#   8. full-state hidden affine binding;
#   9. scalar V_L -> Cons_R -> Inv_C -> V_G execution audits;
#  10. Wilson 95% intervals for Monte Carlo rates;
#  11. logarithmically stable analytical references;
#  12. CSV and JSON run artifacts.
#
# EXPERIMENTAL DESIGN:
#   - Q and k remain fixed throughout the sensitivity experiment.
#   - Only m changes across fragmentation points.
#   - The malicious coalition size is an integer r.
#   - The displayed adversarial fraction is always q_actual = r / Q.
#   - Coalition placement and injective assignment are resampled implicitly at
#     every trajectory by exact hypergeometric sampling.
#
# EXECUTED STOCHASTIC MODEL:
#
#       X ~ Hypergeometric(Q, r, m)
#
# where X is the number of critical fragments directly assigned to colluding
# verifiers. Given X:
#
#       I | X ~ Binomial(m-X, 2^(-h_min_bits))
#
# Reconstruction succeeds exactly when:
#
#       X + I = m.
#
# SUFFICIENT-STATISTIC SAMPLING:
# The program does not create a full Q-element permutation for every trajectory.
# It samples X directly from the exact injective hypergeometric law using
# cryptographically random integer tickets and exact combinatorial weights.
# This preserves the relevant distribution while avoiding an otherwise
# prohibitive engineering cost.
#
# STRUCTURAL EXECUTION AUDIT:
# A configurable subset of trajectories at every (r,m) point is materialized as
# 256-bit candidate states and executed through:
#
#       V_L -> Cons_R -> Inv_C -> V_G.
#
# The program aborts if structural execution disagrees with the sampled
# reconstruction event.
#
# C_int DISCLOSURE CONTROL:
# The pedagogical affine tags are reversible after full C_int disclosure.
# Disclosure therefore reconstructs authentic critical values. It does not
# automatically authorize arbitrary false states: a post-disclosure mutation
# must still be vetoed.
#
# PERFORMANCE NOTE:
# The default remains 100,000 trajectories per point. Because each trajectory
# uses cryptographic randomness and exact large-integer sampling, a smaller
# --iterations value is appropriate for interactive review.
# ==============================================================================


# ==============================================================================
# 256-BIT FINITE FIELD
# ==============================================================================

# secp256k1 field prime:
#     p = 2^256 - 2^32 - 977
#
# It is used only as a standard 256-bit prime modulus. This program does not
# implement elliptic-curve cryptography.
FIELD_PRIME = (
    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
)

SYSTEM_RANDOM = SystemRandom()


# ==============================================================================
# DEFAULT PARAMETERS
# ==============================================================================

Q_VERIFIERS = 2500
TERMINAL_FRAGMENTS = 2048

DEFAULT_ITERATIONS_PER_POINT = 100_000
DEFAULT_AUDIT_TRAJECTORIES = 16

H_MIN_BITS = 1

DEFAULT_Q_LEVELS = [
    0.00,
    0.33,
    0.45,
    0.50,
    0.60,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90,
    0.95,
    0.97,
    0.98,
    0.99,
    1.00,
]

DEFAULT_M_VALUES = [
    1,
    2,
    3,
    5,
    8,
    12,
    16,
    24,
    32,
    48,
    64,
    96,
    128,
    256,
    512,
    1024,
]

SCRIPT_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = (
    SCRIPT_DIR
    / "test_13_outputs"
)

FIGURE_DIR = (
    SCRIPT_DIR
    / "test_13_figures"
)


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass(frozen=True)
class CNVSState256:
    k: int
    m: int

    true_values: Tuple[int, ...]
    critical_indices: Tuple[int, ...]

    # Full-state hidden affine binding.
    tag_a: Tuple[int, ...]
    tag_b: Tuple[int, ...]
    tags: Tuple[int, ...]

    # Auxiliary pairwise critical relations.
    pair_constraints: Tuple[
        Tuple[int, int, int, int],
        ...
    ]

    state_nonce: str


@dataclass(frozen=True)
class VGReport:
    accepted: bool
    local_layer_ok: bool
    relational_consistency_ok: bool
    invariant_binding_ok: bool


@dataclass(frozen=True)
class SecureHypergeometricSampler:
    """
    Exact integer-weight sampler for:
        X ~ Hypergeometric(Q, r, m).
    """
    support: Tuple[int, ...]
    cumulative_weights: Tuple[int, ...]
    total_weight: int

    def sample(self) -> int:
        ticket = secrets.randbelow(
            self.total_weight
        )

        index = bisect.bisect_right(
            self.cumulative_weights,
            ticket,
        )

        return self.support[
            index
        ]


@dataclass(frozen=True)
class SimulationResult:
    nominal_q: float
    actual_q: float

    Q: int
    r: int
    k: int
    m: int

    h_min_bits: int
    p_inf: float
    iterations: int
    structurally_audited_trajectories: int

    reconstruction_success_count: int
    reconstruction_accept_rate: float
    reconstruction_ci_low: float
    reconstruction_ci_high: float

    global_veto_rate: float
    local_pass_global_veto_rate: float

    exact_injective_reference: float
    exact_injective_log10: float

    independent_upper_reference: float
    independent_upper_log10: float

    avg_direct_critical: float
    avg_inferred_critical: float
    avg_failed_critical: float

    cint_disclosure_reconstructs_truth: bool
    cint_disclosure_reconstruction_accepts: bool
    cint_disclosure_false_state_accepts: bool

    full_state_mutation_rejected: bool


# ==============================================================================
# VALIDATION HELPERS
# ==============================================================================

def validate_probability(
    name: str,
    value: float,
) -> float:
    value = float(
        value
    )

    if (
        not math.isfinite(
            value
        )
        or value < 0.0
        or value > 1.0
    ):
        raise ValueError(
            f"{name} must lie in [0,1]."
        )

    return value


def validate_positive_integer(
    name: str,
    value: int,
) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(
            f"{name} must be a positive integer."
        )

    return value


# ==============================================================================
# CSPRNG HELPERS
# ==============================================================================

def rand_field_element() -> int:
    return secrets.randbelow(
        FIELD_PRIME
    )


def rand_nonzero_field_element() -> int:
    return (
        secrets.randbelow(
            FIELD_PRIME - 1
        )
        + 1
    )


def secure_sample_without_replacement(
    population_size: int,
    sample_size: int,
) -> List[int]:
    """
    CSPRNG-based sampling without replacement.

    SystemRandom.sample uses the operating system randomness source.
    """
    if not 0 <= sample_size <= population_size:
        raise ValueError(
            "sample_size must satisfy "
            "0 <= sample_size <= population_size."
        )

    return SYSTEM_RANDOM.sample(
        range(
            population_size
        ),
        sample_size,
    )


def secure_binomial_power_of_two(
    trials: int,
    h_min_bits: int,
) -> int:
    """
    Exact Binomial(trials, 2^(-h_min_bits)) sampling.

    h=1 is optimized by counting zero bits in one CSPRNG bit string.
    The general branch retains exact Bernoulli sampling.
    """
    if trials < 0:
        raise ValueError(
            "trials cannot be negative."
        )

    if type(h_min_bits) is not int or h_min_bits < 0:
        raise ValueError(
            "h_min_bits must be a non-negative integer."
        )

    if trials == 0:
        return 0

    if h_min_bits == 0:
        return trials

    if h_min_bits == 1:
        random_bits = secrets.randbits(
            trials
        )

        return (
            trials
            - random_bits.bit_count()
        )

    successes = 0

    for _ in range(
        trials
    ):
        if secrets.randbits(
            h_min_bits
        ) == 0:
            successes += 1

    return successes


# ==============================================================================
# FINITE-FIELD HELPERS
# ==============================================================================

def inv_mod(
    value: int,
    modulus: int = FIELD_PRIME,
) -> int:
    value = int(
        value
    ) % modulus

    if value == 0:
        raise ValueError(
            "Zero has no multiplicative inverse."
        )

    return pow(
        value,
        -1,
        modulus,
    )


def p_inf_from_h_bits(
    h_min_bits: int,
) -> float:
    if type(h_min_bits) is not int or h_min_bits < 0:
        raise ValueError(
            "h_min_bits must be a non-negative integer."
        )

    return math.ldexp(
        1.0,
        -h_min_bits,
    )


def wrong_field_value(
    true_value: int,
) -> int:
    delta = (
        secrets.randbelow(
            FIELD_PRIME - 1
        )
        + 1
    )

    return (
        int(
            true_value
        )
        + delta
    ) % FIELD_PRIME


# ==============================================================================
# LOGARITHMIC ANALYTICAL REFERENCES
# ==============================================================================

def log_combination(
    n: int,
    k: int,
) -> float:
    if k < 0 or k > n:
        return float(
            "-inf"
        )

    return (
        math.lgamma(
            n + 1
        )
        - math.lgamma(
            k + 1
        )
        - math.lgamma(
            n - k + 1
        )
    )


def logsumexp(
    values: Sequence[float],
) -> float:
    finite_values = [
        value
        for value in values
        if math.isfinite(
            value
        )
    ]

    if not finite_values:
        return float(
            "-inf"
        )

    maximum = max(
        finite_values
    )

    return (
        maximum
        + math.log(
            sum(
                math.exp(
                    value - maximum
                )
                for value in finite_values
            )
        )
    )


def log_exact_injective_reference(
    Q: int,
    r: int,
    m: int,
    p_inf: float,
) -> float:
    """
    Natural logarithm of:
        sum_x Hypergeom(Q,r,m;x) p_inf^(m-x).
    """
    validate_probability(
        "p_inf",
        p_inf,
    )

    minimum_direct = max(
        0,
        m - (
            Q - r
        ),
    )

    maximum_direct = min(
        m,
        r,
    )

    denominator_log = log_combination(
        Q,
        m,
    )

    terms: List[float] = []

    for direct_count in range(
        minimum_direct,
        maximum_direct + 1,
    ):
        missing_count = (
            m
            - direct_count
        )

        if (
            p_inf == 0.0
            and missing_count > 0
        ):
            continue

        inference_log = (
            0.0
            if missing_count == 0
            else missing_count
            * math.log(
                p_inf
            )
        )

        terms.append(
            log_combination(
                r,
                direct_count,
            )
            + log_combination(
                Q - r,
                missing_count,
            )
            - denominator_log
            + inference_log
        )

    return logsumexp(
        terms
    )


def log_independent_upper_reference(
    actual_q: float,
    m: int,
    p_inf: float,
) -> float:
    actual_q = validate_probability(
        "actual_q",
        actual_q,
    )

    p_inf = validate_probability(
        "p_inf",
        p_inf,
    )

    p_comp = (
        actual_q
        + (
            1.0 - actual_q
        )
        * p_inf
    )

    if p_comp == 0.0:
        return float(
            "-inf"
        )

    return (
        m
        * math.log(
            p_comp
        )
    )


def probability_from_log(
    log_probability: float,
) -> float:
    if not math.isfinite(
        log_probability
    ):
        return 0.0

    if log_probability < -745.0:
        return 0.0

    return math.exp(
        log_probability
    )


def log10_from_log(
    log_probability: float,
) -> float:
    if not math.isfinite(
        log_probability
    ):
        return float(
            "-inf"
        )

    return (
        log_probability
        / math.log(
            10.0
        )
    )


# ==============================================================================
# EXACT HYPERGEOMETRIC CSPRNG SAMPLER
# ==============================================================================

def build_secure_hypergeometric_sampler(
    Q: int,
    r: int,
    m: int,
) -> SecureHypergeometricSampler:
    """
    Build exact integer weights:
        w_x = C(r,x) C(Q-r,m-x).

    Vandermonde's identity guarantees:
        sum_x w_x = C(Q,m).
    """
    if not 0 <= r <= Q:
        raise ValueError(
            "r must satisfy 0 <= r <= Q."
        )

    if not 0 <= m <= Q:
        raise ValueError(
            "m must satisfy 0 <= m <= Q."
        )

    minimum_direct = max(
        0,
        m - (
            Q - r
        ),
    )

    maximum_direct = min(
        m,
        r,
    )

    support: List[int] = []
    cumulative_weights: List[int] = []

    running_total = 0

    for direct_count in range(
        minimum_direct,
        maximum_direct + 1,
    ):
        weight = (
            math.comb(
                r,
                direct_count,
            )
            * math.comb(
                Q - r,
                m - direct_count,
            )
        )

        if weight <= 0:
            continue

        support.append(
            direct_count
        )

        running_total += weight

        cumulative_weights.append(
            running_total
        )

    expected_total = math.comb(
        Q,
        m,
    )

    if running_total != expected_total:
        raise AssertionError(
            "Hypergeometric integer weights violated "
            "Vandermonde's identity."
        )

    return SecureHypergeometricSampler(
        support=tuple(
            support
        ),
        cumulative_weights=tuple(
            cumulative_weights
        ),
        total_weight=running_total,
    )


# ==============================================================================
# CONFIDENCE INTERVAL
# ==============================================================================

def wilson_interval(
    successes: int,
    trials: int,
    z: float = 1.959963984540054,
) -> Tuple[float, float]:
    validate_positive_integer(
        "trials",
        trials,
    )

    if not 0 <= successes <= trials:
        raise ValueError(
            "successes must satisfy 0 <= successes <= trials."
        )

    estimate = (
        successes
        / trials
    )

    z_squared = (
        z * z
    )

    denominator = (
        1.0
        + z_squared
        / trials
    )

    centre = (
        estimate
        + z_squared
        / (
            2.0
            * trials
        )
    ) / denominator

    half_width = (
        z
        * math.sqrt(
            estimate
            * (
                1.0 - estimate
            )
            / trials
            + z_squared
            / (
                4.0
                * trials
                * trials
            )
        )
        / denominator
    )

    return (
        max(
            0.0,
            centre
            - half_width,
        ),
        min(
            1.0,
            centre
            + half_width,
        ),
    )


# ==============================================================================
# CNVS-LIKE FULL-STATE CONSTRUCTION
# ==============================================================================

def build_state_256(
    k: int,
    m: int,
) -> CNVSState256:
    """
    Build one 256-bit toy state.

    Every terminal fragment receives a hidden affine tag:
        tag_i = a_i x_i + b_i mod p,
    with a_i != 0.

    Therefore the implemented hidden binding covers the complete state, not only
    the m reconstruction-critical fragments.
    """
    validate_positive_integer(
        "k",
        k,
    )

    validate_positive_integer(
        "m",
        m,
    )

    if m > k:
        raise ValueError(
            "m cannot exceed k."
        )

    true_values = tuple(
        rand_field_element()
        for _ in range(
            k
        )
    )

    critical_indices = tuple(
        sorted(
            secure_sample_without_replacement(
                k,
                m,
            )
        )
    )

    tag_a = tuple(
        rand_nonzero_field_element()
        for _ in range(
            k
        )
    )

    tag_b = tuple(
        rand_field_element()
        for _ in range(
            k
        )
    )

    tags = tuple(
        (
            tag_a[index]
            * true_values[index]
            + tag_b[index]
        ) % FIELD_PRIME
        for index in range(
            k
        )
    )

    pair_constraints: List[
        Tuple[
            int,
            int,
            int,
            int,
        ]
    ] = []

    for left, right in zip(
        critical_indices[:-1],
        critical_indices[1:],
    ):
        coefficient = rand_nonzero_field_element()

        target = (
            true_values[left]
            + coefficient
            * true_values[right]
            + true_values[left]
            * true_values[right]
        ) % FIELD_PRIME

        pair_constraints.append(
            (
                left,
                right,
                coefficient,
                target,
            )
        )

    state = CNVSState256(
        k=k,
        m=m,
        true_values=true_values,
        critical_indices=critical_indices,
        tag_a=tag_a,
        tag_b=tag_b,
        tags=tags,
        pair_constraints=tuple(
            pair_constraints
        ),
        state_nonce=secrets.token_hex(
            16
        ),
    )

    if not V_G(
        state,
        state.true_values,
    ).accepted:
        raise RuntimeError(
            "Fresh honest 256-bit state failed its own validation pipeline."
        )

    return state


# ==============================================================================
# V_L, Cons_R, Inv_C, V_G
# ==============================================================================

def V_L(
    values: Sequence[int],
) -> List[bool]:
    """
    Local field-domain admissibility only.

    Exact type equality rejects bool, which is a subclass of int in Python.
    """
    return [
        (
            type(value) is int
            and 0 <= value < FIELD_PRIME
        )
        for value in values
    ]


def Cons_R(
    state: CNVSState256,
    values: Sequence[int],
    local_ok: Sequence[bool],
) -> bool:
    """
    Exact terminal-vector completeness proxy.

    This is not presented as a complete implementation of formal R_int.
    """
    return (
        len(
            values
        )
        == state.k
        and len(
            local_ok
        )
        == state.k
        and all(
            local_ok
        )
    )


def Inv_C(
    state: CNVSState256,
    values: Sequence[int],
) -> bool:
    """
    Full-state hidden affine binding plus critical pair constraints.
    """
    for index in range(
        state.k
    ):
        if (
            state.tag_a[index]
            * int(
                values[index]
            )
            + state.tag_b[index]
        ) % FIELD_PRIME != state.tags[index]:
            return False

    for (
        left,
        right,
        coefficient,
        target,
    ) in state.pair_constraints:
        if (
            int(
                values[left]
            )
            + coefficient
            * int(
                values[right]
            )
            + int(
                values[left]
            )
            * int(
                values[right]
            )
        ) % FIELD_PRIME != target:
            return False

    return True


def V_G(
    state: CNVSState256,
    values: Sequence[int],
) -> VGReport:
    local_ok = V_L(
        values
    )

    local_layer_ok = (
        len(
            values
        )
        == state.k
        and len(
            local_ok
        )
        == state.k
        and all(
            local_ok
        )
    )

    if not local_layer_ok:
        return VGReport(
            accepted=False,
            local_layer_ok=False,
            relational_consistency_ok=False,
            invariant_binding_ok=False,
        )

    relational_ok = Cons_R(
        state,
        values,
        local_ok,
    )

    if not relational_ok:
        return VGReport(
            accepted=False,
            local_layer_ok=True,
            relational_consistency_ok=False,
            invariant_binding_ok=False,
        )

    invariant_ok = Inv_C(
        state,
        values,
    )

    if not invariant_ok:
        return VGReport(
            accepted=False,
            local_layer_ok=True,
            relational_consistency_ok=True,
            invariant_binding_ok=False,
        )

    return VGReport(
        accepted=True,
        local_layer_ok=True,
        relational_consistency_ok=True,
        invariant_binding_ok=True,
    )


# ==============================================================================
# STRUCTURAL MATERIALIZATION AND AUDIT
# ==============================================================================

def materialize_candidate(
    state: CNVSState256,
    failed_critical_count: int,
) -> List[int]:
    if not 0 <= failed_critical_count <= state.m:
        raise ValueError(
            "failed_critical_count must lie in [0,m]."
        )

    candidate = list(
        state.true_values
    )

    if failed_critical_count == 0:
        return candidate

    failed_indices = secure_sample_without_replacement(
        state.m,
        failed_critical_count,
    )

    for critical_position in failed_indices:
        state_index = state.critical_indices[
            critical_position
        ]

        candidate[
            state_index
        ] = wrong_field_value(
            candidate[
                state_index
            ]
        )

    return candidate


def audit_structural_equivalence(
    state: CNVSState256,
    sampled_failed_counts: Sequence[int],
    audit_trajectories: int,
) -> int:
    if audit_trajectories < 0:
        raise ValueError(
            "audit_trajectories cannot be negative."
        )

    if audit_trajectories == 0:
        return 0

    audit_count = min(
        audit_trajectories,
        len(
            sampled_failed_counts
        ),
    )

    audit_positions = secure_sample_without_replacement(
        len(
            sampled_failed_counts
        ),
        audit_count,
    )

    for position in audit_positions:
        failed_count = int(
            sampled_failed_counts[
                position
            ]
        )

        candidate = materialize_candidate(
            state,
            failed_count,
        )

        report = V_G(
            state,
            candidate,
        )

        expected_acceptance = (
            failed_count == 0
        )

        if report.accepted is not expected_acceptance:
            raise AssertionError(
                "Scalar 256-bit V_G execution disagreed with the "
                "sampled reconstruction event."
            )

        if failed_count > 0:
            if not (
                report.local_layer_ok
                and report.relational_consistency_ok
                and not report.invariant_binding_ok
            ):
                raise AssertionError(
                    "Wrong but locally admissible critical evidence did not "
                    "follow the expected Local-Pass / Global-Veto path."
                )

    return audit_count


# ==============================================================================
# C_int DISCLOSURE AND FULL-STATE CONTROLS
# ==============================================================================

def solve_from_cint_disclosure(
    state: CNVSState256,
    index: int,
) -> int:
    return (
        (
            state.tags[index]
            - state.tag_b[index]
        )
        * inv_mod(
            state.tag_a[index]
        )
    ) % FIELD_PRIME


def execute_cint_disclosure_controls(
    state: CNVSState256,
) -> Dict[str, bool]:
    """
    Distinguish reconstruction/secrecy collapse from false-state acceptance.
    """
    reconstructed = list(
        state.true_values
    )

    for index in state.critical_indices:
        reconstructed[
            index
        ] = solve_from_cint_disclosure(
            state,
            index,
        )

    reconstructs_truth = all(
        reconstructed[index]
        == state.true_values[index]
        for index in state.critical_indices
    )

    reconstruction_accepts = V_G(
        state,
        reconstructed,
    ).accepted

    false_candidate = list(
        reconstructed
    )

    mutation_index = state.critical_indices[
        0
    ]

    false_candidate[
        mutation_index
    ] = wrong_field_value(
        false_candidate[
            mutation_index
        ]
    )

    false_state_accepts = V_G(
        state,
        false_candidate,
    ).accepted

    if not reconstructs_truth:
        raise AssertionError(
            "Full C_int disclosure failed to reconstruct authentic "
            "critical values."
        )

    if not reconstruction_accepts:
        raise AssertionError(
            "Authentic reconstructed state failed V_G."
        )

    if false_state_accepts:
        raise AssertionError(
            "A false post-disclosure state was accepted."
        )

    return {
        "reconstructs_truth": reconstructs_truth,
        "reconstruction_accepts": reconstruction_accepts,
        "false_state_accepts": false_state_accepts,
    }


def execute_full_state_coverage_control(
    state: CNVSState256,
) -> bool:
    """
    Mutate a non-critical value whenever one exists. The full-state hidden
    binding must veto it.
    """
    critical_set = set(
        state.critical_indices
    )

    mutation_index = next(
        (
            index
            for index in range(
                state.k
            )
            if index not in critical_set
        ),
        state.critical_indices[
            0
        ],
    )

    candidate = list(
        state.true_values
    )

    candidate[
        mutation_index
    ] = wrong_field_value(
        candidate[
            mutation_index
        ]
    )

    rejected = not V_G(
        state,
        candidate,
    ).accepted

    if not rejected:
        raise AssertionError(
            "A terminal mutation escaped the full-state invariant binding."
        )

    return rejected


# ==============================================================================
# MONTE CARLO SIMULATION
# ==============================================================================

def simulate_one_m_256(
    Q: int,
    nominal_q: float,
    m: int,
    h_min_bits: int,
    iterations: int,
    audit_trajectories: int,
) -> SimulationResult:
    validate_positive_integer(
        "Q",
        Q,
    )

    nominal_q = validate_probability(
        "nominal_q",
        nominal_q,
    )

    validate_positive_integer(
        "m",
        m,
    )

    validate_positive_integer(
        "iterations",
        iterations,
    )

    if type(h_min_bits) is not int or h_min_bits < 0:
        raise ValueError(
            "h_min_bits must be a non-negative integer."
        )

    if TERMINAL_FRAGMENTS > Q:
        raise ValueError(
            "Injective assignment requires TERMINAL_FRAGMENTS <= Q."
        )

    if m > TERMINAL_FRAGMENTS:
        raise ValueError(
            "m cannot exceed TERMINAL_FRAGMENTS."
        )

    r = max(
        0,
        min(
            Q,
            round(
                nominal_q
                * Q
            ),
        ),
    )

    actual_q = (
        r
        / Q
    )

    p_inf = p_inf_from_h_bits(
        h_min_bits
    )

    state = build_state_256(
        TERMINAL_FRAGMENTS,
        m,
    )

    sampler = build_secure_hypergeometric_sampler(
        Q,
        r,
        m,
    )

    reconstruction_success_count = 0

    direct_total = 0
    inferred_total = 0
    failed_total = 0

    sampled_failed_counts: List[int] = []

    for _ in range(
        iterations
    ):
        direct_count = sampler.sample()

        missing_count = (
            m
            - direct_count
        )

        inferred_count = secure_binomial_power_of_two(
            missing_count,
            h_min_bits,
        )

        failed_count = (
            missing_count
            - inferred_count
        )

        direct_total += direct_count
        inferred_total += inferred_count
        failed_total += failed_count

        sampled_failed_counts.append(
            failed_count
        )

        if failed_count == 0:
            reconstruction_success_count += 1

    veto_count = (
        iterations
        - reconstruction_success_count
    )

    ci_low, ci_high = wilson_interval(
        reconstruction_success_count,
        iterations,
    )

    audited = audit_structural_equivalence(
        state=state,
        sampled_failed_counts=sampled_failed_counts,
        audit_trajectories=audit_trajectories,
    )

    disclosure_controls = execute_cint_disclosure_controls(
        state
    )

    full_state_mutation_rejected = execute_full_state_coverage_control(
        state
    )

    exact_log = log_exact_injective_reference(
        Q=Q,
        r=r,
        m=m,
        p_inf=p_inf,
    )

    upper_log = log_independent_upper_reference(
        actual_q=actual_q,
        m=m,
        p_inf=p_inf,
    )

    if exact_log > upper_log + 1e-10:
        raise AssertionError(
            "Exact injective reconstruction probability exceeded the "
            "independent upper reference."
        )

    return SimulationResult(
        nominal_q=nominal_q,
        actual_q=actual_q,
        Q=Q,
        r=r,
        k=TERMINAL_FRAGMENTS,
        m=m,
        h_min_bits=h_min_bits,
        p_inf=p_inf,
        iterations=iterations,
        structurally_audited_trajectories=audited,
        reconstruction_success_count=reconstruction_success_count,
        reconstruction_accept_rate=(
            reconstruction_success_count
            / iterations
        ),
        reconstruction_ci_low=ci_low,
        reconstruction_ci_high=ci_high,
        global_veto_rate=(
            veto_count
            / iterations
        ),
        local_pass_global_veto_rate=(
            veto_count
            / iterations
        ),
        exact_injective_reference=probability_from_log(
            exact_log
        ),
        exact_injective_log10=log10_from_log(
            exact_log
        ),
        independent_upper_reference=probability_from_log(
            upper_log
        ),
        independent_upper_log10=log10_from_log(
            upper_log
        ),
        avg_direct_critical=(
            direct_total
            / iterations
        ),
        avg_inferred_critical=(
            inferred_total
            / iterations
        ),
        avg_failed_critical=(
            failed_total
            / iterations
        ),
        cint_disclosure_reconstructs_truth=disclosure_controls[
            "reconstructs_truth"
        ],
        cint_disclosure_reconstruction_accepts=disclosure_controls[
            "reconstruction_accepts"
        ],
        cint_disclosure_false_state_accepts=disclosure_controls[
            "false_state_accepts"
        ],
        full_state_mutation_rejected=full_state_mutation_rejected,
    )


# ==============================================================================
# RESULT SERIALIZATION
# ==============================================================================

def write_results_csv(
    results: Mapping[
        float,
        Sequence[
            SimulationResult
        ],
    ],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = list(
        SimulationResult.__dataclass_fields__.keys()
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for rows in results.values():
            for row in rows:
                writer.writerow(
                    asdict(
                        row
                    )
                )


def write_run_metadata(
    run_id: str,
    results: Mapping[
        float,
        Sequence[
            SimulationResult
        ],
    ],
    elapsed_seconds: float,
    output_path: Path,
) -> None:
    metadata = {
        "run_id": run_id,
        "field_prime_bits": FIELD_PRIME.bit_length(),
        "Q_verifiers": Q_VERIFIERS,
        "terminal_fragments": TERMINAL_FRAGMENTS,
        "h_min_bits": H_MIN_BITS,
        "elapsed_seconds": elapsed_seconds,
        "randomness": (
            "Operating-system CSPRNG through secrets/SystemRandom; "
            "no deterministic seed."
        ),
        "actual_q_values": [
            actual_q
            for actual_q in results.keys()
        ],
        "m_values": [
            row.m
            for row in next(
                iter(
                    results.values()
                )
            )
        ] if results else [],
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            metadata,
            handle,
            indent=2,
            ensure_ascii=False,
        )


# ==============================================================================
# PLOTTING
# ==============================================================================

def nearest_available_q(
    results: Mapping[
        float,
        Sequence[
            SimulationResult
        ],
    ],
    target_q: float,
) -> float:
    return min(
        results.keys(),
        key=lambda actual_q: abs(
            actual_q
            - target_q
        ),
    )


def plot_probability_from_log10(
    log10_value: float,
    detection_floor: float,
) -> float:
    floor_log10 = math.log10(
        detection_floor
    )

    if not math.isfinite(
        log10_value
    ):
        return detection_floor

    return 10.0 ** max(
        log10_value,
        floor_log10,
    )


def plot_results(
    results: Mapping[
        float,
        Sequence[
            SimulationResult
        ],
    ],
    iterations: int,
    *,
    show_plots: bool = True,
) -> None:
    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    detection_floor = (
        1.0
        / max(
            1,
            iterations,
        )
    )

    selected_targets = [
        0.50,
        0.70,
        0.90,
        0.99,
        1.00,
    ]

    selected_actual_q: List[float] = []

    for target in selected_targets:
        actual_q = nearest_available_q(
            results,
            target,
        )

        if actual_q not in selected_actual_q:
            selected_actual_q.append(
                actual_q
            )

    # --------------------------------------------------------------------------
    # Plot 1: selected q reconstruction curves.
    # --------------------------------------------------------------------------
    plt.figure(
        figsize=(13, 8)
    )

    for actual_q in selected_actual_q:
        rows = results[
            actual_q
        ]

        m_axis = [
            row.m
            for row in rows
        ]

        empirical = [
            max(
                row.reconstruction_accept_rate,
                detection_floor,
            )
            for row in rows
        ]

        exact_reference = [
            plot_probability_from_log10(
                row.exact_injective_log10,
                detection_floor,
            )
            for row in rows
        ]

        upper_reference = [
            plot_probability_from_log10(
                row.independent_upper_log10,
                detection_floor,
            )
            for row in rows
        ]

        plt.plot(
            m_axis,
            empirical,
            marker="o",
            label=(
                f"CSPRNG reconstruction, q={actual_q:.4f}"
            ),
        )

        plt.plot(
            m_axis,
            exact_reference,
            linestyle="--",
            label=(
                f"Exact injective reference, q={actual_q:.4f}"
            ),
        )

        plt.plot(
            m_axis,
            upper_reference,
            linestyle=":",
            label=(
                f"Independent upper reference, q={actual_q:.4f}"
            ),
        )

    plt.xscale(
        "log",
        base=2,
    )

    plt.yscale(
        "log"
    )

    plt.xlabel(
        "Critical fragmentation cardinality m"
    )

    plt.ylabel(
        "Complete critical reconstruction probability "
        f"(zero observations plotted at 1/{iterations})"
    )

    plt.title(
        "CNVS Test 13: 256-bit CSPRNG Fragmentation Sensitivity"
    )

    plt.grid(
        True,
        which="both",
        linestyle="--",
        linewidth=0.5,
        alpha=0.65,
    )

    plt.legend(
        fontsize=8,
        ncol=2,
    )

    plt.tight_layout()

    output_1 = (
        FIGURE_DIR
        / "test_13_256bit_reconstruction_vs_references.png"
    )

    plt.savefig(
        output_1,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 2: all Monte Carlo points versus references.
    # --------------------------------------------------------------------------
    empirical_all: List[float] = []
    exact_all: List[float] = []
    upper_all: List[float] = []

    for rows in results.values():
        for row in rows:
            empirical_all.append(
                max(
                    row.reconstruction_accept_rate,
                    detection_floor,
                )
            )

            exact_all.append(
                plot_probability_from_log10(
                    row.exact_injective_log10,
                    detection_floor,
                )
            )

            upper_all.append(
                plot_probability_from_log10(
                    row.independent_upper_log10,
                    detection_floor,
                )
            )

    plt.figure(
        figsize=(9, 9)
    )

    plt.scatter(
        exact_all,
        empirical_all,
        marker="o",
        label=(
            "CSPRNG Monte Carlo versus exact injective reference"
        ),
    )

    plt.scatter(
        upper_all,
        empirical_all,
        marker="^",
        label=(
            "CSPRNG Monte Carlo versus independent upper reference"
        ),
    )

    plt.plot(
        [
            detection_floor,
            1.0,
        ],
        [
            detection_floor,
            1.0,
        ],
        linestyle="--",
        label="y = x",
    )

    plt.xscale(
        "log"
    )

    plt.yscale(
        "log"
    )

    plt.xlabel(
        "Reference probability"
    )

    plt.ylabel(
        "Observed complete-reconstruction rate"
    )

    plt.title(
        "CNVS Test 13: CSPRNG Reconstruction vs References"
    )

    plt.grid(
        True,
        which="both",
        linestyle="--",
        linewidth=0.5,
        alpha=0.65,
    )

    plt.legend()
    plt.tight_layout()

    output_2 = (
        FIGURE_DIR
        / "test_13_256bit_empirical_vs_references.png"
    )

    plt.savefig(
        output_2,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 3: local-pass / Global-Veto heatmap.
    # --------------------------------------------------------------------------
    actual_q_values = list(
        results.keys()
    )

    m_values = [
        row.m
        for row in next(
            iter(
                results.values()
            )
        )
    ]

    heatmap = [
        [
            row.local_pass_global_veto_rate
            for row in results[
                actual_q
            ]
        ]
        for actual_q in actual_q_values
    ]

    plt.figure(
        figsize=(13, 8)
    )

    image = plt.imshow(
        heatmap,
        aspect="auto",
        origin="lower",
    )

    plt.colorbar(
        image,
        label=(
            "Locally admissible candidate vetoed by hidden binding"
        ),
    )

    plt.xticks(
        ticks=list(
            range(
                len(
                    m_values
                )
            )
        ),
        labels=[
            str(
                value
            )
            for value in m_values
        ],
        rotation=45,
        ha="right",
    )

    plt.yticks(
        ticks=list(
            range(
                len(
                    actual_q_values
                )
            )
        ),
        labels=[
            f"{value:.4f}"
            for value in actual_q_values
        ],
    )

    plt.xlabel(
        "Critical fragmentation cardinality m"
    )

    plt.ylabel(
        "Actual colluding fraction r/Q"
    )

    plt.title(
        "CNVS Test 13: 256-bit Local-Pass / Global-Veto Sensitivity"
    )

    plt.tight_layout()

    output_3 = (
        FIGURE_DIR
        / "test_13_256bit_local_pass_global_veto_heatmap.png"
    )

    plt.savefig(
        output_3,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 4: maximum m versus actual q.
    # --------------------------------------------------------------------------
    maximum_m = max(
        m_values
    )

    q_axis: List[float] = []
    empirical_final: List[float] = []
    exact_final: List[float] = []
    upper_final: List[float] = []

    for actual_q, rows in results.items():
        row = next(
            item
            for item in rows
            if item.m == maximum_m
        )

        q_axis.append(
            actual_q
        )

        empirical_final.append(
            max(
                row.reconstruction_accept_rate,
                detection_floor,
            )
        )

        exact_final.append(
            plot_probability_from_log10(
                row.exact_injective_log10,
                detection_floor,
            )
        )

        upper_final.append(
            plot_probability_from_log10(
                row.independent_upper_log10,
                detection_floor,
            )
        )

    plt.figure(
        figsize=(12, 7)
    )

    plt.semilogy(
        q_axis,
        empirical_final,
        marker="o",
        label=(
            f"CSPRNG reconstruction at m={maximum_m}"
        ),
    )

    plt.semilogy(
        q_axis,
        exact_final,
        linestyle="--",
        marker="s",
        label=(
            f"Exact injective reference at m={maximum_m}"
        ),
    )

    plt.semilogy(
        q_axis,
        upper_final,
        linestyle=":",
        marker="^",
        label=(
            f"Independent upper reference at m={maximum_m}"
        ),
    )

    plt.xlabel(
        "Actual colluding verifier fraction r/Q"
    )

    plt.ylabel(
        "Probability "
        f"(zero observations plotted at 1/{iterations})"
    )

    plt.title(
        f"CNVS Test 13: Maximum Fragmentation m={maximum_m}"
    )

    plt.grid(
        True,
        which="both",
        linestyle="--",
        linewidth=0.5,
        alpha=0.65,
    )

    plt.legend()
    plt.tight_layout()

    output_4 = (
        FIGURE_DIR
        / "test_13_256bit_max_fragmentation_vs_actual_q.png"
    )

    plt.savefig(
        output_4,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()

    print(
        "\n[Plot Output]"
    )

    for output in (
        output_1,
        output_2,
        output_3,
        output_4,
    ):
        print(
            "Saved:",
            output,
        )

    print(
        "Absolute folder:",
        FIGURE_DIR.resolve(),
    )


# ==============================================================================
# CONFIGURATION HELPERS
# ==============================================================================

def coalition_sizes_from_levels(
    Q: int,
    q_levels: Iterable[float],
) -> List[
    Tuple[
        float,
        int,
    ]
]:
    """
    Convert nominal fractions to unique integer coalition sizes.

    The first nominal level producing a size is retained for reporting.
    """
    by_size: Dict[
        int,
        float,
    ] = {}

    for level in q_levels:
        nominal_q = validate_probability(
            "q level",
            level,
        )

        coalition_size = max(
            0,
            min(
                Q,
                round(
                    nominal_q
                    * Q
                ),
            ),
        )

        by_size.setdefault(
            coalition_size,
            nominal_q,
        )

    return [
        (
            by_size[size],
            size,
        )
        for size in sorted(
            by_size
        )
    ]


def validate_m_values(
    values: Iterable[int],
) -> List[int]:
    validated = sorted(
        {
            int(
                value
            )
            for value in values
        }
    )

    if not validated:
        raise ValueError(
            "At least one m value is required."
        )

    for value in validated:
        if not 1 <= value <= TERMINAL_FRAGMENTS:
            raise ValueError(
                "Every m must satisfy "
                f"1 <= m <= {TERMINAL_FRAGMENTS}."
            )

    return validated


# ==============================================================================
# MAIN TEST RUN
# ==============================================================================

def run_test_13(
    *,
    iterations: int = DEFAULT_ITERATIONS_PER_POINT,
    audit_trajectories: int = DEFAULT_AUDIT_TRAJECTORIES,
    q_levels: Sequence[float] = DEFAULT_Q_LEVELS,
    m_values: Sequence[int] = DEFAULT_M_VALUES,
    show_plots: bool = True,
) -> Dict[
    float,
    List[
        SimulationResult
    ],
]:
    validate_positive_integer(
        "iterations",
        iterations,
    )

    if audit_trajectories < 0:
        raise ValueError(
            "audit_trajectories cannot be negative."
        )

    if TERMINAL_FRAGMENTS > Q_VERIFIERS:
        raise RuntimeError(
            "Injective assignment requires TERMINAL_FRAGMENTS <= Q_VERIFIERS."
        )

    run_id = secrets.token_hex(
        16
    )

    started_at = time.time()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    coalition_specs = coalition_sizes_from_levels(
        Q_VERIFIERS,
        q_levels,
    )

    validated_m_values = validate_m_values(
        m_values
    )

    print(
        "\nCNVS Test 13: Engineering-Hardened 256-bit "
        "Fragmentation Sensitivity"
    )

    print(
        "---------------------------------------------------------------"
    )

    print(
        f"run_id = {run_id}"
    )

    print(
        f"field_prime_bits = {FIELD_PRIME.bit_length()}"
    )

    print(
        f"Q_verifiers = {Q_VERIFIERS}"
    )

    print(
        f"terminal_fragments k = {TERMINAL_FRAGMENTS} "
        "(fixed across all m)"
    )

    print(
        f"h_min_bits = {H_MIN_BITS}"
    )

    print(
        f"p_inf = {p_inf_from_h_bits(H_MIN_BITS)} "
        "(worst-case saturated bound)"
    )

    print(
        f"iterations per point = {iterations}"
    )

    print(
        f"structural V_G audits per point = {audit_trajectories}"
    )

    print(
        "randomness = operating-system CSPRNG; no deterministic seed"
    )

    print(
        f"coalition sizes = {[size for _, size in coalition_specs]}"
    )

    print(
        f"m values = {validated_m_values}"
    )

    print(
        "\nMeasured event: complete reconstruction of every critical value, "
        "followed by acceptance of the authentic reconstructed state."
    )

    print(
        "This is not a false-state-acceptance rate.\n"
    )

    results: Dict[
        float,
        List[
            SimulationResult
        ],
    ] = {}

    for nominal_q, coalition_size in coalition_specs:
        actual_q = (
            coalition_size
            / Q_VERIFIERS
        )

        rows: List[
            SimulationResult
        ] = []

        print(
            f"\n=== r={coalition_size}/{Q_VERIFIERS}, "
            f"q_actual={actual_q:.6f} ==="
        )

        print(
            "m | reconstruct | 95% CI | local-pass/veto | "
            "exact log10 | upper log10 | leak reconstructs | false leak state"
        )

        for m in validated_m_values:
            output = simulate_one_m_256(
                Q=Q_VERIFIERS,
                nominal_q=nominal_q,
                m=m,
                h_min_bits=H_MIN_BITS,
                iterations=iterations,
                audit_trajectories=audit_trajectories,
            )

            rows.append(
                output
            )

            print(
                f"{output.m:4d} | "
                f"{output.reconstruction_accept_rate:.8f} | "
                f"[{output.reconstruction_ci_low:.8f}, "
                f"{output.reconstruction_ci_high:.8f}] | "
                f"{output.local_pass_global_veto_rate:.8f} | "
                f"{output.exact_injective_log10:11.3f} | "
                f"{output.independent_upper_log10:11.3f} | "
                f"{output.cint_disclosure_reconstruction_accepts} | "
                f"{output.cint_disclosure_false_state_accepts}"
            )

        results[
            actual_q
        ] = rows

    elapsed_seconds = (
        time.time()
        - started_at
    )

    csv_path = (
        OUTPUT_DIR
        / f"test_13_results_{run_id}.csv"
    )

    metadata_path = (
        OUTPUT_DIR
        / f"test_13_metadata_{run_id}.json"
    )

    write_results_csv(
        results,
        csv_path,
    )

    write_run_metadata(
        run_id=run_id,
        results=results,
        elapsed_seconds=elapsed_seconds,
        output_path=metadata_path,
    )

    plot_results(
        results,
        iterations,
        show_plots=show_plots,
    )

    print(
        "\nCompleted."
    )

    print(
        f"run_id = {run_id}"
    )

    print(
        f"elapsed_seconds = {elapsed_seconds:.2f}"
    )

    print(
        f"results_csv = {csv_path}"
    )

    print(
        f"metadata_json = {metadata_path}"
    )

    print(
        "\n================ FINAL INTERPRETATION ================\n"
    )

    print(
        "- Q and k remain fixed; m is the only fragmentation dimension varied."
    )

    print(
        "- Coalition placement and injective assignment are resampled exactly "
        "through CSPRNG hypergeometric sampling."
    )

    print(
        "- Every terminal fragment is protected by the hidden full-state binding."
    )

    print(
        "- Monte Carlo outcomes measure complete authentic reconstruction, "
        "not arbitrary false-state acceptance."
    )

    print(
        "- A configurable trajectory sample is materially executed through "
        "V_L -> Cons_R -> Inv_C -> V_G."
    )

    print(
        "- Full C_int disclosure reconstructs authentic critical values in this "
        "reversible toy binding, but a deliberate false mutation remains vetoed."
    )

    print(
        "- Exact injective and independent upper references are comparison curves "
        "only and never decide Monte Carlo outcomes."
    )

    print(
        "- Zero observed events retain Wilson 95% intervals and are not treated "
        "as mathematical zero."
    )

    return results


# ==============================================================================
# COMMAND-LINE INTERFACE
# ==============================================================================

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run corrected CNVS Test 13 engineering-hardened "
            "256-bit fragmentation sensitivity."
        )
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS_PER_POINT,
        help=(
            "CSPRNG Monte Carlo trajectories per (q,m) point "
            f"(default: {DEFAULT_ITERATIONS_PER_POINT})."
        ),
    )

    parser.add_argument(
        "--audit-trajectories",
        type=int,
        default=DEFAULT_AUDIT_TRAJECTORIES,
        help=(
            "Materialized scalar V_G audits per point "
            f"(default: {DEFAULT_AUDIT_TRAJECTORIES})."
        ),
    )

    parser.add_argument(
        "--q-levels",
        type=float,
        nargs="*",
        default=None,
        help=(
            "Optional nominal colluding fractions in [0,1]. "
            "They are converted to unique integer coalition sizes."
        ),
    )

    parser.add_argument(
        "--m-values",
        type=int,
        nargs="*",
        default=None,
        help="Optional critical-fragment cardinalities.",
    )

    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Save plots without displaying them.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    run_test_13(
        iterations=arguments.iterations,
        audit_trajectories=arguments.audit_trajectories,
        q_levels=(
            DEFAULT_Q_LEVELS
            if arguments.q_levels is None
            else arguments.q_levels
        ),
        m_values=(
            DEFAULT_M_VALUES
            if arguments.m_values is None
            else arguments.m_values
        ),
        show_plots=not arguments.no_show,
    )


if __name__ == "__main__":
    main()
