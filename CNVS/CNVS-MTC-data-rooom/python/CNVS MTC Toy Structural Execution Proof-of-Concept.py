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
import secrets
from dataclasses import dataclass
from typing import Dict, Any, Callable, List

# ==============================================================================
# CNVS STRUCTURAL PROOF-OF-CONCEPT: 
# PEDAGOGICAL EXECUTION ENVIRONMENT
#
# PURPOSE:
# This script is an application-layer pedagogical demonstrator. It isolates
# and explicitly models the foundational mechanics of the CNVS framework:
#   1. Terminal fragmentation and opaque selector generation.
#   2. The deliberate weakness of local validation (V_L).
#   3. Identity/instance authentication strictly decoupled from semantic truth.
#   4. Decoupled Global Veto (V_G) based on hidden internal constraints (C_int).
#
# FORMAL ASSUMPTIONS (Pedagogical Abstraction):
# This is a simplified structural model. In the full formal theory, the invariant
# family C = {c_1, ..., c_n} is not a trivial linear equation, but a complex set
# of structural, semantic, and topological constraints.
# Here, a linear placeholder (c_1) is used strictly to render the underlying
# geometric validation logic visible in a minimal execution environment.
#
# EPOCH / REFRESH NOTE:
# This toy model keeps an epoch field only as a compact approximation of
# application-layer replay protection used in many current systems. It is NOT
# presented as the core CNVS replay-resistance mechanism. In the full CNVS model,
# a new verification instance performs a complete topological and semantic
# refresh: new selectors, new binding, new internal topology R_int, and a new
# instantiated invariant family C_int = <theta_C, R_int, binding>.
# ==============================================================================

# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass(frozen=True)
class TerminalFragment:
    """
    Internal representation of a terminal fragment.
    Belongs exclusively to the private global state. Local verifiers do not 
    receive the semantic_key or the true_value.
    """
    semantic_key: str
    selector: str
    typ: type
    true_value: Any

@dataclass(frozen=True)
class LocalEvidence:
    """
    Evidence submitted by a local verifier.
    The identity_proof authenticates the node and the current instance/epoch label,
    NOT the observed_value. A compromised node may submit a locally admissible
    false value while carrying a valid identity proof.

    In this pedagogical model, the epoch field is a compact replay-protection
    proxy. In the full CNVS architecture, replay resistance is primarily modeled
    by full topological and invariant refresh across verification instances.
    """
    selector: str
    observed_value: Any
    local_admissible: bool
    identity_proof: str
    epoch: str

@dataclass(frozen=True)
class PublicInvariantCategory:
    """
    C_pub: Public invariant category.
    Granted to the adversary in the ordinary threat model. It reveals the class 
    of constraints (e.g., "structural-semantic grids") but hides the instantiated 
    parameters, internal topology, and exact binding.
    """
    name: str
    description: str

@dataclass(frozen=True)
class InternalInvariantParameters:
    """
    theta_C: Hidden internal parameters of the instantiated invariant.
    In this pedagogical model, it is abstracted as a simple scale_factor and target.
    """
    scale_factor: int
    target: int
    description: str

@dataclass
class CNVS_Semantic_State:
    """
    Private global CNVS state.
    Contains the full C_int = <theta_C, R_int, binding>. 
    The adversary does not have access to this structure.
    """
    fragments: Dict[str, TerminalFragment]
    hidden_salts: Dict[str, str]
    identity_hashes: Dict[str, str]
    epoch: str
    C_pub: PublicInvariantCategory
    theta_C: InternalInvariantParameters
    hidden_relation_binding: Dict[str, str]

# ==============================================================================
# CRYPTOGRAPHIC UTILITIES
# ==============================================================================

def sha256_text(x: str) -> str:
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

def make_selector(semantic_key: str, salt: str) -> str:
    """Creates an opaque terminal selector, masking the semantic key."""
    return "tau_" + sha256_text(f"{semantic_key}|{salt}")[:12]

def make_identity_hash(salt: str, selector: str, epoch: str) -> str:
    """
    Identity/instance commitment.
    Intentionally excludes the observed value to enforce the separation between
    authentication and global semantic truth.

    The epoch label is retained only as a pedagogical approximation of replay
    protection. Full CNVS replay resistance is represented by topological and
    semantic refresh, not by a timestamp check alone.
    """
    return sha256_text(f"salt={salt}|selector={selector}|epoch={epoch}")

# ==============================================================================
# ENVIRONMENT GENERATION (Trusted Setup)
# ==============================================================================

def build_execution_environment(payload: Dict[str, Any], epoch: str) -> CNVS_Semantic_State:
    """
    Converts a standard payload into a private CNVS semantic state.
    """
    fragments: Dict[str, TerminalFragment] = {}
    hidden_salts: Dict[str, str] = {}
    identity_hashes: Dict[str, str] = {}

    # 1. Terminal decomposition
    for key, value in payload.items():
        salt = secrets.token_hex(16)
        selector = make_selector(key, salt)

        frag = TerminalFragment(
            semantic_key=key,
            selector=selector,
            typ=type(value),
            true_value=value
        )
        fragments[selector] = frag
        hidden_salts[selector] = salt
        identity_hashes[selector] = make_identity_hash(salt, selector, epoch)

    # 2. Public category C_pub
    C_pub = PublicInvariantCategory(
        name="structural_semantic_consistency",
        description="Public view: the state is governed by hidden geometric constraints."
    )

    # 3. Hidden internal binding (R_int surrogate)
    floor_selector = next(s for s, f in fragments.items() if f.semantic_key == "Piano")
    area_selector = next(s for s, f in fragments.items() if f.semantic_key == "Metratura")

    hidden_relation_binding = {
        "floor_role": floor_selector,
        "area_role": area_selector
    }

    # 4. Hidden instantiated parameters (theta_C surrogate)
    scale_factor = 40
    target = (payload["Piano"] * scale_factor) - payload["Metratura"]

    theta_C = InternalInvariantParameters(
        scale_factor=scale_factor,
        target=target,
        description="Pedagogical theta_C for demonstration purposes."
    )

    return CNVS_Semantic_State(
        fragments=fragments,
        hidden_salts=hidden_salts,
        identity_hashes=identity_hashes,
        epoch=epoch,
        C_pub=C_pub,
        theta_C=theta_C,
        hidden_relation_binding=hidden_relation_binding
    )

# ==============================================================================
# LOCAL VALIDATION (V_L) & EVIDENCE EMISSION
# ==============================================================================

def V_L(state: CNVS_Semantic_State, selector: str, observed_value: Any) -> bool:
    """
    Weak local validation. Verifies structure and type, but remains semantically blind.
    """
    if selector not in state.fragments:
        return False
    expected_type = state.fragments[selector].typ
    return isinstance(observed_value, expected_type)

def emit_evidence(
    state: CNVS_Semantic_State,
    selector: str,
    observed_value: Any,
    *,
    use_valid_identity: bool = True,
    epoch_override: str | None = None
) -> LocalEvidence:
    """
    Test helper: simulates emission of evidence by an honest or compromised node.
    """
    epoch = epoch_override if epoch_override is not None else state.epoch
    local_ok = V_L(state, selector, observed_value)

    if selector in state.hidden_salts and use_valid_identity:
        proof = make_identity_hash(state.hidden_salts[selector], selector, epoch)
    else:
        proof = "invalid_identity_proof"

    return LocalEvidence(
        selector=selector,
        observed_value=observed_value,
        local_admissible=local_ok,
        identity_proof=proof,
        epoch=epoch
    )

# ==============================================================================
# GLOBAL VETO (V_G)
# ==============================================================================

def Cons_R(state: CNVS_Semantic_State, evidence: Dict[str, LocalEvidence]) -> bool:
    """Barrier 1: Relational/Topological completeness."""
    expected_selectors = set(state.fragments.keys())
    received_selectors = set(evidence.keys())

    if expected_selectors != received_selectors:
        return False

    for selector, ev in evidence.items():
        if ev.selector != selector or not ev.local_admissible:
            return False
    return True

def Verify_Identity(state: CNVS_Semantic_State, evidence: Dict[str, LocalEvidence]) -> bool:
    """
    Barrier 2: Identity/instance authentication.

    This toy model keeps an epoch field as a simplified replay-protection proxy,
    comparable to current application-layer session or epoch checks. This is not
    the central CNVS defense. In the full model, a replayed view fails because
    the next verification instance refreshes selectors, binding, topology R_int,
    and the instantiated invariant family C_int.
    """
    for selector, ev in evidence.items():
        if selector not in state.hidden_salts or ev.epoch != state.epoch:
            return False
        if ev.identity_proof != state.identity_hashes[selector]:
            return False
    return True

def c_1_geometric_consistency(state: CNVS_Semantic_State, evidence: Dict[str, LocalEvidence]) -> bool:
    """Barrier 3: Hidden constraint evaluation."""
    floor_selector = state.hidden_relation_binding["floor_role"]
    area_selector = state.hidden_relation_binding["area_role"]

    floor_val = evidence[floor_selector].observed_value
    area_val = evidence[area_selector].observed_value

    candidate_result = (floor_val * state.theta_C.scale_factor) - area_val
    return candidate_result == state.theta_C.target

def Inv_C(state: CNVS_Semantic_State, evidence: Dict[str, LocalEvidence]) -> bool:
    """Evaluates the full invariant family C."""
    hidden_constraints: List[Callable[[CNVS_Semantic_State, Dict[str, LocalEvidence]], bool]] = [
        c_1_geometric_consistency
    ]
    return all(c_i(state, evidence) for c_i in hidden_constraints)

def VG(state: CNVS_Semantic_State, evidence: Dict[str, LocalEvidence]) -> str:
    """Decoupled Global Veto V_G execution."""
    if not Cons_R(state, evidence):
        return "VETO: Relational/Topological coherence failed."
    if not Verify_Identity(state, evidence):
        return "VETO: Identity/instance authentication failed."
    if not Inv_C(state, evidence):
        return "VETO: Hidden invariant family C_int failed."

    return "ACCEPTED: Global state validated."

# ==============================================================================
# INTROSPECTION HELPERS
# ==============================================================================

def get_selector_by_semantic_key(state: CNVS_Semantic_State, semantic_key: str) -> str:
    return next(s for s, f in state.fragments.items() if f.semantic_key == semantic_key)

def print_public_adversary_view(state: CNVS_Semantic_State) -> None:
    public_view = {
        "epoch": state.epoch,
        "public_selectors": list(state.fragments.keys()),
        "C_pub_granted": state.C_pub.name,
        "C_int_hidden": ["theta_C", "R_int", "hidden_relation_binding", "true_values", "salts"]
    }
    print(json.dumps(public_view, indent=2, ensure_ascii=False))

# ==============================================================================
# TEST SUITE
# ==============================================================================

def run_scenarios() -> None:
    print("--- CNVS STRUCTURAL PROOF-OF-CONCEPT INITIALIZATION ---")
    payload = {"Proprietario": "Enzo", "Città": "Milano", "Piano": 3, "Metratura": 120}
    state = build_execution_environment(payload, epoch="time_zero")

    sel_owner = get_selector_by_semantic_key(state, "Proprietario")
    sel_city = get_selector_by_semantic_key(state, "Città")
    sel_floor = get_selector_by_semantic_key(state, "Piano")
    sel_area = get_selector_by_semantic_key(state, "Metratura")

    print("\n[Adversary Public View]")
    print_public_adversary_view(state)

    print("\n[Scenario 1] Honest Execution (Baseline)")
    ev_1 = {
        sel_owner: emit_evidence(state, sel_owner, "Enzo"),
        sel_city: emit_evidence(state, sel_city, "Milano"),
        sel_floor: emit_evidence(state, sel_floor, 3),
        sel_area: emit_evidence(state, sel_area, 120)
    }
    print("Result:", VG(state, ev_1))

    print("\n[Scenario 2] Topological Incompleteness (DoS/Censorship)")
    ev_2 = {
        sel_owner: emit_evidence(state, sel_owner, "Enzo"),
        sel_floor: emit_evidence(state, sel_floor, 3),
        sel_area: emit_evidence(state, sel_area, 120)
    }
    print("Result:", VG(state, ev_2))

    print("\n[Scenario 3] Semantic Forgery (C_pub granted, C_int hidden)")
    print("Condition: Adversary submits valid identity + well-typed false value (Piano=1).")
    ev_3 = {
        sel_owner: emit_evidence(state, sel_owner, "Enzo"),
        sel_city: emit_evidence(state, sel_city, "Milano"),
        sel_floor: emit_evidence(state, sel_floor, 1),
        sel_area: emit_evidence(state, sel_area, 120)
    }
    print("Result:", VG(state, ev_3))

    print("\n[Scenario 4] Replay Approximation (Legacy Epoch-Style Guard)")
    print("Note: This is a simplified approximation of replay protection in current")
    print("application-layer systems. It is NOT the central CNVS refresh model.")
    print("In full CNVS, a replayed view fails because the next instance refreshes")
    print("selectors, binding, topology R_int, and the invariant family C_int.")
    ev_4 = {
        sel_owner: emit_evidence(state, sel_owner, "Enzo", epoch_override="wrong_epoch"),
        sel_city: emit_evidence(state, sel_city, "Milano", epoch_override="wrong_epoch"),
        sel_floor: emit_evidence(state, sel_floor, 3, epoch_override="wrong_epoch"),
        sel_area: emit_evidence(state, sel_area, 120, epoch_override="wrong_epoch")
    }
    print("Result:", VG(state, ev_4))

    print("\n[Scenario 5] C_int Leakage (Upper Bound Break)")
    print("Condition: Adversary is artificially granted theta_C and R_int.")
    ev_5 = {
        sel_owner: emit_evidence(state, sel_owner, "Enzo"),
        sel_city: emit_evidence(state, sel_city, "Milano"),
        sel_floor: emit_evidence(state, sel_floor, 1),
        sel_area: emit_evidence(state, sel_area, 40)
    }
    print("Result:", VG(state, ev_5))

if __name__ == "__main__":
    run_scenarios()