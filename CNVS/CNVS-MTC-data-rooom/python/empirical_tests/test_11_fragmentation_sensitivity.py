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

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

import matplotlib.pyplot as plt
import numpy as np


# ==============================================================================
# TEST 11 — EXECUTABLE FRAGMENTATION SENSITIVITY
#
# Test Name: Test 11 - Executable Fragmentation Sensitivity under Hidden Full-State Binding
# filename = "test_11_fragmentation_sensitivity.py"
#
# CLASSIFICATION:
# This program is a reproducible Monte Carlo sensitivity experiment with a
# structurally audited Global-Veto model.
#
# It is NOT:
#   - a formal proof of CNVS;
#   - an empirical validation of a deployed CNVS implementation;
#   - a false-state-acceptance experiment;
#   - a full authentication / networking implementation.
#
# PRIMARY QUESTION:
# How does the probability of reconstructing every critical fragment change as
# the critical fragmentation cardinality m increases?
#
# IMPORTANT SEMANTIC DISTINCTION:
# The ordinary measured event is:
#
#   "the adversary reconstructed every hidden critical value, after which the
#    authentic reconstructed state passed V_G."
#
# It is NOT:
#
#   "V_G accepted a semantically false state."
#
# A separate deterministic false-state control mutates an already reconstructed
# state and verifies that V_G rejects it.
#
# EXECUTION MODEL:
#   1. The complete candidate state contains k terminal fragments.
#   2. Every terminal fragment is protected by a hidden affine finite-field tag,
#      so the implemented invariant family covers the full toy state.
#   3. A hidden subset of m fragments is classified as reconstruction-critical.
#   4. Non-critical values are treated as intact authenticated submissions from
#      the honest aggregation path.
#   5. Critical fragments assigned to the coalition are directly known.
#   6. Every honest-assigned critical fragment is inferred independently with
#      worst-case saturated probability:
#
#          p_inf = 2^(-h_min)
#
#   7. A failed inference produces a wrong but locally admissible field value.
#   8. The statistical experiment samples the exact sufficient statistics of
#      injective assignment:
#
#          X ~ Hypergeometric(Q, r, m)
#
#      followed by:
#
#          I | X ~ Binomial(m-X, p_inf)
#
#   9. Reconstruction succeeds exactly when X + I = m.
#  10. A configurable sample of trajectories is materialized as candidate states
#      and executed through scalar V_L -> Cons_R -> Inv_C -> V_G. The program
#      aborts if structural execution disagrees with the sampled event.
#
# WHY SUFFICIENT-STATISTIC SAMPLING IS USED:
# Generating a complete 2048-element random permutation for every one of
# 100,000 trajectories at every (q,m) point would add large computational cost
# without changing the distribution relevant to this experiment. Hypergeometric
# sampling is the exact distribution induced by injective assignment.
#
# ANALYTICAL REFERENCES:
#   - exact injective reconstruction probability:
#
#       sum_x Hypergeom(Q,r,m;x) * p_inf^(m-x)
#
#   - independent theorem-style upper reference:
#
#       [q_actual + (1-q_actual) p_inf]^m
#
# Neither reference decides an observed Monte Carlo trajectory.
#
# C_int DISCLOSURE CONTROL:
# The hidden affine tags are intentionally reversible in this pedagogical model.
# Full disclosure therefore permits reconstruction of the authentic critical
# values. It does not automatically permit arbitrary false-state acceptance:
# an additional mutation is executed and must be vetoed.
#
# NOTEBOOK COMPATIBILITY:
# Jupyter and Google Colab inject kernel arguments such as '-f kernel.json'.
# They are ignored only during notebook execution; terminal CLI parsing
# remains strict so misspelled Test 11 options still raise an error.
# ==============================================================================


PRIME = 1_000_003


# ==============================================================================
# DATA STRUCTURE
# ==============================================================================

@dataclass(frozen=True)
class State:
    k: int
    m: int

    true_values: np.ndarray
    critical_indices: np.ndarray

    # Full-state hidden binding.
    tag_a: np.ndarray
    tag_b: np.ndarray
    tags: np.ndarray

    # Auxiliary critical cross-fragment constraints.
    pair_left: np.ndarray
    pair_right: np.ndarray
    pair_coeff: np.ndarray
    pair_target: np.ndarray


# ==============================================================================
# RUNTIME ENVIRONMENT HELPERS
# ==============================================================================

def running_inside_notebook_kernel() -> bool:
    """
    Detect Jupyter or Google Colab execution.

    Notebook kernels commonly inject arguments such as:

        -f /root/.local/share/jupyter/runtime/kernel-....json

    These arguments belong to the notebook kernel, not to Test 11.
    """
    launcher_name = Path(sys.argv[0]).name.lower()

    return (
        "ipykernel" in sys.modules
        or "google.colab" in sys.modules
        or launcher_name in {
            "ipykernel_launcher.py",
            "colab_kernel_launcher.py",
        }
    )


def runtime_base_directory() -> Path:
    """
    Return a writable base directory in both script and notebook execution.

    - Executed as a .py file: directory containing the script.
    - Pasted into a notebook cell: current notebook working directory.
    """
    script_filename = globals().get("__file__")

    if script_filename:
        return Path(script_filename).resolve().parent

    return Path.cwd()


# ==============================================================================
# BASIC UTILITIES
# ==============================================================================

def validate_probability(
    name: str,
    value: float,
    *,
    allow_one: bool = True,
) -> float:
    value = float(value)

    upper_ok = (
        value <= 1.0
        if allow_one
        else value < 1.0
    )

    if (
        not math.isfinite(value)
        or value < 0.0
        or not upper_ok
    ):
        upper_symbol = "<=" if allow_one else "<"
        raise ValueError(
            f"{name} must satisfy 0 <= {name} {upper_symbol} 1."
        )

    return value


def inv_mod(
    value: int,
    modulus: int = PRIME,
) -> int:
    value = int(value) % modulus

    if value == 0:
        raise ValueError(
            "Zero has no multiplicative inverse in the finite field."
        )

    return pow(
        value,
        modulus - 2,
        modulus,
    )


def p_inf_from_h(
    h_min: float,
) -> float:
    """
    Worst-case saturation of:
        p_inf <= 2^(-h_min).
    """
    h_min = float(h_min)

    if not math.isfinite(h_min) or h_min < 0.0:
        raise ValueError(
            "h_min must be a finite non-negative value."
        )

    return 2.0 ** (-h_min)


def make_point_rng(
    seed_base: int,
    coalition_size: int,
    m_value: int,
    stream: int = 0,
) -> np.random.Generator:
    sequence = np.random.SeedSequence(
        [
            int(seed_base),
            int(coalition_size),
            int(m_value),
            int(stream),
        ]
    )

    return np.random.default_rng(
        sequence
    )


def wrong_value(
    value: int,
    rng: np.random.Generator,
) -> int:
    """
    Produce a different but locally admissible finite-field value.
    """
    offset = int(
        rng.integers(
            1,
            PRIME,
        )
    )

    return (
        int(value)
        + offset
    ) % PRIME


# ==============================================================================
# STATE CONSTRUCTION
# ==============================================================================

def build_state(
    k: int,
    m: int,
    rng: np.random.Generator,
) -> State:
    """
    Build one fully bound toy state.

    Every terminal value is protected by a hidden affine tag:
        tag_i = a_i x_i + b_i mod PRIME,
    with a_i != 0.

    Therefore, for fixed hidden parameters, each tag identifies exactly one
    accepted finite-field value. The m critical indices determine which values
    must be reconstructed by the adversary; the remaining values are treated as
    intact authenticated contributions from the honest aggregation path.
    """
    if not isinstance(k, int) or k <= 0:
        raise ValueError(
            "k must be a positive integer."
        )

    if not isinstance(m, int) or not 1 <= m <= k:
        raise ValueError(
            "m must satisfy 1 <= m <= k."
        )

    true_values = rng.integers(
        0,
        PRIME,
        size=k,
        dtype=np.int64,
    )

    critical_indices = np.sort(
        rng.choice(
            k,
            size=m,
            replace=False,
        )
    ).astype(
        np.int64
    )

    tag_a = rng.integers(
        1,
        PRIME,
        size=k,
        dtype=np.int64,
    )

    tag_b = rng.integers(
        0,
        PRIME,
        size=k,
        dtype=np.int64,
    )

    tags = np.mod(
        tag_a * true_values
        + tag_b,
        PRIME,
    ).astype(
        np.int64
    )

    if m > 1:
        pair_left = critical_indices[:-1].copy()
        pair_right = critical_indices[1:].copy()

        pair_coeff = rng.integers(
            1,
            PRIME,
            size=m - 1,
            dtype=np.int64,
        )

        left_values = true_values[
            pair_left
        ]

        right_values = true_values[
            pair_right
        ]

        pair_target = np.mod(
            left_values
            + pair_coeff * right_values
            + left_values * right_values,
            PRIME,
        ).astype(
            np.int64
        )
    else:
        pair_left = np.empty(
            0,
            dtype=np.int64,
        )

        pair_right = np.empty(
            0,
            dtype=np.int64,
        )

        pair_coeff = np.empty(
            0,
            dtype=np.int64,
        )

        pair_target = np.empty(
            0,
            dtype=np.int64,
        )

    state = State(
        k=k,
        m=m,
        true_values=true_values,
        critical_indices=critical_indices,
        tag_a=tag_a,
        tag_b=tag_b,
        tags=tags,
        pair_left=pair_left,
        pair_right=pair_right,
        pair_coeff=pair_coeff,
        pair_target=pair_target,
    )

    accepted, _, _, _ = V_G(
        state,
        state.true_values,
    )

    if not accepted:
        raise RuntimeError(
            "Fresh honest state failed its own hidden invariant family."
        )

    return state


# ==============================================================================
# V_L, Cons_R, Inv_C, V_G
# ==============================================================================

def V_L(
    values: np.ndarray,
) -> np.ndarray:
    """
    Local admissibility only.

    Every finite-field integer is locally admissible. This layer does not know
    whether a value is true or globally consistent.
    """
    array = np.asarray(
        values
    )

    if array.ndim != 1:
        return np.zeros(
            array.size,
            dtype=bool,
        )

    integer_type = np.issubdtype(
        array.dtype,
        np.integer,
    )

    if not integer_type:
        return np.zeros(
            array.shape,
            dtype=bool,
        )

    return (
        (array >= 0)
        & (array < PRIME)
    )


def Cons_R(
    state: State,
    values: np.ndarray,
    local_ok: np.ndarray,
) -> bool:
    """
    Structural completeness proxy.

    It verifies the exact terminal-vector cardinality and local admissibility.
    It is not presented as a complete implementation of formal R_int.
    """
    return (
        np.asarray(values).shape
        == (state.k,)
        and np.asarray(local_ok).shape
        == (state.k,)
        and bool(
            np.all(
                local_ok
            )
        )
    )


def Inv_C(
    state: State,
    values: np.ndarray,
) -> bool:
    """
    Full-state hidden invariant binding.

    1. Every terminal fragment must satisfy its hidden affine tag.
    2. Critical neighboring fragments must satisfy auxiliary pair constraints.
    """
    candidate = np.asarray(
        values,
        dtype=np.int64,
    )

    calculated_tags = np.mod(
        state.tag_a * candidate
        + state.tag_b,
        PRIME,
    )

    if not bool(
        np.array_equal(
            calculated_tags,
            state.tags,
        )
    ):
        return False

    if state.pair_left.size:
        left_values = candidate[
            state.pair_left
        ]

        right_values = candidate[
            state.pair_right
        ]

        calculated_pairs = np.mod(
            left_values
            + state.pair_coeff
            * right_values
            + left_values
            * right_values,
            PRIME,
        )

        if not bool(
            np.array_equal(
                calculated_pairs,
                state.pair_target,
            )
        ):
            return False

    return True


def V_G(
    state: State,
    values: np.ndarray,
) -> Tuple[bool, bool, bool, bool]:
    """
    Execute:
        V_L -> Cons_R -> Inv_C -> V_G.
    """
    candidate = np.asarray(
        values
    )

    local_ok = V_L(
        candidate
    )

    local_layer_ok = (
        candidate.shape
        == (state.k,)
        and local_ok.shape
        == (state.k,)
        and bool(
            np.all(
                local_ok
            )
        )
    )

    if not local_layer_ok:
        return (
            False,
            False,
            False,
            False,
        )

    relational_ok = Cons_R(
        state,
        candidate,
        local_ok,
    )

    if not relational_ok:
        return (
            False,
            True,
            False,
            False,
        )

    invariant_ok = Inv_C(
        state,
        candidate,
    )

    if not invariant_ok:
        return (
            False,
            True,
            True,
            False,
        )

    return (
        True,
        True,
        True,
        True,
    )


# ==============================================================================
# CANDIDATE MATERIALIZATION AND STRUCTURAL AUDIT
# ==============================================================================

def materialize_candidate(
    state: State,
    failed_critical_count: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    Materialize one representative candidate for a sampled trajectory.

    All intact non-critical evidence remains authentic. When one or more critical
    inferences fail, the corresponding critical values are replaced by wrong but
    locally admissible field values.
    """
    if not 0 <= failed_critical_count <= state.m:
        raise ValueError(
            "failed_critical_count must lie in [0,m]."
        )

    candidate = np.array(
        state.true_values,
        copy=True,
    )

    if failed_critical_count == 0:
        return candidate

    failed_indices = rng.choice(
        state.critical_indices,
        size=failed_critical_count,
        replace=False,
    )

    for index in failed_indices:
        candidate[int(index)] = wrong_value(
            candidate[int(index)],
            rng,
        )

    return candidate


def audit_structural_equivalence(
    state: State,
    failed_counts: np.ndarray,
    audit_trajectories: int,
    rng: np.random.Generator,
) -> int:
    """
    Execute sampled trajectories through scalar V_G.

    The Monte Carlo sufficient-statistic event and scalar structural execution
    must agree exactly. Any disagreement aborts the experiment.
    """
    if audit_trajectories <= 0:
        return 0

    audit_count = min(
        int(audit_trajectories),
        int(failed_counts.size),
    )

    audit_indices = rng.choice(
        failed_counts.size,
        size=audit_count,
        replace=False,
    )

    for trajectory_index in audit_indices:
        failure_count = int(
            failed_counts[
                trajectory_index
            ]
        )

        candidate = materialize_candidate(
            state=state,
            failed_critical_count=failure_count,
            rng=rng,
        )

        accepted, local_ok, relational_ok, invariant_ok = V_G(
            state,
            candidate,
        )

        expected_acceptance = (
            failure_count == 0
        )

        if accepted is not expected_acceptance:
            raise AssertionError(
                "Scalar V_G execution disagreed with the sampled "
                "critical-reconstruction event."
            )

        if failure_count > 0:
            if not (
                local_ok
                and relational_ok
                and not invariant_ok
            ):
                raise AssertionError(
                    "A wrong but locally admissible critical value did not "
                    "produce the expected Local-Pass / Global-Veto path."
                )

    return audit_count


# ==============================================================================
# C_int DISCLOSURE AND FALSE-STATE CONTROLS
# ==============================================================================

def solve_from_Cint_disclosure(
    state: State,
    index: int,
) -> int:
    """
    Reconstruct the unique affine-tag-consistent value after full C_int
    disclosure.
    """
    return (
        (
            int(
                state.tags[
                    index
                ]
            )
            - int(
                state.tag_b[
                    index
                ]
            )
        )
        * inv_mod(
            int(
                state.tag_a[
                    index
                ]
            )
        )
    ) % PRIME


def execute_Cint_disclosure_controls(
    state: State,
    rng: np.random.Generator,
) -> Dict[str, bool]:
    """
    Distinguish secrecy collapse from integrity collapse.

    1. Full C_int disclosure reconstructs all critical authentic values.
    2. The reconstructed authentic state is accepted.
    3. A subsequent false mutation is still vetoed.
    """
    reconstructed = np.array(
        state.true_values,
        copy=True,
    )

    for index in state.critical_indices:
        reconstructed[int(index)] = solve_from_Cint_disclosure(
            state,
            int(index),
        )

    reconstruction_matches_truth = bool(
        np.array_equal(
            reconstructed[
                state.critical_indices
            ],
            state.true_values[
                state.critical_indices
            ],
        )
    )

    reconstruction_accepts = V_G(
        state,
        reconstructed,
    )[0]

    false_candidate = np.array(
        reconstructed,
        copy=True,
    )

    mutation_index = int(
        state.critical_indices[
            0
        ]
    )

    false_candidate[
        mutation_index
    ] = wrong_value(
        false_candidate[
            mutation_index
        ],
        rng,
    )

    false_state_accepts = V_G(
        state,
        false_candidate,
    )[0]

    if not reconstruction_matches_truth:
        raise AssertionError(
            "C_int disclosure failed to reconstruct the authentic critical state."
        )

    if not reconstruction_accepts:
        raise AssertionError(
            "Authentic reconstructed state failed V_G."
        )

    if false_state_accepts:
        raise AssertionError(
            "False state was accepted after C_int disclosure."
        )

    return {
        "reconstruction_matches_truth": reconstruction_matches_truth,
        "reconstruction_accepts": reconstruction_accepts,
        "false_state_accepts": false_state_accepts,
    }


def execute_full_state_coverage_control(
    state: State,
    rng: np.random.Generator,
) -> bool:
    """
    Mutate one terminal value, including a non-critical value when available.
    Full-state hidden binding must reject the mutation.
    """
    non_critical = np.setdiff1d(
        np.arange(
            state.k,
            dtype=np.int64,
        ),
        state.critical_indices,
        assume_unique=True,
    )

    if non_critical.size:
        index = int(
            non_critical[
                0
            ]
        )
    else:
        index = int(
            state.critical_indices[
                0
            ]
        )

    candidate = np.array(
        state.true_values,
        copy=True,
    )

    candidate[index] = wrong_value(
        candidate[index],
        rng,
    )

    rejected = not V_G(
        state,
        candidate,
    )[0]

    if not rejected:
        raise AssertionError(
            "Full-state coverage control failed: a terminal mutation was accepted."
        )

    return rejected


# ==============================================================================
# EXACT AND THEOREM-STYLE REFERENCES
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
    Natural logarithm of the exact injective reconstruction probability.
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

        if p_inf == 0.0 and missing_count > 0:
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


def log_theorem_reference(
    q_actual: float,
    m: int,
    p_inf: float,
) -> float:
    """
    Natural logarithm of:
        [q_actual + (1-q_actual)p_inf]^m.
    """
    p_comp = (
        q_actual
        + (
            1.0 - q_actual
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


def wilson_interval(
    successes: int,
    trials: int,
    z: float = 1.959963984540054,
) -> Tuple[float, float]:
    if trials <= 0:
        raise ValueError(
            "trials must be positive."
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
# MONTE CARLO SIMULATION
# ==============================================================================

def simulate_one_m(
    Q: int,
    coalition_size: int,
    m: int,
    h_min: float,
    iterations: int,
    rng: np.random.Generator,
    terminal_fragments: int,
    audit_trajectories: int,
) -> Dict[str, Any]:
    """
    Simulate one exact injective-assignment fragmentation point.
    """
    if not isinstance(Q, int) or Q <= 0:
        raise ValueError(
            "Q must be a positive integer."
        )

    if not isinstance(coalition_size, int) or not (
        0 <= coalition_size <= Q
    ):
        raise ValueError(
            "coalition_size must satisfy 0 <= r <= Q."
        )

    if not isinstance(iterations, int) or iterations <= 0:
        raise ValueError(
            "iterations must be positive."
        )

    k = int(
        terminal_fragments
    )

    if k > Q:
        raise ValueError(
            "Injective assignment requires terminal_fragments <= Q."
        )

    if not 1 <= m <= k:
        raise ValueError(
            "m must satisfy 1 <= m <= terminal_fragments."
        )

    q_actual = (
        coalition_size
        / Q
    )

    p_inf = p_inf_from_h(
        h_min
    )

    state = build_state(
        k,
        m,
        rng,
    )

    # X = number of critical fragments directly assigned to the coalition.
    direct_counts = rng.hypergeometric(
        ngood=coalition_size,
        nbad=Q - coalition_size,
        nsample=m,
        size=iterations,
    ).astype(
        np.int32
    )

    missing_counts = (
        m
        - direct_counts
    ).astype(
        np.int32
    )

    inferred_counts = rng.binomial(
        missing_counts,
        p_inf,
    ).astype(
        np.int32
    )

    failed_counts = (
        missing_counts
        - inferred_counts
    ).astype(
        np.int32
    )

    reconstruction_success = (
        failed_counts == 0
    )

    success_count = int(
        np.count_nonzero(
            reconstruction_success
        )
    )

    veto_count = (
        iterations
        - success_count
    )

    ci_low, ci_high = wilson_interval(
        success_count,
        iterations,
    )

    audited = audit_structural_equivalence(
        state=state,
        failed_counts=failed_counts,
        audit_trajectories=audit_trajectories,
        rng=rng,
    )

    disclosure_controls = execute_Cint_disclosure_controls(
        state,
        rng,
    )

    full_state_coverage_rejects = execute_full_state_coverage_control(
        state,
        rng,
    )

    exact_log = log_exact_injective_reference(
        Q=Q,
        r=coalition_size,
        m=m,
        p_inf=p_inf,
    )

    theorem_log = log_theorem_reference(
        q_actual=q_actual,
        m=m,
        p_inf=p_inf,
    )

    if (
        exact_log
        > theorem_log
        + 1e-10
    ):
        raise AssertionError(
            "Exact injective probability exceeded the independent "
            "theorem-style reference."
        )

    return {
        "Q": Q,
        "coalition_size": coalition_size,
        "q_actual": q_actual,
        "k": k,
        "m": m,
        "h_min": float(
            h_min
        ),
        "p_inf": p_inf,

        "iterations": iterations,
        "structurally_audited_trajectories": audited,

        "reconstruction_success_count": success_count,
        "reconstruction_accept_rate": (
            success_count
            / iterations
        ),
        "reconstruction_ci_low": ci_low,
        "reconstruction_ci_high": ci_high,

        "global_veto_rate": (
            veto_count
            / iterations
        ),
        "local_pass_global_veto_rate": (
            veto_count
            / iterations
        ),

        "exact_injective_reference": probability_from_log(
            exact_log
        ),
        "exact_injective_log10": log10_from_log(
            exact_log
        ),

        "theorem_reference": probability_from_log(
            theorem_log
        ),
        "theorem_log10": log10_from_log(
            theorem_log
        ),

        "avg_direct_critical": float(
            np.mean(
                direct_counts
            )
        ),
        "avg_inferred_critical": float(
            np.mean(
                inferred_counts
            )
        ),
        "avg_failed_critical": float(
            np.mean(
                failed_counts
            )
        ),

        "Cint_disclosure_reconstructs_truth": disclosure_controls[
            "reconstruction_matches_truth"
        ],
        "Cint_disclosure_reconstruction_accepts": disclosure_controls[
            "reconstruction_accepts"
        ],
        "Cint_disclosure_false_state_accepts": disclosure_controls[
            "false_state_accepts"
        ],

        "full_state_mutation_rejected": full_state_coverage_rejects,
    }


# ==============================================================================
# PLOTTING
# ==============================================================================

def nearest_available_q(
    results: Mapping[float, Sequence[Mapping[str, Any]]],
    target_q: float,
) -> float:
    return min(
        results.keys(),
        key=lambda available_q: abs(
            available_q
            - target_q
        ),
    )


def plot_probability_from_log10(
    log10_value: float,
    floor: float,
) -> float:
    floor_log10 = math.log10(
        floor
    )

    if not math.isfinite(
        log10_value
    ):
        return floor

    return 10.0 ** max(
        log10_value,
        floor_log10,
    )


def plot_test11_comparisons(
    results: Mapping[float, Sequence[Mapping[str, Any]]],
    iterations: int,
    out_dir: Path,
    selected_q_for_curves: Sequence[float],
    *,
    show_plots: bool = True,
) -> None:
    out_dir.mkdir(
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

    # --------------------------------------------------------------------------
    # Plot 1: selected actual-q curves.
    # --------------------------------------------------------------------------
    plt.figure(
        figsize=(13, 8)
    )

    used_q_values: Set[float] = set()

    for target_q in selected_q_for_curves:
        actual_q = nearest_available_q(
            results,
            target_q,
        )

        if actual_q in used_q_values:
            continue

        used_q_values.add(
            actual_q
        )

        rows = results[
            actual_q
        ]

        m_axis = np.array(
            [
                row["m"]
                for row in rows
            ],
            dtype=float,
        )

        empirical = np.array(
            [
                max(
                    row[
                        "reconstruction_accept_rate"
                    ],
                    detection_floor,
                )
                for row in rows
            ],
            dtype=float,
        )

        exact_reference = np.array(
            [
                plot_probability_from_log10(
                    row[
                        "exact_injective_log10"
                    ],
                    detection_floor,
                )
                for row in rows
            ],
            dtype=float,
        )

        theorem_reference_values = np.array(
            [
                plot_probability_from_log10(
                    row[
                        "theorem_log10"
                    ],
                    detection_floor,
                )
                for row in rows
            ],
            dtype=float,
        )

        plt.plot(
            m_axis,
            empirical,
            marker="o",
            label=(
                f"Monte Carlo reconstruction, "
                f"q={actual_q:.4f}"
            ),
        )

        plt.plot(
            m_axis,
            exact_reference,
            linestyle="--",
            label=(
                f"Exact injective reference, "
                f"q={actual_q:.4f}"
            ),
        )

        plt.plot(
            m_axis,
            theorem_reference_values,
            linestyle=":",
            label=(
                f"Independent upper reference, "
                f"q={actual_q:.4f}"
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
        "Reconstruction probability / reference "
        f"(zero observations plotted at 1/{iterations})"
    )

    plt.title(
        "CNVS Test 11: Critical Reconstruction Sensitivity"
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
        out_dir
        / "test_11_selected_q_reconstruction_vs_references.png"
    )

    plt.savefig(
        output_1,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 2: empirical versus exact and upper references.
    # --------------------------------------------------------------------------
    empirical_all: List[float] = []
    exact_all: List[float] = []
    theorem_all: List[float] = []

    for rows in results.values():
        for row in rows:
            empirical_all.append(
                max(
                    row[
                        "reconstruction_accept_rate"
                    ],
                    detection_floor,
                )
            )

            exact_all.append(
                plot_probability_from_log10(
                    row[
                        "exact_injective_log10"
                    ],
                    detection_floor,
                )
            )

            theorem_all.append(
                plot_probability_from_log10(
                    row[
                        "theorem_log10"
                    ],
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
            "Monte Carlo versus exact injective reference"
        ),
    )

    plt.scatter(
        theorem_all,
        empirical_all,
        marker="^",
        label=(
            "Monte Carlo versus independent upper reference"
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
        "Observed reconstruction rate"
    )

    plt.title(
        "CNVS Test 11: Monte Carlo Reconstruction vs References"
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
        out_dir
        / "test_11_empirical_vs_references.png"
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
    q_values = list(
        results.keys()
    )

    m_values = [
        row["m"]
        for row in next(
            iter(
                results.values()
            )
        )
    ]

    heatmap = np.array(
        [
            [
                row[
                    "local_pass_global_veto_rate"
                ]
                for row in results[
                    q_value
                ]
            ]
            for q_value in q_values
        ],
        dtype=float,
    )

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
            "Locally admissible candidate rejected by hidden invariants"
        ),
    )

    plt.xticks(
        ticks=np.arange(
            len(
                m_values
            )
        ),
        labels=[
            str(
                m_value
            )
            for m_value in m_values
        ],
        rotation=45,
        ha="right",
    )

    plt.yticks(
        ticks=np.arange(
            len(
                q_values
            )
        ),
        labels=[
            f"{q_value:.4f}"
            for q_value in q_values
        ],
    )

    plt.xlabel(
        "Critical fragmentation cardinality m"
    )

    plt.ylabel(
        "Actual colluding fraction r/Q"
    )

    plt.title(
        "CNVS Test 11: Local-Pass / Global-Veto Sensitivity"
    )

    plt.tight_layout()

    output_3 = (
        out_dir
        / "test_11_local_pass_global_veto_heatmap.png"
    )

    plt.savefig(
        output_3,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 4: maximum fragmentation versus actual q.
    # --------------------------------------------------------------------------
    maximum_m = max(
        m_values
    )

    q_axis: List[float] = []
    empirical_final: List[float] = []
    exact_final: List[float] = []
    theorem_final: List[float] = []

    for actual_q, rows in results.items():
        row = next(
            item
            for item in rows
            if item["m"] == maximum_m
        )

        q_axis.append(
            actual_q
        )

        empirical_final.append(
            max(
                row[
                    "reconstruction_accept_rate"
                ],
                detection_floor,
            )
        )

        exact_final.append(
            plot_probability_from_log10(
                row[
                    "exact_injective_log10"
                ],
                detection_floor,
            )
        )

        theorem_final.append(
            plot_probability_from_log10(
                row[
                    "theorem_log10"
                ],
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
            f"Monte Carlo reconstruction at m={maximum_m}"
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
        theorem_final,
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
        f"CNVS Test 11: Maximum Fragmentation m={maximum_m}"
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
        out_dir
        / "test_11_max_fragmentation_vs_actual_q.png"
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
        out_dir.resolve(),
    )


# ==============================================================================
# RESULT SERIALIZATION
# ==============================================================================

def save_results_json(
    results: Mapping[float, Sequence[Mapping[str, Any]]],
    output_path: Path,
) -> None:
    serializable = {
        f"{actual_q:.12f}": list(
            rows
        )
        for actual_q, rows in results.items()
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
            serializable,
            handle,
            indent=2,
            ensure_ascii=False,
        )


# ==============================================================================
# CONFIGURATION HELPERS
# ==============================================================================

DEFAULT_Q_LEVELS = [
    0.33,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
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
    4,
    8,
    16,
    32,
    64,
    128,
    256,
    512,
    1024,
    2048,
]


def coalition_sizes_from_levels(
    Q: int,
    q_levels: Iterable[float],
) -> List[int]:
    sizes = set()

    for level in q_levels:
        validate_probability(
            "q level",
            level,
        )

        sizes.add(
            max(
                0,
                min(
                    Q,
                    round(
                        float(level)
                        * Q
                    ),
                ),
            )
        )

    return sorted(
        sizes
    )


def validate_m_values(
    m_values: Iterable[int],
    k: int,
) -> List[int]:
    validated = sorted(
        {
            int(
                value
            )
            for value in m_values
        }
    )

    if not validated:
        raise ValueError(
            "At least one m value is required."
        )

    for value in validated:
        if not 1 <= value <= k:
            raise ValueError(
                f"Every m must satisfy 1 <= m <= {k}."
            )

    return validated


# ==============================================================================
# MAIN TEST RUN
# ==============================================================================

def run_test_11(
    *,
    iterations: int = 100_000,
    audit_trajectories: int = 32,
    q_levels: Sequence[float] = DEFAULT_Q_LEVELS,
    m_values: Sequence[int] = DEFAULT_M_VALUES,
    show_plots: bool = True,
) -> Dict[float, List[Dict[str, Any]]]:
    Q = 2048
    terminal_fragments = 2048

    h_min = 1.0
    seed_base = 42

    coalition_sizes = coalition_sizes_from_levels(
        Q,
        q_levels,
    )

    validated_m_values = validate_m_values(
        m_values,
        terminal_fragments,
    )

    selected_q_for_curves = [
        0.50,
        0.70,
        0.90,
        0.99,
        1.00,
    ]

    output_dir = (
        runtime_base_directory()
        / "test_11_figures"
    )

    results: Dict[
        float,
        List[
            Dict[
                str,
                Any,
            ]
        ],
    ] = {}

    print(
        "\nCNVS Test 11: Executable Fragmentation Sensitivity"
    )

    print(
        "--------------------------------------------------"
    )

    print(
        f"Q = {Q}"
    )

    print(
        f"terminal fragments k = {terminal_fragments}"
    )

    print(
        f"h_min = {h_min}"
    )

    print(
        f"p_inf = {p_inf_from_h(h_min)} "
        "(worst-case saturated bound)"
    )

    print(
        f"iterations per point = {iterations}"
    )

    print(
        f"scalar V_G audit trajectories per point = "
        f"{audit_trajectories}"
    )

    print(
        f"coalition sizes = {coalition_sizes}"
    )

    print(
        f"m values = {validated_m_values}"
    )

    print(
        "\nMeasured event: complete reconstruction of every critical value, "
        "followed by V_G acceptance of the authentic reconstructed state."
    )

    print(
        "This is not a false-state-acceptance rate.\n"
    )

    for coalition_size in coalition_sizes:
        actual_q = (
            coalition_size
            / Q
        )

        rows: List[
            Dict[
                str,
                Any,
            ]
        ] = []

        print(
            f"\n=== r={coalition_size}/{Q}, "
            f"q_actual={actual_q:.6f} ==="
        )

        print(
            "m | reconstruct | 95% CI | local-pass/veto | "
            "exact log10 | upper log10 | leak reconstructs | false leak state"
        )

        for m in validated_m_values:
            rng = make_point_rng(
                seed_base=seed_base,
                coalition_size=coalition_size,
                m_value=m,
            )

            output = simulate_one_m(
                Q=Q,
                coalition_size=coalition_size,
                m=m,
                h_min=h_min,
                iterations=iterations,
                rng=rng,
                terminal_fragments=terminal_fragments,
                audit_trajectories=audit_trajectories,
            )

            rows.append(
                output
            )

            print(
                f"{m:4d} | "
                f"{output['reconstruction_accept_rate']:.8f} | "
                f"[{output['reconstruction_ci_low']:.8f}, "
                f"{output['reconstruction_ci_high']:.8f}] | "
                f"{output['local_pass_global_veto_rate']:.8f} | "
                f"{output['exact_injective_log10']:11.3f} | "
                f"{output['theorem_log10']:11.3f} | "
                f"{output['Cint_disclosure_reconstruction_accepts']} | "
                f"{output['Cint_disclosure_false_state_accepts']}"
            )

        results[
            actual_q
        ] = rows

    plot_test11_comparisons(
        results=results,
        iterations=iterations,
        out_dir=output_dir,
        selected_q_for_curves=selected_q_for_curves,
        show_plots=show_plots,
    )

    results_path = (
        output_dir
        / "test_11_results.json"
    )

    save_results_json(
        results,
        results_path,
    )

    print(
        "Saved:",
        results_path,
    )

    print(
        "\n================ FINAL INTERPRETATION ================\n"
    )

    print(
        "- Every terminal fragment is covered by the hidden full-state binding."
    )

    print(
        "- m identifies the hidden reconstruction-critical subset; intact "
        "non-critical values are supplied by the honest aggregation path."
    )

    print(
        "- Injective assignment is sampled exactly through its hypergeometric "
        "sufficient statistic."
    )

    print(
        "- Every audited sampled trajectory is materialized and executed through "
        "V_L -> Cons_R -> Inv_C -> V_G."
    )

    print(
        "- Exact injective and independent upper references are comparison curves "
        "only and do not decide Monte Carlo outcomes."
    )

    print(
        "- C_int disclosure collapses secrecy in this reversible toy binding, "
        "but a deliberately false post-disclosure state remains vetoed."
    )

    print(
        "- Zero observed reconstructions are accompanied by Wilson intervals and "
        "are not interpreted as mathematical zero."
    )

    return results


# ==============================================================================
# COMMAND-LINE INTERFACE
# ==============================================================================

def parse_arguments(
    argv: Optional[Sequence[str]] = None,
) -> argparse.Namespace:
    """
    Parse Test 11 options.

    Behaviour:
      - explicit argv: strict parsing;
      - ordinary terminal execution: strict parsing;
      - Jupyter / Colab: parse Test 11 options and ignore only kernel-injected
        arguments such as "-f kernel.json".
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run corrected CNVS Test 11 fragmentation sensitivity."
        )
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=100_000,
        help=(
            "Monte Carlo trajectories per (q,m) point "
            "(default: 100000)."
        ),
    )

    parser.add_argument(
        "--audit-trajectories",
        type=int,
        default=32,
        help=(
            "Scalar V_G materialization audits per point "
            "(default: 32)."
        ),
    )

    parser.add_argument(
        "--q-levels",
        type=float,
        nargs="*",
        default=None,
        help=(
            "Optional nominal q levels in [0,1]. They are converted to unique "
            "integer coalition sizes."
        ),
    )

    parser.add_argument(
        "--m-values",
        type=int,
        nargs="*",
        default=None,
        help=(
            "Optional critical-fragment cardinalities."
        ),
    )

    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Save plots without displaying them.",
    )

    if argv is not None:
        return parser.parse_args(list(argv))

    if running_inside_notebook_kernel():
        arguments, ignored_arguments = parser.parse_known_args()

        if ignored_arguments:
            print(
                "[Notebook compatibility] Ignored kernel arguments:",
                " ".join(ignored_arguments),
            )

        return arguments

    return parser.parse_args()


def main(
    argv: Optional[Sequence[str]] = None,
) -> None:
    arguments = parse_arguments(argv)

    if arguments.iterations <= 0:
        raise ValueError(
            "--iterations must be positive."
        )

    if arguments.audit_trajectories < 0:
        raise ValueError(
            "--audit-trajectories cannot be negative."
        )

    run_test_11(
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
