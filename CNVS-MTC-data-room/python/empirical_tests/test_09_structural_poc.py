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

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap


# ==============================================================================
# TEST 9 — STRUCTURAL PROOF-OF-CONCEPT
#
# Test Name: # Test 9 - Structural Proof-of-Concept (Decoupled Pedagogical Validation Model)
# filename = "test_09_structural_poc.py"
#
# CLASSIFICATION:
# This is an application-layer structural proof-of-concept and automated
# pedagogical test suite.
#
# It is NOT:
#   - a statistical simulation;
#   - an empirical proof of CNVS security;
#   - a complete implementation of the formal CNVS architecture;
#   - an independent proof of the CNVS theorems.
#
# PURPOSE:
# The code explicitly models:
#   1. terminal fragmentation and opaque selector generation;
#   2. strict software separation between local task knowledge and global state;
#   3. deliberately weak local validation V_L;
#   4. authenticated origin and message integrity, separated from semantic truth;
#   5. exact submission-set completeness;
#   6. recomputation of local admissibility at the global layer;
#   7. a hidden invariant family C_int covering the full pedagogical payload;
#   8. structured short-circuit Global-Veto outcomes;
#   9. legacy epoch-style replay protection, retained intentionally;
#  10. a separate full-instance-refresh replay scenario;
#  11. explicit structural-assumption failure after C_int disclosure.
#
# PEDAGOGICAL ABSTRACTION:
# In the formal theory, C_int is a potentially complex family of structural,
# semantic, relational, and topological constraints. Here it is represented by:
#
#   c_1: geometric floor/area consistency;
#   c_2: hidden owner commitment;
#   c_3: hidden city commitment;
#   c_4: basic semantic-domain constraints.
#
# This implements option B: the entire toy payload is covered by the hidden
# invariant family, rather than merely declaring partial coverage.
#
# EPOCH / REFRESH NOTE:
# The epoch field is intentionally retained as a compact approximation of
# application-layer replay protection used in many current systems.
#
# It is NOT presented as the core CNVS replay-resistance mechanism.
#
# A separate scenario performs a full verification-instance refresh with:
#   - new selectors;
#   - new verifier credentials;
#   - new hidden salts;
#   - new role binding;
#   - new theta_C parameters;
#   - a new epoch label.
#
# Old evidence then fails against the refreshed instance even before semantic
# validation, because it belongs to a stale structural instance.
# ==============================================================================


# ==============================================================================
# ENUMERATIONS AND STRUCTURED RESULTS
# ==============================================================================

class BarrierStatus(Enum):
    PASS = 1
    FAIL = 0
    SKIPPED = -1


@dataclass(frozen=True)
class ValidationResult:
    """
    Structured result of the application-layer validation pipeline.
    """
    accepted: bool
    failed_barrier: Optional[str]
    outcomes: Mapping[str, BarrierStatus]
    message: str


@dataclass(frozen=True)
class ScenarioCase:
    """
    One deterministic structural test case.
    """
    label: str
    description: str
    validation_state: "CNVS_Semantic_State"
    evidence: Mapping[str, "LocalEvidence"]
    expected_accepted: bool
    expected_failed_barrier: Optional[str]


@dataclass(frozen=True)
class ScenarioExecution:
    """
    Executed scenario plus its structured result.
    """
    case: ScenarioCase
    result: ValidationResult


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass(frozen=True)
class TerminalFragment:
    """
    Private internal representation of a terminal fragment.

    Local verifiers never receive this object. In particular, they do not receive
    semantic_key, true_value, theta_C, hidden binding, or unrelated fragments.
    """
    semantic_key: str
    selector: str
    typ: type
    true_value: Any


@dataclass(frozen=True)
class LocalTaskSpec:
    """
    Minimal local task view.

    This is the only semantic specification required by V_L. It enforces the
    local/global knowledge separation at the software-interface level.
    """
    selector: str
    expected_type: type
    assigned_verifier_id: str
    epoch: str


@dataclass(frozen=True)
class LocalEvidence:
    """
    Evidence submitted by one local verifier.

    The signature authenticates:
      - verifier identity;
      - selector;
      - epoch / verification instance;
      - observed value;
      - claimed local-admissibility result.

    Authentication proves origin and message integrity. It does NOT prove that
    the observed value is semantically true.
    """
    verifier_id: str
    selector: str
    observed_value: Any
    local_admissible: bool
    signature: str
    epoch: str


@dataclass(frozen=True)
class PublicInvariantCategory:
    """
    C_pub: public invariant category.

    The ordinary threat model may grant this category to the adversary while
    keeping instantiated parameters, role binding, and exact constraints hidden.
    """
    name: str
    description: str


@dataclass(frozen=True)
class InternalInvariantParameters:
    """
    theta_C: hidden instantiated parameters of the pedagogical invariant family.
    """
    scale_factor: int
    geometric_target: int

    owner_commitment_salt: str
    owner_commitment: str

    city_commitment_salt: str
    city_commitment: str

    description: str


@dataclass(frozen=True)
class LeakedInternalView:
    """
    Explicit representation of the information granted in the structural
    assumption-break scenario.

    Credential compromise is modeled separately and is not implied by C_int
    disclosure.
    """
    scale_factor: int
    geometric_target: int
    hidden_relation_binding: Mapping[str, str]


@dataclass
class CNVS_Semantic_State:
    """
    Trusted private global state.

    The state stores the full pedagogical C_int and trusted verifier credentials.
    V_L never receives this object.
    """
    fragments: Dict[str, TerminalFragment]
    local_tasks: Dict[str, LocalTaskSpec]

    verifier_secrets: Dict[str, bytes]
    selector_to_verifier: Dict[str, str]

    epoch: str
    C_pub: PublicInvariantCategory
    theta_C: InternalInvariantParameters
    hidden_relation_binding: Dict[str, str]


# ==============================================================================
# CANONICALIZATION AND CRYPTOGRAPHIC UTILITIES
# ==============================================================================

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_typed_value(value: Any) -> Dict[str, Any]:
    """
    Canonical typed representation for the primitive values used in this PoC.

    Including the exact Python type prevents bool/int ambiguity in signed data.
    """
    if type(value) not in {str, int, float, bool, type(None)}:
        raise TypeError(
            "This pedagogical canonicalizer supports only primitive JSON values."
        )

    return {
        "python_type": type(value).__qualname__,
        "value": value,
    }


def canonical_evidence_payload(
    verifier_id: str,
    selector: str,
    epoch: str,
    observed_value: Any,
    local_admissible: bool,
) -> bytes:
    payload = {
        "verifier_id": verifier_id,
        "selector": selector,
        "epoch": epoch,
        "observed_value": canonical_typed_value(observed_value),
        "local_admissible": bool(local_admissible),
    }

    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def make_message_signature(
    verifier_secret: bytes,
    verifier_id: str,
    selector: str,
    epoch: str,
    observed_value: Any,
    local_admissible: bool,
) -> str:
    """
    HMAC-based application-layer authentication surrogate.

    This is stronger than the previous unsalted digest because it binds the
    verifier and complete submitted message. It is still a pedagogical surrogate
    rather than a public-key signature or full PKI deployment.
    """
    payload = canonical_evidence_payload(
        verifier_id=verifier_id,
        selector=selector,
        epoch=epoch,
        observed_value=observed_value,
        local_admissible=local_admissible,
    )

    return hmac.new(
        verifier_secret,
        payload,
        hashlib.sha256,
    ).hexdigest()


def make_selector(semantic_key: str, salt: str) -> str:
    """
    Produce a 128-bit opaque selector.

    The longer truncation avoids the previous 48-bit pedagogical selector.
    """
    return "tau_" + sha256_text(f"{semantic_key}|{salt}")[:32]


def make_hidden_value_commitment(
    role: str,
    salt: str,
    value: Any,
) -> str:
    payload = {
        "role": role,
        "salt": salt,
        "typed_value": canonical_typed_value(value),
    }

    return sha256_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


# ==============================================================================
# TRUSTED ENVIRONMENT GENERATION
# ==============================================================================

def build_execution_environment(
    payload: Mapping[str, Any],
    epoch: str,
    *,
    scale_factor: int,
) -> CNVS_Semantic_State:
    """
    Convert a standard payload into one private pedagogical CNVS instance.

    Every invocation performs a fresh instance construction:
      - new selector salts;
      - new selectors;
      - new verifier credentials;
      - new hidden commitment salts;
      - new binding objects.
    """
    required_keys = {
        "Proprietario",
        "Città",
        "Piano",
        "Metratura",
    }

    if set(payload.keys()) != required_keys:
        raise ValueError(
            f"Payload keys must be exactly {sorted(required_keys)}."
        )

    if type(scale_factor) is not int or scale_factor <= 0:
        raise ValueError("scale_factor must be a strictly positive integer.")

    fragments: Dict[str, TerminalFragment] = {}
    local_tasks: Dict[str, LocalTaskSpec] = {}
    verifier_secrets: Dict[str, bytes] = {}
    selector_to_verifier: Dict[str, str] = {}

    # 1. Terminal decomposition and unique opaque selector generation.
    for index, (semantic_key, value) in enumerate(payload.items(), start=1):
        while True:
            selector_salt = secrets.token_hex(32)
            selector = make_selector(semantic_key, selector_salt)

            if selector not in fragments:
                break

        verifier_id = f"verifier_{index:02d}"
        verifier_secret = secrets.token_bytes(32)

        fragment = TerminalFragment(
            semantic_key=semantic_key,
            selector=selector,
            typ=type(value),
            true_value=value,
        )

        task = LocalTaskSpec(
            selector=selector,
            expected_type=type(value),
            assigned_verifier_id=verifier_id,
            epoch=epoch,
        )

        fragments[selector] = fragment
        local_tasks[selector] = task
        verifier_secrets[verifier_id] = verifier_secret
        selector_to_verifier[selector] = verifier_id

    # 2. Public category.
    C_pub = PublicInvariantCategory(
        name="structural_semantic_consistency",
        description=(
            "Public category only: the candidate state is governed by hidden "
            "semantic and relational constraints."
        ),
    )

    # 3. Hidden role binding, used as a pedagogical R_int surrogate.
    selector_by_key = {
        fragment.semantic_key: selector
        for selector, fragment in fragments.items()
    }

    hidden_relation_binding = {
        "owner_role": selector_by_key["Proprietario"],
        "city_role": selector_by_key["Città"],
        "floor_role": selector_by_key["Piano"],
        "area_role": selector_by_key["Metratura"],
    }

    # 4. Hidden instantiated parameters.
    geometric_target = (
        payload["Piano"] * scale_factor
        - payload["Metratura"]
    )

    owner_commitment_salt = secrets.token_hex(32)
    city_commitment_salt = secrets.token_hex(32)

    theta_C = InternalInvariantParameters(
        scale_factor=scale_factor,
        geometric_target=geometric_target,
        owner_commitment_salt=owner_commitment_salt,
        owner_commitment=make_hidden_value_commitment(
            "owner",
            owner_commitment_salt,
            payload["Proprietario"],
        ),
        city_commitment_salt=city_commitment_salt,
        city_commitment=make_hidden_value_commitment(
            "city",
            city_commitment_salt,
            payload["Città"],
        ),
        description=(
            "Pedagogical hidden parameters covering geometric, owner, city, "
            "and semantic-domain constraints."
        ),
    )

    return CNVS_Semantic_State(
        fragments=fragments,
        local_tasks=local_tasks,
        verifier_secrets=verifier_secrets,
        selector_to_verifier=selector_to_verifier,
        epoch=epoch,
        C_pub=C_pub,
        theta_C=theta_C,
        hidden_relation_binding=hidden_relation_binding,
    )


# ==============================================================================
# LOCAL VALIDATION V_L AND EVIDENCE EMISSION
# ==============================================================================

def V_L(
    task: LocalTaskSpec,
    observed_value: Any,
) -> bool:
    """
    Deliberately weak local validation.

    It checks only exact Python type equality. Exact equality is used instead of
    isinstance so that bool is not accepted as int.
    """
    return type(observed_value) is task.expected_type


def emit_evidence(
    task: LocalTaskSpec,
    verifier_secret: bytes,
    observed_value: Any,
    *,
    epoch_override: Optional[str] = None,
    use_valid_signature: bool = True,
    claimed_local_admissible: Optional[bool] = None,
) -> LocalEvidence:
    """
    Emit signed evidence from one assigned verifier.

    claimed_local_admissible exists only to construct adversarial test cases.
    The global layer never trusts it blindly and recomputes V_L.
    """
    epoch = (
        epoch_override
        if epoch_override is not None
        else task.epoch
    )

    recomputed_local = V_L(
        task,
        observed_value,
    )

    local_claim = (
        recomputed_local
        if claimed_local_admissible is None
        else bool(claimed_local_admissible)
    )

    signature = make_message_signature(
        verifier_secret=verifier_secret,
        verifier_id=task.assigned_verifier_id,
        selector=task.selector,
        epoch=epoch,
        observed_value=observed_value,
        local_admissible=local_claim,
    )

    if not use_valid_signature:
        signature = "invalid_signature"

    return LocalEvidence(
        verifier_id=task.assigned_verifier_id,
        selector=task.selector,
        observed_value=observed_value,
        local_admissible=local_claim,
        signature=signature,
        epoch=epoch,
    )


# ==============================================================================
# VALIDATION BARRIERS
# ==============================================================================

def Cons_Submission_Set(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> bool:
    """
    Barrier 1: exact submission-set completeness and selector consistency.

    This function deliberately avoids claiming that it implements the entire
    formal relational topology R. It verifies the exact pedagogical submission
    set expected by the current instance.
    """
    expected_selectors = set(state.fragments.keys())
    received_selectors = set(evidence.keys())

    if expected_selectors != received_selectors:
        return False

    for selector, item in evidence.items():
        if item.selector != selector:
            return False

        expected_verifier = state.selector_to_verifier.get(selector)

        if item.verifier_id != expected_verifier:
            return False

    return True


def Verify_Identity_And_Message(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> bool:
    """
    Barrier 2: verifier identity, instance binding, and message integrity.

    The signature binds the complete evidence message but does not assert
    semantic truth.
    """
    for selector, item in evidence.items():
        expected_verifier = state.selector_to_verifier.get(selector)

        if expected_verifier is None:
            return False

        if item.verifier_id != expected_verifier:
            return False

        if item.epoch != state.epoch:
            return False

        verifier_secret = state.verifier_secrets.get(
            item.verifier_id
        )

        if verifier_secret is None:
            return False

        expected_signature = make_message_signature(
            verifier_secret=verifier_secret,
            verifier_id=item.verifier_id,
            selector=item.selector,
            epoch=item.epoch,
            observed_value=item.observed_value,
            local_admissible=item.local_admissible,
        )

        if not hmac.compare_digest(
            item.signature,
            expected_signature,
        ):
            return False

    return True


def Verify_Local_Admissibility(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> bool:
    """
    Barrier 3: trusted recomputation of V_L.

    The submitted local_admissible flag is treated as a signed claim, not as an
    authoritative result. The global layer recomputes V_L from the minimal task
    specification and rejects false local-status claims.
    """
    for selector, item in evidence.items():
        task = state.local_tasks.get(selector)

        if task is None:
            return False

        recomputed = V_L(
            task,
            item.observed_value,
        )

        if not recomputed:
            return False

        if item.local_admissible is not recomputed:
            return False

    return True


# ==============================================================================
# HIDDEN INVARIANT FAMILY C_int
# ==============================================================================

def c_1_geometric_consistency(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> bool:
    floor_selector = state.hidden_relation_binding["floor_role"]
    area_selector = state.hidden_relation_binding["area_role"]

    floor_value = evidence[floor_selector].observed_value
    area_value = evidence[area_selector].observed_value

    candidate_result = (
        floor_value * state.theta_C.scale_factor
        - area_value
    )

    return candidate_result == state.theta_C.geometric_target


def c_2_owner_binding(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> bool:
    owner_selector = state.hidden_relation_binding["owner_role"]
    owner_value = evidence[owner_selector].observed_value

    candidate_commitment = make_hidden_value_commitment(
        "owner",
        state.theta_C.owner_commitment_salt,
        owner_value,
    )

    return hmac.compare_digest(
        candidate_commitment,
        state.theta_C.owner_commitment,
    )


def c_3_city_binding(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> bool:
    city_selector = state.hidden_relation_binding["city_role"]
    city_value = evidence[city_selector].observed_value

    candidate_commitment = make_hidden_value_commitment(
        "city",
        state.theta_C.city_commitment_salt,
        city_value,
    )

    return hmac.compare_digest(
        candidate_commitment,
        state.theta_C.city_commitment,
    )


def c_4_semantic_domain(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> bool:
    owner_selector = state.hidden_relation_binding["owner_role"]
    city_selector = state.hidden_relation_binding["city_role"]
    floor_selector = state.hidden_relation_binding["floor_role"]
    area_selector = state.hidden_relation_binding["area_role"]

    owner_value = evidence[owner_selector].observed_value
    city_value = evidence[city_selector].observed_value
    floor_value = evidence[floor_selector].observed_value
    area_value = evidence[area_selector].observed_value

    return (
        type(owner_value) is str
        and len(owner_value.strip()) > 0
        and type(city_value) is str
        and len(city_value.strip()) > 0
        and type(floor_value) is int
        and floor_value >= 0
        and type(area_value) is int
        and area_value > 0
    )


def Inv_C(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> bool:
    """
    Evaluate the complete pedagogical hidden invariant family.
    """
    hidden_constraints: Sequence[
        Callable[
            [CNVS_Semantic_State, Mapping[str, LocalEvidence]],
            bool,
        ]
    ] = (
        c_1_geometric_consistency,
        c_2_owner_binding,
        c_3_city_binding,
        c_4_semantic_domain,
    )

    return all(
        constraint(state, evidence)
        for constraint in hidden_constraints
    )


# ==============================================================================
# STRUCTURED GLOBAL VALIDATION PIPELINE
# ==============================================================================

BARRIER_ORDER = (
    "Submission_Set",
    "Identity",
    "Local_Validation",
    "Inv_C",
)


def VG(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> ValidationResult:
    """
    Execute the pedagogical application-layer validation pipeline.

    Identity and message authentication are operational admissibility barriers.
    Inv_C is the hidden semantic/global constraint barrier.
    """
    outcomes: Dict[str, BarrierStatus] = {
        name: BarrierStatus.SKIPPED
        for name in BARRIER_ORDER
    }

    if not Cons_Submission_Set(state, evidence):
        outcomes["Submission_Set"] = BarrierStatus.FAIL

        return ValidationResult(
            accepted=False,
            failed_barrier="Submission_Set",
            outcomes=outcomes,
            message=(
                "VETO: current-instance submission set is incomplete "
                "or structurally inconsistent."
            ),
        )

    outcomes["Submission_Set"] = BarrierStatus.PASS

    if not Verify_Identity_And_Message(state, evidence):
        outcomes["Identity"] = BarrierStatus.FAIL

        return ValidationResult(
            accepted=False,
            failed_barrier="Identity",
            outcomes=outcomes,
            message=(
                "VETO: verifier identity, instance binding, "
                "or message integrity failed."
            ),
        )

    outcomes["Identity"] = BarrierStatus.PASS

    if not Verify_Local_Admissibility(state, evidence):
        outcomes["Local_Validation"] = BarrierStatus.FAIL

        return ValidationResult(
            accepted=False,
            failed_barrier="Local_Validation",
            outcomes=outcomes,
            message=(
                "VETO: recomputed local admissibility failed "
                "or contradicted the signed local claim."
            ),
        )

    outcomes["Local_Validation"] = BarrierStatus.PASS

    if not Inv_C(state, evidence):
        outcomes["Inv_C"] = BarrierStatus.FAIL

        return ValidationResult(
            accepted=False,
            failed_barrier="Inv_C",
            outcomes=outcomes,
            message=(
                "VETO: hidden pedagogical invariant family C_int failed."
            ),
        )

    outcomes["Inv_C"] = BarrierStatus.PASS

    return ValidationResult(
        accepted=True,
        failed_barrier=None,
        outcomes=outcomes,
        message=(
            "ACCEPTED: candidate state satisfies the implemented "
            "pedagogical invariant family."
        ),
    )


# ==============================================================================
# TRUSTED TEST-HARNESS HELPERS
# ==============================================================================

def get_selector_by_semantic_key(
    state: CNVS_Semantic_State,
    semantic_key: str,
) -> str:
    return next(
        selector
        for selector, fragment in state.fragments.items()
        if fragment.semantic_key == semantic_key
    )


def emit_for_semantic_key(
    state: CNVS_Semantic_State,
    semantic_key: str,
    observed_value: Any,
    **kwargs: Any,
) -> LocalEvidence:
    selector = get_selector_by_semantic_key(
        state,
        semantic_key,
    )

    task = state.local_tasks[selector]
    secret = state.verifier_secrets[
        task.assigned_verifier_id
    ]

    return emit_evidence(
        task=task,
        verifier_secret=secret,
        observed_value=observed_value,
        **kwargs,
    )


def assemble_evidence(
    state: CNVS_Semantic_State,
    values_by_key: Mapping[str, Any],
    **kwargs: Any,
) -> Dict[str, LocalEvidence]:
    evidence: Dict[str, LocalEvidence] = {}

    for semantic_key, observed_value in values_by_key.items():
        item = emit_for_semantic_key(
            state,
            semantic_key,
            observed_value,
            **kwargs,
        )

        evidence[item.selector] = item

    return evidence


def leak_internal_view(
    state: CNVS_Semantic_State,
) -> LeakedInternalView:
    """
    Explicitly disclose the geometric parameters and hidden role binding.

    This does not disclose verifier secrets.
    """
    return LeakedInternalView(
        scale_factor=state.theta_C.scale_factor,
        geometric_target=state.theta_C.geometric_target,
        hidden_relation_binding=dict(
            state.hidden_relation_binding
        ),
    )


def craft_alternative_candidate_from_leak(
    state: CNVS_Semantic_State,
    leaked_view: LeakedInternalView,
    *,
    desired_floor: int,
) -> Dict[str, LocalEvidence]:
    """
    Build an alternative candidate after two separately declared grants:
      1. C_int role/parameter disclosure;
      2. control of the assigned verifier credentials in this test harness.

    C_int disclosure alone does not reveal authentication credentials.
    """
    if type(desired_floor) is not int or desired_floor < 0:
        raise ValueError(
            "desired_floor must be a non-negative integer."
        )

    alternative_area = (
        desired_floor * leaked_view.scale_factor
        - leaked_view.geometric_target
    )

    if alternative_area <= 0:
        raise ValueError(
            "Selected desired_floor produces a non-positive area."
        )

    # Owner and city remain bound to their hidden commitments.
    values = {
        "Proprietario": "Enzo",
        "Città": "Milano",
        "Piano": desired_floor,
        "Metratura": alternative_area,
    }

    return assemble_evidence(
        state,
        values,
    )


def print_public_adversary_view(
    state: CNVS_Semantic_State,
) -> None:
    public_view = {
        "epoch": state.epoch,
        "public_selectors": list(
            state.fragments.keys()
        ),
        "C_pub_granted": state.C_pub.name,
        "C_int_hidden": [
            "theta_C",
            "hidden_relation_binding",
            "true_values",
            "commitment_salts",
            "verifier_credentials",
        ],
    }

    print(
        json.dumps(
            public_view,
            indent=2,
            ensure_ascii=False,
        )
    )


# ==============================================================================
# SCENARIO CONSTRUCTION
# ==============================================================================

def build_scenario_suite() -> List[ScenarioCase]:
    payload = {
        "Proprietario": "Enzo",
        "Città": "Milano",
        "Piano": 3,
        "Metratura": 120,
    }

    state = build_execution_environment(
        payload,
        epoch="epoch_zero",
        scale_factor=40,
    )

    refreshed_state = build_execution_environment(
        payload,
        epoch="epoch_one",
        scale_factor=47,
    )

    honest_values = dict(payload)

    honest_evidence = assemble_evidence(
        state,
        honest_values,
    )

    # Scenario 2: exact submission-set failure.
    missing_fragment_values = {
        "Proprietario": "Enzo",
        "Piano": 3,
        "Metratura": 120,
    }

    # Scenario 3: typed semantic forgery.
    geometric_forgery_values = {
        "Proprietario": "Enzo",
        "Città": "Milano",
        "Piano": 1,
        "Metratura": 120,
    }

    # Scenario 4: option B coverage check for owner/city.
    owner_city_forgery_values = {
        "Proprietario": "Mallory",
        "Città": "Roma",
        "Piano": 3,
        "Metratura": 120,
    }

    # Scenario 5: valid signature over a false local-admissibility claim.
    false_local_claim = assemble_evidence(
        state,
        honest_values,
    )

    floor_selector = get_selector_by_semantic_key(
        state,
        "Piano",
    )

    floor_task = state.local_tasks[floor_selector]
    floor_secret = state.verifier_secrets[
        floor_task.assigned_verifier_id
    ]

    false_local_claim[floor_selector] = emit_evidence(
        task=floor_task,
        verifier_secret=floor_secret,
        observed_value=True,
        claimed_local_admissible=True,
    )

    # Scenario 6: message tampering after a valid signature.
    tampered_message = dict(honest_evidence)
    tampered_floor = tampered_message[floor_selector]

    tampered_message[floor_selector] = replace(
        tampered_floor,
        observed_value=1,
    )

    # Scenario 7: intentionally retained legacy epoch-style replay proxy.
    wrong_epoch_evidence = assemble_evidence(
        state,
        honest_values,
        epoch_override="wrong_epoch",
    )

    # Scenario 8: full structural-instance refresh replay.
    # Old selectors, credentials, binding, theta_C, and epoch are presented to
    # the refreshed instance.
    full_refresh_replay = dict(honest_evidence)

    # Scenario 9: explicit hidden-C_int structural assumption break.
    leaked_view = leak_internal_view(state)

    alternative_valid_evidence = craft_alternative_candidate_from_leak(
        state,
        leaked_view,
        desired_floor=1,
    )

    return [
        ScenarioCase(
            label="Honest baseline",
            description=(
                "All submitted values are authentic, locally admissible, "
                "and globally invariant-consistent."
            ),
            validation_state=state,
            evidence=honest_evidence,
            expected_accepted=True,
            expected_failed_barrier=None,
        ),
        ScenarioCase(
            label="Missing fragment",
            description=(
                "One expected terminal submission is absent."
            ),
            validation_state=state,
            evidence=assemble_evidence(
                state,
                missing_fragment_values,
            ),
            expected_accepted=False,
            expected_failed_barrier="Submission_Set",
        ),
        ScenarioCase(
            label="Geometric forgery",
            description=(
                "A well-typed false floor value passes V_L but violates c_1."
            ),
            validation_state=state,
            evidence=assemble_evidence(
                state,
                geometric_forgery_values,
            ),
            expected_accepted=False,
            expected_failed_barrier="Inv_C",
        ),
        ScenarioCase(
            label="Owner/city forgery",
            description=(
                "Option B coverage check: owner and city are well typed "
                "but violate hidden commitments c_2 and c_3."
            ),
            validation_state=state,
            evidence=assemble_evidence(
                state,
                owner_city_forgery_values,
            ),
            expected_accepted=False,
            expected_failed_barrier="Inv_C",
        ),
        ScenarioCase(
            label="False local claim",
            description=(
                "A compromised verifier signs local_admissible=True for bool "
                "where exact int is required. Global recomputation detects it."
            ),
            validation_state=state,
            evidence=false_local_claim,
            expected_accepted=False,
            expected_failed_barrier="Local_Validation",
        ),
        ScenarioCase(
            label="Message tampering",
            description=(
                "The observed value is changed after signature generation."
            ),
            validation_state=state,
            evidence=tampered_message,
            expected_accepted=False,
            expected_failed_barrier="Identity",
        ),
        ScenarioCase(
            label="Epoch replay proxy",
            description=(
                "Legacy epoch-style replay protection rejects evidence "
                "signed for a different epoch label."
            ),
            validation_state=state,
            evidence=wrong_epoch_evidence,
            expected_accepted=False,
            expected_failed_barrier="Identity",
        ),
        ScenarioCase(
            label="Full refresh replay",
            description=(
                "Evidence from the old structural instance is presented to a "
                "fully refreshed state with new selectors, credentials, "
                "binding, theta_C, and epoch."
            ),
            validation_state=refreshed_state,
            evidence=full_refresh_replay,
            expected_accepted=False,
            expected_failed_barrier="Submission_Set",
        ),
        ScenarioCase(
            label="C_int disclosure break",
            description=(
                "Hidden role/parameter disclosure plus separately granted "
                "credential control allows synthesis of an alternative state "
                "that satisfies the implemented invariant family."
            ),
            validation_state=state,
            evidence=alternative_valid_evidence,
            expected_accepted=True,
            expected_failed_barrier=None,
        ),
    ]


# ==============================================================================
# AUTOMATED EXECUTION AND ASSERTIONS
# ==============================================================================

def execute_scenario_suite(
    cases: Sequence[ScenarioCase],
) -> List[ScenarioExecution]:
    executions: List[ScenarioExecution] = []

    for case in cases:
        result = VG(
            case.validation_state,
            case.evidence,
        )

        if result.accepted is not case.expected_accepted:
            raise AssertionError(
                f"{case.label}: expected accepted="
                f"{case.expected_accepted}, received {result.accepted}."
            )

        if result.failed_barrier != case.expected_failed_barrier:
            raise AssertionError(
                f"{case.label}: expected failed_barrier="
                f"{case.expected_failed_barrier!r}, received "
                f"{result.failed_barrier!r}."
            )

        executions.append(
            ScenarioExecution(
                case=case,
                result=result,
            )
        )

    return executions


def print_scenario_results(
    executions: Sequence[ScenarioExecution],
) -> None:
    print(
        "--- CNVS STRUCTURAL PROOF-OF-CONCEPT "
        "AND AUTOMATED TEST SUITE ---"
    )

    if executions:
        print("\n[Adversary Public View]")
        print_public_adversary_view(
            executions[0].case.validation_state
        )

    for index, execution in enumerate(
        executions,
        start=1,
    ):
        case = execution.case
        result = execution.result

        print(f"\n[Scenario {index}] {case.label}")
        print("Condition:", case.description)
        print("Result:", result.message)

        barrier_text = {
            barrier: status.name
            for barrier, status in result.outcomes.items()
        }

        print(
            "Barrier outcomes:",
            json.dumps(
                barrier_text,
                ensure_ascii=False,
            ),
        )

    print(
        "\n[Automated Assertions] "
        f"{len(executions)} / {len(executions)} scenarios passed."
    )


# ==============================================================================
# PLOT-DATA COLLECTION FROM THE SAME EXECUTIONS
# ==============================================================================

def submitted_local_admissibility_rate(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> float:
    """
    Recomputed local admissibility among submitted evidence.

    Unknown stale selectors count as locally unavailable/invalid.
    """
    if not evidence:
        return 0.0

    admissible = 0

    for selector, item in evidence.items():
        task = state.local_tasks.get(selector)

        if task is not None and V_L(
            task,
            item.observed_value,
        ):
            admissible += 1

    return admissible / len(evidence)


def submission_completeness_ratio(
    state: CNVS_Semantic_State,
    evidence: Mapping[str, LocalEvidence],
) -> float:
    expected = set(state.fragments.keys())

    if not expected:
        return 1.0

    received_current = expected.intersection(
        evidence.keys()
    )

    return len(received_current) / len(expected)


def collect_test09_plot_data(
    executions: Sequence[ScenarioExecution],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for execution in executions:
        case = execution.case
        result = execution.result

        row: Dict[str, Any] = {
            "scenario": case.label,
            "submitted_local_rate": (
                submitted_local_admissibility_rate(
                    case.validation_state,
                    case.evidence,
                )
            ),
            "submission_completeness": (
                submission_completeness_ratio(
                    case.validation_state,
                    case.evidence,
                )
            ),
            "V_G": (
                BarrierStatus.PASS.value
                if result.accepted
                else BarrierStatus.FAIL.value
            ),
        }

        for barrier in BARRIER_ORDER:
            row[barrier] = result.outcomes[
                barrier
            ].value

        rows.append(row)

    return rows


# ==============================================================================
# PLOT GENERATION
# ==============================================================================

def plot_test09(
    rows: Sequence[Mapping[str, Any]],
    out_dir: Path,
    *,
    show_plots: bool = True,
) -> None:
    """
    Generate explanatory plots from the exact scenario executions.

    PASS  =  1
    FAIL  =  0
    SKIPPED = -1
    """
    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    labels = [
        str(row["scenario"])
        for row in rows
    ]

    x = np.arange(
        len(labels)
    )

    width = 0.25

    # --------------------------------------------------------------------------
    # Plot 1: submitted-local admissibility, completeness, global acceptance.
    # --------------------------------------------------------------------------
    plt.figure(
        figsize=(14, 7)
    )

    plt.bar(
        x - width,
        [
            row["submitted_local_rate"]
            for row in rows
        ],
        width,
        label="Local admissibility among submitted evidence",
    )

    plt.bar(
        x,
        [
            row["submission_completeness"]
            for row in rows
        ],
        width,
        label="Current-instance submission completeness",
    )

    plt.bar(
        x + width,
        [
            1 if row["V_G"] == 1 else 0
            for row in rows
        ],
        width,
        label="Final application-layer acceptance",
    )

    plt.xticks(
        x,
        labels,
        rotation=24,
        ha="right",
    )

    plt.ylim(
        0,
        1.1,
    )

    plt.ylabel(
        "Rate / binary outcome"
    )

    plt.title(
        "CNVS Test 9: Local Admissibility, "
        "Submission Completeness, and Final Acceptance"
    )

    plt.grid(
        True,
        axis="y",
        linestyle="--",
        linewidth=0.5,
        alpha=0.65,
    )

    plt.legend()
    plt.tight_layout()

    output_1 = (
        out_dir
        / "test_09_local_completeness_global_acceptance.png"
    )

    plt.savefig(
        output_1,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 2: tri-state short-circuit barrier matrix.
    # --------------------------------------------------------------------------
    barriers = [
        *BARRIER_ORDER,
        "V_G",
    ]

    values = np.array(
        [
            [
                int(row[barrier])
                for barrier in barriers
            ]
            for row in rows
        ],
        dtype=int,
    )

    fig, ax = plt.subplots(
        figsize=(11, 7)
    )

    cmap = ListedColormap(
        [
            "#6e7681",  # SKIPPED
            "#d62728",  # FAIL
            "#2ca02c",  # PASS
        ]
    )

    norm = BoundaryNorm(
        [-1.5, -0.5, 0.5, 1.5],
        cmap.N,
    )

    ax.imshow(
        values,
        cmap=cmap,
        norm=norm,
        aspect="auto",
    )

    ax.set_xticks(
        np.arange(
            len(barriers)
        )
    )

    ax.set_yticks(
        np.arange(
            len(labels)
        )
    )

    ax.set_xticklabels(
        barriers
    )

    ax.set_yticklabels(
        labels
    )

    plt.setp(
        ax.get_xticklabels(),
        rotation=20,
        ha="right",
        rotation_mode="anchor",
    )

    label_for_value = {
        BarrierStatus.PASS.value: "PASS",
        BarrierStatus.FAIL.value: "FAIL",
        BarrierStatus.SKIPPED.value: "SKIPPED",
    }

    for row_index in range(
        len(labels)
    ):
        for column_index in range(
            len(barriers)
        ):
            value = int(
                values[
                    row_index,
                    column_index,
                ]
            )

            ax.text(
                column_index,
                row_index,
                label_for_value[value],
                ha="center",
                va="center",
                color="white",
                fontweight="bold",
                fontsize=8.5,
            )

    ax.set_title(
        "CNVS Test 9: Structured Short-Circuit "
        "Validation Outcomes"
    )

    fig.tight_layout()

    output_2 = (
        out_dir
        / "test_09_validation_barrier_outcomes.png"
    )

    plt.savefig(
        output_2,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()


# ==============================================================================
# MAIN
# ==============================================================================

def main() -> None:
    cases = build_scenario_suite()

    executions = execute_scenario_suite(
        cases
    )

    print_scenario_results(
        executions
    )

    rows = collect_test09_plot_data(
        executions
    )

    output_dir = Path(
        "figures/test_09"
    )

    plot_test09(
        rows,
        output_dir,
        show_plots=True,
    )

    print("\n[Plot Output]")
    print(
        "Saved:",
        output_dir
        / "test_09_local_completeness_global_acceptance.png",
    )
    print(
        "Saved:",
        output_dir
        / "test_09_validation_barrier_outcomes.png",
    )
    print(
        "Absolute folder:",
        output_dir.resolve(),
    )


if __name__ == "__main__":
    main()
