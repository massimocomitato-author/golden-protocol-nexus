# Empirical Tests

This folder contains the **empirical and executable structural tests** of the CNVS MTC suite.

These tests instantiate simplified execution environments that evaluate CNVS behavior through explicit validation pipelines rather than through projection formulas alone.

---

## Scope

The empirical tests focus on the executable separation between:

```text
local admissibility
```

and

```text
global validity
```

They are designed to demonstrate that a candidate state may pass local syntactic or relational checks while still failing global validation through hidden invariant binding.

---

## Included Tests

| Test | Description | Recommended File |
|---|---|---|
| Test 9 | Structural Proof-of-Concept / Decoupled Pedagogical Validation Model | `test_09_structural_poc.py` |
| Test 10 | Advanced Execution Environment / Full Structural-Semantic Model | `test_10_full_structural_semantic_model.py` |
| Test 11 | Executable Fragmentation Sensitivity under Hidden Invariant Binding | `test_11_fragmentation_sensitivity.py` |

---

## Architectural Notice

This folder includes:

```text
Architectural_Notice.md
```

The notice explains the simplification boundary of the empirical tests.

In particular, the empirical tests intentionally compress the broader CNVS architecture into an executable model centered on the hidden invariant binding `C_int`.

This is a conservative simplification.

The full CNVS architecture includes additional layers such as:

- `V_L` local verification;
- `R_int` intrinsic topological relations;
- structural and relational coherence;
- partial sub-invariants `c_i`;
- hidden global invariant binding `C_int`;
- final Global Veto.

Because `C_int` appears centrally in these empirical tests, the architectural notice is placed in this folder rather than in the repository root.

---

## Scientific Role

The empirical tests are intended to show that:

- local verification does not imply global truth;
- authentication does not imply semantic acceptance;
- peripheral verifier compromise does not automatically imply global falsification;
- hidden invariant binding can reject locally admissible forged states;
- exfiltration of `C_int` collapses the ordinary security model in the control scenario.

---

## Methodological Notice

The empirical tests do not replace the formal CNVS proof.

They are executable structural models under explicit assumptions.

They should be read as technical due-diligence artifacts and proof-of-concept environments, not as production CNVS protocol implementations.

---

## Important Limitation

The empirical tests simplify the full CNVS stack.

They do not claim to implement all topological, semantic, cryptographic, networking, storage, key-management, adversarial-adaptation, or production-hardening layers required for deployment.

---

## Licensing

Documentation and explanatory materials are governed by `LICENSE-DOCS.md`.

Python source files are governed by `LICENSE-CODE.md`.

Commercial use requires prior written authorization from the author.

---

## Author

Massimo Comitato  
Copyright © 2026.
