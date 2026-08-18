# CNVS Test 13: Engineering-Hardened 256-bit Fragmentation Sensitivity

**Author:** Massimo Comitato  
**License:** PolyForm Noncommercial 1.0.0

## Overview

`test_13_engineering_hardened_256bit_fragmentation.py` is a protocol-engineering test designed to evaluate the critical fragmentation sensitivity of the Closed Native Verification Systems (CNVS) architecture under production-oriented cryptographic constraints. 

Unlike the projective academic suite, which relies on standard 64-bit floating-point math and deterministic pseudo-random number generators, Test 13 implements a rigorous Cryptographically Secure Pseudo-Random Number Generator (CSPRNG) Monte Carlo environment utilizing arbitrary-precision Python integers and a 256-bit prime finite field (secp256k1 field prime).

The primary question evaluated by this execution is: *How does the probability of an adversary successfully reconstructing every hidden critical fragment scale as the critical fragmentation cardinality (m) increases?*

---

## Engineering-Hardening Properties

This test intentionally strips away typical simulation conveniences in favor of strict execution primitives:

- **256-bit Prime Field:** All state evaluations occur modulo $p = 2^{256} - 2^{32} - 977$.
- **CSPRNG Execution:** All assignments and inferences are drawn using OS-level entropy (`secrets.SystemRandom`). There are no deterministic simulation seeds.
- **Exact Sufficient-Statistic Sampling:** To bypass the prohibitive cost of generating millions of 2500-element cryptographic permutations, the engine models injective assignment without replacement by calculating exact large-integer combinatorial weights and applying a secure hypergeometric sampler.
- **Logarithmically Stable References:** Analytical upper bounds are calculated entirely in log-space to prevent numerical underflow when tracking infinitesimally small reconstruction probabilities.

---

## Experimental Design and Measured Event

Throughout the sensitivity sweep, the verifier pool ($Q = 2500$) and the terminal fragment universe ($k = 2048$) remain fixed. Only the critical subset ($m$) is scaled. 

**The Strictest Distinction:**
The measured event in Test 13 is *complete authentic reconstruction*. It evaluates whether the adversary can securely capture or correctly infer every critical piece of data, after which the *authentic* reconstructed state is submitted and accepted by $V_G$. 

This is **not** a false-state acceptance rate. A separate full-state mutation control verifies that if an adversary reconstructs the state and subsequently alters a value, the hidden affine invariant binding automatically vetoes the corrupted payload.

### The Stochastic Model
Given a coalition size $r$, the number of critical fragments directly captured ($X$) follows:

    X ~ Hypergeometric(Q, r, m)

For the remaining missing fragments, the exact cryptographic binomial inference follows:

    I | X ~ Binomial(m - X, 2^(-h_min))

The systemic reconstruction is flagged as successful exactly when $X + I = m$.

---

## Structural Execution Audits

Statistical projection alone is insufficient for protocol engineering. At every $(r, m)$ coordinate, a configurable subset of trajectories is structurally materialized as 256-bit candidate arrays and routed through the concrete CNVS validation pipeline:

    V_L -> Cons_R -> Inv_C -> V_G

The test engine asserts a hard failure if the literal finite-field execution of $V_G$ disagrees with the mathematically sampled reconstruction event, guaranteeing that the mathematical model and the executable code are perfectly aligned.

### C_int Disclosure Boundary Control
The pedagogical affine tags used in this implementation are reversible. The test implements an explicit boundary control: if the hidden parameters ($C_{int}$) are fully disclosed, the adversary can legitimately reconstruct the authentic critical values. However, the test proves that full disclosure does not authorize arbitrary forgery—any subsequent post-disclosure mutation of the candidate state still triggers a deterministic $V_G$ veto.

---

## Execution Instructions

The test is fully self-contained. It requires Python 3.10+ and the `numpy` and `matplotlib` libraries.

**Standard Execution (Default 100,000 iterations per point):**

    python test_13_engineering_hardened_256bit_fragmentation.py

*Note: Because this test relies entirely on OS-level cryptographic randomness and arbitrary-precision integer sampling, it is highly computationally intensive. 100,000 trajectories per point will require substantial execution time.*

**Rapid/Interactive Execution:**
To run the test with a smaller iteration budget for faster review or debugging, explicitly pass the iteration flag:

    python test_13_engineering_hardened_256bit_fragmentation.py --iterations 1000

## Outputs

Execution artifacts are routed to dynamically generated folders (`test_13_outputs` and `test_13_figures`). The suite generates:
- `test_13_results_[run_id].csv`: Raw Monte Carlo frequency data, Wilson 95% confidence intervals, and analytical references.
- `test_13_metadata_[run_id].json`: The cryptographic metadata logging the 256-bit field constraints and execution times.
- Four distinct high-resolution plots illustrating the decay of the reconstruction probability, the Monte Carlo scatter against theoretical limits, a Local-Pass/Global-Veto heatmap, and the maximum fragmentation limit ($m=1024$).