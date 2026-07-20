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
import hashlib
import hmac
import json
import math
import random
import statistics
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

import matplotlib.pyplot as plt
import numpy as np


# ==============================================================================
# TEST 10 — ADVANCED STRUCTURAL-SEMANTIC ADVERSARIAL MODEL
#
# Test Name: Test 10 - Advanced Hybrid Structural-Monte Carlo Adversarial Model (Full-Coverage Structural-Semantic Consistency).
# filename = "test_10_full_structural_semantic_model.py"
#
# CLASSIFICATION:
# This program is an executable hybrid structural / Monte Carlo adversarial
# model. It is not an empirical proof of CNVS security and does not independently
# prove the CNVS theorems.
#
# WHAT IS EXECUTED:
#   1. Fresh opaque selectors at every verification instance.
#   2. Randomized injective assignment of terminal fragments to verifiers.
#   3. Strict local-task / private-global-state separation.
#   4. Message-bound verifier authentication through an HMAC surrogate.
#   5. Trusted recomputation of exact local type/domain admissibility.
#   6. A hidden structural-semantic invariant family covering every fragment.
#   7. A hidden topology refreshed at every verification instance.
#   8. One-shot dependent inference whose conditional probability is capped.
#   9. Blind false-state synthesis followed by actual V_G execution.
#  10. C_int-disclosure synthesis followed by actual V_G execution.
#  11. Full structural refresh and stale-evidence rejection.
#
# IMPORTANT INTERPRETIVE LIMITS:
#   - HMAC is a pedagogical authentication surrogate, not a deployed PKI.
#   - The semantic policies are stylized executable domain rules.
#   - The topology-leak parameter is an edge-disclosure probability, not the
#     formal information-theoretic gamma_top quantity.
#   - The bounded-inference comparison curve is a simplified injective reference,
#     not a theorem proved by this script.
#   - Zero observed false acceptances are not interpreted as zero probability.
#   - Colab/Jupyter kernel arguments are ignored only in notebook execution;
#     ordinary terminal argument parsing remains strict.
# ==============================================================================


PRIME = 1_000_003


# ==============================================================================
# BASIC UTILITIES
# ==============================================================================

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def rng_token_hex(
    rnd: random.Random,
    nbytes: int = 32,
) -> str:
    return "".join(
        f"{rnd.getrandbits(8):02x}"
        for _ in range(nbytes)
    )


def canonical_typed_value(value: Any) -> Dict[str, Any]:
    if type(value) not in {str, int, float, bool, type(None)}:
        raise TypeError(
            "The pedagogical canonicalizer supports primitive JSON values only."
        )

    return {
        "python_type": type(value).__qualname__,
        "value": value,
    }


def make_selector(
    semantic_key: str,
    salt: str,
) -> str:
    """
    Produce a 128-bit opaque selector.
    """
    return "tau_" + sha256_text(
        f"{semantic_key}|{salt}"
    )[:32]


def canonical_evidence_payload(
    verifier_id: str,
    selector: str,
    instance_id: str,
    observed_value: Any,
    local_admissible: bool,
) -> bytes:
    payload = {
        "verifier_id": verifier_id,
        "selector": selector,
        "instance_id": instance_id,
        "observed_value": canonical_typed_value(
            observed_value
        ),
        "local_admissible": bool(
            local_admissible
        ),
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
    instance_id: str,
    observed_value: Any,
    local_admissible: bool,
) -> str:
    """
    Authenticate verifier origin, instance binding, and complete message
    integrity. This does not assert semantic truth.
    """
    payload = canonical_evidence_payload(
        verifier_id=verifier_id,
        selector=selector,
        instance_id=instance_id,
        observed_value=observed_value,
        local_admissible=local_admissible,
    )

    return hmac.new(
        verifier_secret,
        payload,
        hashlib.sha256,
    ).hexdigest()


def stable_hidden_feature(
    value: Any,
    salt: str,
) -> int:
    """
    Hidden feature used only for the auxiliary finite-field consistency
    fingerprint. It is not presented as semantic understanding.
    """
    raw = json.dumps(
        canonical_typed_value(value),
        sort_keys=True,
        ensure_ascii=False,
    )

    return int(
        sha256_text(f"{salt}|{raw}")[:16],
        16,
    ) % PRIME


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass(frozen=True)
class DomainSpec:
    name: str
    typ: type
    values: Tuple[Any, ...]


@dataclass(frozen=True)
class PrivateFragment:
    semantic_key: str
    selector: str
    typ: type
    true_value: Any
    domain: DomainSpec


@dataclass(frozen=True)
class LocalTaskView:
    """
    Minimal view delivered to one assigned verifier.
    """
    selector: str
    expected_type: type
    domain_name: str
    allowed_values: Tuple[Any, ...]
    instance_id: str
    verifier_id: str


@dataclass(frozen=True)
class LocalEvidence:
    selector: str
    observed_value: Any
    local_admissible: bool
    signature: str
    instance_id: str
    verifier_id: str


@dataclass(frozen=True)
class PublicInvariantCategory:
    name: str
    description: str


@dataclass(frozen=True)
class HiddenConstraint:
    """
    Executable hidden structural-semantic rule.

    params are private instantiated parameters. selectors encode the hidden role
    binding for the rule.
    """
    cid: str
    kind: str
    semantic_group_label: str
    selectors: Tuple[str, ...]
    params: Mapping[str, Any]


@dataclass(frozen=True)
class HiddenPolynomialFingerprint:
    """
    Auxiliary finite-field consistency fingerprint.

    It supplements the semantic rules but is not called a semantic law.
    """
    cid: str
    selectors: Tuple[str, ...]
    feature_salts: Tuple[str, ...]
    linear_coeffs: Tuple[int, ...]
    quadratic_coeffs: Tuple[int, ...]
    pair_coeffs: Tuple[int, ...]
    target: int
    modulus: int = PRIME


@dataclass
class PrivateCNVSInstance:
    fragments: Dict[str, PrivateFragment]
    local_tasks: Dict[str, LocalTaskView]

    assignment: Dict[str, str]
    verifier_secrets: Dict[str, bytes]

    instance_id: str
    C_pub: PublicInvariantCategory

    semantic_constraints: List[HiddenConstraint]
    polynomial_fingerprints: List[HiddenPolynomialFingerprint]

    hidden_topology_edges: Set[Tuple[str, str]]
    critical_selectors: Set[str]


@dataclass(frozen=True)
class AdversaryView:
    selectors: Tuple[str, ...]
    compromised_local_tasks: Mapping[str, LocalTaskView]
    C_pub: PublicInvariantCategory

    leaked_metadata_edges: Set[Tuple[str, str]]

    compromised_values: Mapping[str, Any]
    compromised_secrets: Mapping[str, bytes]
    compromised_verifiers: Set[str]

    C_int_leaked: bool = False


@dataclass(frozen=True)
class SimulationConfig:
    trials: int = 100_000
    n_verifiers: int = 64

    edge_disclosure_probability: float = 0.12

    dependent_infer_base: float = 0.015
    dependent_infer_rho: float = 0.35
    p_infer_cap: float = 0.45
    p_identity_after_infer: float = 0.15

    blind_attempts: int = 1
    leak_solver_attempts: int = 250

    seed: int = 42


# ==============================================================================
# DECLARATION AND DOMAIN UNIVERSE
# ==============================================================================

def default_payload() -> Dict[str, Any]:
    return {
        "owner_id": "owner_042",
        "city_code": "MIL",
        "asset_class": "government",
        "floor": 3,
        "area_sqm": 120,
        "parcel_zone": "Z7",
        "risk_tier": 6,
        "clearance_level": 4,
        "facility_class": "S",
        "access_count": 48,
        "device_count": 17,
        "data_sensitivity": 6,
        "audit_class": "restricted",
        "device_firmware_class": "hardened",
        "network_zone": "segmented",
        "operator_role": "admin",
    }


def domain_specs() -> Dict[str, DomainSpec]:
    return {
        "owner_id": DomainSpec(
            "private_identifier",
            str,
            tuple(f"owner_{i:03d}" for i in range(100)),
        ),
        "city_code": DomainSpec(
            "geo_code",
            str,
            ("MIL", "ROM", "TOR", "GEN", "NAP", "BOL", "FIR"),
        ),
        "asset_class": DomainSpec(
            "asset_class",
            str,
            ("residential", "industrial", "government", "restricted"),
        ),
        "floor": DomainSpec(
            "integer_level",
            int,
            tuple(range(-2, 31)),
        ),
        "area_sqm": DomainSpec(
            "bounded_measure",
            int,
            tuple(range(40, 401, 5)),
        ),
        "parcel_zone": DomainSpec(
            "zone_code",
            str,
            tuple(f"Z{i}" for i in range(1, 15)),
        ),
        "risk_tier": DomainSpec(
            "risk_tier",
            int,
            tuple(range(1, 10)),
        ),
        "clearance_level": DomainSpec(
            "clearance_level",
            int,
            tuple(range(0, 6)),
        ),
        "facility_class": DomainSpec(
            "facility_class",
            str,
            ("A", "B", "C", "D", "S"),
        ),
        "access_count": DomainSpec(
            "count",
            int,
            tuple(range(0, 200)),
        ),
        "device_count": DomainSpec(
            "count",
            int,
            tuple(range(1, 80)),
        ),
        "data_sensitivity": DomainSpec(
            "sensitivity",
            int,
            tuple(range(1, 8)),
        ),
        "audit_class": DomainSpec(
            "audit_class",
            str,
            ("open", "internal", "restricted", "classified"),
        ),
        "device_firmware_class": DomainSpec(
            "firmware_class",
            str,
            ("legacy", "standard", "hardened", "certified"),
        ),
        "network_zone": DomainSpec(
            "network_zone",
            str,
            ("flat", "segmented", "isolated", "airgapped"),
        ),
        "operator_role": DomainSpec(
            "operator_role",
            str,
            ("guest", "user", "admin", "root"),
        ),
    }


# ==============================================================================
# HIDDEN SEMANTIC CONSTRAINT FAMILY
# ==============================================================================

def owner_numeric_id(owner_id: str) -> int:
    prefix = "owner_"

    if not owner_id.startswith(prefix):
        return -1

    suffix = owner_id[len(prefix):]

    if not suffix.isdigit():
        return -1

    return int(suffix)


def check_semantic_constraint(
    constraint: HiddenConstraint,
    candidate_values: Mapping[str, Any],
) -> bool:
    values = [
        candidate_values[selector]
        for selector in constraint.selectors
    ]

    kind = constraint.kind
    params = constraint.params

    if kind == "owner_bucket":
        owner_value = values[0]
        numeric = owner_numeric_id(owner_value)

        return (
            numeric >= 0
            and numeric % int(params["modulus"])
            == int(params["residue"])
        )

    if kind == "city_zone_asset":
        candidate_tuple = tuple(values)

        return candidate_tuple in set(
            tuple(item)
            for item in params["allowed_tuples"]
        )

    if kind == "floor_area_relation":
        floor_value, area_value = values

        return (
            area_value
            == int(params["scale"]) * floor_value
            + int(params["offset"])
        )

    if kind == "risk_clearance_sensitivity":
        risk, clearance, sensitivity = values

        return (
            clearance
            + int(params["clearance_margin"])
            >= sensitivity
            and risk >= sensitivity
            and risk <= int(params["max_risk"])
        )

    if kind == "facility_device_density":
        facility, device_count, area = values

        return (
            facility in set(params["allowed_facilities"])
            and device_count
            * int(params["area_per_device"])
            <= area
        )

    if kind == "access_device_relation":
        access_count, device_count = values

        return (
            access_count
            >= int(params["minimum_multiplier"])
            * device_count
        )

    if kind == "audit_policy":
        audit_class, sensitivity, clearance = values

        if audit_class in {"restricted", "classified"}:
            return (
                sensitivity >= int(params["minimum_sensitivity"])
                and clearance >= int(params["minimum_clearance"])
            )

        return True

    if kind == "firmware_network_facility":
        firmware, network, facility = values

        if firmware in {"hardened", "certified"}:
            return (
                network in set(params["secure_networks"])
                and facility in set(params["secure_facilities"])
            )

        return True

    if kind == "operator_access_risk":
        operator, access_count, risk, clearance = values

        if operator in {"admin", "root"}:
            return (
                access_count <= int(params["maximum_access"])
                and risk <= int(params["maximum_risk"])
                and clearance >= int(params["minimum_clearance"])
            )

        return True

    if kind == "asset_network_audit":
        asset_class, network, audit_class = values

        if asset_class in {"government", "restricted"}:
            return (
                network in set(params["allowed_networks"])
                and audit_class in set(params["allowed_audits"])
            )

        return True

    raise ValueError(
        f"Unknown hidden constraint kind: {kind}"
    )


def build_hidden_semantic_constraints(
    key_to_selector: Mapping[str, str],
    payload: Mapping[str, Any],
    domains: Mapping[str, DomainSpec],
    rnd: random.Random,
) -> List[HiddenConstraint]:
    """
    Build a stylized but executable semantic policy family covering every field.

    The owner constraint deliberately allows a hidden equivalence class rather
    than committing to one exact owner value. This permits a real C_int-disclosure
    alternative-state synthesis experiment.
    """
    true_owner_number = owner_numeric_id(
        payload["owner_id"]
    )

    owner_modulus = rnd.choice(
        [5, 7, 8, 10, 11]
    )

    city_tuple = (
        payload["city_code"],
        payload["parcel_zone"],
        payload["asset_class"],
    )

    decoy_city_tuples = {
        city_tuple,
        ("ROM", "Z7", "government"),
        ("MIL", "Z8", "government"),
    }

    constraints = [
        HiddenConstraint(
            cid="c_1",
            kind="owner_bucket",
            semantic_group_label="owner_hidden_equivalence_class",
            selectors=(
                key_to_selector["owner_id"],
            ),
            params={
                "modulus": owner_modulus,
                "residue": (
                    true_owner_number
                    % owner_modulus
                ),
            },
        ),
        HiddenConstraint(
            cid="c_2",
            kind="city_zone_asset",
            semantic_group_label="city_zone_asset_policy",
            selectors=(
                key_to_selector["city_code"],
                key_to_selector["parcel_zone"],
                key_to_selector["asset_class"],
            ),
            params={
                "allowed_tuples": tuple(
                    sorted(decoy_city_tuples)
                ),
            },
        ),
        HiddenConstraint(
            cid="c_3",
            kind="floor_area_relation",
            semantic_group_label="geospatial_area_floor",
            selectors=(
                key_to_selector["floor"],
                key_to_selector["area_sqm"],
            ),
            params={
                "scale": 40,
                "offset": 0,
            },
        ),
        HiddenConstraint(
            cid="c_4",
            kind="risk_clearance_sensitivity",
            semantic_group_label="classification_sensitivity_clearance",
            selectors=(
                key_to_selector["risk_tier"],
                key_to_selector["clearance_level"],
                key_to_selector["data_sensitivity"],
            ),
            params={
                "clearance_margin": 2,
                "max_risk": 8,
            },
        ),
        HiddenConstraint(
            cid="c_5",
            kind="facility_device_density",
            semantic_group_label="facility_device_density",
            selectors=(
                key_to_selector["facility_class"],
                key_to_selector["device_count"],
                key_to_selector["area_sqm"],
            ),
            params={
                "allowed_facilities": (
                    "S",
                    "C",
                ),
                "area_per_device": 5,
            },
        ),
        HiddenConstraint(
            cid="c_6",
            kind="access_device_relation",
            semantic_group_label="sensitivity_access_devices",
            selectors=(
                key_to_selector["access_count"],
                key_to_selector["device_count"],
            ),
            params={
                "minimum_multiplier": 2,
            },
        ),
        HiddenConstraint(
            cid="c_7",
            kind="audit_policy",
            semantic_group_label="audit_sensitivity_clearance",
            selectors=(
                key_to_selector["audit_class"],
                key_to_selector["data_sensitivity"],
                key_to_selector["clearance_level"],
            ),
            params={
                "minimum_sensitivity": 5,
                "minimum_clearance": 3,
            },
        ),
        HiddenConstraint(
            cid="c_8",
            kind="firmware_network_facility",
            semantic_group_label="firmware_network_facility",
            selectors=(
                key_to_selector["device_firmware_class"],
                key_to_selector["network_zone"],
                key_to_selector["facility_class"],
            ),
            params={
                "secure_networks": (
                    "segmented",
                    "isolated",
                    "airgapped",
                ),
                "secure_facilities": (
                    "S",
                    "C",
                ),
            },
        ),
        HiddenConstraint(
            cid="c_9",
            kind="operator_access_risk",
            semantic_group_label="operator_access_risk",
            selectors=(
                key_to_selector["operator_role"],
                key_to_selector["access_count"],
                key_to_selector["risk_tier"],
                key_to_selector["clearance_level"],
            ),
            params={
                "maximum_access": 80,
                "maximum_risk": 7,
                "minimum_clearance": 4,
            },
        ),
        HiddenConstraint(
            cid="c_10",
            kind="asset_network_audit",
            semantic_group_label="asset_network_audit",
            selectors=(
                key_to_selector["asset_class"],
                key_to_selector["network_zone"],
                key_to_selector["audit_class"],
            ),
            params={
                "allowed_networks": (
                    "segmented",
                    "isolated",
                    "airgapped",
                ),
                "allowed_audits": (
                    "restricted",
                    "classified",
                ),
            },
        ),
    ]

    return constraints


# ==============================================================================
# AUXILIARY HIDDEN POLYNOMIAL CONSISTENCY FINGERPRINTS
# ==============================================================================

def fingerprint_score(
    fingerprint: HiddenPolynomialFingerprint,
    candidate_values: Mapping[str, Any],
) -> int:
    xs = [
        stable_hidden_feature(
            candidate_values[selector],
            salt,
        )
        for selector, salt in zip(
            fingerprint.selectors,
            fingerprint.feature_salts,
        )
    ]

    accumulator = 0

    for x, linear, quadratic in zip(
        xs,
        fingerprint.linear_coeffs,
        fingerprint.quadratic_coeffs,
    ):
        accumulator = (
            accumulator
            + linear * x
            + quadratic * x * x
        ) % fingerprint.modulus

    pair_index = 0

    for left_index in range(len(xs)):
        for right_index in range(
            left_index + 1,
            len(xs),
        ):
            accumulator = (
                accumulator
                + fingerprint.pair_coeffs[pair_index]
                * xs[left_index]
                * xs[right_index]
            ) % fingerprint.modulus

            pair_index += 1

    return accumulator


def build_polynomial_fingerprints(
    semantic_constraints: Sequence[HiddenConstraint],
    true_values: Mapping[str, Any],
    rnd: random.Random,
) -> List[HiddenPolynomialFingerprint]:
    """
    Build one auxiliary fingerprint for selected multi-fragment semantic groups.

    Owner equivalence is intentionally excluded so that the disclosure solver can
    construct a different owner inside the hidden semantic equivalence class.
    """
    fingerprints: List[HiddenPolynomialFingerprint] = []

    eligible_constraints = [
        constraint
        for constraint in semantic_constraints
        if len(constraint.selectors) >= 2
    ]

    selected = rnd.sample(
        eligible_constraints,
        k=min(5, len(eligible_constraints)),
    )

    for index, constraint in enumerate(
        selected,
        start=1,
    ):
        selectors = constraint.selectors
        arity = len(selectors)

        provisional = HiddenPolynomialFingerprint(
            cid=f"p_{index}",
            selectors=selectors,
            feature_salts=tuple(
                rng_token_hex(rnd, 16)
                for _ in range(arity)
            ),
            linear_coeffs=tuple(
                rnd.randint(1, PRIME - 1)
                for _ in range(arity)
            ),
            quadratic_coeffs=tuple(
                rnd.randint(1, PRIME - 1)
                for _ in range(arity)
            ),
            pair_coeffs=tuple(
                rnd.randint(1, PRIME - 1)
                for _ in range(
                    arity * (arity - 1) // 2
                )
            ),
            target=0,
        )

        target = fingerprint_score(
            provisional,
            true_values,
        )

        fingerprints.append(
            replace(
                provisional,
                target=target,
            )
        )

    return fingerprints


# ==============================================================================
# REFRESHED CNVS INSTANCE GENERATION
# ==============================================================================

def build_refreshed_cnvs_instance(
    instance_id: str,
    n_verifiers: int,
    seed: int,
    payload: Optional[Mapping[str, Any]] = None,
) -> PrivateCNVSInstance:
    rnd = random.Random(seed)

    payload = dict(
        payload
        if payload is not None
        else default_payload()
    )

    domains = domain_specs()

    if set(payload.keys()) != set(domains.keys()):
        raise ValueError(
            "Payload keys must exactly match the declared domain universe."
        )

    if n_verifiers < len(payload):
        raise ValueError(
            "n_verifiers must be at least the number of terminal fragments."
        )

    fragments: Dict[str, PrivateFragment] = {}
    local_tasks: Dict[str, LocalTaskView] = {}

    for semantic_key, value in payload.items():
        while True:
            selector_salt = rng_token_hex(
                rnd,
                32,
            )

            selector = make_selector(
                semantic_key,
                selector_salt,
            )

            if selector not in fragments:
                break

        domain = domains[semantic_key]

        fragment = PrivateFragment(
            semantic_key=semantic_key,
            selector=selector,
            typ=type(value),
            true_value=value,
            domain=domain,
        )

        fragments[selector] = fragment

    verifiers = [
        f"V{index:03d}"
        for index in range(n_verifiers)
    ]

    assigned_verifiers = rnd.sample(
        verifiers,
        len(fragments),
    )

    assignment = {
        selector: verifier_id
        for selector, verifier_id in zip(
            fragments.keys(),
            assigned_verifiers,
        )
    }

    verifier_secrets = {
        verifier_id: bytes.fromhex(
            rng_token_hex(
                rnd,
                32,
            )
        )
        for verifier_id in verifiers
    }

    for selector, fragment in fragments.items():
        verifier_id = assignment[selector]

        local_tasks[selector] = LocalTaskView(
            selector=selector,
            expected_type=fragment.typ,
            domain_name=fragment.domain.name,
            allowed_values=fragment.domain.values,
            instance_id=instance_id,
            verifier_id=verifier_id,
        )

    C_pub = PublicInvariantCategory(
        name="hidden_structural_semantic_invariant_family",
        description=(
            "Public category only. Instantiated semantic policies, topology, "
            "binding, and auxiliary fingerprints remain hidden."
        ),
    )

    key_to_selector = {
        fragment.semantic_key: selector
        for selector, fragment in fragments.items()
    }

    semantic_constraints = build_hidden_semantic_constraints(
        key_to_selector=key_to_selector,
        payload=payload,
        domains=domains,
        rnd=rnd,
    )

    true_values = {
        selector: fragment.true_value
        for selector, fragment in fragments.items()
    }

    polynomial_fingerprints = build_polynomial_fingerprints(
        semantic_constraints=semantic_constraints,
        true_values=true_values,
        rnd=rnd,
    )

    hidden_topology_edges: Set[Tuple[str, str]] = set()

    for constraint in semantic_constraints:
        selectors = constraint.selectors

        for left_index in range(len(selectors)):
            for right_index in range(
                left_index + 1,
                len(selectors),
            ):
                hidden_topology_edges.add(
                    tuple(
                        sorted(
                            (
                                selectors[left_index],
                                selectors[right_index],
                            )
                        )
                    )
                )

    critical_selectors = {
        selector
        for constraint in semantic_constraints
        for selector in constraint.selectors
    }

    uncovered = (
        set(fragments.keys())
        - critical_selectors
    )

    if uncovered:
        uncovered_keys = [
            fragments[selector].semantic_key
            for selector in uncovered
        ]

        raise RuntimeError(
            "Full structural-semantic coverage failed. "
            f"Uncovered fields: {uncovered_keys}"
        )

    state = PrivateCNVSInstance(
        fragments=fragments,
        local_tasks=local_tasks,
        assignment=assignment,
        verifier_secrets=verifier_secrets,
        instance_id=instance_id,
        C_pub=C_pub,
        semantic_constraints=semantic_constraints,
        polynomial_fingerprints=polynomial_fingerprints,
        hidden_topology_edges=hidden_topology_edges,
        critical_selectors=critical_selectors,
    )

    if not VG_accepts(
        state,
        honest_evidence(state),
    ):
        raise RuntimeError(
            "Fresh honest state failed its own validation pipeline."
        )

    return state


# ==============================================================================
# LOCAL EVIDENCE AND GLOBAL VALIDATION
# ==============================================================================

def V_L(
    task: LocalTaskView,
    observed_value: Any,
) -> bool:
    """
    Exact local type and public-domain admissibility.
    """
    return (
        type(observed_value)
        is task.expected_type
        and observed_value
        in task.allowed_values
    )


def emit_evidence(
    task: LocalTaskView,
    verifier_secret: bytes,
    observed_value: Any,
    *,
    instance_id_override: Optional[str] = None,
    claimed_local_admissible: Optional[bool] = None,
    use_valid_signature: bool = True,
) -> LocalEvidence:
    instance_id = (
        task.instance_id
        if instance_id_override is None
        else instance_id_override
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
        verifier_id=task.verifier_id,
        selector=task.selector,
        instance_id=instance_id,
        observed_value=observed_value,
        local_admissible=local_claim,
    )

    if not use_valid_signature:
        signature = "invalid_signature"

    return LocalEvidence(
        selector=task.selector,
        observed_value=observed_value,
        local_admissible=local_claim,
        signature=signature,
        instance_id=instance_id,
        verifier_id=task.verifier_id,
    )


def honest_evidence(
    state: PrivateCNVSInstance,
) -> Dict[str, LocalEvidence]:
    evidence: Dict[str, LocalEvidence] = {}

    for selector, fragment in state.fragments.items():
        task = state.local_tasks[selector]
        secret = state.verifier_secrets[
            task.verifier_id
        ]

        evidence[selector] = emit_evidence(
            task=task,
            verifier_secret=secret,
            observed_value=fragment.true_value,
        )

    return evidence


def semantic_family_accepts(
    state: PrivateCNVSInstance,
    values: Mapping[str, Any],
) -> bool:
    return all(
        check_semantic_constraint(
            constraint,
            values,
        )
        for constraint in state.semantic_constraints
    )


def fingerprints_accept(
    state: PrivateCNVSInstance,
    values: Mapping[str, Any],
) -> bool:
    return all(
        fingerprint_score(
            fingerprint,
            values,
        )
        == fingerprint.target
        for fingerprint in state.polynomial_fingerprints
    )


def VG_accepts(
    state: PrivateCNVSInstance,
    evidence: Mapping[str, LocalEvidence],
) -> bool:
    """
    Execute the application-layer validation pipeline.
    """
    if set(evidence.keys()) != set(
        state.fragments.keys()
    ):
        return False

    for selector, item in evidence.items():
        if item.selector != selector:
            return False

        task = state.local_tasks.get(
            selector
        )

        if task is None:
            return False

        if item.verifier_id != task.verifier_id:
            return False

        if item.instance_id != state.instance_id:
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
            instance_id=item.instance_id,
            observed_value=item.observed_value,
            local_admissible=item.local_admissible,
        )

        if not hmac.compare_digest(
            item.signature,
            expected_signature,
        ):
            return False

        recomputed_local = V_L(
            task,
            item.observed_value,
        )

        if not recomputed_local:
            return False

        if item.local_admissible is not recomputed_local:
            return False

    values = {
        selector: item.observed_value
        for selector, item in evidence.items()
    }

    return (
        semantic_family_accepts(
            state,
            values,
        )
        and fingerprints_accept(
            state,
            values,
        )
    )


# ==============================================================================
# ADVERSARY VIEW AND ONE-SHOT DEPENDENT INFERENCE
# ==============================================================================

def make_adversary_view(
    state: PrivateCNVSInstance,
    cfg: SimulationConfig,
    coalition_size: int,
    rnd: random.Random,
) -> AdversaryView:
    all_verifiers = [
        f"V{index:03d}"
        for index in range(
            cfg.n_verifiers
        )
    ]

    if not 0 <= coalition_size <= len(
        all_verifiers
    ):
        raise ValueError(
            "coalition_size is outside the verifier population."
        )

    compromised_verifiers = set(
        rnd.sample(
            all_verifiers,
            coalition_size,
        )
    )

    compromised_local_tasks: Dict[
        str,
        LocalTaskView,
    ] = {}

    compromised_values: Dict[
        str,
        Any,
    ] = {}

    compromised_secrets: Dict[
        str,
        bytes,
    ] = {}

    for selector, fragment in state.fragments.items():
        verifier_id = state.assignment[
            selector
        ]

        if verifier_id in compromised_verifiers:
            compromised_local_tasks[
                selector
            ] = state.local_tasks[
                selector
            ]

            compromised_values[
                selector
            ] = fragment.true_value

            compromised_secrets[
                selector
            ] = state.verifier_secrets[
                verifier_id
            ]

    leaked_edges = {
        edge
        for edge in state.hidden_topology_edges
        if rnd.random()
        < cfg.edge_disclosure_probability
    }

    unknown_critical = [
        selector
        for selector in state.critical_selectors
        if selector not in compromised_values
    ]

    rnd.shuffle(
        unknown_critical
    )

    # Every unknown selector receives at most one inference trial.
    # Therefore p_infer_cap is a true per-selector conditional cap in this model.
    for selector in unknown_critical:
        neighbors = {
            right
            for left, right in leaked_edges
            if left == selector
        } | {
            left
            for left, right in leaked_edges
            if right == selector
        }

        if neighbors:
            known_fraction = (
                sum(
                    neighbor
                    in compromised_values
                    for neighbor in neighbors
                )
                / len(neighbors)
            )
        else:
            known_fraction = 0.0

        p_infer = min(
            cfg.p_infer_cap,
            cfg.dependent_infer_base
            + cfg.dependent_infer_rho
            * known_fraction,
        )

        if rnd.random() < p_infer:
            compromised_values[
                selector
            ] = state.fragments[
                selector
            ].true_value

            if (
                rnd.random()
                < cfg.p_identity_after_infer
            ):
                compromised_secrets[
                    selector
                ] = state.verifier_secrets[
                    state.assignment[
                        selector
                    ]
                ]

                compromised_local_tasks[
                    selector
                ] = state.local_tasks[
                    selector
                ]

    return AdversaryView(
        selectors=tuple(
            state.fragments.keys()
        ),
        compromised_local_tasks=compromised_local_tasks,
        C_pub=state.C_pub,
        leaked_metadata_edges=leaked_edges,
        compromised_values=compromised_values,
        compromised_secrets=compromised_secrets,
        compromised_verifiers=compromised_verifiers,
        C_int_leaked=False,
    )


def controlled_critical_selectors(
    state: PrivateCNVSInstance,
    adversary: AdversaryView,
) -> Set[str]:
    return (
        state.critical_selectors
        & set(
            adversary.compromised_values.keys()
        )
        & set(
            adversary.compromised_secrets.keys()
        )
    )


def random_alternative_value(
    fragment: PrivateFragment,
    rnd: random.Random,
) -> Any:
    alternatives = [
        value
        for value in fragment.domain.values
        if value != fragment.true_value
    ]

    if not alternatives:
        raise RuntimeError(
            f"No alternative value exists for {fragment.semantic_key}."
        )

    return rnd.choice(
        alternatives
    )


def build_signed_candidate_evidence(
    state: PrivateCNVSInstance,
    adversary: AdversaryView,
    candidate_values: Mapping[str, Any],
) -> Optional[Dict[str, LocalEvidence]]:
    evidence: Dict[str, LocalEvidence] = {}

    for selector in state.fragments:
        secret = adversary.compromised_secrets.get(
            selector
        )

        if secret is None:
            return None

        task = state.local_tasks[
            selector
        ]

        evidence[selector] = emit_evidence(
            task=task,
            verifier_secret=secret,
            observed_value=candidate_values[
                selector
            ],
        )

    return evidence


def blind_forgery_attempt(
    state: PrivateCNVSInstance,
    adversary: AdversaryView,
    cfg: SimulationConfig,
    rnd: random.Random,
) -> Tuple[bool, int, int]:
    controlled = controlled_critical_selectors(
        state,
        adversary,
    )

    h_crit = len(
        state.critical_selectors
    )

    if len(controlled) < h_crit:
        return (
            False,
            len(controlled),
            h_crit,
        )

    selector_list = list(
        controlled
    )

    for _ in range(
        cfg.blind_attempts
    ):
        forged_values = {
            selector: fragment.true_value
            for selector, fragment in state.fragments.items()
        }

        mutation_count = rnd.randint(
            1,
            min(
                3,
                len(selector_list),
            ),
        )

        mutated_selectors = rnd.sample(
            selector_list,
            mutation_count,
        )

        for selector in mutated_selectors:
            forged_values[
                selector
            ] = random_alternative_value(
                state.fragments[
                    selector
                ],
                rnd,
            )

        forged_evidence = build_signed_candidate_evidence(
            state,
            adversary,
            forged_values,
        )

        if forged_evidence is None:
            continue

        if (
            VG_accepts(
                state,
                forged_evidence,
            )
            and any(
                forged_values[selector]
                != state.fragments[
                    selector
                ].true_value
                for selector in state.fragments
            )
        ):
            return (
                True,
                len(controlled),
                h_crit,
            )

    return (
        False,
        len(controlled),
        h_crit,
    )


# ==============================================================================
# EXECUTED C_int-DISCLOSURE ATTACK
# ==============================================================================

def find_alternative_state_with_leaked_Cint(
    state: PrivateCNVSInstance,
    cfg: SimulationConfig,
    rnd: random.Random,
) -> Optional[Dict[str, Any]]:
    """
    Search for an alternative state using the disclosed instantiated constraints.

    The solver first exploits the hidden owner equivalence class. If that does
    not yield a valid alternative, it performs a bounded guided random search.
    """
    true_values = {
        selector: fragment.true_value
        for selector, fragment in state.fragments.items()
    }

    owner_constraint = next(
        constraint
        for constraint in state.semantic_constraints
        if constraint.kind == "owner_bucket"
    )

    owner_selector = owner_constraint.selectors[
        0
    ]

    owner_fragment = state.fragments[
        owner_selector
    ]

    for alternative_owner in owner_fragment.domain.values:
        if alternative_owner == owner_fragment.true_value:
            continue

        candidate = dict(
            true_values
        )

        candidate[
            owner_selector
        ] = alternative_owner

        if (
            semantic_family_accepts(
                state,
                candidate,
            )
            and fingerprints_accept(
                state,
                candidate,
            )
        ):
            return candidate

    selectors = list(
        state.critical_selectors
    )

    for _ in range(
        cfg.leak_solver_attempts
    ):
        candidate = dict(
            true_values
        )

        mutation_count = rnd.randint(
            1,
            min(
                4,
                len(selectors),
            ),
        )

        for selector in rnd.sample(
            selectors,
            mutation_count,
        ):
            candidate[
                selector
            ] = random_alternative_value(
                state.fragments[
                    selector
                ],
                rnd,
            )

        if (
            semantic_family_accepts(
                state,
                candidate,
            )
            and fingerprints_accept(
                state,
                candidate,
            )
        ):
            return candidate

    return None


def Cint_disclosure_attack(
    state: PrivateCNVSInstance,
    adversary: AdversaryView,
    cfg: SimulationConfig,
    rnd: random.Random,
) -> Tuple[bool, bool]:
    """
    Execute, rather than assume, the C_int disclosure boundary.

    Returns:
      attack_accepted:
          an actually forged alternative state passed V_G;

      solver_found_alternative:
          the disclosed constraints admitted and exposed an alternative candidate
          within the bounded solver budget.
    """
    if not adversary.C_int_leaked:
        return False, False

    controlled = controlled_critical_selectors(
        state,
        adversary,
    )

    if len(controlled) < len(
        state.critical_selectors
    ):
        return False, False

    alternative = find_alternative_state_with_leaked_Cint(
        state,
        cfg,
        rnd,
    )

    if alternative is None:
        return False, False

    evidence = build_signed_candidate_evidence(
        state,
        adversary,
        alternative,
    )

    if evidence is None:
        return False, True

    differs_from_truth = any(
        alternative[selector]
        != state.fragments[
            selector
        ].true_value
        for selector in state.fragments
    )

    accepted = (
        differs_from_truth
        and VG_accepts(
            state,
            evidence,
        )
    )

    return accepted, True


# ==============================================================================
# REFRESH SCENARIO
# ==============================================================================

def fingerprint_Cint(
    state: PrivateCNVSInstance,
) -> str:
    serializable = {
        "semantic_constraints": [
            {
                "cid": constraint.cid,
                "kind": constraint.kind,
                "label": constraint.semantic_group_label,
                "selectors": constraint.selectors,
                "params": constraint.params,
            }
            for constraint in state.semantic_constraints
        ],
        "polynomial_fingerprints": [
            {
                "cid": fingerprint.cid,
                "selectors": fingerprint.selectors,
                "feature_salts": fingerprint.feature_salts,
                "linear_coeffs": fingerprint.linear_coeffs,
                "quadratic_coeffs": fingerprint.quadratic_coeffs,
                "pair_coeffs": fingerprint.pair_coeffs,
                "target": fingerprint.target,
                "modulus": fingerprint.modulus,
            }
            for fingerprint in state.polynomial_fingerprints
        ],
        "topology": sorted(
            state.hidden_topology_edges
        ),
        "assignment": sorted(
            state.assignment.items()
        ),
    }

    return sha256_text(
        json.dumps(
            serializable,
            sort_keys=True,
            ensure_ascii=False,
        )
    )[:24]


def scenario_full_refresh_attack(
    cfg: SimulationConfig,
) -> None:
    payload = default_payload()

    state_t = build_refreshed_cnvs_instance(
        "instance_t",
        cfg.n_verifiers,
        cfg.seed,
        payload,
    )

    state_t1 = build_refreshed_cnvs_instance(
        "instance_t_plus_1",
        cfg.n_verifiers,
        cfg.seed + 1,
        payload,
    )

    print(
        "\n================ FULL STRUCTURAL REFRESH ================\n"
    )

    print(
        "Same declaration, independently refreshed internal instance."
    )

    print(
        "C_int fingerprint at t:    ",
        fingerprint_Cint(
            state_t
        ),
    )

    print(
        "C_int fingerprint at t + 1:",
        fingerprint_Cint(
            state_t1
        ),
    )

    stale_evidence = honest_evidence(
        state_t
    )

    replay_result = VG_accepts(
        state_t1,
        stale_evidence,
    )

    if replay_result:
        raise AssertionError(
            "Stale evidence was accepted after full structural refresh."
        )

    print(
        "\nReplay of old evidence against refreshed instance accepted:",
        replay_result,
    )


# ==============================================================================
# ANALYTICAL COMPARISON REFERENCES
# ==============================================================================

def exact_injective_direct_control_probability(
    population_size: int,
    coalition_size: int,
    critical_count: int,
) -> float:
    """
    Exact probability that every critical fragment is directly assigned to the
    coalition under injective assignment without replacement.
    """
    if critical_count <= 0:
        return 1.0

    if coalition_size < critical_count:
        return 0.0

    return (
        math.comb(
            coalition_size,
            critical_count,
        )
        / math.comb(
            population_size,
            critical_count,
        )
    )


def simplified_injective_inference_reference(
    population_size: int,
    coalition_size: int,
    critical_count: int,
    p_indirect_control: float,
) -> float:
    """
    Simplified comparison reference.

    Direct assignment is treated exactly through the hypergeometric law.
    Every honest-assigned critical selector is then independently and indirectly
    controlled with probability p_indirect_control.

    This is a comparison model, not the dependent topology process executed by
    make_adversary_view and not a theorem proved here.
    """
    if critical_count <= 0:
        return 1.0

    if not 0.0 <= p_indirect_control <= 1.0:
        raise ValueError(
            "p_indirect_control must lie in [0, 1]."
        )

    denominator = math.comb(
        population_size,
        critical_count,
    )

    probability = 0.0

    minimum_direct = max(
        0,
        critical_count
        - (
            population_size
            - coalition_size
        ),
    )

    maximum_direct = min(
        critical_count,
        coalition_size,
    )

    for direct_count in range(
        minimum_direct,
        maximum_direct + 1,
    ):
        honest_count = (
            critical_count
            - direct_count
        )

        assignment_probability = (
            math.comb(
                coalition_size,
                direct_count,
            )
            * math.comb(
                population_size
                - coalition_size,
                honest_count,
            )
            / denominator
        )

        probability += (
            assignment_probability
            * (
                p_indirect_control
                ** honest_count
            )
        )

    return probability


def wilson_interval(
    successes: int,
    trials: int,
    z: float = 1.959963984540054,
) -> Tuple[float, float]:
    if trials <= 0:
        raise ValueError(
            "trials must be positive."
        )

    p_hat = successes / trials
    z_squared = z * z

    denominator = (
        1.0
        + z_squared / trials
    )

    centre = (
        p_hat
        + z_squared
        / (
            2.0 * trials
        )
    ) / denominator

    half_width = (
        z
        * math.sqrt(
            p_hat
            * (
                1.0 - p_hat
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
            centre - half_width,
        ),
        min(
            1.0,
            centre + half_width,
        ),
    )


# ==============================================================================
# PROGRESSIVE MASS-COLLUSION EXPERIMENT
# ==============================================================================

def run_single_collusion_size(
    cfg: SimulationConfig,
    coalition_size: int,
    trials: int,
    seed_offset: int = 0,
) -> Dict[str, Any]:
    blind_false_accepts = 0
    disclosure_false_accepts = 0
    disclosure_solver_found = 0
    all_critical_controlled = 0

    controlled_counts: List[int] = []
    h_values: List[int] = []
    metadata_edges_seen: List[int] = []

    for trial in range(
        trials
    ):
        state_seed = (
            cfg.seed
            + seed_offset
            + 10 * trial
        )

        adversary_seed = (
            cfg.seed
            + seed_offset
            + 10 * trial
            + 1
        )

        blind_seed = (
            cfg.seed
            + seed_offset
            + 10 * trial
            + 2
        )

        disclosure_seed = (
            cfg.seed
            + seed_offset
            + 10 * trial
            + 3
        )

        state = build_refreshed_cnvs_instance(
            instance_id=(
                f"instance_{coalition_size}_{trial}"
            ),
            n_verifiers=cfg.n_verifiers,
            seed=state_seed,
            payload=default_payload(),
        )

        adversary = make_adversary_view(
            state=state,
            cfg=cfg,
            coalition_size=coalition_size,
            rnd=random.Random(
                adversary_seed
            ),
        )

        blind_ok, controlled, h_crit = blind_forgery_attempt(
            state=state,
            adversary=adversary,
            cfg=cfg,
            rnd=random.Random(
                blind_seed
            ),
        )

        disclosure_adversary = replace(
            adversary,
            C_int_leaked=True,
        )

        disclosure_ok, solver_found = Cint_disclosure_attack(
            state=state,
            adversary=disclosure_adversary,
            cfg=cfg,
            rnd=random.Random(
                disclosure_seed
            ),
        )

        controlled_counts.append(
            controlled
        )

        h_values.append(
            h_crit
        )

        metadata_edges_seen.append(
            len(
                adversary.leaked_metadata_edges
            )
        )

        if controlled == h_crit:
            all_critical_controlled += 1

        if blind_ok:
            blind_false_accepts += 1

        if solver_found:
            disclosure_solver_found += 1

        if disclosure_ok:
            disclosure_false_accepts += 1

    actual_q = (
        coalition_size
        / cfg.n_verifiers
    )

    average_h = statistics.mean(
        h_values
    )

    p_indirect_reference = (
        cfg.p_infer_cap
        * cfg.p_identity_after_infer
    )

    direct_reference = (
        exact_injective_direct_control_probability(
            population_size=cfg.n_verifiers,
            coalition_size=coalition_size,
            critical_count=int(
                round(
                    average_h
                )
            ),
        )
    )

    inference_reference = (
        simplified_injective_inference_reference(
            population_size=cfg.n_verifiers,
            coalition_size=coalition_size,
            critical_count=int(
                round(
                    average_h
                )
            ),
            p_indirect_control=(
                p_indirect_reference
            ),
        )
    )

    all_ci = wilson_interval(
        all_critical_controlled,
        trials,
    )

    blind_ci = wilson_interval(
        blind_false_accepts,
        trials,
    )

    disclosure_ci = wilson_interval(
        disclosure_false_accepts,
        trials,
    )

    return {
        "coalition_size": coalition_size,
        "actual_q": actual_q,
        "avg_h_crit": average_h,
        "avg_controlled_critical": statistics.mean(
            controlled_counts
        ),
        "max_controlled_critical": max(
            controlled_counts
        ),
        "avg_leaked_edges": statistics.mean(
            metadata_edges_seen
        ),
        "all_critical_controlled_count": all_critical_controlled,
        "all_critical_controlled_rate": (
            all_critical_controlled
            / trials
        ),
        "all_critical_ci_low": all_ci[0],
        "all_critical_ci_high": all_ci[1],
        "blind_false_accept_count": blind_false_accepts,
        "blind_false_accept_rate": (
            blind_false_accepts
            / trials
        ),
        "blind_false_accept_ci_low": blind_ci[0],
        "blind_false_accept_ci_high": blind_ci[1],
        "Cint_disclosure_solver_found_count": disclosure_solver_found,
        "Cint_disclosure_solver_found_rate": (
            disclosure_solver_found
            / trials
        ),
        "Cint_disclosure_false_accept_count": disclosure_false_accepts,
        "Cint_disclosure_false_accept_rate": (
            disclosure_false_accepts
            / trials
        ),
        "Cint_disclosure_ci_low": disclosure_ci[0],
        "Cint_disclosure_ci_high": disclosure_ci[1],
        "exact_direct_reference": direct_reference,
        "simplified_inference_reference": inference_reference,
        "trials": trials,
    }


def default_coalition_sizes(
    n_verifiers: int,
) -> List[int]:
    nominal_fractions = [
        0.10,
        0.20,
        0.30,
        0.40,
        0.50,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
        0.95,
        0.98,
        0.99,
        1.00,
    ]

    sizes = {
        max(
            0,
            min(
                n_verifiers,
                round(
                    fraction
                    * n_verifiers
                ),
            ),
        )
        for fraction in nominal_fractions
    }

    sizes.add(
        n_verifiers
    )

    return sorted(
        sizes
    )


def run_progressive_mass_collusion(
    cfg: SimulationConfig,
    coalition_sizes: Optional[Sequence[int]] = None,
) -> List[Dict[str, Any]]:
    sizes = (
        list(coalition_sizes)
        if coalition_sizes is not None
        else default_coalition_sizes(
            cfg.n_verifiers
        )
    )

    results: List[Dict[str, Any]] = []

    for index, coalition_size in enumerate(
        sizes
    ):
        print(
            f"Running coalition size {coalition_size}/{cfg.n_verifiers} "
            f"({coalition_size / cfg.n_verifiers:.4f})..."
        )

        results.append(
            run_single_collusion_size(
                cfg=cfg,
                coalition_size=coalition_size,
                trials=cfg.trials,
                seed_offset=(
                    10_000_000
                    * index
                ),
            )
        )

    return results


def print_progressive_mass_collusion_results(
    results: Sequence[Mapping[str, Any]],
) -> None:
    print(
        "\n================ PROGRESSIVE MASS COLLUSION ================\n"
    )

    header = (
        "r/Q       | avg_h | avg_ctrl | P(all critical) "
        "| P(blind false accept) | P(C_int disclosure false accept)"
    )

    print(
        header
    )

    print(
        "-" * len(
            header
        )
    )

    for result in results:
        print(
            f"{result['coalition_size']:2d}/{64:<2d} "
            f"({100.0 * result['actual_q']:6.2f}%) | "
            f"{result['avg_h_crit']:5.2f} | "
            f"{result['avg_controlled_critical']:8.3f} | "
            f"{result['all_critical_controlled_rate']:15.8f} | "
            f"{result['blind_false_accept_rate']:21.8f} | "
            f"{result['Cint_disclosure_false_accept_rate']:31.8f}"
        )

    print(
        "\nZero observed events are reported with Wilson 95% intervals "
        "in the stored result rows and are not interpreted as zero probability."
    )


# ==============================================================================
# PLOTTING
# ==============================================================================

def plot_progressive_mass_collusion_comparison(
    results: Sequence[Mapping[str, Any]],
    cfg: SimulationConfig,
    out_dir: Path,
    *,
    show_plots: bool = True,
) -> None:
    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    x = [
        100.0
        * float(
            result["actual_q"]
        )
        for result in results
    ]

    p_all = [
        float(
            result[
                "all_critical_controlled_rate"
            ]
        )
        for result in results
    ]

    p_false = [
        float(
            result[
                "blind_false_accept_rate"
            ]
        )
        for result in results
    ]

    p_disclosure = [
        float(
            result[
                "Cint_disclosure_false_accept_rate"
            ]
        )
        for result in results
    ]

    direct_reference = [
        float(
            result[
                "exact_direct_reference"
            ]
        )
        for result in results
    ]

    inference_reference = [
        float(
            result[
                "simplified_inference_reference"
            ]
        )
        for result in results
    ]

    average_h = [
        float(
            result[
                "avg_h_crit"
            ]
        )
        for result in results
    ]

    average_controlled = [
        float(
            result[
                "avg_controlled_critical"
            ]
        )
        for result in results
    ]

    maximum_controlled = [
        float(
            result[
                "max_controlled_critical"
            ]
        )
        for result in results
    ]

    detection_floor = (
        1.0
        / max(
            1,
            cfg.trials,
        )
    )

    # --------------------------------------------------------------------------
    # Plot 1: complete-control probability and analytical references.
    # --------------------------------------------------------------------------
    plt.figure(
        figsize=(12, 7)
    )

    plt.plot(
        x,
        p_all,
        marker="o",
        label="Observed P(all critical controlled)",
    )

    plt.plot(
        x,
        direct_reference,
        linestyle="--",
        marker="s",
        label="Exact injective direct-control reference",
    )

    plt.plot(
        x,
        inference_reference,
        linestyle=":",
        marker="^",
        label=(
            "Simplified injective independent-inference reference"
        ),
    )

    plt.xlabel(
        "Actual colluding verifier fraction q (%)"
    )

    plt.ylabel(
        "Probability"
    )

    plt.title(
        "CNVS Test 10: Complete Critical Control and Injective References"
    )

    plt.grid(
        True,
        linestyle="--",
        linewidth=0.5,
        alpha=0.65,
    )

    plt.legend()
    plt.tight_layout()

    output_1 = (
        out_dir
        / "test_10_complete_control_vs_injective_references.png"
    )

    plt.savefig(
        output_1,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 2: executed ordinary and disclosure false acceptance.
    # --------------------------------------------------------------------------
    plt.figure(
        figsize=(12, 7)
    )

    plt.semilogy(
        x,
        [
            max(
                value,
                detection_floor,
            )
            for value in p_false
        ],
        marker="o",
        label=(
            "Observed blind false acceptance "
            "(zero observations plotted at detection floor)"
        ),
    )

    plt.semilogy(
        x,
        [
            max(
                value,
                detection_floor,
            )
            for value in p_disclosure
        ],
        marker="s",
        label=(
            "Executed C_int-disclosure false acceptance "
            "(zero observations plotted at detection floor)"
        ),
    )

    plt.xlabel(
        "Actual colluding verifier fraction q (%)"
    )

    plt.ylabel(
        "Observed rate, logarithmic scale"
    )

    plt.title(
        "CNVS Test 10: Executed False-State Acceptance Experiments"
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
        / "test_10_executed_false_acceptance_logscale.png"
    )

    plt.savefig(
        output_2,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 3: controlled critical count.
    # --------------------------------------------------------------------------
    plt.figure(
        figsize=(12, 7)
    )

    plt.plot(
        x,
        average_controlled,
        marker="o",
        label="Average controlled critical selectors",
    )

    plt.plot(
        x,
        average_h,
        linestyle="--",
        label="Critical-selector threshold h_crit",
    )

    plt.plot(
        x,
        maximum_controlled,
        linestyle=":",
        marker="s",
        label="Maximum controlled critical selectors",
    )

    plt.xlabel(
        "Actual colluding verifier fraction q (%)"
    )

    plt.ylabel(
        "Critical selector count"
    )

    plt.title(
        "CNVS Test 10: Controlled Critical Selectors vs Full-Coverage Threshold"
    )

    plt.grid(
        True,
        linestyle="--",
        linewidth=0.5,
        alpha=0.65,
    )

    plt.legend()
    plt.tight_layout()

    output_3 = (
        out_dir
        / "test_10_controlled_critical_vs_threshold.png"
    )

    plt.savefig(
        output_3,
        dpi=300,
    )

    if show_plots:
        plt.show()

    plt.close()

    print(
        "\n[Plot Output]"
    )

    print(
        "Saved:",
        output_1,
    )

    print(
        "Saved:",
        output_2,
    )

    print(
        "Saved:",
        output_3,
    )

    print(
        "Absolute folder:",
        out_dir.resolve(),
    )


# ==============================================================================
# RESULT SERIALIZATION
# ==============================================================================

def save_results_json(
    results: Sequence[Mapping[str, Any]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            list(results),
            handle,
            indent=2,
            ensure_ascii=False,
        )


# ==============================================================================
# COMMAND-LINE INTERFACE
# ==============================================================================

def running_inside_notebook_kernel() -> bool:
    """
    Detect Jupyter or Google Colab execution.

    Notebook kernels inject arguments such as:

        -f /root/.local/share/jupyter/runtime/kernel-....json

    These are kernel arguments, not Test 10 parameters.
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


def parse_arguments(
    argv: Optional[Sequence[str]] = None,
) -> argparse.Namespace:
    """
    Parse Test 10 options.

    - Explicit argv: strict parsing.
    - Ordinary terminal execution: strict parsing.
    - Jupyter/Colab: parse Test 10 options and ignore only kernel-injected
      arguments such as "-f kernel.json".
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run the corrected CNVS Test 10 structural-semantic "
            "mass-collusion experiment."
        )
    )

    parser.add_argument(
        "--trials",
        type=int,
        default=100_000,
        help=(
            "Monte Carlo trajectories per coalition size "
            "(default: 100000)."
        ),
    )

    parser.add_argument(
        "--levels",
        type=float,
        nargs="*",
        default=None,
        help=(
            "Optional nominal coalition fractions in [0,1]. "
            "They are converted to unique integer coalition sizes."
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


def coalition_sizes_from_levels(
    levels: Optional[Iterable[float]],
    n_verifiers: int,
) -> Optional[List[int]]:
    if levels is None:
        return None

    sizes: Set[int] = set()

    for level in levels:
        if not 0.0 <= level <= 1.0:
            raise ValueError(
                "Every coalition level must lie in [0,1]."
            )

        sizes.add(
            max(
                0,
                min(
                    n_verifiers,
                    round(
                        level
                        * n_verifiers
                    ),
                ),
            )
        )

    return sorted(
        sizes
    )


# ==============================================================================
# MAIN
# ==============================================================================

def main(
    argv: Optional[Sequence[str]] = None,
) -> None:
    arguments = parse_arguments(argv)

    if arguments.trials <= 0:
        raise ValueError(
            "--trials must be positive."
        )

    cfg = SimulationConfig(
        trials=arguments.trials,
        n_verifiers=64,
        edge_disclosure_probability=0.12,
        dependent_infer_base=0.015,
        dependent_infer_rho=0.35,
        p_infer_cap=0.45,
        p_identity_after_infer=0.15,
        blind_attempts=1,
        leak_solver_attempts=250,
        seed=42,
    )

    scenario_full_refresh_attack(
        cfg
    )

    coalition_sizes = coalition_sizes_from_levels(
        arguments.levels,
        cfg.n_verifiers,
    )

    results = run_progressive_mass_collusion(
        cfg,
        coalition_sizes=coalition_sizes,
    )

    print_progressive_mass_collusion_results(
        results
    )

    output_dir = (
        Path(__file__).resolve().parent
        / "test_10_figures"
    )

    plot_progressive_mass_collusion_comparison(
        results=results,
        cfg=cfg,
        out_dir=output_dir,
        show_plots=not arguments.no_show,
    )

    results_path = (
        output_dir
        / "test_10_results.json"
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
        "\n================ FINAL ARCHITECTURAL INTERPRETATION ================\n"
    )

    print(
        "- Every payload field belongs to at least one hidden semantic constraint."
    )

    print(
        "- Every evidence message is bound to verifier, selector, instance, "
        "observed value, and local-admissibility claim."
    )

    print(
        "- Local admissibility is recomputed by the trusted global pipeline."
    )

    print(
        "- Dependent inference receives one trial per unknown critical selector, "
        "so p_infer_cap is an actual per-selector cap in this model."
    )

    print(
        "- The ordinary blind attack and C_int-disclosure attack both construct "
        "candidate states and execute V_G."
    )

    print(
        "- The direct reference is exact for injective assignment; the inference "
        "reference is explicitly a simplified comparison model."
    )

    print(
        "- Results at nominal fractions are reported using actual integer "
        "coalition sizes r/Q."
    )

    print(
        "- Zero observed events are accompanied by Wilson confidence intervals "
        "and are not interpreted as mathematical zero."
    )


if __name__ == "__main__":
    main()
