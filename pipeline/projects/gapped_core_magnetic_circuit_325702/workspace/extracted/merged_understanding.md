# Gapped Core Magnetic Circuit — Ramped Excitation

## Simulation

| setting | value |
| --- | --- |
| start time | 0.0 s |
| stop time | 1.0 s |
| output samples | 1000 |
| solver tolerance | 1e-06 |

**Domains:** `magnetic_circuit`

## Engineering brief

Canonical entities and aliases:
- Excitation coil: a coil with 500 turns [nominal].
- Core (iron path), alias iron core: magnetic core segment with mean path length 0.4 m, cross-section 4 cm^2 = 0.0004 m^2, and relative permeability 2000 [all nominal].
- Air gap: magnetic gap segment with length 2 mm = 0.002 m and cross-section 4 cm^2 = 0.0004 m^2 [nominal].
- Magnetic reference: one reference [nominal] with exactly one magnetic ground.
- magnetic ground.

Topology and relationships:
- The air gap is in series with the core (iron path).
- The excitation coil drives magnetic flux around the closed iron core.
- The core (iron path) carries the same flux in series with the air gap.
- Because the core and air gap are stated to have the same flux and the same cross-section, the requirement note explicitly states that the core flux density and air-gap flux density are the same.

Scenario and behaviour:
- The requirement specification defines a ramped excitation current for the excitation coil from 0 A at 0 s to 2 A at 0.1 s, then holding at 2 A thereafter. This is grounded by the coil entity values and by the behavioural requirement that every reported quantity shall rise with coil current during the 0–0.1 s ramp and then hold steady at its final value for the rest of the 1 s run.
- The simulation duration is 1 second.

Reported variables contract for later stages:
- mmf_At [A-turn]: coil magnetomotive force.
- Phi_core_Wb [Wb]: magnetic flux in the core.
- B_core_T [T]: magnetic flux density in the core.
- B_gap_T [T]: magnetic flux density in the air gap.
- Vm_core_At [A-turn]: magnetic potential drop across the iron core.
- Vm_gap_At [A-turn]: magnetic potential drop across the air gap.
These names are taken directly from the approved acceptance criteria and satisfy the reporting requirement to report these quantities for the whole run, not only at the end.

Physical relationships explicitly stated in the notes:
- mmf_At = N * I, with approved reference value at full current given as 500 * 2 = 1000 A-turn. This is explicit from the requirement note under Physical relationships and AC-02.
- B_core_T and B_gap_T are equal because the same flux passes through core and air gap in series and both are stated to have the same cross-section.
- The approved acceptance criterion AC-08 requires the magnetic potential drops across the core and air gap to sum to the applied mmf at t = 1.0 s, expressed as abs((mmf_At - Vm_core_At - Vm_gap_At) / mmf_At) <= 0.005.

Derived consistency from approved end values:
- Derived: Phi_core_Wb = B_core_T * A = 0.571199 T * 0.0004 m^2 = 0.0002284796 Wb, numerically consistent with the approved value 0.00022848 Wb in AC-03.
- Derived: Vm_core_At + Vm_gap_At = 90.9091 + 909.091 = 1000.0001 A-turn, consistent with AC-08 and AC-02 within the stated tolerance and rounding.

There are no other equations, nonlinear magnetic properties, inductance values, or dynamic electrical circuit elements stated in the notes. The note establishes a magnetic-circuit requirement case with a prescribed current ramp and required reported magnetic quantities over time.

## Acceptance checks (9)

| # | when | expression | expected | tolerance | source |
| --- | --- | --- | --- | --- | --- |
| 1 | at 0 s | `mmf_At <= 1e-06` | 1 | 0 | 01_gapped_core.txt <AC-00> |
| 2 | ever | `mmf_At >= 999.0` | 1 | 0 | 01_gapped_core.txt <AC-01> |
| 3 | at 1 s | `mmf_At` | 1000 | 1 | 01_gapped_core.txt <AC-02> |
| 4 | at 1 s | `Phi_core_Wb` | 0.00022848 | 2.2848e-06 | 01_gapped_core.txt <AC-03> |
| 5 | at 1 s | `B_core_T` | 0.571199 | 0.00571199 | 01_gapped_core.txt <AC-04> |
| 6 | at 1 s | `B_gap_T` | 0.571199 | 0.00571199 | 01_gapped_core.txt <AC-05> |
| 7 | at 1 s | `Vm_core_At` | 90.9091 | 0.909091 | 01_gapped_core.txt <AC-06> |
| 8 | at 1 s | `Vm_gap_At` | 909.091 | 9.09091 | 01_gapped_core.txt <AC-07> |
| 9 | at 1 s | `abs((mmf_At - Vm_core_At - Vm_gap_At) / mmf_At) <= 0.005` | 1 | 0 | 01_gapped_core.txt <AC-08> |

## Assumptions (3)

- The excitation current schedule is treated as a prescribed model input: linear ramp from 0 A at 0 s to 2 A at 0.1 s, then constant at 2 A through 1 s. This is needed to make the requirement case executable because the note gives endpoint values and a behavioural description but no separate input table.
- 1000 output intervals are chosen because the note specifies the 1 s duration but does not specify sample count or output interval.
- No additional monotonicity checks were added for 'rise during the 0–0.1 s ramp and then hold steady' because the note does not provide a mechanically evaluable tolerance or discrete sampled criterion for monotonic rise/hold over the whole trajectory beyond the stated endpoint and attainment checks.
