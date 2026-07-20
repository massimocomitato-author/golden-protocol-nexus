# Protocol Engineering Tests

This folder contains the **engineering-hardening tests** for the CNVS protocol.

These tests are separate from the academic MTC suite.

Their purpose is to evaluate whether core CNVS execution patterns can be migrated from simplified academic simulations toward more production-oriented engineering constraints.

---

## Scope

Protocol engineering tests focus on implementation hardening, not on proving the mathematical CNVS theory.

They are designed to address engineering limitations identified during red-team-style review, including:

- replacement of fixed-width numerical arrays;
- avoidance of `np.int64` finite-field state;
- arbitrary-precision integer arithmetic;
- 256-bit prime finite-field execution;
- cryptographically secure randomness;
- removal of deterministic simulation seeds;
- CSPRNG-based generation of hidden invariant parameters;
- adaptive or randomized malicious verifier sampling;
- clearer distinction between reproducible academic simulators and production-oriented protocol tests.

---

## Included Tests

| Test | Description | Recommended File |
|---|---|---|
| Test 13 | Engineering-Hardened 256-bit Fragmentation Sensitivity Test under Hidden Invariant Binding | `test_13_engineering_hardened_256bit_fragmentation.py` |
| Test 14 | Full-Pipeline Semantic Execution and Progressive Invariant Validation | `test_14_semantic_end_to_end_cnvs_full_pipeline.py` |

---

## Scientific and Engineering Role

The protocol engineering tests preserve the CNVS validation pipeline:

```text
V_L -> Cons_R -> Inv_C -> V_G
