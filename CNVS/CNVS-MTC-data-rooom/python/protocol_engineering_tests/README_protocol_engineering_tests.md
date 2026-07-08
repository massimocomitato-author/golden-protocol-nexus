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
| Test 12 | Engineering-Hardened 256-bit Fragmentation Sensitivity Test under Hidden Invariant Binding | `test_12_engineering_hardened_256bit_fragmentation.py` |

---

## Scientific and Engineering Role

The protocol engineering tests preserve the CNVS validation pipeline:

```text
V_L -> Cons_R -> Inv_C -> V_G
```

but replace proof-of-concept engineering assumptions with stronger execution primitives.

These tests are intended to verify that the separation between local admissibility and global validity remains executable under more realistic implementation constraints.

---

## Distinction from the Academic MTC Suite

The projective and empirical MTC tests are designed for academic reproducibility, mathematical stress testing, and technical due diligence.

The protocol engineering tests are different.

They are designed to evaluate implementation hardening.

For this reason, protocol engineering tests may use:

- non-reproducible cryptographic randomness;
- Python arbitrary-precision integers;
- 256-bit finite-field moduli;
- CSPRNG-based secret generation;
- randomized or adaptive adversarial sampling.

This makes them less convenient for deterministic academic reproduction, but more relevant for engineering review.

---

## Important Limitation

These tests are still not production CNVS node implementations.

They do not include:

- production networking;
- authenticated storage;
- secure key custody;
- hardware security modules;
- side-channel protection;
- complete `R_int` production topology;
- validator identity lifecycle;
- full adversarial adaptive strategy space;
- operational deployment hardening.

They should be read as engineering-hardening artifacts, not as enterprise-ready infrastructure.

---

## Output Structure

```text
protocol_engineering_tests/
├── README_protocol_engineering_tests.md
├── test_12_engineering_hardened_256bit_fragmentation.py
├── outputs/
│   ├── logs/
│   └── raw_results/
└── outcome_tests/
    └── test_12/
```

---

## Licensing

Documentation and explanatory materials are governed by `LICENSE-DOCS.md`.

Python source files are governed by `LICENSE-CODE.md`.

Commercial use requires prior written authorization from the author.

---

## Author

Massimo Comitato  
Copyright © 2026.
