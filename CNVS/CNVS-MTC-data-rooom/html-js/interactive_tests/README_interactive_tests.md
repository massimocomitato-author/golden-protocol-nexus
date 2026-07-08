# Interactive Tests

This folder contains the **interactive statistical projection tests** of the CNVS MTC suite.

These tests are implemented as HTML/JavaScript dashboards and are intended to make the CNVS risk surfaces explorable in real time.

---

## Scope

The interactive tests allow the user to manipulate key CNVS parameters and observe their effect on projected reconstruction probability, expected adversarial value, entropy erosion, and Global Veto behavior.

They are not production CNVS implementations.

They are explanatory, projective, and exploratory tools designed to support technical review and conceptual understanding.

---

## Included Tests

| Test | Description | Recommended File |
|---|---|---|
| Test 6 | Interactive Projection of Expected Value and Economic Tolerance under Global Veto | `test_06_expected_value_dashboard.html` |
| Test 7 | Interactive Projection of Probabilistic Decay and Epistemic Isolation | `test_07_reconstruction_decay_dashboard.html` |
| Test 8 | Interactive Projection / Stress Test of Dynamic Min-Entropy Erosion | `test_08_dynamic_entropy_erosion_dashboard.html` |

---

## Scientific Role

These dashboards illustrate the behavior of the CNVS equations under adjustable parameters such as:

- adversarial verifier fraction `q`;
- critical fragmentation cardinality `m`;
- residual min-entropy `h_min`;
- maximum entropy baseline `h_max`;
- reward and penalty parameters;
- expected adversarial value;
- dynamic erosion profiles.

They are intended to make the mathematical projections visually inspectable.

---

## Methodological Notice

The interactive tests execute projected equations and parameter surfaces. They should not be read as independent empirical proof of CNVS security.

They support the MTC suite by providing a real-time exploratory interface for the same assumptions evaluated in the statistical projection tests.

---

## Important Limitation

The dashboards do not implement a full CNVS node, production cryptography, live adversarial networking, secure key management, or full hidden invariant binding.

They are interactive review instruments.

---

## Licensing

Documentation and explanatory materials are governed by `LICENSE-DOCS.md`.

HTML and JavaScript files are governed by `LICENSE-CODE.md`.

Commercial use requires prior written authorization from the author.

---

## Author

Massimo Comitato  
Copyright © 2026.
