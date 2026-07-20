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

## The non-uniform distribution of the weight of invariant constraints


In the CNVS architecture, the existence of a non-uniform distribution of invariant constraints along the graph up to the terminal leaves produces an obfuscation mechanism that hinders inference through observation of network traffic. The engineering translation of this fundamental theoretical feature occurs in implementation tests through the introduction of the k-factor and TOPOLOGY_MULTIPLIER.

In other words, the system does not distribute algebraic criticality uniformly across all fragments. Instead, the algebraic weight of C_int is concentrated asymmetrically within a restricted critical subset of cardinality $m$, while the remaining fragments populate the broader topology as structurally valid but algebraically non-critical elements.

Thus, the network contains:

m       critical fragments carrying invariant relevance
k - m   non-critical structural fragments acting as topological camouflage

All fragments remain locally admissible and generate comparable local verification workloads. From the perspective of a peripheral verifier or a packet-sniffing adversary, a critical fragment and a non-critical structural fragment are not distinguishable through local observation alone.

This creates topological camouflage: the adversary cannot determine which fragments are load-bearing for C_int and which fragments are merely structural noise within the validation topology.

As a consequence, traffic analysis does not directly reveal the critical subset. The adversary is forced into a combinatorial uncertainty space, where successful reconstruction requires identifying or inferring the hidden critical subset and satisfying the corresponding invariant constraints.

## 2. Extension of the Shattered Object Metaphor

This mechanism extends the shattered-object metaphor introduced in the architectural notice.

In that metaphor, the original semantic mother-data is represented as an intact drinking glass, which CNVS shatters into microscopic, geometrically non-uniform fragments. The critical fragments $m$ correspond to those pieces that are necessary to reconstruct the semantic object.

The topological multiplier adds a further layer of epistemic isolation.

Instead of shattering only the target drinking glass, the system simultaneously shatters additional unrelated objects, such as:

a glass ashtray;
a beer bottle;
a picture frame;
other structurally similar but semantically unrelated objects.

All resulting shards are then mixed into the same distributed validation environment.

A compromised peripheral verifier may intercept a fragment and correctly measure its local properties, such as:

angle;
thickness;
curvature;
local edge compatibility;
admissible field value;
syntactic validity.

However, the verifier cannot determine whether that fragment is:

a critical load-bearing piece of the original drinking glass

or merely:

a non-critical shard of structural camouflage

The fragment may pass V_L because it is locally well-formed. It may even appear compatible with nearby fragments under limited local observation. Yet the verifier still lacks the hidden relational topology R_int, the partial sub-invariant map c_i, and the global invariant binding C_int required to identify its semantic role.

This is the engineering meaning of non-uniform criticality.

The system does not merely hide values. It hides the structural relevance of values.

## 3. Security Interpretation

The topological multiplier increases the adversary’s uncertainty in two distinct ways.

First, it increases the number of fragments that must be observed, classified, or controlled before reconstruction can be attempted.

Second, it prevents the adversary from knowing which fragments actually matter for the hidden invariant binding.

Therefore, even if the adversary compromises a large number of peripheral verifiers, the attack does not automatically translate into global state control. The adversary must still identify the critical subset and satisfy the hidden invariant constraints.

In CNVS terms:

local visibility ≠ criticality knowledge

and:

fragment possession ≠ global reconstructability

This is why the protocol-engineering tests separate k from m.

The parameter m measures the critical fragmentation cardinality.

The parameter k measures the broader distributed fragment universe.

The difference k - m represents the topological camouflage layer that surrounds the critical subset.

## 4. Engineering Meaning inside Test 13

In Test 13, this behavior is represented by:

k = max(MIN_TERMINAL_FRAGMENTS, TOPOLOGY_MULTIPLIER * m)

This ensures that increasing m does not merely increase the number of critical fragments. It also expands the surrounding fragment universe.

The result is a more realistic engineering model in which the adversary does not observe a clean set of only critical fragments. Instead, the adversary operates inside a larger mixed topology containing both critical and non-critical fragments.

This better approximates the intended CNVS architecture, where the hidden invariant structure is distributed non-uniformly and cannot be reconstructed from local fragment inspection alone.

## 5. Final Interpretation

The topological multiplier should therefore be interpreted as an engineering approximation of CNVS topological camouflage.

It supports the following CNVS principle:

The adversary may observe fragments,
but cannot locally infer which fragments carry global invariant relevance.

or, more compactly:

CNVS does not only hide the value of the fragment.
It hides the role of the fragment inside the global structure.

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
├── test_13_engineering_hardened_256bit_fragmentation.py
├── outputs/
│   ├── logs/
│   └── raw_results/
└── outcome_tests/
    └── test_13/
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
