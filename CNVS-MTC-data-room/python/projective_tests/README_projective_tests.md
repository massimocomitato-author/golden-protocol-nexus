# Projective Tests

This folder contains the **statistical projection tests** and design-equation simulations of the CNVS MTC suite.

These tests evaluate the behavior predicted by the CNVS mathematical framework under explicit assumptions.

---

## Scope

Projective tests simulate reconstruction probabilities, entropy erosion, economic penalty surfaces, topological refresh behavior, and minimum critical fragmentation requirements.

They are not physical implementations of CNVS.

They are numerical stress tests used to evaluate whether the projected behavior of the CNVS equations remains coherent across adversarial scenarios.

---

## Included Tests

| Test | Description | Recommended File |
|---|---|---|
| Test 1 | Statistical Projection of Systemic Reconstruction under Dependent Collusion / Min-Entropy Variation | `test_01_statistical_projection_min_entropy.py` |
| Test 2 | Statistical Projection / Stress Test under Dynamic Erosion of Residual Min-Entropy | `test_02_dynamic_entropy_erosion.py` |
| Test 3 | Statistical Projection of Reconstruction Decay and Economic Penalty / Slashing Model | `test_03_slashing_expected_value.py` |
| Test 4 | Statistical Projection of Topological Refresh and Sybil Purge | `test_04_topological_refresh_sybil_purge.py` |
| Test 5 | Minimum Critical Fragmentation / `m_min` Design Formula under Asymmetric Topological Exposure | `test_05_mmin_design_formula.py` |

---

## Scientific Role

The projective tests evaluate the numerical behavior of CNVS variables such as:

- adversarial verifier fraction `q`;
- critical fragmentation cardinality `m`;
- residual min-entropy `h_min`;
- entropy erosion profiles;
- reconstruction probability;
- expected adversarial value;
- semantic feasibility bounds;
- minimum critical fragmentation `m_min`.

These tests support the report by showing numerical consistency between Monte Carlo sampling and the expected analytical behavior.

---

## Methodological Notice

The projective tests assume the validity of the CNVS mathematical framework being evaluated.

They do not independently prove the formal theory.

Their purpose is to stress-test the consequences of the assumptions and equations across large numerical parameter ranges.

---

## Reproducibility

Projective Monte Carlo tests may use deterministic seeds for reproducibility.

In this context, deterministic pseudo-randomness is intentional and supports scientific review.

Deterministic PRNGs used in projective tests must not be interpreted as cryptographic randomness sources for production CNVS implementations.

---

## Important Limitation

These tests are not production protocol code.

They are numerical and statistical projection engines designed for academic review, technical due diligence, and reproducibility.

---

## Licensing

Documentation and explanatory materials are governed by `LICENSE-DOCS.md`.

Python source files are governed by `LICENSE-CODE.md`.

Commercial use requires prior written authorization from the author.

---

## Author

Massimo Comitato  
Copyright © 2026.
