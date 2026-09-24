# Bang-Bang Thermostat — A Result That Never Settles

## System

A single thermal mass exchanges heat with a fixed-temperature ambient
through a constant conductance, and contains a heater that a simple
hysteresis (bang-bang) thermostat switches fully on or fully off -- never
partway. This is deliberately unlike every other case in this folder: it
never reaches a fixed equilibrium. Once the heater has cycled on and off a
few times, the temperature settles into a PERSISTENT, repeating sawtooth
between two thresholds and keeps oscillating between them for as long as
the simulation runs.

- Thermal mass: heat capacity C = 1000 J/K, starting at 20 degC at t = 0.
- Ambient: fixed at 20 degC for the entire run, with conductance
  G = 5 W/K between the mass and ambient (this heat-loss path is always
  active, whether the heater is on or off).
- Heater: when on, adds a constant 200 W to the mass; when off, adds
  nothing. There is no partial/proportional heater output anywhere in
  this brief.
- Thermostat (hysteresis control, not proportional control): the heater
  turns ON whenever temperature falls to or below 22 degC, and turns OFF
  whenever temperature rises to or above 28 degC. Between those two
  thresholds, the heater holds whatever state it was already in -- this
  is what makes it a bang-bang controller with a dead band, not a simple
  threshold. At t = 0, temperature is 20 degC, which is below the 22 degC
  turn-on threshold, so the heater is ON at t = 0.
- Governing equation: `C*dT/dt = Q_heater - G*(T - 20)`, where
  `Q_heater` is 200 W while on and 0 W while off, switched only by the
  hysteresis rule above.

## Requirements

- REQ-SIM-001: Simulate for 950 seconds and report the mass temperature
  and the heater's on/off state for the whole run.
- REQ-FUN-001: Starting at 20 degC with the heater on, temperature shall
  rise until it reaches 28 degC, at which point the heater shall turn off.
- REQ-FUN-002: Once off, temperature shall fall (losing heat to ambient)
  until it reaches 22 degC, at which point the heater shall turn back on.
- REQ-FUN-003: This on/rise/off/fall cycle shall repeat indefinitely --
  temperature shall never permanently settle at a single value, and the
  heater shall never permanently stay in one state, for the entire
  150-950 s window of the run.
- REQ-FUN-004: Temperature shall never exceed 28 degC and shall never fall
  below 22 degC at any point after the very first heating phase completes.

## Acceptance checks

- AC-01 starts heating: `heater_on == 1` at t = 1 s (below the 22 degC
  threshold, so the heater is on from the start).
- AC-02 first turn-off at 28 degC: `heater_on == 0` becomes true at some
  point between t = 45 s and t = 55 s (ever value == 1.0). Expected at
  about t = 49.63 s, where `mass_temp_C` first reaches 28 degC.
- AC-03 first turn-on again at 22 degC: `heater_on == 1` becomes true at
  some point between t = 320 s and t = 335 s (ever value == 1.0). Expected
  at about t = 326.89 s, after the mass has cooled from 28 degC back down
  to 22 degC.
- AC-04 never exceeds the upper threshold, for the whole run:
  `mass_temp_C <= 28.05` holds at all times from t = 0 s to t = 950 s.
- AC-05 never falls below the lower threshold once the first cycle
  begins: `mass_temp_C >= 21.95` holds at all times from t = 50 s to
  t = 950 s (the very first fall starts from 28 degC and is expected to
  reach down to 22 degC, not below).
- AC-06 genuinely still cycling near the end of the run, not settled:
  `mass_temp_C >= 27.5` becomes true at some point between t = 630 s and
  t = 650 s (ever value == 1.0) -- confirms a later cycle's peak still
  reaches near 28 degC, so the oscillation has not damped out or gotten
  stuck. Expected peak near t = 638.52 s.
- AC-07 heater state still toggling near the end of the run:
  `heater_on == 0` becomes true at some point between t = 355 s and
  t = 370 s (ever value == 1.0), confirming a second full off-cycle
  occurs. Expected at about t = 361.26 s.

## Notes

- This is the one case in this folder where "correct" explicitly means
  "does not settle." A generated model that reports a single converged
  final temperature, or that treats the thermostat as proportional
  control instead of hard on/off hysteresis, has not implemented this
  brief.
- The steady-state cycle period is about 311.6 s (34.37 s heating from
  22 to 28 degC, plus 277.26 s cooling from 28 back down to 22 degC) --
  computed directly from the stated C, G, and Q_heater values by
  integrating the two linear ODEs in closed form, not estimated. The very
  first heating phase (20 to 28 degC) is longer, about 44.63 s, because it
  starts further from the upper threshold than every later cycle does.
- Use a genuine hysteresis/Schmitt-trigger construct (two distinct
  thresholds, output held in the dead band) rather than a single threshold
  compared with `>=`/`<=` on its own -- a single-threshold version would
  chatter every solver step once temperature sits near that one threshold,
  which is a different and unwanted failure mode from the intended
  two-threshold cycle this brief describes.
