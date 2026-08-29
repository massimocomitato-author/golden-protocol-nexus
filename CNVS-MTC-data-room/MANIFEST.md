# MANIFEST.md

# CNVS MTC Data Room Manifest

Author: **Massimo Comitato** Date: **2026-07-08** Repository: **cnvs-mtc-data-room** Project: **Closed Native Verification Systems — Monte Carlo Test Suite**

---

## Current Main Artifacts

```text
Report_Monte_Carlo_ENG.pdf
```

Description:

```text
MTC Technical Report: Stochastic and Empirical Evaluation of the CNVS Framework.
```

SHA-256:

```text
f39f29ef36b744aba43e619ab826496402d6e480ef2e6b15e8d1c045ce14957f
```

Size:

```text
1627197 bytes
```

Status:

```text
CURRENT
```

---

```text
ing_mtc_report_eng_v3.pdf
```

Description:

```text
CNVS Framework: Engineering-Hardened Execution Report (Tests 13-15)
```

SHA-256:

```text
a0774f61f37f75a787704d0297f1bcdfa85611948252e58c8d7ab9d11fb6d91f
```

Size:

```text
5390336 bytes
```

Status:

```text
CURRENT
```

---

## Repository Root Files

| File | Purpose | Status |
|---|---|---|
| `README.md` | Repository overview and structure | Current |
| `LICENSE-DOCS.md` | Documentation/report license notice | Current |
| `LICENSE-CODE.md` | Code/software license notice | Current |
| `AI_USE_STATEMENT.md` | AI assistance disclosure | Current |
| `CHANGELOG.md` | Version history | Current |
| `MANIFEST.md` | Artifact inventory and provenance index | Current |
| `ENGINEERING_LIMITATIONS.md` | Model Limitations | Current |
| `CITATION.cff` | Citation metadata | Current |

---

## Current Reports

| File | Folder | Status | Notes |
|---|---|---|---|
| `Report_Monte_Carlo_ENG.pdf` | `reports/` | Current | Final MTC Technical Report (Tests 1-12) |
| `ing_mtc_report_eng_v3.pdf` | `reports/` | Current | Engineering-Hardened Execution Report (Tests 13-15) |

---

## Current Python Test Files

| Test | Filename | Folder | Status |
|---|---|---|---|
| Test 1 | `test_01_statistical_projection_min_entropy.py` | `python/projective_tests/` | Current |
| Test 2 | `test_02_dynamic_entropy_erosion.py` | `python/projective_tests/` | Current |
| Test 3 | `test_03_slashing_expected_value.py` | `python/projective_tests/` | Current |
| Test 4 | `test_04_topological_refresh_sybil_purge.py` | `python/projective_tests/` | Current |
| Test 5 | `test_05_mmin_design_formula.py` | `python/projective_tests/` | Current |
| Test 9 | `test_09_structural_poc.py` | `python/empirical_tests/` | Current |
| Test 10 | `test_10_full_structural_semantic_model.py` | `python/empirical_tests/` | Current |
| Test 11 | `test_11_fragmentation_sensitivity.py` | `python/empirical_tests/` | Current |
| Test 12 | `test_12_entropy_calibrated_topology_invariant_leakage.py` | `python/empirical_tests/` | Current |
| Test 13 | `test_13_engineering_hardened_256bit_fragmentation` | `python/protocol_engineering_tests/` | Current |
| Test 14 | `test_14_semantic_end_to_end_cnvs_full_pipeline.py` | `python/protocol_engineering_tests/` | Current |
| Test 15 | `test_15_cnvs_m_sensitivity_full_pipeline.py` | `python/protocol_engineering_tests/` | Current |

---

## Current HTML / JavaScript Dashboards

| Test | Filename | Folder | Status |
|---|---|---|---|
| Test 6 | `test_06_expected_value_dashboard.html` | `html-js/interactive_tests/` | Current |
| Test 7 | `test_07_reconstruction_decay_dashboard.html` | `html-js/interactive_tests/` | Current |
| Test 8 | `test_08_dynamic_entropy_erosion_dashboard.html` | `html-js/interactive_tests/` | Current |

---

## Figures

Outcomes and figures are structurally mapped inside their respective test domains:

```text
python/empirical_tests/figures/
python/projective_tests/figures/
python/protocol_engineering_tests/test_13_figures/
python/protocol_engineering_tests/test_14_full_pipeline_outputs/figures/
python/protocol_engineering_tests/test_15_m_sensitivity_outputs/figures/
```

Output formats:

```text
.png
.pdf
.svg
```

---

## Outputs

Raw logs, metadata, CSV summaries and JSON results are stored under:

```text
python/empirical_tests/log/
python/empirical_tests/test_12_entropy_outputs/
python/projective_tests/log/
python/protocol_engineering_tests/test_13_outputs/
python/protocol_engineering_tests/test_14_full_pipeline_outputs/
python/protocol_engineering_tests/test_15_m_sensitivity_outputs/
```

File types:

```text
.txt
.csv
.json
```

---

## Provenance

Provenance files are stored under:

```text
provenance/
```

Contents:

| File | Purpose |
|---|---|
| `timestamp_manifest.md` | List of timestamped files |
| `hashes_sha256.txt` | SHA-256 hashes of current artifacts |
| `opentimestamps/` | OpenTimestamps proof files |

---

## Archive Policy

Deprecated, obsolete, exploratory, or superseded materials are archived in the dedicated repository directories:

```text
archive/deprecated_tests/
archive/old_reports/
```

```text
These files are preserved only for historical and provenance purposes.
They are obsolete exploratory versions and are not part of the current MTC suite.
```

---

## Licensing Summary

Documentation and reports:

```text
CC BY-NC 4.0
See: LICENSE-DOCS.md
```

Code and executable tests:

```text
PolyForm Noncommercial License 1.0.0
See: LICENSE-CODE.md
```

Commercial use requires prior written authorization from the author.

---

Command:

```bash
sha256sum reports/Report_Monte_Carlo_ENG.pdf
sha256sum reports/ing_mtc_report_eng_v3.pdf
```

For Windows PowerShell:

```powershell
Get-FileHash .\reports\Report_Monte_Carlo_ENG.pdf -Algorithm SHA256
Get-FileHash .\reports\ing_mtc_report_eng_v3.pdf -Algorithm SHA256
```

---

## Author

Massimo Comitato  
Copyright © 2026.
