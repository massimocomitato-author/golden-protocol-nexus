# CNVS Test 14: Full-Pipeline Semantic Execution and Progressive Invariant Validation

**Author:** Massimo Comitato  
**License:** PolyForm Noncommercial 1.0.0

## Overview

`test_14_semantic_end_to_end_cnvs_full_pipeline.py` is an engineering-hardened executable environment that validates the core Closed Native Verification Systems (CNVS) architecture. 

Unlike prior mathematical models that process abstract prime-field integers, Test 14 evaluates the framework using a highly structured, heterogeneous real-world dataset. The test executes the rigid, consensus-free global validation pipeline (`V_L -> Cons_R -> Inv_C -> V_G`) across 500,000 vectorized iterations per parametric cycle, cross-referencing the statistical arrays with literal, node-by-node object-graph audits.

The analytical probability bounds (e.g., exact hypergeometric distributions and Theorem 4 limits) are calculated strictly for comparative plotting; they **never** decide the acceptance or rejection of a candidate state.

---

## The Canonical Semantic Instance: "Enzo's House"

To empirically prove the CNVS "Shattered Object" metaphor, Test 14 abandons randomly generated integers and instead parses a canonical text document describing a physical reality: **The building and apartment of dr. Vincenzo Comitato ("Enzo").**

This is not merely a narrative choice; it serves as a strict technical scaffolding that mimics a complex Building Information Model (BIM) or an architectural registry. It introduces several critical engineering constraints:

### 1. Heterogeneous Data Typology
The framework must process and validate different data types simultaneously. The Enzo instance generates facts as:
*   **Strings:** (e.g., `building.color = "light green"`)
*   **Booleans:** (e.g., `enzo.entry_door.armored = True`)
*   **Integers:** (e.g., `building.floors = 4`)
*   **Floats with defined local error tolerances ($\epsilon$):** (e.g., `garden.length_ew_m = 100.0`, with $\epsilon = 0.05$)

### 2. The Atomization Rule
To distribute the validation across thousands of verifiers without artificially duplicating data, the physical description is logically atomized into distinct terminal data points. 
For example, the garden's perimeter wall is described as having 1,980 individual columns. The CNVS engine instantiates 1,980 distinct, addressable leaf selectors (`fence.column.0001` through `fence.column.1980`), proving that real-world payloads naturally provide enough entropy and terminal fragmentation to sustain high-scale geometric distribution.

### 3. Progressive Semantic Equations (Physical Laws)
By using a physical building, the test introduces **Semantic Equations**. These are explicit mathematical relationships that bind the dispersed fragments together. Examples implemented in the code include:
*   `building_footprint`: Area = Length x Depth
*   `apartment_count`: Total = Floors x Apartments_per_Floor
*   `fence_column_count`: Columns = Modular_Length / Pitch

These semantic invariants are evaluated *progressively* during the bottom-up reconstruction of the tree. If a malicious verifier subtly alters the width of the kitchen (staying within the local $\epsilon$ tolerance so V_L passes), the node responsible for computing the `kitchen_area` equation will detect the geometrical impossibility and veto the entire branch *before* the computation reaches the global root.

---

## The Validation Pipeline

Test 14 rigorously enforces the four-stage short-circuit logic:

1. **V_L (Local Admissibility):** Checks if the observed value conforms to the declared type and falls within the authorized local measurement tolerance ($\epsilon$).
2. **Cons_R (Relational Consistency):** Verifies the structural integrity of the decomposition graph D(s), ensuring no missing leaves, no duplicated assignments (injectivity check), and confirming cryptographically bound parent/child roles.
3. **Inv_C (Invariant Consistency):** Progressively evaluates the physical/semantic equations (described above) and solves the hidden, full-rank linear matrix over the normalized critical state.
4. **V_G (Global Veto):** The final boolean. Any failure in stages 1, 2, or 3 immediately triggers a systemic rejection.

---

## Experimental Threat Vectors

The script subjects the "Enzo" dataset to multiple adversarial stress tests:

*   **Stealth Semantic Forgeries:** The adversary modifies critical values (e.g., room dimensions) strictly *inside* the $\epsilon$ tolerance limits. This forces V_L to pass, proving that the system successfully relies on the hidden global constraints (Inv_C) to catch the forgery.
*   **Relational Attacks:** The adversary attempts to bypass Cons_R through blind parent-node guesses, role-swapping between semantic objects, assignment collisions, and replay attacks with stale task digests.
*   **Epistemic Leakage:** The framework progressively leaks rows of the hidden invariant matrix (C_int) to the adversary. The test measures the bounded solver's ability to locate a feasible false state within the leaked nullspace.
*   **Absurd Data & Topology Refresh:** Blatant data falsifications (exceeding $\epsilon$) immediately trigger V_L rejection. The system then simulates the expulsion of the colluding verifiers and executes both isolated branch-refresh and full-topology refresh algorithms, logging the computational latencies (in nanoseconds) required to restore consensus-free security.

---

## Execution Instructions

The test is fully self-contained. It requires Python 3.10+ and the `numpy` and `matplotlib` libraries.

**Full Execution (Default 500,000 iterations per cycle):**

    python test_14_semantic_end_to_end_cnvs_full_pipeline.py

*Note: Due to the extreme density of the Monte Carlo arrays and the literal object-graph cross-audits, a full execution will consume significant CPU time.*

**Smoke Test (Rapid Syntax & Workflow Audit):**

    python test_14_semantic_end_to_end_cnvs_full_pipeline.py --smoke --no-show

The `--smoke` flag strictly reduces the computational budget (iterations per cycle) without altering the validation architecture, allowing for quick debugging.

## Outputs

All execution artifacts are automatically routed to a dynamically generated folder (`test_14_outputs` by default). The suite generates:
*   High-resolution `.csv` data tables charting failure rates across V_L, Cons_R, and Inv_C.
*   `.png` plots comparing empirical acceptance rates against exact theoretical models.
*   A comprehensive JSON manifest containing the cryptographic seed records, matrix ranks, and simulation conditions for deterministic reproducibility.