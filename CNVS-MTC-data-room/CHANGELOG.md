# CHANGELOG.md

All notable changes to the CNVS MTC Data Room are documented in this file.

---

## [1.0.0] - 2026-07-08

### Added

- Initial public structure of the CNVS MTC Data Room.
- MTC Technical Report: `Report_Monte_Carlo_ENG.pdf`.
- Repository documentation files:
  - `README.md`
  - `LICENSE-DOCS.md`
  - `LICENSE-CODE.md`
  - `AI_USE_STATEMENT.md`
  - `CHANGELOG.md`
  - `MANIFEST.md`
  - `ENGINEERING_LIMITATIONS.md`
- repository folders:
  - `reports/`
  - `python/`
  - `python/projective_tests/`
  - `python/empirical_tests/`
  - `python/protocol_engineering_tests/`
  - `html-js/`
  - `html-js/interactive_tests`
  - `figures/`
  - `outputs/`
  - `provenance/`
  - `archive/`
- Also enabled license separation between documentation and code (two different legal protection Licenses).
- AI use disclosure.
- Provenance and timestamping structure.

### Report Content

- Statistical Projection Tests.
- Interactive Statistical Projection Tests.
- Minimum Critical Fragmentation / `m_min` provisioning test.
- Executable structural tests.
- Test 10: full structural-semantic model with ordinary vs. `C_int` leak control.
- Test 11: executable fragmentation sensitivity under hidden invariant binding.
- Final conclusions and author responsibility statement.

### Scientific Framing

- Clarified that the MTC suite does not replace formal CNVS proof.
- Clarified that the tests do not establish unconditional security.
- Clarified the ordinary CNVS threat model:
  - `C_pub` may be known;
  - `C_int`, hidden binding, and internal relational parameters remain outside the adversarial view.
- Clarified the role of Global Veto and non-reducible global validation.

### Provenance

- Added manifest placeholders for SHA-256 hashes, OpenTimestamps records, and archived deprecated materials.

---

## [0.x] - Historical / Deprecated

Previous exploratory builds, obsolete Monte Carlo tests, preliminary drafts, and completed reports are stored in the section:

```text
archive/
```

These materials are preserved only for historical and provenance purposes and are not part of the current MTC suite.
