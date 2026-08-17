## Engineering Limitations

The code in this repository is intended as a reproducible academic simulation, executable proof-of-concept environment, and protocol-engineering test suite for the CNVS MTC framework.

It is not a production-grade cryptographic implementation or a deployed distributed network.

The repository contains two distinct experimental layers.

### Tests 1–12: Projective and Numerical Validation

Tests 1–12 primarily provide numerical, projective, interactive, and Monte Carlo support for the CNVS theoretical model.

These tests may use computationally convenient finite fields, floating-point numerical structures, and seeded NumPy pseudo-random generators in order to ensure tractable execution and reproducibility.

Accordingly, the cryptographic parameters and random generators used in Tests 1–12 must not be interpreted as production-grade cryptographic primitives.

### Tests 13–15: Protocol-Engineering Layer

Tests 13–15 introduce a substantially more demanding engineering layer and should not be described by the same limitations as the earlier projective suite.

**Test 13** executes the fragmentation-sensitivity model in a 256-bit prime finite field corresponding to the secp256k1 field modulus:

    p = 2^256 - 2^32 - 977

It uses Python arbitrary-precision integers and operating-system-backed cryptographically secure randomness through the `secrets` module. The test therefore removes the small-field and predictable-PRNG assumptions used in earlier numerical experiments.

**Test 14** moves beyond abstract numerical states and instantiates the complete validation pipeline

    V_L -> Cons_R -> Inv_C -> V_G

over a large, heterogeneous, fully synthetic semantic environment ("Enzo's House"). The implementation includes terminal semantic fragments, relational topology, hidden invariant binding, progressive leakage experiments, relational attacks, semantic attacks, topology refresh, and literal object-graph audits in addition to high-volume vectorized Monte Carlo execution.

**Test 15** preserves the Test-14 semantic architecture while directly varying the critical-fragment cardinality

    m ∈ {32, 64, 128, 256, 512}

in order to evaluate its effect on adversarial reconstruction, Global Veto behavior, hidden-invariant leakage, latency, scalability, and throughput.

Tests 14 and 15 retain deterministic or seeded pseudo-random generation where reproducibility of Monte Carlo campaigns is required. These reproducible generators should not be confused with cryptographic randomness requirements in a production deployment. Security-sensitive generation mechanisms and reproducible statistical sampling serve different experimental purposes.

### Remaining Engineering Limitations

Despite the stronger engineering assumptions introduced in Tests 13–15, the CNVS MTC suite remains an in-silico research environment.

The current repository does not constitute a complete implementation of:

- production-grade key management;
- secure distributed storage of hidden invariant structures (`C_int`);
- hardware-backed secret protection;
- authenticated network transport;
- side-channel resistance;
- traffic-analysis resistance under a deployed adversarial network;
- production Sybil-defense infrastructure;
- real distributed liveness and timeout management;
- fault-tolerant multi-server reconstruction;
- audited cryptographic protocol integration;
- large-scale adversarial deployment on heterogeneous physical networks.

The latency and throughput measurements reported for Tests 14 and 15 describe the local computational pipeline on the stated execution hardware. They do not directly measure communication complexity, network latency, or end-to-end performance of a future distributed CNVS deployment.

Similarly, the adversarial experiments evaluate explicitly implemented attack classes and parameterized threat models. The absence of an observed bypass under those experiments must not be interpreted as a universal proof of security against arbitrary adversaries.

Accordingly, the repository should be interpreted as a progression from projective numerical validation (Tests 1–12) to increasingly realistic executable protocol-engineering experiments (Tests 13–15), while remaining a research and proof-of-concept environment rather than a production security engine.
