# CNVS MTC Data Room

**CNVS MTC Data Room** contains the Monte Carlo Test Suite, executable evaluation environments, figures, reports, and provenance material for the **Closed Native Verification Systems (CNVS)** framework.

Author: **Massimo Comitato**  
Repository scope: **MTC Technical Report, Monte Carlo simulations, executable structural tests, interactive dashboards, figures, outputs, and provenance records.**

---

## Purpose

This repository documents the numerical, projective, interactive, and executable evaluation layer of the CNVS framework.

The MTC suite is designed to evaluate the operational behavior of CNVS under explicit formal assumptions, including:

- critical fragmentation cardinality `m`;
- adversarial verifier fraction `q`;
- residual min-entropy margin `h_min`;
- hidden invariant binding `C_int`;
- topological refresh;
- Global Veto;
- executable separation between local admissibility and global validity.

  The suite also includes a dedicated repository of engineerable prototypes (.../python/CNVS Engineering Hardening Tests/).

The tests do **not** replace the formal proof of the CNVS theory and do **not** establish unconditional security. They provide numerical, projective, and executable support under the stated CNVS assumptions.

---

## Repository Structure

```text
cnvs-mtc-data-room/
├── README.md
├── LICENSE-DOCS.md
├── LICENSE-CODE.md
├── CITATION.cff
├── CHANGELOG.md
├── AI_USE_STATEMENT.md
├── MANIFEST.md
├── ENGINEERING_LIMITATIONS.md
│
├── reports/
│   └── Report_Monte_Carlo_ENG.pdf
│
├── python/projective_tests/
│   ├── test_01_statistical_projection_min_entropy.py
│   ├── test_02_dynamic_entropy_erosion.py
│   ├── test_03_slashing_expected_value.py
│   ├── test_04_topological_refresh_sybil_purge.py
│   ├── test_05_mmin_design_formula.py
│
├── python/empirical_tests/
│   ├── test_09_structural_poc.py
│   ├── test_10_full_structural_semantic_model.py
│   └── test_11_fragmentation_sensitivity.py
│
├── python/protocol_engineering_tests/
│   ├── test_12_engineering_hardened_256bit_fragmentation.py
│   ├── test_13_engineering_hardened_256bit_full_strs.py
│
├── html-js/interactive_tests/
│   ├── test_06_expected_value_dashboard.html
│   ├── test_07_reconstruction_decay_dashboard.html
│   └── test_08_dynamic_entropy_erosion_dashboard.html
│
├── outcomes_tests/
│   ├── test_01/
│   ├── test_02/
│   ├── test_03/
│   ├── test_04/
│   ├── test_05/
│   ├── test_10/
│   ├── test_11/
│   ├── test_12/
│   └── test_13/
│
├── outputs/
│   ├── logs/
│   └── raw_results/
│
├── provenance/
│   ├── timestamp_manifest.md
│   ├── hashes_sha256.txt
│   └── opentimestamps/
│
└── archive/
    ├── deprecated_tests/
    ├── old_reports/
    └── exploratory_versions/
```

---

## Current Main Report

```text
reports/Report_Monte_Carlo_ENG.pdf
```

SHA-256 entry:

```text
SHA256: f39f29ef36b744aba43e619ab826496402d6e480ef2e6b15e8d1c045ce14957f
Size: 1627197 bytes
```

---

## Test Categories

1. **Statistical Projection Tests** — Monte Carlo engines that simulate network behavior assuming the formal validity of the CNVS equations.
2. **Interactive Statistical Projection Tests** — HTML/JS dashboards for real-time exploration of risk surfaces.
3. **Minimum Critical Fragmentation Test** — design-formula stress test for the minimum critical fragmentation threshold `m_min`.
4. **Executable Demonstrative Tests** — structural execution environments testing `V_L`, `Cons_R`, `Inv_C`, `V_G`, hidden invariant binding, topological refresh, and fragmentation sensitivity.

---

## Important Scientific Notice

The MTC suite is not a formal proof of CNVS.

It should be read as:

```text
numerical, projective, interactive, and executable support
under explicit CNVS assumptions.
```

In particular:

- the tests do not establish unconditional security;
- the tests assume preservation of `C_int` outside the adversarial view unless an explicit leak-control scenario is being tested;
- executable tests illustrate the separation between local admissibility and global validity;
- the Global Veto depends on hidden invariant binding, non-reducible global validation, and preservation of the ordinary CNVS threat model.

---

## Licensing

Documentation, reports, diagrams, and textual materials are licensed under the terms described in:

```text
LICENSE-DOCS.md
```

Source code, Python scripts, JavaScript dashboards, and executable environments are licensed under the terms described in:

```text
LICENSE-CODE.md
```

Commercial use is not authorized without prior written permission from the author.

---

## Citation

Please cite this repository and the MTC Technical Report as:

```text
Comitato, M. (2026). CNVS MTC Data Room: Monte Carlo Test Suite and Executable Evaluation Environment for Closed Native Verification Systems. Version 3.0.
```


---

## Author

**Massimo Comitato**  
Copyright © 2026, Massimo Comitato.
