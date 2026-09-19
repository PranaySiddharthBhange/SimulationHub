"""Domain skill: Electromagnetic / Magnetic Circuit. Appended to a
reasoning prompt (not called as a function) -- see `new direction.txt`
§11, Domain 3, and PRD L3 ("Multiphysics energy transfer across domains,
with an explicit loss path").
"""

SKILL = """\
DOMAIN: Magnetic Circuit (electromagnetic energy transfer, multi-domain coupling)

CORE PHYSICS
A magnetic circuit is the magnetic analog of an electrical circuit: instead \
of voltage/current/resistance, it uses magnetomotive force (MMF, driven by \
a coil's current times its number of turns), magnetic flux (the "current" \
analog, conserved at a junction the same way electrical current is), and \
reluctance (the "resistance" analog, a property of a magnetic path's \
geometry and the material it passes through -- air gaps have high \
reluctance, high-permeability core material has low reluctance). Ohm's-law \
analog: MMF = flux x reluctance. A coil wound around a magnetic core \
converts electrical energy (voltage and current at its terminals) into \
magnetic energy (flux through the core) and back -- this is precisely the \
MULTIPHYSICS coupling the problem tests: an electrical domain (voltage, \
current, resistance, inductance) coupled to a magnetic domain (flux, \
MMF, reluctance) through a coil, which is the energy-transfer element \
between them.

ROLES TO DISTINGUISH
- The excitation source (a voltage or current source on the electrical \
side): drives current through the coil.
- The coil (winding): the coupling element -- N turns of wire around a \
core leg, converting between electrical (V, I) and magnetic (flux, MMF) \
quantities. Its own electrical resistance is a real, usually unavoidable \
loss path (I^2 R heating) distinct from the magnetic circuit itself.
- The magnetic core / flux path (including any air gap): the reluctance \
network the flux actually flows through -- typically modeled as one or \
more reluctance elements in series/parallel, exactly like resistors in an \
electrical circuit, EXCEPT flux (not current) is what's conserved at a \
junction.
- The explicit loss path: a real magnetic circuit problem in this test \
suite specifically wants a modeled loss mechanism, not an ideal \
lossless transformer -- this is usually the coil's winding resistance \
(electrical-side I^2 R loss) and/or a core-loss term (eddy-current/ \
hysteresis loss, if the problem statement mentions it). "Explicit loss \
path" means: energy put in by the source must be traceable to where it \
is actually dissipated, not silently conserved by construction.

WORKED EXAMPLE
A voltage source drives current through a coil's winding resistance and \
its coupled inductance. That current, times the coil's turns count, \
produces an MMF that drives flux around the magnetic core's reluctance \
path (core reluctance in series with any air-gap reluctance, since flux \
must cross both to complete the loop). The flux linking the coil in turn \
determines the coil's back-EMF (via Faraday's law), which is exactly what \
couples the magnetic circuit's state back into the electrical circuit's \
own equation for current -- this is the two-way multiphysics coupling: \
electrical current creates magnetic flux, and changing magnetic flux \
creates an opposing electrical voltage. Energy supplied by the source \
splits between resistive loss in the winding (dissipated, leaves the \
system as heat) and energy stored/transferred in the magnetic field. \
Verifying the model is "reasonable" means checking that energy is \
conserved end-to-end (source energy = resistive loss + magnetic energy \
change + any core loss), not just that the equations compile.

WHAT THIS IMPLIES FOR MODELING
A faithful model needs: (1) a real electrical sub-circuit (source, \
winding resistance, at minimum) using the target tool's electrical \
component library, not an invented generic block; (2) a real magnetic \
sub-circuit (reluctance elements for core and any air gap) using the \
target tool's magnetic/flux-tube library if one exists, connected in a \
loop the same way an electrical circuit must close; (3) the actual \
electromechanical coupling element (the coil/winding component that \
converts between the two domains) connecting both sub-circuits -- a model \
with an electrical circuit and a separate, disconnected magnetic circuit \
has not modeled the coupling the problem is actually testing.
"""
