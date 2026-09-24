# Gapped Core Magnetic Circuit — Ramped Excitation

## System

A 500-turn excitation coil drives magnetic flux around a closed iron core
interrupted by a single air gap in series with the iron. The coil current
starts at 0 A and ramps linearly up to 2 A over the first 0.1 s of the run,
then holds steady at 2 A for the remainder of the run. There is no operator
command and no switching -- the excitation is a simple, one-shot startup
ramp followed by a hold.

- Excitation coil: N = 500 turns. Current I(t): 0 A at t = 0 s, ramping
  linearly to 2 A by t = 0.1 s, then held constant at 2 A from t = 0.1 s to
  the end of the run.
- Core (iron path): mean path length 0.4 m, cross-section 4 cm^2 (0.0004 m^2),
  relative permeability 2000.
- Air gap: length 2 mm (0.002 m), same cross-section as the core (4 cm^2,
  0.0004 m^2), in series with the core, no fringing.
- Magnetic reference: the circuit has exactly one magnetic ground.

## Requirements

- REQ-SIM-001: Simulate for 1 second and report the coil mmf, the core flux,
  the core flux density, the air-gap flux density, the magnetic potential
  drop across the iron core, and the magnetic potential drop across the air
  gap for the whole run, not only at the end.
- REQ-FUN-001: Starting from zero, every reported quantity shall rise with
  the coil current during the 0-0.1 s ramp and then hold steady at its final
  value for the rest of the run.

## Acceptance checks

- AC-00 zero before the ramp: `mmf_At <= 1e-06` at t = 0.0 s.
- AC-01 full mmf reached: `mmf_At >= 999.0` becomes true at some point during
  the run (ever value == 1.0) -- the ramp must actually reach full current.
- AC-02 final mmf: `mmf_At == 1000.0` A-turn at t = 1.0 s (N * I = 500 * 2,
  absolute tolerance 1.0 A-turn).
- AC-03 final core flux: `Phi_core_Wb == 0.00022848` Wb at t = 1.0 s
  (absolute tolerance 1% of expected).
- AC-04 final core flux density: `B_core_T == 0.571199` T at t = 1.0 s
  (absolute tolerance 1% of expected).
- AC-05 final air-gap flux density: `B_gap_T == 0.571199` T at t = 1.0 s
  (absolute tolerance 1% of expected) -- same flux, same cross-section as
  the core, so the same flux density.
- AC-06 final core magnetic potential drop: `Vm_core_At == 90.9091` A-turn
  at t = 1.0 s (absolute tolerance 1% of expected).
- AC-07 final air-gap magnetic potential drop: `Vm_gap_At == 909.091`
  A-turn at t = 1.0 s (absolute tolerance 1% of expected).
- AC-08 mmf balance: `abs((mmf_At - Vm_core_At - Vm_gap_At) / mmf_At) <= 0.005`
  at t = 1.0 s (the core drop plus the gap drop must equal the applied mmf).

## Notes

- This is a linear, quasi-static circuit: no saturation, no hysteresis, no
  eddy currents, no frequency-dependent effects, and no leakage flux path
  (the core and gap carry the same flux in series).
- Every reported quantity is a direct algebraic function of the coil current
  at each instant (there is no accumulating/stored state), so each one is
  expected to trace the same 0-0.1 s ramp shape as the current itself, scaled
  by a constant factor, then hold flat afterward.
