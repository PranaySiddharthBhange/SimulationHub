"""Domain skill: Fluid / Tank Systems. Appended to a reasoning prompt (not
called as a function) so the model has real domain vocabulary and physical
patterns in context when reasoning about a system it hasn't seen described
this way before -- see `new direction.txt` §11, Domain 1, and PRD §9.1
("Valve sequencing in a two-tank rig is the same pattern as sequencing in
a process gas delivery chain... optimize for the pattern.").

Deliberately generic: no specific tank volume, valve name, or threshold
from any one dataset. Those come from the problem statement/documents, not
from this skill (§12 -- no problem-specific skills).
"""

SKILL = """\
DOMAIN: Fluid / Tank Systems (liquid storage, transfer, and sequenced batch processing)

CORE PHYSICS
A tank (vessel, reservoir) accumulates fluid: its level (or mass, or volume) \
changes over time as a mass balance -- the net of every inflow minus every \
outflow, integrated over time. A pump adds pressure head to drive flow \
against resistance; a valve is a variable or two-state (open/closed) flow \
restriction with a real pressure drop across it. Flow through a valve or \
pipe is only well-defined when there is an actual pressure differential \
driving it and a real medium (a working fluid, e.g. water, air, a process \
liquid) with a defined density/state -- a valve or vessel component from a \
library is USUALLY generic over which fluid flows through it, and requires \
that fluid to be specified before it means anything physically.

ROLES TO DISTINGUISH
- Storage/capacity components (tanks, vessels, reservoirs, accumulators): \
they integrate a balance over time and have a "level" or "amount" state.
- Flow-gating components (valves, dampers, restrictors): they have no \
storage of their own; they only ever sit between two other components and \
either permit or restrict flow between them.
- Flow-driving components (pumps, compressors, fans): they add energy to \
the fluid to move it against resistance.
- Sensing components (level sensors, flow sensors, pressure sensors): they \
measure a physical quantity of a storage or flow component; they don't \
themselves store or move fluid.
- Sequencing/control components (a PLC, sequencer, or a state-machine \
controller): they read sensors and command valves/pumps according to a \
defined procedure, not according to physics -- this is where a real \
"state machine" (fill -> wait -> transfer -> wait -> drain -> repeat, or \
similar) usually lives, often with named states and edge-triggered \
transitions (a level crossing a setpoint, a timer expiring, an operator \
command).

TYPICAL CONTROL PATTERN, WORKED EXAMPLE
Consider a two-vessel batch process: Vessel A fills from a source through \
Valve 1 until its level reaches a high setpoint; Valve 1 then closes and, \
after a short settling delay, Valve 2 opens to transfer A's contents into \
Vessel B until A reaches a low setpoint; Valve 2 closes and, after another \
delay, Valve 3 opens to drain Vessel B to empty; the cycle then repeats \
from fill. This is a single closed-loop discrete state machine (a sequence \
of named states, each with an entry action -- e.g. "open Valve 1" -- and an \
exit condition -- e.g. "Vessel A level >= high setpoint"), NOT a continuous \
control law: the transitions are triggered by threshold crossings and \
timers, not by a PID controller. A safe-stop requirement typically means: \
on a stop command, close all valves immediately regardless of which state \
the sequence was in, and remember enough context (which state, how much \
delay remained) to resume correctly rather than restarting the whole cycle. \
Interlocks typically mean: two valves that would create an unintended \
direct path (e.g. simultaneously draining and filling the same vessel) must \
never both be commanded open at once, independent of the sequencer's own \
state logic -- a safety check layered on top of, not instead of, the \
sequence.

WHAT THIS IMPLIES FOR MODELING
A faithful model needs: (1) a real mass/volume balance equation per vessel, \
not just a placeholder; (2) real flow equations through each valve/pump, \
which in Modelica's Fluid library specifically require a concrete working \
fluid (`Medium`) to be assigned before the component means anything -- see \
the Modelica modeling skill; (3) the actual state-transition logic (which \
state leads to which, on what trigger) rendered as real conditional/event \
logic, not merely a comment referencing the requirement it came from -- a \
model that declares valves and vessels but never advances a sequencer will \
compile and simulate but never actually fill, transfer, or drain anything.
"""
