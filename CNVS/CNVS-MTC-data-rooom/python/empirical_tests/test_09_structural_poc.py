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
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Callable, List

import numpy as np
import matplotlib.pyplot as plt


# ==============================================================================
#
# Test Name: Test 9 - Structural Proof-of-Concept (Decoupled Pedagogical Validation Model)
# filename = "test_09_structural_poc.py"
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
    Belongs exclusively to the private global state.
    Local verifiers do not receive the semantic_key or the true_value.
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
    of constraints but hides the instantiated parameters, internal topology,
    and exact binding.
    """
    name: str
    description: str


@dataclass(frozen=True)
class InternalInvariantParameters:
    """
    theta_C: Hidden internal parameters of the instantiated invariant.

    In this pedagogical model, theta_C is abstracted as a simple scale_factor
    and target.
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
    """
    Creates an opaque terminal selector, masking the semantic key.
    """
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
# ENVIRONMENT GENERATION — TRUSTED SETUP
# ==============================================================================

def build_execution_environment(
    payload: Dict[str, Any],
    epoch: str
) -> CNVS_Semantic_State:
    """
    Converts a standard payload into a private CNVS semantic state.
    """
    fragments: Dict[str, TerminalFragment] = {}
    hidden_salts: Dict[str, str] = {}
    identity_hashes: Dict[str, str] = {}

    # 1. Terminal decomposition.
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

    # 2. Public invariant category C_pub.
    C_pub = PublicInvariantCategory(
        name="structural_semantic_consistency",
        description="Public view: the state is governed by hidden geometric constraints."
    )

    # 3. Hidden internal binding, used here as an R_int surrogate.
    floor_selector = next(
        s for s, f in fragments.items()
        if f.semantic_key == "Piano"
    )

    area_selector = next(
        s for s, f in fragments.items()
        if f.semantic_key == "Metratura"
    )

    hidden_relation_binding = {
        "floor_role": floor_selector,
        "area_role": area_selector
    }

    # 4. Hidden instantiated parameters, used here as theta_C surrogate.
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
# LOCAL VALIDATION V_L AND EVIDENCE EMISSION
# ==============================================================================

def V_L(
    state: CNVS_Semantic_State,
    selector: str,
    observed_value: Any
) -> bool:
    """
    Weak local validation.

    Verifies only structure and type.
    It remains semantically blind.
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
    Test helper.

    Simulates emission of evidence by an honest or compromised node.
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
# GLOBAL VETO V_G
# ==============================================================================

def Cons_R(
    state: CNVS_Semantic_State,
    evidence: Dict[str, LocalEvidence]
) -> bool:
    """
    Barrier 1: Relational / topological completeness.
    """
    expected_selectors = set(state.fragments.keys())
    received_selectors = set(evidence.keys())

    if expected_selectors != received_selectors:
        return False

    for selector, ev in evidence.items():
        if ev.selector != selector:
            return False

        if not ev.local_admissible:
            return False

    return True


def Verify_Identity(
    state: CNVS_Semantic_State,
    evidence: Dict[str, LocalEvidence]
) -> bool:
    """
    Barrier 2: Identity / instance authentication.

    This toy model keeps an epoch field as a simplified replay-protection proxy.
    This is not the central CNVS defense.

    In the full CNVS model, a replayed view fails because the next verification
    instance refreshes selectors, binding, topology R_int, and the instantiated
    invariant family C_int.
    """
    for selector, ev in evidence.items():
        if selector not in state.hidden_salts:
            return False

        if ev.epoch != state.epoch:
            return False

        if ev.identity_proof != state.identity_hashes[selector]:
            return False

    return True


def c_1_geometric_consistency(
    state: CNVS_Semantic_State,
    evidence: Dict[str, LocalEvidence]
) -> bool:
    """
    Barrier 3: Hidden constraint evaluation.

    Pedagogical hidden invariant:

        candidate_result = Piano * scale_factor - Metratura

    The candidate must match the hidden target.
    """
    floor_selector = state.hidden_relation_binding["floor_role"]
    area_selector = state.hidden_relation_binding["area_role"]

    floor_val = evidence[floor_selector].observed_value
    area_val = evidence[area_selector].observed_value

    candidate_result = (floor_val * state.theta_C.scale_factor) - area_val

    return candidate_result == state.theta_C.target


def Inv_C(
    state: CNVS_Semantic_State,
    evidence: Dict[str, LocalEvidence]
) -> bool:
    """
    Evaluates the hidden invariant family C.
    """
    hidden_constraints: List[
        Callable[[CNVS_Semantic_State, Dict[str, LocalEvidence]], bool]
    ] = [
        c_1_geometric_consistency
    ]

    return all(c_i(state, evidence) for c_i in hidden_constraints)


def VG(
    state: CNVS_Semantic_State,
    evidence: Dict[str, LocalEvidence]
) -> str:
    """
    Decoupled Global Veto V_G execution.
    """
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

def get_selector_by_semantic_key(
    state: CNVS_Semantic_State,
    semantic_key: str
) -> str:
    return next(
        s for s, f in state.fragments.items()
        if f.semantic_key == semantic_key
    )


def print_public_adversary_view(state: CNVS_Semantic_State) -> None:
    public_view = {
        "epoch": state.epoch,
        "public_selectors": list(state.fragments.keys()),
        "C_pub_granted": state.C_pub.name,
        "C_int_hidden": [
            "theta_C",
            "R_int",
            "hidden_relation_binding",
            "true_values",
            "salts"
        ]
    }

    print(json.dumps(public_view, indent=2, ensure_ascii=False))


# ==============================================================================
# TEST SUITE — TERMINAL OUTPUT
# ==============================================================================

def run_scenarios() -> None:
    print("--- CNVS STRUCTURAL PROOF-OF-CONCEPT INITIALIZATION ---")

    payload = {
        "Proprietario": "Enzo",
        "Città": "Milano",
        "Piano": 3,
        "Metratura": 120
    }

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


# ==============================================================================
# TEST 9 PLOT DATA COLLECTION
# ==============================================================================

def collect_test09_plot_data() -> List[Dict[str, Any]]:
    """
    Collect structured scenario outcomes for Test 9 plotting.

    This function re-executes the five pedagogical scenarios and records:
      - local admissibility rate;
      - Cons_R outcome;
      - identity verification outcome;
      - Inv_C outcome;
      - final V_G acceptance outcome.

    The plots are explanatory only.
    They do not alter the validation logic.
    """

    payload = {
        "Proprietario": "Enzo",
        "Città": "Milano",
        "Piano": 3,
        "Metratura": 120
    }

    state = build_execution_environment(payload, epoch="time_zero")

    sel_owner = get_selector_by_semantic_key(state, "Proprietario")
    sel_city = get_selector_by_semantic_key(state, "Città")
    sel_floor = get_selector_by_semantic_key(state, "Piano")
    sel_area = get_selector_by_semantic_key(state, "Metratura")

    scenarios = [
        (
            "Honest",
            {
                sel_owner: emit_evidence(state, sel_owner, "Enzo"),
                sel_city: emit_evidence(state, sel_city, "Milano"),
                sel_floor: emit_evidence(state, sel_floor, 3),
                sel_area: emit_evidence(state, sel_area, 120),
            }
        ),
        (
            "Missing fragment",
            {
                sel_owner: emit_evidence(state, sel_owner, "Enzo"),
                sel_floor: emit_evidence(state, sel_floor, 3),
                sel_area: emit_evidence(state, sel_area, 120),
            }
        ),
        (
            "Semantic forgery",
            {
                sel_owner: emit_evidence(state, sel_owner, "Enzo"),
                sel_city: emit_evidence(state, sel_city, "Milano"),
                sel_floor: emit_evidence(state, sel_floor, 1),
                sel_area: emit_evidence(state, sel_area, 120),
            }
        ),
        (
            "Replay approximation",
            {
                sel_owner: emit_evidence(
                    state,
                    sel_owner,
                    "Enzo",
                    epoch_override="wrong_epoch"
                ),
                sel_city: emit_evidence(
                    state,
                    sel_city,
                    "Milano",
                    epoch_override="wrong_epoch"
                ),
                sel_floor: emit_evidence(
                    state,
                    sel_floor,
                    3,
                    epoch_override="wrong_epoch"
                ),
                sel_area: emit_evidence(
                    state,
                    sel_area,
                    120,
                    epoch_override="wrong_epoch"
                ),
            }
        ),
        (
            "C_int leak break",
            {
                sel_owner: emit_evidence(state, sel_owner, "Enzo"),
                sel_city: emit_evidence(state, sel_city, "Milano"),
                sel_floor: emit_evidence(state, sel_floor, 1),
                sel_area: emit_evidence(state, sel_area, 40),
            }
        ),
    ]

    rows: List[Dict[str, Any]] = []

    for label, evidence in scenarios:
        received = len(evidence)

        local_rate = (
            sum(bool(ev.local_admissible) for ev in evidence.values())
            / max(1, received)
        )

        cons_ok = bool(Cons_R(state, evidence))
        identity_ok = bool(Verify_Identity(state, evidence)) if cons_ok else False
        inv_ok = bool(Inv_C(state, evidence)) if cons_ok and identity_ok else False

        vg_result = VG(state, evidence)
        vg_ok = vg_result.startswith("ACCEPTED")

        rows.append({
            "scenario": label,
            "local_rate": local_rate,
            "Cons_R": int(cons_ok),
            "Identity": int(identity_ok),
            "Inv_C": int(inv_ok),
            "V_G": int(vg_ok),
        })

    return rows


# ==============================================================================
# TEST 9 PLOT GENERATION
# ==============================================================================

def plot_test09(
    rows: List[Dict[str, Any]],
    out_dir: Path,
    show_plots: bool = True
) -> None:
    """
    Generates Test 9 comparison plots.

    Output:
      - test_09_local_vs_global_acceptance.png
      - test_09_validation_barrier_outcomes.png

    If show_plots=True, the figures are also displayed in the notebook output.
    """

    out_dir.mkdir(parents=True, exist_ok=True)

    labels = [r["scenario"] for r in rows]
    x = np.arange(len(labels))
    width = 0.35

    # --------------------------------------------------------------------------
    # Plot 1: local admissibility vs global acceptance.
    # --------------------------------------------------------------------------

    plt.figure(figsize=(12, 7))

    plt.bar(
        x - width / 2,
        [r["local_rate"] for r in rows],
        width,
        label="Local admissibility rate"
    )

    plt.bar(
        x + width / 2,
        [r["V_G"] for r in rows],
        width,
        label="Global V_G acceptance"
    )

    plt.xticks(x, labels, rotation=20, ha="right")
    plt.ylim(0, 1.1)
    plt.ylabel("Rate / binary outcome")
    plt.title("CNVS Test 9: Local Admissibility vs Global Acceptance")
    plt.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    plt.tight_layout()

    output_1 = out_dir / "test_09_local_vs_global_acceptance.png"

    plt.savefig(
        output_1,
        dpi=300
    )

    if show_plots:
        plt.show()

    plt.close()

    # --------------------------------------------------------------------------
    # Plot 2: Sequential Validation Barrier Outcomes (Heatmap)
    # --------------------------------------------------------------------------
    from matplotlib.colors import ListedColormap

    barriers = ["Cons_R", "Identity", "Inv_C", "V_G"]
    values = np.array([[r[b] for b in barriers] for r in rows])

    fig, ax = plt.subplots(figsize=(10, 6))

    # Red (0 = Fail), Green (1 = Pass)
    cmap = ListedColormap(['#d62728', '#2ca02c'])

    cax = ax.imshow(values, cmap=cmap, aspect='auto')

    # Config X e Y
    ax.set_xticks(np.arange(len(barriers)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(barriers)
    ax.set_yticklabels(labels)

    
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Insert Matrix
    for i in range(len(labels)):
        for j in range(len(barriers)):
            val = values[i, j]
            text_label = "PASS" if val == 1 else "FAIL"
            ax.text(j, i, text_label, ha="center", va="center", color="white", fontweight="bold")

    ax.set_title("CNVS Test 9: Sequential Validation Barrier Outcomes (State Matrix)")
    fig.tight_layout()

    output_2 = out_dir / "test_09_validation_barrier_outcomes.png"

    plt.savefig(
        output_2,
        dpi=300
    )

    if show_plots:
        plt.show()

    plt.close()

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    run_scenarios()

    plot_rows = collect_test09_plot_data()

    output_dir = Path("figures/test_09")

    plot_test09(
        plot_rows,
        output_dir,
        show_plots=True
    )

    print("\n[Plot Output]")
    print(f"Saved: {output_dir / 'test_09_local_vs_global_acceptance.png'}")
    print(f"Saved: {output_dir / 'test_09_validation_barrier_outcomes.png'}")
    print(f"Absolute folder: {output_dir.resolve()}")
