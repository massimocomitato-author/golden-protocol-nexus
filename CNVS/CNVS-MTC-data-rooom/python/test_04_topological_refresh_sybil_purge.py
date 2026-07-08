# ==============================================================================
# CNVS FRAMEWORK - EXECUTION ENVIRONMENT
# Copyright (c) 2026 Massimo Comitato.
#
# This file is part of the CNVS MTC Data Room.
# Licensed under the PolyForm Noncommercial License 1.0.0.
#
# Commercial use is prohibited without prior written authorization.
# Academic review and technical due diligence use are permitted under the license.
#
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ==============================================================================
# CNVS THEOREM 4 STATISTICAL PROJECTION:
# TOPOLOGICAL REFRESH, FAULT-INJECTION, AND SYBIL EPURATION
#
#  Test Name: Test 4: Statistical Projection of Topological Refresh and Sybil Purge (Iterative Fault-Injection Model).
#  
#
# PURPOSE:
# This script projects the behavior of metadata accumulation over time under 
# repeated fault-injection attacks. It contrasts a static topology against the 
# CNVS ephemeral topology, ASSUMING the formal validity of the evaluation 
# windows and topological refresh mechanisms.
#
# It does NOT construct the full formal architecture (𝓢, 𝔇, V_L, Cons_R, Inv_C).
#
# FORMAL ASSUMPTIONS:
#   1. Static Topology Baseline: Metadata accumulates continuously without reset.
#   2. CNVS Bounded Evaluation (t_eval): The Global Verification function V_G 
#      resolves candidate transitions within a polynomially bounded window.
#   3. Topological Refresh: A rejected transition (V_G = 0) triggers an immediate 
#      reset of intra-cycle observable metadata.
#   4. Sybil Epuration: Authenticated malicious identities utilized in a failed 
#      transition are identified and excluded, reducing the adversary's future 
#      metadata accumulation capacity.
#   5. Bounded Leakage Proxy (gamma_top_limit): Used as a normalized operational 
#      threshold, not as the strict mutual-information quantity I(X_S; M_S).
# ==============================================================================

def simulate_fault_injection_refresh(
    max_ticks=600,
    t_eval=100,
    gamma_top_limit=50.0,
    initial_sybils=1200,
    expulsion_rate=250,
    base_accumulation_rate=0.35
):
    """
    Simulates metadata accumulation and Sybil identity population over discrete 
    time ticks, comparing static networks versus CNVS ephemeral topologies.
    """
    if max_ticks <= 0 or t_eval <= 0 or gamma_top_limit <= 0:
        raise ValueError("Time and threshold parameters must be positive.")
    if initial_sybils < 0 or expulsion_rate < 0 or base_accumulation_rate < 0:
        raise ValueError("Population and rate parameters must be non-negative.")

    t_axis = np.arange(1, max_ticks + 1)

    static_metadata = np.zeros(max_ticks)
    cnvs_metadata = np.zeros(max_ticks)
    sybil_population = np.zeros(max_ticks)
    burned_identities = np.zeros(max_ticks)

    current_static_metadata = 0.0
    current_cnvs_metadata = 0.0
    current_sybils = initial_sybils

    veto_ticks = []
    cnvs_cycle_peaks = []

    for i, t in enumerate(t_axis):

        # 1. Static topology baseline
        static_rate = base_accumulation_rate
        current_static_metadata += static_rate
        static_metadata[i] = current_static_metadata

        # 2. CNVS ephemeral topology (accumulation scales with active Sybils)
        if current_sybils > 0:
            cnvs_rate = base_accumulation_rate * (current_sybils / initial_sybils)
            current_cnvs_metadata += cnvs_rate
        else:
            cnvs_rate = 0.0
            current_cnvs_metadata = 0.0

        cnvs_metadata[i] = current_cnvs_metadata

        # 3. Global verification boundary (t_eval)
        # Rejection triggers metadata reset and identity epuration.
        if (t % t_eval == 0) and (current_sybils > 0):
            veto_ticks.append(t)
            cnvs_cycle_peaks.append(current_cnvs_metadata)

            # Topological Refresh
            current_cnvs_metadata = 0.0

            # Sybil Epuration
            current_sybils = max(0, current_sybils - expulsion_rate)

        sybil_population[i] = current_sybils
        burned_identities[i] = initial_sybils - current_sybils

    return {
        "t_axis": t_axis,
        "static_metadata": static_metadata,
        "cnvs_metadata": cnvs_metadata,
        "sybil_population": sybil_population,
        "burned_identities": burned_identities,
        "gamma_top_limit": gamma_top_limit,
        "veto_ticks": np.array(veto_ticks),
        "cnvs_cycle_peaks": np.array(cnvs_cycle_peaks),
        "initial_sybils": initial_sybils,
        "t_eval": t_eval
    }

# ==============================================================================
# EXECUTION & VALIDATION
# ==============================================================================

result = simulate_fault_injection_refresh(
    max_ticks=600,
    t_eval=100,
    gamma_top_limit=50.0,
    initial_sybils=1200,
    expulsion_rate=250,
    base_accumulation_rate=0.35
)

t = result["t_axis"]
static_metadata = result["static_metadata"]
cnvs_metadata = result["cnvs_metadata"]
sybils = result["sybil_population"]
burned = result["burned_identities"]
threshold = result["gamma_top_limit"]
veto_ticks = result["veto_ticks"]
cnvs_cycle_peaks = result["cnvs_cycle_peaks"]
initial_sybils = result["initial_sybils"]
t_eval = result["t_eval"]

print("CNVS Statistical Projection: Temporal Refresh and Epuration Model")
print(f"Evaluation window proxy t_eval: {t_eval} ticks")
print(f"Operational leakage threshold gamma_top_limit: {threshold}")
print(f"Static topology final metadata: {static_metadata[-1]:.2f}")
print(f"CNVS maximum intra-cycle metadata: {np.max(cnvs_metadata):.2f}")
print(f"Final active Sybil identities: {int(sybils[-1])}")
print(f"Final excluded identities: {int(burned[-1])}")

if np.max(cnvs_metadata) <= threshold:
    print("Result: CNVS intra-cycle metadata remains strictly below the leakage threshold.")
else:
    print("Warning: CNVS intra-cycle metadata exceeds the leakage threshold under these parameters.")

# ==============================================================================
# PLOTTING
# ==============================================================================

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# ------------------------------------------------------------------------------
# Plot 1: Metadata accumulation and topological refresh
# ------------------------------------------------------------------------------
ax1.plot(
    t, static_metadata,
    linewidth=3,
    label="Static topology: continuous metadata accumulation"
)

ax1.plot(
    t, cnvs_metadata,
    linewidth=2.6, drawstyle="steps-post",
    label="CNVS ephemeral topology: reset after V_G rejection"
)

ax1.fill_between(t, 0, cnvs_metadata, alpha=0.14)

ax1.axhline(
    y=threshold, linestyle="--", linewidth=2.2,
    label=r"Operational leakage threshold proxy ($\gamma_{top}$)"
)

# Mark global verification boundaries
for tick in veto_ticks:
    ax1.axvline(x=tick, linestyle=":", linewidth=0.9, alpha=0.45)

if len(veto_ticks) > 0:
    ax1.scatter(
        veto_ticks, cnvs_cycle_peaks,
        s=36, zorder=5,
        label=r"$V_G(S')=0$ refresh events"
    )

ax1.set_title(
    "1. Topological Refresh Against Iterative Fault-Injection",
    fontsize=14, fontweight="bold"
)
ax1.set_ylabel(r"Observable topological metadata proxy $M_S(t)$", fontsize=12)
ax1.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
ax1.legend(loc="upper left", fontsize=10, frameon=True)

# ------------------------------------------------------------------------------
# Plot 2: Sybil epuration
# ------------------------------------------------------------------------------
ax2.plot(
    t, sybils,
    linewidth=3,
    label="Active Sybil identities"
)

ax2.fill_between(
    t, sybils, initial_sybils,
    alpha=0.16,
    label="Excluded authenticated identities"
)

for tick in veto_ticks:
    ax2.axvline(x=tick, linestyle=":", linewidth=0.9, alpha=0.45)

ax2.set_title(
    "2. Progressive Sybil Epuration and Reduced Accumulation Capacity",
    fontsize=14, fontweight="bold"
)
ax2.set_xlabel(
    r"Discrete time ticks within polynomially bounded $V_G$ evaluation windows",
    fontsize=12
)
ax2.set_ylabel("Number of adversarial identities", fontsize=12)
ax2.set_ylim(0, initial_sybils * 1.08)
ax2.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
ax2.legend(loc="lower left", fontsize=10, frameon=True)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

fig.suptitle(
    "CNVS Statistical Projection: Topological Refresh and Sybil Epuration",
    fontsize=15, fontweight="bold"
)

plt.tight_layout()
plt.show()
