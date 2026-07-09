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
import json
import random
import statistics
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Set, Optional

# ==============================================================================
# Test Name: Test 10: Advanced Execution Environment (Full Structural-Semantic Model).
# filename = "test_10_full_structural_semantic_model.py"
#
# PURPOSE:
# This script is an executable adversarial model for the CNVS framework.
# It projects the resilience of the Global Veto (V_G) against progressive mass 
# collusion (up to 100%), incorporating a non-linear cryptographic polynomial 
# engine, moving target defense (Topological Refresh), and bounded metadata leakage.
#
# FORMAL ASSUMPTIONS:
#   1. Epistemic Isolation: Strict separation between the trusted global state, 
#      the local verifier view, and the adversary view.
#   2. Injective Assignment: Randomized one-to-one assignment of terminal fragments.
#   3. Moving Target Defense: At each instance, the topology, binding, and hidden 
#      invariant family C={c_i} are fully refreshed.
#   4. Non-Linear Constraints: The invariant family evaluates polynomial constraints 
#      (linear, quadratic, cubic, and pairwise interactions) over a finite field.
#   5. Dependent Collusion: Metadata leakage propagates through the topology, 
#      increasing the adversarial inference probability up to a defined cap.
#   6. Leakage Boundary (Stress Test): A parallel execution evaluates the theoretical 
#      upper bound by simulating the complete exfiltration of C_int.
# ==============================================================================

# ==============================================================================
# GLOBAL CONSTANTS AND BASIC UTILITIES
# ==============================================================================

PRIME = 1_000_003

def sha256_text(x: str) -> str:
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

def rng_token_hex(rnd: random.Random, nbytes: int = 16) -> str:
    return "".join(f"{rnd.getrandbits(8):02x}" for _ in range(nbytes))

def make_selector(semantic_key: str, salt: str) -> str:
    return "tau_" + sha256_text(f"{semantic_key}|{salt}")[:12]

def make_identity_proof(salt: str, selector: str, instance_id: str, verifier_id: str) -> str:
    """
    Identity/instance proof.
    The observed value is intentionally NOT included to enforce separation 
    between identity authentication and semantic validity.
    """
    return sha256_text(
        f"salt={salt}|selector={selector}|instance={instance_id}|verifier={verifier_id}"
    )

def stable_hidden_feature(value: Any, salt: str) -> int:
    """
    Hidden semantic feature extraction for the polynomial engine.
    Not exposed in C_pub and not available in the ordinary adversarial view.
    """
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return int(sha256_text(f"{salt}|{raw}")[:12], 16) % PRIME

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
    selector: str
    type_name: str
    public_domain_name: str
    instance_id: str
    verifier_id: str

@dataclass(frozen=True)
class LocalEvidence:
    selector: str
    observed_value: Any
    local_admissible: bool
    identity_proof: str
    instance_id: str
    verifier_id: str

@dataclass(frozen=True)
class PublicInvariantCategory:
    name: str
    description: str

@dataclass(frozen=True)
class HiddenConstraint:
    cid: str
    semantic_group_label: str
    selectors: Tuple[str, ...]
    feature_salts: Tuple[str, ...]
    linear_coeffs: Tuple[int, ...]
    quadratic_coeffs: Tuple[int, ...]
    pair_coeffs: Tuple[int, ...]
    cubic_mask: Tuple[int, ...]
    target: int
    modulus: int = PRIME

@dataclass
class PrivateCNVSInstance:
    fragments: Dict[str, PrivateFragment]
    hidden_salts: Dict[str, str]
    assignment: Dict[str, str]
    identity_hashes: Dict[str, str]
    instance_id: str
    C_pub: PublicInvariantCategory
    C_int: List[HiddenConstraint]
    hidden_topology_edges: Set[Tuple[str, str]]
    critical_selectors: Set[str]

@dataclass
class AdversaryView:
    selectors: Tuple[str, ...]
    local_tasks: Dict[str, LocalTaskView]
    C_pub: PublicInvariantCategory
    leaked_metadata_edges: Set[Tuple[str, str]]
    compromised_values: Dict[str, Any]
    compromised_proofs: Dict[str, str]
    compromised_verifiers: Set[str]
    C_int_leaked: bool = False

@dataclass
class SimulationConfig:
    trials: int = 10_000
    n_verifiers: int = 64
    coalition_fraction: float = 0.10
    gamma_top_leak: float = 0.12
    dependent_infer_base: float = 0.015
    dependent_infer_rho: float = 0.35
    p_infer_cap: float = 0.45
    p_identity_after_infer: float = 0.15
    blind_attempts: int = 1
    C_int_leak_probability: float = 0.0
    seed: int = 42

# ==============================================================================
# DECLARATION AND INVARIANT UNIVERSE
# ==============================================================================

def default_payload() -> Dict[str, Any]:
    return {
        "owner_id": "owner_042", "city_code": "MIL", "asset_class": "government",
        "floor": 3, "area_sqm": 120, "parcel_zone": "Z7", "risk_tier": 6,
        "clearance_level": 4, "facility_class": "S", "access_count": 48,
        "device_count": 17, "data_sensitivity": 6, "audit_class": "restricted",
        "device_firmware_class": "hardened", "network_zone": "segmented",
        "operator_role": "admin",
    }

def domain_specs() -> Dict[str, DomainSpec]:
    return {
        "owner_id": DomainSpec("private_identifier", str, tuple(f"owner_{i:03d}" for i in range(100))),
        "city_code": DomainSpec("geo_code", str, ("MIL", "ROM", "TOR", "GEN", "NAP", "BOL", "FIR")),
        "asset_class": DomainSpec("asset_class", str, ("residential", "industrial", "government", "restricted")),
        "floor": DomainSpec("integer_level", int, tuple(range(-2, 31))),
        "area_sqm": DomainSpec("bounded_measure", int, tuple(range(40, 401, 5))),
        "parcel_zone": DomainSpec("zone_code", str, tuple(f"Z{i}" for i in range(1, 15))),
        "risk_tier": DomainSpec("risk_tier", int, tuple(range(1, 10))),
        "clearance_level": DomainSpec("clearance_level", int, tuple(range(0, 6))),
        "facility_class": DomainSpec("facility_class", str, ("A", "B", "C", "D", "S")),
        "access_count": DomainSpec("count", int, tuple(range(0, 200))),
        "device_count": DomainSpec("count", int, tuple(range(1, 80))),
        "data_sensitivity": DomainSpec("sensitivity", int, tuple(range(1, 8))),
        "audit_class": DomainSpec("audit_class", str, ("open", "internal", "restricted", "classified")),
        "device_firmware_class": DomainSpec("firmware_class", str, ("legacy", "standard", "hardened", "certified")),
        "network_zone": DomainSpec("network_zone", str, ("flat", "segmented", "isolated", "airgapped")),
        "operator_role": DomainSpec("operator_role", str, ("guest", "user", "admin", "root")),
    }

def invariant_universe() -> List[Tuple[str, Tuple[str, ...]]]:
    """
    Stylized universe of possible invariant templates representing C_pub.
    """
    return [
        ("classification_sensitivity_clearance", ("asset_class", "clearance_level", "data_sensitivity")),
        ("facility_risk_device_density", ("facility_class", "risk_tier", "device_count")),
        ("geospatial_area_floor", ("parcel_zone", "area_sqm", "floor")),
        ("asset_facility_risk_clearance", ("asset_class", "facility_class", "risk_tier", "clearance_level")),
        ("sensitivity_access_devices", ("data_sensitivity", "access_count", "device_count")),
        ("city_zone_asset", ("city_code", "parcel_zone", "asset_class")),
        ("area_devices_facility_risk", ("area_sqm", "device_count", "facility_class", "risk_tier")),
        ("audit_sensitivity_clearance", ("audit_class", "data_sensitivity", "clearance_level")),
        ("firmware_network_facility", ("device_firmware_class", "network_zone", "facility_class")),
        ("operator_access_risk", ("operator_role", "access_count", "risk_tier")),
        ("asset_network_audit", ("asset_class", "network_zone", "audit_class")),
        ("firmware_devices_sensitivity", ("device_firmware_class", "device_count", "data_sensitivity")),
        ("operator_clearance_facility_zone", ("operator_role", "clearance_level", "facility_class", "network_zone")),
        ("geo_audit_asset_sensitivity", ("city_code", "parcel_zone", "audit_class", "data_sensitivity")),
        ("restricted_stack", ("asset_class", "facility_class", "network_zone", "audit_class", "device_firmware_class")),
    ]

# ==============================================================================
# HIDDEN CONSTRAINT EVALUATION (Polynomial Engine)
# ==============================================================================

def constraint_score(c: HiddenConstraint, candidate_values: Dict[str, Any]) -> int:
    """
    Nonlinear hidden structural-semantic constraint evaluation.
    Evaluates polynomial constraints over a finite field.
    """
    xs = [
        stable_hidden_feature(candidate_values[selector], salt)
        for selector, salt in zip(c.selectors, c.feature_salts)
    ]

    acc = 0

    for x, a, b, cmask in zip(xs, c.linear_coeffs, c.quadratic_coeffs, c.cubic_mask):
        acc = (acc + a * x + b * x * x + cmask * x * x * x) % c.modulus

    k = 0
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            acc = (acc + c.pair_coeffs[k] * xs[i] * xs[j]) % c.modulus
            k += 1

    return acc

def check_constraint(c: HiddenConstraint, evidence_values: Dict[str, Any]) -> bool:
    return constraint_score(c, evidence_values) == c.target

# ==============================================================================
# REFRESHED CNVS INSTANCE GENERATION
# ==============================================================================

def build_refreshed_cnvs_instance(
    instance_id: str,
    n_verifiers: int,
    seed: int,
    payload: Optional[Dict[str, Any]] = None,
) -> PrivateCNVSInstance:
    """
    Builds a fully refreshed CNVS instance (Moving Target Defense).
    Regenerates topology, assignments, and hidden invariants at every execution.
    """
    rnd = random.Random(seed)
    payload = payload or default_payload()
    domains = domain_specs()

    fragments: Dict[str, PrivateFragment] = {}
    hidden_salts: Dict[str, str] = {}

    for key, value in payload.items():
        salt = rng_token_hex(rnd, 16)
        selector = make_selector(key, salt)

        fragments[selector] = PrivateFragment(
            semantic_key=key, selector=selector, typ=type(value),
            true_value=value, domain=domains[key]
        )
        hidden_salts[selector] = salt

    verifiers = [f"V{i:03d}" for i in range(n_verifiers)]
    if len(verifiers) < len(fragments):
        raise ValueError("n_verifiers must be >= number of terminal fragments.")

    assigned_verifiers = rnd.sample(verifiers, len(fragments))
    assignment = {selector: verifier_id for selector, verifier_id in zip(fragments.keys(), assigned_verifiers)}

    identity_hashes = {
        selector: make_identity_proof(hidden_salts[selector], selector, instance_id, assignment[selector])
        for selector in fragments
    }

    C_pub = PublicInvariantCategory(
        name="hidden_structural_semantic_invariant_family",
        description="Public category only. C_int (theta_C, R_int, binding) remains hidden."
    )

    key_to_selector = {fragment.semantic_key: selector for selector, fragment in fragments.items()}
    universe = invariant_universe()
    k_constraints = rnd.randint(7, min(11, len(universe)))
    selected_templates = rnd.sample(universe, k_constraints)

    true_values = {selector: fragment.true_value for selector, fragment in fragments.items()}

    C_int: List[HiddenConstraint] = []
    hidden_topology_edges: Set[Tuple[str, str]] = set()

    for idx, (label, semantic_keys) in enumerate(selected_templates):
        selectors = tuple(key_to_selector[key] for key in semantic_keys)
        arity = len(selectors)

        feature_salts = tuple(rng_token_hex(rnd, 16) for _ in range(arity))
        linear_coeffs = tuple(rnd.randint(1, PRIME - 1) for _ in range(arity))
        quadratic_coeffs = tuple(rnd.randint(1, PRIME - 1) for _ in range(arity))
        cubic_mask = tuple(rnd.randint(0, PRIME - 1) for _ in range(arity))
        pair_coeffs = tuple(rnd.randint(1, PRIME - 1) for _ in range(arity * (arity - 1) // 2))

        provisional = HiddenConstraint(
            cid=f"c_{idx + 1}", semantic_group_label=label, selectors=selectors,
            feature_salts=feature_salts, linear_coeffs=linear_coeffs,
            quadratic_coeffs=quadratic_coeffs, pair_coeffs=pair_coeffs,
            cubic_mask=cubic_mask, target=0
        )

        target = constraint_score(provisional, true_values)

        C_int.append(HiddenConstraint(
            cid=provisional.cid, semantic_group_label=label, selectors=selectors,
            feature_salts=feature_salts, linear_coeffs=linear_coeffs,
            quadratic_coeffs=quadratic_coeffs, pair_coeffs=pair_coeffs,
            cubic_mask=cubic_mask, target=target
        ))

        for i in range(arity):
            for j in range(i + 1, arity):
                hidden_topology_edges.add(tuple(sorted((selectors[i], selectors[j]))))

    critical_selectors = {selector for c in C_int for selector in c.selectors}

    return PrivateCNVSInstance(
        fragments=fragments, hidden_salts=hidden_salts, assignment=assignment,
        identity_hashes=identity_hashes, instance_id=instance_id,
        C_pub=C_pub, C_int=C_int, hidden_topology_edges=hidden_topology_edges,
        critical_selectors=critical_selectors
    )

# ==============================================================================
# LOCAL EVIDENCE AND GLOBAL VALIDATION
# ==============================================================================

def emit_evidence(
    state: PrivateCNVSInstance, selector: str, observed_value: Any,
    identity_proof: Optional[str] = None, instance_id: Optional[str] = None,
) -> LocalEvidence:
    instance = instance_id or state.instance_id
    fragment = state.fragments[selector]
    local_ok = isinstance(observed_value, fragment.typ)
    proof = identity_proof if identity_proof is not None else state.identity_hashes[selector]

    return LocalEvidence(
        selector=selector, observed_value=observed_value,
        local_admissible=local_ok, identity_proof=proof,
        instance_id=instance, verifier_id=state.assignment[selector]
    )

def honest_evidence(state: PrivateCNVSInstance) -> Dict[str, LocalEvidence]:
    return {selector: emit_evidence(state, selector, fragment.true_value) for selector, fragment in state.fragments.items()}

def VG_accepts(state: PrivateCNVSInstance, evidence: Dict[str, LocalEvidence]) -> bool:
    """Decoupled global veto V_G."""
    if set(evidence.keys()) != set(state.fragments.keys()): return False
    for selector, ev in evidence.items():
        if ev.selector != selector or not ev.local_admissible: return False
        if ev.instance_id != state.instance_id: return False
        if ev.identity_proof != state.identity_hashes[selector]: return False

    values = {selector: ev.observed_value for selector, ev in evidence.items()}
    return all(check_constraint(c_i, values) for c_i in state.C_int)

# ==============================================================================
# ADVERSARY VIEW AND DEPENDENT MASS COLLUSION
# ==============================================================================

def make_adversary_view(state: PrivateCNVSInstance, cfg: SimulationConfig, rnd: random.Random) -> AdversaryView:
    all_verifiers = [f"V{i:03d}" for i in range(cfg.n_verifiers)]
    coalition_size = max(0, min(len(all_verifiers), round(cfg.coalition_fraction * cfg.n_verifiers)))
    compromised_verifiers = set(rnd.sample(all_verifiers, coalition_size))

    local_tasks, compromised_values, compromised_proofs = {}, {}, {}

    for selector, fragment in state.fragments.items():
        verifier_id = state.assignment[selector]
        local_tasks[selector] = LocalTaskView(
            selector=selector, type_name=fragment.typ.__name__,
            public_domain_name=fragment.domain.name, instance_id=state.instance_id,
            verifier_id=verifier_id
        )
        if verifier_id in compromised_verifiers:
            compromised_values[selector] = fragment.true_value
            compromised_proofs[selector] = state.identity_hashes[selector]

    leaked_edges = {edge for edge in state.hidden_topology_edges if rnd.random() < cfg.gamma_top_leak}
    selectors = list(state.fragments.keys())
    rnd.shuffle(selectors)

    changed = True
    propagation_passes = 0
    while changed and propagation_passes < 3:
        changed = False
        propagation_passes += 1
        for selector in selectors:
            if selector in compromised_values or selector not in state.critical_selectors: continue

            neighbors = {b for a, b in leaked_edges if a == selector} | {a for a, b in leaked_edges if b == selector}

            if not neighbors:
                p_infer = cfg.dependent_infer_base
            else:
                known_fraction = sum(1 for n in neighbors if n in compromised_values) / len(neighbors)
                p_infer = min(cfg.p_infer_cap, cfg.dependent_infer_base + cfg.dependent_infer_rho * known_fraction)

            if rnd.random() < p_infer:
                compromised_values[selector] = state.fragments[selector].true_value
                if rnd.random() < cfg.p_identity_after_infer:
                    compromised_proofs[selector] = state.identity_hashes[selector]
                changed = True

    C_int_leaked = rnd.random() < cfg.C_int_leak_probability

    return AdversaryView(
        selectors=tuple(state.fragments.keys()), local_tasks=local_tasks,
        C_pub=state.C_pub, leaked_metadata_edges=leaked_edges,
        compromised_values=compromised_values, compromised_proofs=compromised_proofs,
        compromised_verifiers=compromised_verifiers, C_int_leaked=C_int_leaked
    )

def random_alternative_value(fragment: PrivateFragment, rnd: random.Random) -> Any:
    values = list(fragment.domain.values)
    if fragment.true_value in values and len(values) > 1: values.remove(fragment.true_value)
    return rnd.choice(values)

def blind_forgery_attempt(state: PrivateCNVSInstance, adv: AdversaryView, cfg: SimulationConfig, rnd: random.Random) -> Tuple[bool, int, int]:
    controlled_critical = state.critical_selectors & set(adv.compromised_values.keys()) & set(adv.compromised_proofs.keys())
    h_crit = len(state.critical_selectors)
    if len(controlled_critical) < h_crit: return False, len(controlled_critical), h_crit

    for _ in range(cfg.blind_attempts):
        forged_values = {selector: fragment.true_value for selector, fragment in state.fragments.items()}
        mutated_selector = rnd.choice(list(controlled_critical))
        forged_values[mutated_selector] = random_alternative_value(state.fragments[mutated_selector], rnd)

        for selector in controlled_critical:
            if selector != mutated_selector and rnd.random() < 0.25:
                forged_values[selector] = random_alternative_value(state.fragments[selector], rnd)

        forged_evidence = {}
        for selector, fragment in state.fragments.items():
            proof = state.identity_hashes[selector] if selector in controlled_critical or selector not in state.critical_selectors else "missing_identity_proof"
            forged_evidence[selector] = emit_evidence(state, selector, forged_values[selector], identity_proof=proof)

        if VG_accepts(state, forged_evidence):
            if any(forged_values[s] != state.fragments[s].true_value for s in state.fragments):
                return True, len(controlled_critical), h_crit

    return False, len(controlled_critical), h_crit

def Cint_leak_worst_case_attack(state: PrivateCNVSInstance, adv: AdversaryView) -> bool:
    """Upper-bound validation boundary: Assumes full C_int exfiltration."""
    if not adv.C_int_leaked: return False
    controlled_critical = state.critical_selectors & set(adv.compromised_values.keys()) & set(adv.compromised_proofs.keys())
    return len(controlled_critical) == len(state.critical_selectors)

# ==============================================================================
# REFRESH SCENARIO
# ==============================================================================

def fingerprint_Cint(state: PrivateCNVSInstance) -> str:
    serializable = [{
        "cid": c.cid, "selectors": c.selectors, "linear_coeffs": c.linear_coeffs,
        "target": c.target, "modulus": c.modulus
    } for c in state.C_int]
    return sha256_text(json.dumps(serializable, sort_keys=True))[:16]

def scenario_full_refresh_attack(cfg: SimulationConfig) -> None:
    payload = default_payload()
    state_t = build_refreshed_cnvs_instance("instance_t", cfg.n_verifiers, cfg.seed, payload)
    state_t1 = build_refreshed_cnvs_instance("instance_t_plus_1", cfg.n_verifiers, cfg.seed + 1, payload)

    print("\n================ TOPOLOGICAL REFRESH (MTD) ================\n")
    print("Same declaration/payload, different CNVS internal structure.")
    print(f"C_int fingerprint at t:     {fingerprint_Cint(state_t)}")
    print(f"C_int fingerprint at t + 1: {fingerprint_Cint(state_t1)}")
    
    stale_evidence = honest_evidence(state_t)
    replay_result = VG_accepts(state_t1, stale_evidence)
    print(f"\nReplay of old evidence against refreshed instance accepted by V_G: {replay_result}")

# ==============================================================================
# PROGRESSIVE MASS COLLUSION EXPERIMENT
# ==============================================================================

def run_single_collusion_level(cfg: SimulationConfig, coalition_fraction: float, trials: int, seed_offset: int = 0) -> Dict[str, Any]:
    rnd = random.Random(cfg.seed + seed_offset)
    blind_false_accepts, Cint_leak_breaks, all_critical_controlled = 0, 0, 0
    controlled_counts, h_values, metadata_edges_seen = [], [], []

    for trial in range(trials):
        state = build_refreshed_cnvs_instance(f"instance_{seed_offset}_{trial}", cfg.n_verifiers, cfg.seed + seed_offset + trial, default_payload())
        if not VG_accepts(state, honest_evidence(state)): raise RuntimeError("Honest CNVS state must validate.")

        local_cfg = SimulationConfig(
            trials=cfg.trials, n_verifiers=cfg.n_verifiers, coalition_fraction=coalition_fraction,
            gamma_top_leak=cfg.gamma_top_leak, dependent_infer_base=cfg.dependent_infer_base,
            dependent_infer_rho=cfg.dependent_infer_rho, p_infer_cap=cfg.p_infer_cap,
            p_identity_after_infer=cfg.p_identity_after_infer, blind_attempts=cfg.blind_attempts,
            C_int_leak_probability=cfg.C_int_leak_probability, seed=cfg.seed + seed_offset + trial,
        )

        adv = make_adversary_view(state, local_cfg, rnd)
        blind_ok, controlled, h_crit = blind_forgery_attempt(state, adv, local_cfg, rnd)
        leak_ok = Cint_leak_worst_case_attack(state, adv)

        controlled_counts.append(controlled)
        h_values.append(h_crit)
        metadata_edges_seen.append(len(adv.leaked_metadata_edges))

        if controlled == h_crit: all_critical_controlled += 1
        if blind_ok: blind_false_accepts += 1
        if leak_ok: Cint_leak_breaks += 1

    return {
        "coalition_fraction": coalition_fraction,
        "avg_h_crit": statistics.mean(h_values),
        "avg_controlled_critical": statistics.mean(controlled_counts),
        "max_controlled_critical": max(controlled_counts),
        "all_critical_controlled_rate": all_critical_controlled / trials,
        "blind_false_accept_rate": blind_false_accepts / trials,
        "Cint_leak_break_rate": Cint_leak_breaks / trials,
    }

def run_progressive_mass_collusion(cfg: SimulationConfig) -> List[Dict[str, Any]]:
    fractions = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.98, 0.99, 1.00]
    return [run_single_collusion_level(cfg, frac, cfg.trials, 10_000 * i) for i, frac in enumerate(fractions)]

def print_progressive_mass_collusion_results(results: List[Dict[str, Any]], title: str) -> None:
    print(f"\n================ {title} ================\n")
    header = "collusion | avg_h | avg_ctrl | max_ctrl | P(all critical) | P(false accept) | P(C_int leak break)"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['coalition_fraction'] * 100:7.0f}% | {r['avg_h_crit']:5.2f} | {r['avg_controlled_critical']:8.2f} | {r['max_controlled_critical']:8d} | {r['all_critical_controlled_rate']:15.8f} | {r['blind_false_accept_rate']:15.8f} | {r['Cint_leak_break_rate']:19.8f}")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    ordinary_cfg = SimulationConfig(
        trials=10_000, n_verifiers=64, coalition_fraction=0.10, gamma_top_leak=0.12,
        dependent_infer_base=0.015, dependent_infer_rho=0.35, p_infer_cap=0.45,
        p_identity_after_infer=0.15, blind_attempts=1, C_int_leak_probability=0.0, seed=42,
    )

    scenario_full_refresh_attack(ordinary_cfg)

    ordinary_results = run_progressive_mass_collusion(ordinary_cfg)
    print_progressive_mass_collusion_results(ordinary_results, title="PROGRESSIVE MASS COLLUSION — ORDINARY MODEL (C_pub ONLY)")

    # Upper-Bound Validation (Assumption of total C_int leakage)
    leakage_cfg = SimulationConfig(
        trials=10_000, n_verifiers=64, coalition_fraction=0.10, gamma_top_leak=0.12,
        dependent_infer_base=0.015, dependent_infer_rho=0.35, p_infer_cap=0.45,
        p_identity_after_infer=0.15, blind_attempts=1, C_int_leak_probability=1.0, seed=4242,
    )

    leak_results = run_progressive_mass_collusion(leakage_cfg)
    print_progressive_mass_collusion_results(leak_results, title="PROGRESSIVE MASS COLLUSION — C_int LEAKAGE BOUNDARY PROJECTION")

    print("\n================ FINAL ARCHITECTURAL INTERPRETATION ================\n")
    print("- Moving Target Defense: Each instance refreshes topology, binding, and invariant family C={c_i}.")
    print("- Progressive mass collusion tested up to 100%.")
    print("- P(all critical) measures threshold breach.")
    print("- P(false accept) measures false global acceptance under the ordinary C_pub-only view.")
    print("- The C_int leak run provides a theoretical upper-bound break model.")
