# MANIFEST.md

# CNVS MTC Data Room Manifest

Author: **Massimo Comitato**  
Date: **2026-07-08**  
Repository: **cnvs-mtc-data-room**  
Project: **Closed Native Verification Systems — Monte Carlo Test Suite**

---

## Current Main Artifact

```text
reports/Report_Monte_Carlo_ENG.pdf
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

## Repository Root Files

| File | Purpose | Status |
|---|---|---|
| `README.md` | Repository overview and structure | Current |
| `LICENSE-DOCS.md` | Documentation/report license notice | Current |
| `LICENSE-CODE.md` | Code/software license notice | Current |
| `AI_USE_STATEMENT.md` | AI assistance disclosure | Current |
| `CHANGELOG.md` | Version history | Current |
| `MANIFEST.md` | Artifact inventory and provenance index | Current |
| `CITATION.cff` | Citation metadata | To be added |

---

## Current Report

| File | Folder | Status | Notes |
|---|---|---|---|
| `Report_Monte_Carlo_ENG.pdf` | `reports/` | Current | Final MTC Technical Report |

---

## Current Python Test Files

| Test | Recommended Filename | Status |
|---|---|---|
| Test 1 | `test_01_statistical_projection_min_entropy.py` | Current |
| Test 2 | `test_02_dynamic_entropy_erosion.py` | Current |
| Test 3 | `test_03_slashing_expected_value.py` | Current |
| Test 4 | `test_04_topological_refresh_sybil_purge.py` | Current |
| Test 5 | `test_05_mmin_design_formula.py` | Current |
| Test 9 | `test_09_structural_poc.py` | Current |
| Test 10 | `test_10_full_structural_semantic_model.py` | Current |
| Test 11 | `test_11_fragmentation_sensitivity.py` | Current |

---

## Current HTML / JavaScript Dashboards

| Test | Recommended Filename | Status |
|---|---|---|
| Test 6 | `test_06_expected_value_dashboard.html` | Current |
| Test 7 | `test_07_reconstruction_decay_dashboard.html` | Current |
| Test 8 | `test_08_dynamic_entropy_erosion_dashboard.html` | Current |

---

## Figures

Figures should be stored under:

```text
figures/test_01/
figures/test_02/
figures/test_03/
figures/test_04/
figures/test_05/
figures/test_10/
figures/test_11/
```

Recommended output formats:

```text
.png
.pdf
.svg
```

---

## Outputs

Raw logs and numerical outputs should be stored under:

```text
outputs/logs/
outputs/raw_results/
```

Recommended file types:

```text
.txt
.csv
.json
```

---

## Provenance

Provenance files should be stored under:

```text
provenance/
```

Recommended contents:

| File | Purpose |
|---|---|
| `timestamp_manifest.md` | List of timestamped files |
| `hashes_sha256.txt` | SHA-256 hashes of current artifacts |
| `opentimestamps/` | OpenTimestamps proof files |

---

## Archive Policy

Deprecated, obsolete, tautological, exploratory, or superseded materials should not remain in the repository root.

They should be moved to:

```text
archive/deprecated_tests/
archive/old_reports/
archive/exploratory_versions/
```

Each archive folder should contain a `README_ARCHIVE.md` stating:

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

## Integrity Notes

The SHA-256 hash above should be recomputed after every modification of the PDF or any source file.

Suggested command:

```bash
sha256sum reports/Report_Monte_Carlo_ENG.pdf
```

For Windows PowerShell:

```powershell
Get-FileHash .\reports\Report_Monte_Carlo_ENG.pdf -Algorithm SHA256
```

---

## Author

Massimo Comitato  
Copyright © 2026.
