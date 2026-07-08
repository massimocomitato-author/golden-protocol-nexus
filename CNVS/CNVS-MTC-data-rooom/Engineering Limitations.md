## Engineering Limitations

The code in this repository is intended as a reproducible academic simulation and executable proof-of-concept environment for the CNVS MTC suite.

It is not a production-grade cryptographic implementation.

The finite-field modulus used in the executable tests is intentionally small and selected for computational tractability and reproducible Monte Carlo execution. Production-grade deployments require arbitrary-precision arithmetic or dedicated cryptographic finite-field libraries.

The random generators used in the simulations, including seeded NumPy PRNGs, are used for reproducibility and statistical testing. They must not be interpreted as cryptographically secure randomness sources. Production implementations require CSPRNG-based randomness, such as Python's `secrets` module, operating-system entropy, or audited cryptographic libraries (with the exception of the tests in the /.../protocol_engineering_tests/ directory).

The adversarial models implemented in the MTC suite evaluate fixed peripheral compromise fractions and injective assignment behavior. Adaptive Sybil relocation, dynamic adversarial topology, production-grade key management, side-channel resistance, secure storage of C_int, and enterprise deployment hardening are outside the scope of this repository.

Accordingly, the MTC suite should be read as numerical, projective, interactive, and executable support under explicit CNVS assumptions, not as a production security engine.