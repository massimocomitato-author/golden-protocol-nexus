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

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass
from itertools import permutations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np


# ==============================================================================
# TEST 12 — ENTROPY-CALIBRATED TOPOLOGY / INVARIANT LEAKAGE
#
# Test Name: Test 12 - Entropy-Calibrated Leakage of Theta_C and R_int with Executed Coherent False-State Injection
# filename: test_12_entropy_calibrated_topology_invariant_leakage.py
#
# CLASSIFICATION:
# Executable in-silico Monte Carlo adversarial-knowledge experiment.
#
# PRIMARY QUESTION:
# How does the probability of constructing a false but globally coherent state
# change as the residual min-entropy of:
#
#       Theta_C  — the hidden generative parameter core of C_int; and
#       R_int    — the hidden semantic-role / opaque-selector topology
#
# is varied over explicit, increasing bit levels?
#
# The central event is executed, not imposed algebraically:
#
#       X' != X  and  V_G(X') == ACCEPT.
#
# The program NEVER sets P(false accept) = 2^(-h).  The entropy values only define
# the adversary's posterior hypothesis support.  A bounded adversarial solver must
# still synthesize a candidate and submit it to the true hidden V_G.
#
# ------------------------------------------------------------------------------
# CNVS ORDINARY-MODEL SEPARATION
# ------------------------------------------------------------------------------
# In the ordinary CNVS model used here, compromise of peripheral verifiers does
# not automatically reveal Theta_C.  The authentic selector-level state is made
# compatible with every posterior (Theta_C, R_int) hypothesis by construction.
# Therefore the baseline data shown to verifiers does not itself reduce the
# hypothesis space.  Theta_C entropy is reduced only by an EXPLICIT side-channel
# scenario selected by the experimenter.
#
# The colluding fraction q is used only in the separate end-to-end credential
# projection.  Increasing q does not alter h_Theta, h_R, the solver posterior, or
# the pure epistemic false-acceptance experiment.
#
# ------------------------------------------------------------------------------
# HIDDEN WORLD
# ------------------------------------------------------------------------------
# A hidden world is:
#
#       W = (Theta_C, R_int).
#
# R_int is one of all 5! = 120 injective mappings from five semantic roles to five
# opaque selector positions.
#
# Theta_C is a hidden generative core:
#
#       Theta_C = (template_id, a, e)
#
# with four relation templates and non-zero coefficients a,e in F_31.  The full
# core universe therefore contains:
#
#       4 * 30 * 30 = 3,600 Theta_C hypotheses
#
# and has maximum uniform min-entropy log2(3600) ~= 11.81 bits.
#
# Given an authentic selector-level state X, a candidate Theta_C, and a candidate
# R_int, the remaining hidden offsets (b,c,d,f) are instantiated so that X is
# accepted.  Consequently every world in the posterior explains the same honest
# observation.  This is an intentional non-inferability control: the authentic
# data alone does not select one Theta_C or one topology from the posterior.
#
# The non-identifying relational family is:
#
#       x_v = e*x_u + f          (mod 31)
#       x_p = a*x_u + b          (mod 31)
#       x_q = x_v + c            (mod 31)
#       x_r = x_u + x_v + d      (mod 31)
#
# For fixed hidden parameters it accepts a one-dimensional class of 31 states.
# This makes coherent false-state synthesis possible after sufficient knowledge.
#
# ------------------------------------------------------------------------------
# ENTROPY-CALIBRATED POSTERIORS
# ------------------------------------------------------------------------------
# The independent side-channel experiment uses nested, uniform posterior supports.
# For a requested bit level h, the support contains exactly 2^h hypotheses whenever
# that size is available.  The special level "max" uses the complete universe.
# Therefore:
#
#       h_Theta = log2(|Omega_Theta|)
#       h_R     = log2(|Omega_R|)
#       h_joint = h_Theta + h_R
#
# in the independent posterior scenario.
#
# A separate pathological-coupling control uses a joint list of paired Theta_C and
# R_int hypotheses rather than their Cartesian product.  It demonstrates that the
# same marginal uncertainty can have lower JOINT entropy when topology and
# invariant parameters are accidentally correlated.  This scenario is explicitly
# outside the intended CNVS decoupling assumption.
#
# ------------------------------------------------------------------------------
# TWO TRUE V_G REGIMES
# ------------------------------------------------------------------------------
# equivalence:
#     V_G accepts every state satisfying the hidden relational family.  A false but
#     coherent alternative can therefore exist.
#
# identifying:
#     The same relational checks are supplemented by an idealized exact-state
#     binding.  Any X' != X is rejected.  This is a boundary control showing that
#     complete knowledge does not necessarily imply falsifiability.
#
# ------------------------------------------------------------------------------
# AUTHENTICATION SEPARATION
# ------------------------------------------------------------------------------
# The primary heatmaps grant authentication (Auth=1) to isolate epistemic ability.
# End-to-end projections then multiply each executed pure success by the exact
# probability that a coalition of r among Q injectively assigned verifiers controls
# every credential required for the changed selector set:
#
#       P_auth(d | Q,r) = C(r,d) / C(Q,d).
#
# This credential calculation does not decide V_G and is reported separately.
#
# ------------------------------------------------------------------------------
# INTERPRETIVE LIMITS
# ------------------------------------------------------------------------------
#   - finite-field toy semantic universe;
#   - bounded posterior solver and finite candidate pool;
#   - entropy-calibrated posterior supports, not measured deployment leakage;
#   - application-layer V_G model, not a production network / PKI implementation;
#   - zero observed false acceptance is not proof of impossibility;
#   - the equivalence regime deliberately admits alternative valid states;
#   - the identifying regime deliberately excludes every false accepted state.
# ==============================================================================


MODULUS = 31
ROLE_COUNT = 5
SELECTOR_COUNT = 5
TEMPLATE_COUNT = 4
THETA_COUNT = TEMPLATE_COUNT * (MODULUS - 1) * (MODULUS - 1)
TOPOLOGY_COUNT = math.factorial(SELECTOR_COUNT)


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass(frozen=True)
class TemplateSpec:
    template_id: int
    free_u: int
    free_v: int
    dep_p: int
    dep_q: int
    dep_r: int


@dataclass(frozen=True)
class ThetaCore:
    template_id: int
    a: int
    e: int


@dataclass(frozen=True)
class InvariantFamily:
    theta: ThetaCore
    b: int
    c: int
    d: int
    f: int


@dataclass(frozen=True)
class GlobalModel:
    templates: Tuple[TemplateSpec, ...]
    topologies: Tuple[Tuple[int, ...], ...]
    topology_array: np.ndarray
    template_u: np.ndarray
    template_v: np.ndarray
    template_p: np.ndarray
    template_q: np.ndarray
    template_r: np.ndarray


@dataclass(frozen=True)
class EntropyLevel:
    label: str
    target_bits: float
    support_size: int
    realized_bits: float


@dataclass(frozen=True)
class SolverResult:
    candidate_found: bool
    candidate: Optional[Tuple[int, ...]]
    posterior_score: float
    changed_selectors: int
    proposal_count: int


@dataclass(frozen=True)
class CellResult:
    scenario: str
    regime: str
    theta_level: str
    r_level: str
    target_h_theta: float
    target_h_r: float
    realized_h_theta: float
    realized_h_r: float
    realized_h_joint: float
    theta_support_size: int
    r_support_size: int
    joint_support_size: int
    trials: int
    candidate_found_count: int
    candidate_found_rate: float
    pure_false_accept_count: int
    pure_false_accept_rate: float
    pure_ci_low: float
    pure_ci_high: float
    mean_posterior_score: float
    mean_changed_selectors: float
    end_to_end_rates: Mapping[str, float]
    end_to_end_ci_low: Mapping[str, float]
    end_to_end_ci_high: Mapping[str, float]


@dataclass(frozen=True)
class CoupledResult:
    regime: str
    pair_level: str
    marginal_support_size: int
    realized_h_theta: float
    realized_h_r: float
    realized_h_joint: float
    trials: int
    pure_false_accept_count: int
    pure_false_accept_rate: float
    pure_ci_low: float
    pure_ci_high: float
    mean_posterior_score: float
    mean_changed_selectors: float


@dataclass(frozen=True)
class ExperimentConfig:
    trials: int
    theta_levels: Tuple[EntropyLevel, ...]
    r_levels: Tuple[EntropyLevel, ...]
    q_values: Tuple[float, ...]
    verifier_population: int
    proposal_hypotheses: int
    score_hypotheses: int
    alternatives_per_hypothesis: int
    max_candidate_pool: int
    coupled_max_bits: int
    seed: int
    regimes: Tuple[str, ...]


# ==============================================================================
# COLAB / JUPYTER COMPATIBILITY
# ==============================================================================


def running_inside_notebook_kernel() -> bool:
    launcher_name = Path(sys.argv[0]).name.lower()
    return (
        "ipykernel" in sys.modules
        or "google.colab" in sys.modules
        or launcher_name in {"ipykernel_launcher.py", "colab_kernel_launcher.py"}
    )


def runtime_base_directory() -> Path:
    script_filename = globals().get("__file__")
    if script_filename:
        return Path(script_filename).resolve().parent
    return Path.cwd()


# ==============================================================================
# MODEL CONSTRUCTION
# ==============================================================================


def build_global_model() -> GlobalModel:
    templates = (
        TemplateSpec(0, free_u=0, free_v=2, dep_p=1, dep_q=3, dep_r=4),
        TemplateSpec(1, free_u=0, free_v=1, dep_p=2, dep_q=4, dep_r=3),
        TemplateSpec(2, free_u=1, free_v=3, dep_p=0, dep_q=2, dep_r=4),
        TemplateSpec(3, free_u=2, free_v=4, dep_p=3, dep_q=0, dep_r=1),
    )

    for template in templates:
        roles = {
            template.free_u,
            template.free_v,
            template.dep_p,
            template.dep_q,
            template.dep_r,
        }
        if roles != set(range(ROLE_COUNT)):
            raise AssertionError("Every template must cover all semantic roles exactly once.")

    topologies = tuple(permutations(range(SELECTOR_COUNT)))
    topology_array = np.asarray(topologies, dtype=np.int16)

    return GlobalModel(
        templates=templates,
        topologies=topologies,
        topology_array=topology_array,
        template_u=np.asarray([t.free_u for t in templates], dtype=np.int16),
        template_v=np.asarray([t.free_v for t in templates], dtype=np.int16),
        template_p=np.asarray([t.dep_p for t in templates], dtype=np.int16),
        template_q=np.asarray([t.dep_q for t in templates], dtype=np.int16),
        template_r=np.asarray([t.dep_r for t in templates], dtype=np.int16),
    )


def encode_theta(theta: ThetaCore) -> int:
    return (
        (int(theta.template_id) * (MODULUS - 1) + (int(theta.a) - 1))
        * (MODULUS - 1)
        + (int(theta.e) - 1)
    )


def decode_theta(theta_code: int) -> ThetaCore:
    value = int(theta_code)
    e = value % (MODULUS - 1) + 1
    value //= MODULUS - 1
    a = value % (MODULUS - 1) + 1
    template_id = value // (MODULUS - 1)
    return ThetaCore(template_id=int(template_id), a=int(a), e=int(e))


def decode_theta_arrays(theta_codes: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = theta_codes.astype(np.int64).copy()
    e = values % (MODULUS - 1) + 1
    values //= MODULUS - 1
    a = values % (MODULUS - 1) + 1
    template_id = values // (MODULUS - 1)
    return (
        template_id.astype(np.int16),
        a.astype(np.int16),
        e.astype(np.int16),
    )


def make_semantic_state(
    family: InvariantFamily,
    template: TemplateSpec,
    x_u: int,
) -> np.ndarray:
    x_u = int(x_u) % MODULUS
    x_v = (family.theta.e * x_u + family.f) % MODULUS
    state = np.empty(ROLE_COUNT, dtype=np.int16)
    state[template.free_u] = x_u
    state[template.free_v] = x_v
    state[template.dep_p] = (family.theta.a * x_u + family.b) % MODULUS
    state[template.dep_q] = (x_v + family.c) % MODULUS
    state[template.dep_r] = (x_u + x_v + family.d) % MODULUS
    return state


def map_semantic_to_selector(
    semantic_state: Sequence[int],
    topology: Sequence[int],
) -> np.ndarray:
    selector_state = np.empty(SELECTOR_COUNT, dtype=np.int16)
    for role, selector in enumerate(topology):
        selector_state[int(selector)] = int(semantic_state[role])
    return selector_state


def map_selector_to_semantic(
    selector_state: Sequence[int],
    topology: Sequence[int],
) -> np.ndarray:
    selector_array = np.asarray(selector_state, dtype=np.int16)
    topology_array = np.asarray(topology, dtype=np.int16)
    return selector_array[topology_array]


def instantiate_family_from_authentic(
    authentic_selector_state: Sequence[int],
    theta: ThetaCore,
    topology: Sequence[int],
    model: GlobalModel,
) -> InvariantFamily:
    """Instantiate hidden offsets so that the authentic state fits every hypothesis.

    This construction is the explicit ordinary-model non-inferability control:
    observing the authentic selector-level state does not eliminate any candidate
    Theta_C core or topology from the experiment's prior support.
    """

    template = model.templates[theta.template_id]
    semantic = map_selector_to_semantic(authentic_selector_state, topology)
    x_u = int(semantic[template.free_u])
    x_v = int(semantic[template.free_v])
    x_p = int(semantic[template.dep_p])
    x_q = int(semantic[template.dep_q])
    x_r = int(semantic[template.dep_r])

    return InvariantFamily(
        theta=theta,
        b=(x_p - theta.a * x_u) % MODULUS,
        c=(x_q - x_v) % MODULUS,
        d=(x_r - x_u - x_v) % MODULUS,
        f=(x_v - theta.e * x_u) % MODULUS,
    )


# ==============================================================================
# V_L, Cons_R, Inv_C, V_G
# ==============================================================================


def V_L(candidate: Sequence[int]) -> bool:
    if len(candidate) != SELECTOR_COUNT:
        return False
    for value in candidate:
        if not isinstance(value, (int, np.integer)):
            return False
        if not 0 <= int(value) < MODULUS:
            return False
    return True


def Cons_R(candidate: Sequence[int]) -> bool:
    return len(candidate) == SELECTOR_COUNT


def family_accepts_semantic(
    family: InvariantFamily,
    template: TemplateSpec,
    semantic: Sequence[int],
) -> bool:
    x_u = int(semantic[template.free_u])
    x_v = int(semantic[template.free_v])
    return (
        x_v == (family.theta.e * x_u + family.f) % MODULUS
        and int(semantic[template.dep_p])
        == (family.theta.a * x_u + family.b) % MODULUS
        and int(semantic[template.dep_q]) == (x_v + family.c) % MODULUS
        and int(semantic[template.dep_r])
        == (x_u + x_v + family.d) % MODULUS
    )


def Inv_C(
    candidate: Sequence[int],
    authentic: Sequence[int],
    family: InvariantFamily,
    template: TemplateSpec,
    topology: Sequence[int],
    regime: str,
) -> bool:
    semantic = map_selector_to_semantic(candidate, topology)
    if not family_accepts_semantic(family, template, semantic):
        return False

    if regime == "equivalence":
        return True
    if regime == "identifying":
        return tuple(int(v) for v in candidate) == tuple(int(v) for v in authentic)
    raise ValueError(f"Unknown invariant regime: {regime}")


def V_G(
    candidate: Sequence[int],
    authentic: Sequence[int],
    family: InvariantFamily,
    template: TemplateSpec,
    topology: Sequence[int],
    regime: str,
) -> Tuple[bool, bool, bool, bool]:
    local_ok = V_L(candidate)
    relational_ok = local_ok and Cons_R(candidate)
    invariant_ok = relational_ok and Inv_C(
        candidate=candidate,
        authentic=authentic,
        family=family,
        template=template,
        topology=topology,
        regime=regime,
    )
    return bool(invariant_ok), bool(local_ok), bool(relational_ok), bool(invariant_ok)


# ==============================================================================
# ENTROPY LEVELS AND NESTED POSTERIOR SUPPORTS
# ==============================================================================


def parse_entropy_level_list(text: str, maximum_count: int) -> Tuple[EntropyLevel, ...]:
    maximum_bits = math.log2(maximum_count)
    levels: List[EntropyLevel] = []
    seen_sizes: set[int] = set()

    for raw_token in text.split(","):
        token = raw_token.strip().lower()
        if not token:
            continue

        if token == "max":
            support_size = maximum_count
            target_bits = maximum_bits
            label = "max"
        else:
            target_bits = float(token)
            if target_bits < 0:
                raise argparse.ArgumentTypeError("Entropy levels must be non-negative.")
            rounded_bits = round(target_bits)
            if not math.isclose(target_bits, rounded_bits, abs_tol=1e-9):
                raise argparse.ArgumentTypeError(
                    "Use integer bit levels or the token 'max'. "
                    "Uniform supports of size 2^h are used deliberately."
                )
            support_size = 2 ** int(rounded_bits)
            if support_size > maximum_count:
                raise argparse.ArgumentTypeError(
                    f"Entropy level {target_bits:g} requires {support_size} hypotheses, "
                    f"but the universe contains only {maximum_count}. Use 'max' instead."
                )
            label = str(int(rounded_bits))

        if support_size in seen_sizes:
            continue
        seen_sizes.add(support_size)
        levels.append(
            EntropyLevel(
                label=label,
                target_bits=float(target_bits),
                support_size=int(support_size),
                realized_bits=math.log2(support_size),
            )
        )

    if not levels:
        raise argparse.ArgumentTypeError("At least one entropy level is required.")

    levels.sort(key=lambda level: level.support_size)
    return tuple(levels)


def nested_ordering(
    universe_size: int,
    true_index: int,
    rng: np.random.Generator,
) -> np.ndarray:
    others = np.delete(np.arange(universe_size, dtype=np.int32), int(true_index))
    rng.shuffle(others)
    return np.concatenate(
        [np.asarray([true_index], dtype=np.int32), others]
    )


def support_prefix(ordering: np.ndarray, level: EntropyLevel) -> np.ndarray:
    return ordering[: level.support_size]


def sample_independent_worlds(
    theta_support: np.ndarray,
    r_support: np.ndarray,
    sample_size: int,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray]:
    total = int(theta_support.size) * int(r_support.size)
    if total <= sample_size:
        theta_grid = np.repeat(theta_support, r_support.size)
        r_grid = np.tile(r_support, theta_support.size)
        return theta_grid.astype(np.int32), r_grid.astype(np.int16)

    theta_positions = rng.integers(theta_support.size, size=sample_size)
    r_positions = rng.integers(r_support.size, size=sample_size)
    return (
        theta_support[theta_positions].astype(np.int32),
        r_support[r_positions].astype(np.int16),
    )


def sample_coupled_worlds(
    theta_support: np.ndarray,
    r_support: np.ndarray,
    sample_size: int,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray]:
    pair_count = min(theta_support.size, r_support.size)
    if pair_count <= 0:
        raise ValueError("Coupled posterior requires a non-empty paired support.")

    if pair_count <= sample_size:
        return (
            theta_support[:pair_count].astype(np.int32),
            r_support[:pair_count].astype(np.int16),
        )

    positions = rng.integers(pair_count, size=sample_size)
    return (
        theta_support[positions].astype(np.int32),
        r_support[positions].astype(np.int16),
    )


# ==============================================================================
# VECTORIZED WORLD EVALUATION
# ==============================================================================


def world_accepts_candidate_vector(
    model: GlobalModel,
    authentic: np.ndarray,
    candidate: np.ndarray,
    theta_codes: np.ndarray,
    topology_ids: np.ndarray,
) -> np.ndarray:
    template_ids, a, e = decode_theta_arrays(theta_codes)
    topology_ids64 = topology_ids.astype(np.int64)
    topologies = model.topology_array[topology_ids64]

    authentic_semantic = authentic[topologies]
    candidate_semantic = candidate[topologies]
    rows = np.arange(theta_codes.size)

    u_idx = model.template_u[template_ids]
    v_idx = model.template_v[template_ids]
    p_idx = model.template_p[template_ids]
    q_idx = model.template_q[template_ids]
    r_idx = model.template_r[template_ids]

    auth_u = authentic_semantic[rows, u_idx]
    auth_v = authentic_semantic[rows, v_idx]
    auth_p = authentic_semantic[rows, p_idx]
    auth_q = authentic_semantic[rows, q_idx]
    auth_r = authentic_semantic[rows, r_idx]

    b = (auth_p - a * auth_u) % MODULUS
    f = (auth_v - e * auth_u) % MODULUS
    c = (auth_q - auth_v) % MODULUS
    d = (auth_r - auth_u - auth_v) % MODULUS

    cand_u = candidate_semantic[rows, u_idx]
    cand_v = candidate_semantic[rows, v_idx]

    return (
        cand_v == (e * cand_u + f) % MODULUS
    ) & (
        candidate_semantic[rows, p_idx] == (a * cand_u + b) % MODULUS
    ) & (
        candidate_semantic[rows, q_idx] == (cand_v + c) % MODULUS
    ) & (
        candidate_semantic[rows, r_idx] == (cand_u + cand_v + d) % MODULUS
    )


# ==============================================================================
# BOUNDED ADVERSARIAL SOLVER
# ==============================================================================


def propose_candidates_from_worlds(
    model: GlobalModel,
    authentic: np.ndarray,
    theta_codes: np.ndarray,
    topology_ids: np.ndarray,
    alternatives_per_hypothesis: int,
    max_candidate_pool: int,
    rng: np.random.Generator,
) -> List[Tuple[int, ...]]:
    authentic_tuple = tuple(int(v) for v in authentic)
    candidates: set[Tuple[int, ...]] = set()

    for theta_code, topology_id in zip(theta_codes, topology_ids):
        theta = decode_theta(int(theta_code))
        topology = model.topologies[int(topology_id)]
        template = model.templates[theta.template_id]
        family = instantiate_family_from_authentic(
            authentic_selector_state=authentic,
            theta=theta,
            topology=topology,
            model=model,
        )

        authentic_semantic = map_selector_to_semantic(authentic, topology)
        authentic_x_u = int(authentic_semantic[template.free_u])
        alternative_x_values = [
            value for value in range(MODULUS) if value != authentic_x_u
        ]
        rng.shuffle(alternative_x_values)

        for x_u in alternative_x_values[:alternatives_per_hypothesis]:
            semantic = make_semantic_state(family, template, x_u)
            selector_candidate = map_semantic_to_selector(semantic, topology)
            candidate_tuple = tuple(int(v) for v in selector_candidate)
            if candidate_tuple == authentic_tuple:
                continue
            candidates.add(candidate_tuple)
            if len(candidates) >= max_candidate_pool:
                return list(candidates)

    return list(candidates)


def solve_false_candidate_independent(
    model: GlobalModel,
    authentic: np.ndarray,
    theta_support: np.ndarray,
    r_support: np.ndarray,
    proposal_hypotheses: int,
    score_hypotheses: int,
    alternatives_per_hypothesis: int,
    max_candidate_pool: int,
    rng: np.random.Generator,
) -> SolverResult:
    proposal_theta, proposal_r = sample_independent_worlds(
        theta_support=theta_support,
        r_support=r_support,
        sample_size=proposal_hypotheses,
        rng=rng,
    )
    candidates = propose_candidates_from_worlds(
        model=model,
        authentic=authentic,
        theta_codes=proposal_theta,
        topology_ids=proposal_r,
        alternatives_per_hypothesis=alternatives_per_hypothesis,
        max_candidate_pool=max_candidate_pool,
        rng=rng,
    )

    if not candidates:
        return SolverResult(False, None, 0.0, 0, 0)

    score_theta, score_r = sample_independent_worlds(
        theta_support=theta_support,
        r_support=r_support,
        sample_size=score_hypotheses,
        rng=rng,
    )
    scores = np.empty(len(candidates), dtype=float)

    for index, candidate_tuple in enumerate(candidates):
        candidate = np.asarray(candidate_tuple, dtype=np.int16)
        scores[index] = float(
            np.mean(
                world_accepts_candidate_vector(
                    model=model,
                    authentic=authentic,
                    candidate=candidate,
                    theta_codes=score_theta,
                    topology_ids=score_r,
                )
            )
        )

    best_score = float(scores.max())
    best_positions = np.flatnonzero(np.isclose(scores, best_score))
    best_position = int(rng.choice(best_positions))
    best_candidate = candidates[best_position]
    changed = sum(
        int(candidate_value != authentic_value)
        for candidate_value, authentic_value in zip(best_candidate, authentic)
    )

    return SolverResult(
        candidate_found=True,
        candidate=best_candidate,
        posterior_score=best_score,
        changed_selectors=changed,
        proposal_count=len(candidates),
    )


def solve_false_candidate_coupled(
    model: GlobalModel,
    authentic: np.ndarray,
    theta_support: np.ndarray,
    r_support: np.ndarray,
    proposal_hypotheses: int,
    score_hypotheses: int,
    alternatives_per_hypothesis: int,
    max_candidate_pool: int,
    rng: np.random.Generator,
) -> SolverResult:
    proposal_theta, proposal_r = sample_coupled_worlds(
        theta_support, r_support, proposal_hypotheses, rng
    )
    candidates = propose_candidates_from_worlds(
        model=model,
        authentic=authentic,
        theta_codes=proposal_theta,
        topology_ids=proposal_r,
        alternatives_per_hypothesis=alternatives_per_hypothesis,
        max_candidate_pool=max_candidate_pool,
        rng=rng,
    )

    if not candidates:
        return SolverResult(False, None, 0.0, 0, 0)

    score_theta, score_r = sample_coupled_worlds(
        theta_support, r_support, score_hypotheses, rng
    )
    scores = np.empty(len(candidates), dtype=float)

    for index, candidate_tuple in enumerate(candidates):
        candidate = np.asarray(candidate_tuple, dtype=np.int16)
        scores[index] = float(
            np.mean(
                world_accepts_candidate_vector(
                    model=model,
                    authentic=authentic,
                    candidate=candidate,
                    theta_codes=score_theta,
                    topology_ids=score_r,
                )
            )
        )

    best_score = float(scores.max())
    best_positions = np.flatnonzero(np.isclose(scores, best_score))
    best_position = int(rng.choice(best_positions))
    best_candidate = candidates[best_position]
    changed = sum(
        int(candidate_value != authentic_value)
        for candidate_value, authentic_value in zip(best_candidate, authentic)
    )

    return SolverResult(
        candidate_found=True,
        candidate=best_candidate,
        posterior_score=best_score,
        changed_selectors=changed,
        proposal_count=len(candidates),
    )


# ==============================================================================
# STATISTICAL UTILITIES
# ==============================================================================


def wilson_interval(successes: int, trials: int, z: float = 1.959963984540054) -> Tuple[float, float]:
    if trials <= 0:
        return 0.0, 0.0
    p_hat = successes / trials
    denominator = 1.0 + z * z / trials
    center = (p_hat + z * z / (2.0 * trials)) / denominator
    margin = (
        z
        * math.sqrt(
            p_hat * (1.0 - p_hat) / trials
            + z * z / (4.0 * trials * trials)
        )
        / denominator
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def mean_interval(values: Sequence[float], z: float = 1.959963984540054) -> Tuple[float, float]:
    if not values:
        return 0.0, 0.0
    array = np.asarray(values, dtype=float)
    mean = float(np.mean(array))
    if array.size <= 1:
        return mean, mean
    standard_error = float(np.std(array, ddof=1)) / math.sqrt(array.size)
    return max(0.0, mean - z * standard_error), min(1.0, mean + z * standard_error)


def exact_credential_control_probability(
    verifier_population: int,
    coalition_size: int,
    changed_selectors: int,
) -> float:
    if changed_selectors <= 0:
        return 1.0
    if coalition_size < changed_selectors:
        return 0.0
    if changed_selectors > verifier_population:
        return 0.0
    return math.comb(coalition_size, changed_selectors) / math.comb(
        verifier_population, changed_selectors
    )


def coalition_size_from_q(q_value: float, verifier_population: int) -> int:
    return min(
        verifier_population,
        max(0, int(round(float(q_value) * verifier_population))),
    )


# ==============================================================================
# EXPERIMENT
# ==============================================================================


def initialise_raw_record(q_values: Sequence[float]) -> Dict[str, Any]:
    return {
        "candidate_found": 0,
        "pure_success": 0,
        "posterior_scores": [],
        "changed": [],
        "end_to_end": {str(q): [] for q in q_values},
    }


def run_experiment(
    config: ExperimentConfig,
    model: GlobalModel,
) -> Tuple[List[CellResult], List[CoupledResult], Dict[str, int]]:
    independent_raw: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for regime in config.regimes:
        for theta_level in config.theta_levels:
            for r_level in config.r_levels:
                independent_raw[(regime, theta_level.label, r_level.label)] = (
                    initialise_raw_record(config.q_values)
                )

    coupled_levels = [
        level
        for level in config.r_levels
        if level.realized_bits <= config.coupled_max_bits
        and level.support_size <= THETA_COUNT
    ]
    coupled_raw: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for regime in config.regimes:
        for level in coupled_levels:
            coupled_raw[(regime, level.label)] = {
                "pure_success": 0,
                "posterior_scores": [],
                "changed": [],
            }

    controls = {
        "authentic_accept_failures": 0,
        "baseline_noninferability_failures": 0,
        "true_world_support_failures": 0,
        "nested_support_failures": 0,
        "identifying_false_acceptances": 0,
        "equivalence_full_disclosure_failures": 0,
        "q_entropy_coupling_failures": 0,
    }

    for trial_index in range(config.trials):
        trial_rng = np.random.default_rng(
            np.random.SeedSequence([config.seed, trial_index, 1300])
        )

        true_topology_id = int(trial_rng.integers(TOPOLOGY_COUNT))
        true_theta = ThetaCore(
            template_id=int(trial_rng.integers(TEMPLATE_COUNT)),
            a=int(trial_rng.integers(1, MODULUS)),
            e=int(trial_rng.integers(1, MODULUS)),
        )
        true_theta_code = encode_theta(true_theta)
        true_topology = model.topologies[true_topology_id]
        true_template = model.templates[true_theta.template_id]

        # The true hidden offsets and authentic state are sampled independently.
        true_family = InvariantFamily(
            theta=true_theta,
            b=int(trial_rng.integers(MODULUS)),
            c=int(trial_rng.integers(MODULUS)),
            d=int(trial_rng.integers(MODULUS)),
            f=int(trial_rng.integers(MODULUS)),
        )
        true_x_u = int(trial_rng.integers(MODULUS))
        authentic_semantic = make_semantic_state(
            true_family, true_template, true_x_u
        )
        authentic = map_semantic_to_selector(authentic_semantic, true_topology)

        # Every candidate world is instantiated to accept the same authentic data.
        # This explicitly prevents the baseline verifier-visible state from reducing
        # Theta_C or R_int entropy in the ordinary model.
        theta_order = nested_ordering(THETA_COUNT, true_theta_code, trial_rng)
        r_order = nested_ordering(TOPOLOGY_COUNT, true_topology_id, trial_rng)

        if int(theta_order[0]) != true_theta_code or int(r_order[0]) != true_topology_id:
            controls["true_world_support_failures"] += 1
            raise AssertionError("True world not preserved in nested support orderings.")

        # Verify nesting across all configured levels.
        previous_theta: set[int] = set()
        for level in config.theta_levels:
            current = set(int(v) for v in support_prefix(theta_order, level))
            if not previous_theta.issubset(current):
                controls["nested_support_failures"] += 1
                raise AssertionError("Theta_C posterior supports are not nested.")
            previous_theta = current

        previous_r: set[int] = set()
        for level in config.r_levels:
            current = set(int(v) for v in support_prefix(r_order, level))
            if not previous_r.issubset(current):
                controls["nested_support_failures"] += 1
                raise AssertionError("R_int posterior supports are not nested.")
            previous_r = current

        # Sampled non-inferability control: every sampled world accepts X.
        control_theta, control_r = sample_independent_worlds(
            theta_support=theta_order,
            r_support=r_order,
            sample_size=min(256, THETA_COUNT * TOPOLOGY_COUNT),
            rng=trial_rng,
        )
        if not bool(
            np.all(
                world_accepts_candidate_vector(
                    model=model,
                    authentic=authentic,
                    candidate=authentic,
                    theta_codes=control_theta,
                    topology_ids=control_r,
                )
            )
        ):
            controls["baseline_noninferability_failures"] += 1
            raise AssertionError(
                "Authentic data eliminated a candidate world, violating the constructed non-inferability control."
            )

        # The true V_G must accept the authentic state in every regime.
        for regime in config.regimes:
            accepted_authentic, *_ = V_G(
                candidate=authentic,
                authentic=authentic,
                family=true_family,
                template=true_template,
                topology=true_topology,
                regime=regime,
            )
            if not accepted_authentic:
                controls["authentic_accept_failures"] += 1
                raise AssertionError("The authentic state must pass true V_G.")

        # Main entropy grid: independent Theta_C and R_int posteriors.
        solver_cache: Dict[Tuple[str, str], SolverResult] = {}
        for theta_index, theta_level in enumerate(config.theta_levels):
            theta_support = support_prefix(theta_order, theta_level)
            for r_index, r_level in enumerate(config.r_levels):
                r_support = support_prefix(r_order, r_level)
                solver_rng = np.random.default_rng(
                    np.random.SeedSequence(
                        [config.seed, trial_index, theta_index, r_index, 1313]
                    )
                )
                solver_cache[(theta_level.label, r_level.label)] = (
                    solve_false_candidate_independent(
                        model=model,
                        authentic=authentic,
                        theta_support=theta_support,
                        r_support=r_support,
                        proposal_hypotheses=config.proposal_hypotheses,
                        score_hypotheses=config.score_hypotheses,
                        alternatives_per_hypothesis=config.alternatives_per_hypothesis,
                        max_candidate_pool=config.max_candidate_pool,
                        rng=solver_rng,
                    )
                )

        for regime in config.regimes:
            for theta_level in config.theta_levels:
                for r_level in config.r_levels:
                    record = independent_raw[
                        (regime, theta_level.label, r_level.label)
                    ]
                    solver = solver_cache[(theta_level.label, r_level.label)]
                    record["posterior_scores"].append(solver.posterior_score)
                    record["changed"].append(solver.changed_selectors)

                    pure_success = False
                    if solver.candidate_found and solver.candidate is not None:
                        record["candidate_found"] += 1
                        candidate = np.asarray(solver.candidate, dtype=np.int16)
                        if np.array_equal(candidate, authentic):
                            raise AssertionError("The solver returned the authentic state.")

                        accepted, local_ok, relational_ok, invariant_ok = V_G(
                            candidate=candidate,
                            authentic=authentic,
                            family=true_family,
                            template=true_template,
                            topology=true_topology,
                            regime=regime,
                        )
                        if not local_ok or not relational_ok:
                            raise AssertionError(
                                "Solver candidates must remain locally admissible."
                            )
                        pure_success = bool(accepted and invariant_ok)
                        if pure_success:
                            record["pure_success"] += 1

                    # q appears only here.  It cannot modify the posterior entropy
                    # or pure solver outcome in the ordinary CNVS separation.
                    h_theta_before_q = theta_level.realized_bits
                    h_r_before_q = r_level.realized_bits
                    for q_value in config.q_values:
                        coalition_size = coalition_size_from_q(
                            q_value, config.verifier_population
                        )
                        auth_probability = exact_credential_control_probability(
                            verifier_population=config.verifier_population,
                            coalition_size=coalition_size,
                            changed_selectors=solver.changed_selectors,
                        )
                        record["end_to_end"][str(q_value)].append(
                            auth_probability if pure_success else 0.0
                        )
                        if (
                            h_theta_before_q != theta_level.realized_bits
                            or h_r_before_q != r_level.realized_bits
                        ):
                            controls["q_entropy_coupling_failures"] += 1
                            raise AssertionError(
                                "q changed posterior entropy in the ordinary model."
                            )

                    if regime == "identifying" and pure_success:
                        controls["identifying_false_acceptances"] += 1
                        raise AssertionError(
                            "Identifying V_G accepted a false state."
                        )

                    if (
                        regime == "equivalence"
                        and theta_level.support_size == 1
                        and r_level.support_size == 1
                        and not pure_success
                    ):
                        controls["equivalence_full_disclosure_failures"] += 1
                        raise AssertionError(
                            "Full disclosure must permit a coherent false alternative in the equivalence regime."
                        )

        # Pathological coupling control.  The marginal supports are paired rather
        # than combined independently, reducing joint entropy and violating the
        # intended CNVS decoupling between Theta_C and R_int.
        coupled_solver_cache: Dict[str, SolverResult] = {}
        for level_index, level in enumerate(coupled_levels):
            pair_count = level.support_size
            theta_support = theta_order[:pair_count]
            r_support = r_order[:pair_count]
            coupled_rng = np.random.default_rng(
                np.random.SeedSequence([config.seed, trial_index, level_index, 1399])
            )
            coupled_solver_cache[level.label] = solve_false_candidate_coupled(
                model=model,
                authentic=authentic,
                theta_support=theta_support,
                r_support=r_support,
                proposal_hypotheses=config.proposal_hypotheses,
                score_hypotheses=config.score_hypotheses,
                alternatives_per_hypothesis=config.alternatives_per_hypothesis,
                max_candidate_pool=config.max_candidate_pool,
                rng=coupled_rng,
            )

        for regime in config.regimes:
            for level in coupled_levels:
                record = coupled_raw[(regime, level.label)]
                solver = coupled_solver_cache[level.label]
                record["posterior_scores"].append(solver.posterior_score)
                record["changed"].append(solver.changed_selectors)

                pure_success = False
                if solver.candidate_found and solver.candidate is not None:
                    candidate = np.asarray(solver.candidate, dtype=np.int16)
                    accepted, local_ok, relational_ok, invariant_ok = V_G(
                        candidate=candidate,
                        authentic=authentic,
                        family=true_family,
                        template=true_template,
                        topology=true_topology,
                        regime=regime,
                    )
                    if not local_ok or not relational_ok:
                        raise AssertionError(
                            "Coupled-solver candidates must remain locally admissible."
                        )
                    pure_success = bool(accepted and invariant_ok)
                    if pure_success:
                        record["pure_success"] += 1

                if regime == "identifying" and pure_success:
                    controls["identifying_false_acceptances"] += 1
                    raise AssertionError(
                        "Identifying V_G accepted a false state in coupled control."
                    )

    independent_cells: List[CellResult] = []
    for regime in config.regimes:
        for theta_level in config.theta_levels:
            for r_level in config.r_levels:
                record = independent_raw[
                    (regime, theta_level.label, r_level.label)
                ]
                pure_count = int(record["pure_success"])
                pure_rate = pure_count / config.trials
                pure_low, pure_high = wilson_interval(pure_count, config.trials)

                end_rates: Dict[str, float] = {}
                end_low: Dict[str, float] = {}
                end_high: Dict[str, float] = {}
                for q_value in config.q_values:
                    key = str(q_value)
                    values = record["end_to_end"][key]
                    end_rates[key] = float(np.mean(values))
                    end_low[key], end_high[key] = mean_interval(values)

                independent_cells.append(
                    CellResult(
                        scenario="independent_side_channel",
                        regime=regime,
                        theta_level=theta_level.label,
                        r_level=r_level.label,
                        target_h_theta=theta_level.target_bits,
                        target_h_r=r_level.target_bits,
                        realized_h_theta=theta_level.realized_bits,
                        realized_h_r=r_level.realized_bits,
                        realized_h_joint=(
                            theta_level.realized_bits + r_level.realized_bits
                        ),
                        theta_support_size=theta_level.support_size,
                        r_support_size=r_level.support_size,
                        joint_support_size=(
                            theta_level.support_size * r_level.support_size
                        ),
                        trials=config.trials,
                        candidate_found_count=int(record["candidate_found"]),
                        candidate_found_rate=(
                            int(record["candidate_found"]) / config.trials
                        ),
                        pure_false_accept_count=pure_count,
                        pure_false_accept_rate=pure_rate,
                        pure_ci_low=pure_low,
                        pure_ci_high=pure_high,
                        mean_posterior_score=float(
                            np.mean(record["posterior_scores"])
                        ),
                        mean_changed_selectors=float(np.mean(record["changed"])),
                        end_to_end_rates=end_rates,
                        end_to_end_ci_low=end_low,
                        end_to_end_ci_high=end_high,
                    )
                )

    coupled_results: List[CoupledResult] = []
    for regime in config.regimes:
        for level in coupled_levels:
            record = coupled_raw[(regime, level.label)]
            pure_count = int(record["pure_success"])
            pure_rate = pure_count / config.trials
            pure_low, pure_high = wilson_interval(pure_count, config.trials)
            coupled_results.append(
                CoupledResult(
                    regime=regime,
                    pair_level=level.label,
                    marginal_support_size=level.support_size,
                    realized_h_theta=level.realized_bits,
                    realized_h_r=level.realized_bits,
                    realized_h_joint=level.realized_bits,
                    trials=config.trials,
                    pure_false_accept_count=pure_count,
                    pure_false_accept_rate=pure_rate,
                    pure_ci_low=pure_low,
                    pure_ci_high=pure_high,
                    mean_posterior_score=float(
                        np.mean(record["posterior_scores"])
                    ),
                    mean_changed_selectors=float(np.mean(record["changed"])),
                )
            )

    return independent_cells, coupled_results, controls


# ==============================================================================
# OUTPUTS
# ==============================================================================


def write_csv(path: Path, cells: Sequence[CellResult]) -> None:
    fieldnames = [
        "scenario",
        "regime",
        "theta_level",
        "r_level",
        "target_h_theta",
        "target_h_r",
        "realized_h_theta",
        "realized_h_r",
        "realized_h_joint",
        "theta_support_size",
        "r_support_size",
        "joint_support_size",
        "trials",
        "candidate_found_count",
        "candidate_found_rate",
        "pure_false_accept_count",
        "pure_false_accept_rate",
        "pure_ci_low",
        "pure_ci_high",
        "mean_posterior_score",
        "mean_changed_selectors",
        "end_to_end_rates_json",
        "end_to_end_ci_low_json",
        "end_to_end_ci_high_json",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for cell in cells:
            row = asdict(cell)
            row["end_to_end_rates_json"] = json.dumps(row.pop("end_to_end_rates"))
            row["end_to_end_ci_low_json"] = json.dumps(row.pop("end_to_end_ci_low"))
            row["end_to_end_ci_high_json"] = json.dumps(row.pop("end_to_end_ci_high"))
            writer.writerow(row)


def write_coupled_csv(path: Path, rows: Sequence[CoupledResult]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def cell_lookup(
    cells: Sequence[CellResult],
    regime: str,
    theta_label: str,
    r_label: str,
) -> CellResult:
    for cell in cells:
        if (
            cell.regime == regime
            and cell.theta_level == theta_label
            and cell.r_level == r_label
        ):
            return cell
    raise KeyError((regime, theta_label, r_label))


def plot_heatmap(
    matrix: np.ndarray,
    x_labels: Sequence[str],
    y_labels: Sequence[str],
    title: str,
    xlabel: str,
    ylabel: str,
    output_path: Path,
    value_format: str = ".3f",
) -> None:
    plt.figure(figsize=(11, 8))
    image = plt.imshow(matrix, origin="lower", aspect="auto")
    plt.colorbar(image, label="Observed rate")
    plt.xticks(range(len(x_labels)), x_labels)
    plt.yticks(range(len(y_labels)), y_labels)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            plt.text(
                column,
                row,
                format(float(matrix[row, column]), value_format),
                ha="center",
                va="center",
                fontsize=8,
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def create_plots(
    output_dir: Path,
    config: ExperimentConfig,
    cells: Sequence[CellResult],
    coupled_results: Sequence[CoupledResult],
) -> None:
    theta_labels = [level.label for level in config.theta_levels]
    r_labels = [level.label for level in config.r_levels]

    for regime in config.regimes:
        matrix = np.empty((len(config.r_levels), len(config.theta_levels)))
        for r_index, r_level in enumerate(config.r_levels):
            for theta_index, theta_level in enumerate(config.theta_levels):
                matrix[r_index, theta_index] = cell_lookup(
                    cells, regime, theta_level.label, r_level.label
                ).pure_false_accept_rate

        plot_heatmap(
            matrix=matrix,
            x_labels=theta_labels,
            y_labels=r_labels,
            title=(
                f"Test 12 — Executed false acceptance ({regime}, Auth=1)"
            ),
            xlabel="Residual min-entropy h_Theta (bits; 'max' = full universe)",
            ylabel="Residual min-entropy h_R (bits; 'max' = full universe)",
            output_path=output_dir
            / f"test_12_{regime}_pure_false_accept_heatmap.png",
        )

    # End-to-end heatmaps for each q in the equivalence regime.
    for q_value in config.q_values:
        matrix = np.empty((len(config.r_levels), len(config.theta_levels)))
        for r_index, r_level in enumerate(config.r_levels):
            for theta_index, theta_level in enumerate(config.theta_levels):
                cell = cell_lookup(
                    cells, "equivalence", theta_level.label, r_level.label
                )
                matrix[r_index, theta_index] = cell.end_to_end_rates[str(q_value)]

        plot_heatmap(
            matrix=matrix,
            x_labels=theta_labels,
            y_labels=r_labels,
            title=(
                "Test 12 — End-to-end false acceptance "
                f"(equivalence, q={q_value:g})"
            ),
            xlabel="Residual min-entropy h_Theta (bits)",
            ylabel="Residual min-entropy h_R (bits)",
            output_path=output_dir
            / f"test_12_end_to_end_q_{str(q_value).replace('.', '_')}.png",
        )

    # Curves versus h_Theta for selected h_R levels.
    plt.figure(figsize=(11, 7))
    selected_r_levels = config.r_levels[:: max(1, len(config.r_levels) // 4)]
    x_values = [level.realized_bits for level in config.theta_levels]
    for r_level in selected_r_levels:
        y_values = [
            cell_lookup(cells, "equivalence", theta_level.label, r_level.label)
            .pure_false_accept_rate
            for theta_level in config.theta_levels
        ]
        plt.plot(x_values, y_values, marker="o", label=f"h_R={r_level.realized_bits:.2f}")
    plt.xlabel("Residual min-entropy h_Theta (bits)")
    plt.ylabel("Executed P(false coherent acceptance | Auth=1)")
    plt.title("Test 12 — False acceptance as Theta_C uncertainty increases")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "test_12_false_accept_vs_h_theta.png", dpi=180)
    plt.close()

    # Ordinary CNVS q sweep at maximum configured entropies.
    max_theta = config.theta_levels[-1]
    max_r = config.r_levels[-1]
    ordinary_cell = cell_lookup(
        cells, "equivalence", max_theta.label, max_r.label
    )
    q_values = list(config.q_values)
    end_values = [ordinary_cell.end_to_end_rates[str(q)] for q in q_values]
    pure_values = [ordinary_cell.pure_false_accept_rate for _ in q_values]

    plt.figure(figsize=(10, 7))
    plt.plot(q_values, pure_values, marker="o", label="Pure epistemic rate (q-independent)")
    plt.plot(q_values, end_values, marker="s", label="End-to-end with credential control")
    plt.xlabel("Colluding verifier fraction q")
    plt.ylabel("Rate")
    plt.title(
        "Test 12 — Ordinary CNVS separation: q changes credentials, not h_Theta"
    )
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "test_12_ordinary_q_separation.png", dpi=180)
    plt.close()

    # Independent vs pathologically coupled diagonal control.
    coupled_equivalence = [
        row for row in coupled_results if row.regime == "equivalence"
    ]
    if coupled_equivalence:
        x_values = [row.realized_h_theta for row in coupled_equivalence]
        coupled_values = [row.pure_false_accept_rate for row in coupled_equivalence]
        independent_values = []
        for row in coupled_equivalence:
            matching_theta = min(
                config.theta_levels,
                key=lambda level: abs(level.realized_bits - row.realized_h_theta),
            )
            matching_r = min(
                config.r_levels,
                key=lambda level: abs(level.realized_bits - row.realized_h_r),
            )
            independent_values.append(
                cell_lookup(
                    cells,
                    "equivalence",
                    matching_theta.label,
                    matching_r.label,
                ).pure_false_accept_rate
            )

        plt.figure(figsize=(10, 7))
        plt.plot(
            x_values,
            independent_values,
            marker="o",
            label="Independent posterior (h_joint = h_Theta + h_R)",
        )
        plt.plot(
            x_values,
            coupled_values,
            marker="s",
            label="Pathologically coupled posterior (h_joint = h_Theta = h_R)",
        )
        plt.xlabel("Marginal residual min-entropy h_Theta = h_R (bits)")
        plt.ylabel("Executed P(false coherent acceptance | Auth=1)")
        plt.title("Test 12 — Independent versus correlated hidden structures")
        plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
        plt.legend()
        plt.tight_layout()
        plt.savefig(
            output_dir / "test_12_independent_vs_coupled.png", dpi=180
        )
        plt.close()


def print_summary(
    config: ExperimentConfig,
    cells: Sequence[CellResult],
    coupled_results: Sequence[CoupledResult],
    controls: Mapping[str, int],
) -> None:
    print("=" * 90)
    print("CNVS TEST 12 — ENTROPY-CALIBRATED THETA_C / R_int LEAKAGE")
    print("=" * 90)
    print(f"trials per cell: {config.trials}")
    print(
        "Theta_C levels: "
        + ", ".join(
            f"{level.label}:{level.realized_bits:.3f}b"
            for level in config.theta_levels
        )
    )
    print(
        "R_int levels: "
        + ", ".join(
            f"{level.label}:{level.realized_bits:.3f}b"
            for level in config.r_levels
        )
    )
    print(f"q values: {config.q_values}")
    print()

    candidate_pairs = [
        (config.theta_levels[0], config.r_levels[0]),
        (
            config.theta_levels[len(config.theta_levels) // 2],
            config.r_levels[len(config.r_levels) // 2],
        ),
        (config.theta_levels[-1], config.r_levels[-1]),
    ]
    representative_pairs = []
    seen_pairs: set[Tuple[str, str]] = set()
    for theta_level, r_level in candidate_pairs:
        key = (theta_level.label, r_level.label)
        if key not in seen_pairs:
            representative_pairs.append((theta_level, r_level))
            seen_pairs.add(key)

    for regime in config.regimes:
        print(f"[{regime} regime]")
        for theta_level, r_level in representative_pairs:
            cell = cell_lookup(
                cells, regime, theta_level.label, r_level.label
            )
            print(
                f"  h_Theta={cell.realized_h_theta:6.3f}, "
                f"h_R={cell.realized_h_r:6.3f}, "
                f"h_joint={cell.realized_h_joint:6.3f} -> "
                f"P_FA={cell.pure_false_accept_rate:.6f} "
                f"[{cell.pure_ci_low:.6f}, {cell.pure_ci_high:.6f}]"
            )
        print()

    max_theta = config.theta_levels[-1]
    max_r = config.r_levels[-1]
    ordinary = cell_lookup(cells, "equivalence", max_theta.label, max_r.label)
    print("[ordinary CNVS separation at maximum configured entropy]")
    print(
        f"  fixed h_Theta={ordinary.realized_h_theta:.6f} bits, "
        f"fixed h_R={ordinary.realized_h_r:.6f} bits"
    )
    print(f"  pure epistemic P_FA={ordinary.pure_false_accept_rate:.8f}")
    for q_value in config.q_values:
        print(
            f"  q={q_value:5.2f} -> end-to-end rate="
            f"{ordinary.end_to_end_rates[str(q_value)]:.8f}"
        )
    print()

    if coupled_results:
        print("[pathological Theta_C / R_int coupling control]")
        for row in coupled_results:
            if row.regime != "equivalence":
                continue
            print(
                f"  marginal h={row.realized_h_theta:.3f}, "
                f"joint h={row.realized_h_joint:.3f} -> "
                f"P_FA={row.pure_false_accept_rate:.6f}"
            )
        print()

    print("[control failures]")
    for key, value in controls.items():
        print(f"  {key}: {value}")


# ==============================================================================
# CLI
# ==============================================================================


def parse_probability_list(text: str) -> Tuple[float, ...]:
    values = tuple(float(token.strip()) for token in text.split(",") if token.strip())
    if not values:
        raise argparse.ArgumentTypeError("At least one q value is required.")
    if any(value < 0.0 or value > 1.0 for value in values):
        raise argparse.ArgumentTypeError("q values must lie in [0,1].")
    return tuple(sorted(set(values)))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Entropy-calibrated CNVS topology / invariant leakage experiment "
            "with executed coherent false-state injection."
        )
    )
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument(
        "--theta-bits",
        default="0,1,2,4,6,8,10,max",
        help="Comma-separated integer bit levels or 'max'.",
    )
    parser.add_argument(
        "--r-bits",
        default="0,1,2,3,4,5,6,max",
        help="Comma-separated integer bit levels or 'max'.",
    )
    parser.add_argument(
        "--q-values",
        type=parse_probability_list,
        default=parse_probability_list("0.25,0.5,0.75,0.9,1"),
    )
    parser.add_argument("--verifier-population", type=int, default=64)
    parser.add_argument("--proposal-hypotheses", type=int, default=20)
    parser.add_argument("--score-hypotheses", type=int, default=96)
    parser.add_argument("--alternatives-per-hypothesis", type=int, default=2)
    parser.add_argument("--max-candidate-pool", type=int, default=80)
    parser.add_argument("--coupled-max-bits", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20260715)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Default: test_12_entropy_outputs beside the script or in cwd.",
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if args.trials <= 0:
        raise ValueError("--trials must be positive.")
    if args.verifier_population < SELECTOR_COUNT:
        raise ValueError("--verifier-population must be at least SELECTOR_COUNT.")
    for name in (
        "proposal_hypotheses",
        "score_hypotheses",
        "alternatives_per_hypothesis",
        "max_candidate_pool",
    ):
        if getattr(args, name) <= 0:
            raise ValueError(f"--{name.replace('_', '-')} must be positive.")
    if args.coupled_max_bits < 0:
        raise ValueError("--coupled-max-bits must be non-negative.")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    if argv is None and running_inside_notebook_kernel():
        args, _unknown = parser.parse_known_args()
    else:
        args = parser.parse_args(argv)
    validate_args(args)

    theta_levels = parse_entropy_level_list(args.theta_bits, THETA_COUNT)
    r_levels = parse_entropy_level_list(args.r_bits, TOPOLOGY_COUNT)

    config = ExperimentConfig(
        trials=args.trials,
        theta_levels=theta_levels,
        r_levels=r_levels,
        q_values=tuple(args.q_values),
        verifier_population=args.verifier_population,
        proposal_hypotheses=args.proposal_hypotheses,
        score_hypotheses=args.score_hypotheses,
        alternatives_per_hypothesis=args.alternatives_per_hypothesis,
        max_candidate_pool=args.max_candidate_pool,
        coupled_max_bits=args.coupled_max_bits,
        seed=args.seed,
        regimes=("equivalence", "identifying"),
    )

    output_dir = args.output_dir
    if output_dir is None:
        output_dir = runtime_base_directory() / "test_12_entropy_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    model = build_global_model()
    cells, coupled_results, controls = run_experiment(config, model)

    write_csv(output_dir / "test_12_entropy_grid.csv", cells)
    write_coupled_csv(
        output_dir / "test_12_pathological_coupling.csv", coupled_results
    )

    json_payload = {
        "test_name": (
            "Test 12 - Entropy-Calibrated Leakage of Theta_C and R_int "
            "with Executed Coherent False-State Injection"
        ),
        "classification": "executable in-silico Monte Carlo experiment",
        "config": {
            "trials": config.trials,
            "theta_levels": [asdict(level) for level in config.theta_levels],
            "r_levels": [asdict(level) for level in config.r_levels],
            "q_values": config.q_values,
            "verifier_population": config.verifier_population,
            "proposal_hypotheses": config.proposal_hypotheses,
            "score_hypotheses": config.score_hypotheses,
            "alternatives_per_hypothesis": config.alternatives_per_hypothesis,
            "max_candidate_pool": config.max_candidate_pool,
            "coupled_max_bits": config.coupled_max_bits,
            "seed": config.seed,
            "theta_universe": THETA_COUNT,
            "topology_universe": TOPOLOGY_COUNT,
            "maximum_h_theta": math.log2(THETA_COUNT),
            "maximum_h_r": math.log2(TOPOLOGY_COUNT),
        },
        "controls": controls,
        "independent_cells": [asdict(cell) for cell in cells],
        "pathological_coupling": [asdict(row) for row in coupled_results],
        "interpretive_limits": [
            "Theta_C entropy is experimentally calibrated, not measured from a deployment.",
            "q affects only the separate credential-control projection.",
            "False acceptance is decided by an executed true V_G call.",
            "The equivalence regime deliberately admits alternative coherent states.",
            "The identifying regime deliberately accepts only the authentic state.",
            "Zero observed events do not prove zero underlying probability.",
        ],
    }
    with (output_dir / "test_12_entropy_results.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(json_payload, handle, indent=2)

    create_plots(output_dir, config, cells, coupled_results)
    print_summary(config, cells, coupled_results, controls)
    print()
    print(f"Outputs written to: {output_dir}")
    return 0


if __name__ == "__main__":
    exit_code = main()
    # IPython/Colab renders even SystemExit(0) as a red exception block.
    # Preserve the conventional process exit code in a terminal, but avoid
    # raising a harmless SystemExit inside notebook kernels.
    if not running_inside_notebook_kernel():
        raise SystemExit(exit_code)
