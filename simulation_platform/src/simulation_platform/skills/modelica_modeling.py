"""Meta-skill: Modelica modeling conventions, including real Modelica
Standard Library (MSL) usage requirements. Appended to Stage 3 (Modelica
generation/reasoning) prompts. Distills real, live-found lessons from
building and debugging this pipeline against a real, locally installed
OpenModelica compiler (`omc`) -- see DECISIONS.md D21, D35-D56 -- into
forward-looking guidance, so a future run doesn't have to rediscover the
same class of gap live, on a new dataset, one compile error at a time.
"""

SKILL = """\
SKILL: Modelica modeling conventions (verified against a real OpenModelica \
compiler and the real Modelica Standard Library source, not just the language \
spec or a class's documentation string).

STRUCTURE
- `equation` sections hold only genuine equations (`a = b`, `der(x) = ...`). \
`algorithm` sections hold assignments (`:=`) and `when ... then ... end \
when;` blocks. Mixing them (an assignment inside `equation`) is a real, \
hard compiler error ("Equations can not contain assignments") -- when \
reusing or transcribing existing procedural logic, keep it in `algorithm`.
- A file literally named `package.mo` carries special meaning: the package \
it declares must match the name of its *containing directory*. This only \
matters for a real directory-based library layout, not a flat file list.
- Modelica unit strings never use `^` for exponents -- the canonical form \
is `m3/s`, not `m^3/s`, even though the human-written source document \
almost always uses the caret form.
- A variable's declared type in reused/legacy code is whatever it actually \
is (a custom `enumeration(...)` type is common for a sequencer's state \
variable), not only Real/Boolean/Integer/String -- and a `discrete` \
variable with an explicit `start=` value needs BOTH the qualifier and the \
start value preserved on reuse, or it becomes undetermined.

THE CHECKMODEL VS. SIMULATE GAP (the single most important lesson here)
`checkModel()` is a structural/type check -- it will happily accept a class \
with parameters that have no value, an under-determined equation system, \
or a component whose control-signal input was never given a value. A real \
`simulate()` attempt (even a short one, a few seconds of simulated time) \
catches all of these, because it actually needs to solve the system, not \
just type-check it. TREAT `checkModel()`-PASSING AS NECESSARY, NOT \
SUFFICIENT -- an actual simulate() attempt is the only reliable check that \
a generated model will do anything at all.

MSL FLUID COMPONENTS -- REAL MANDATORY REQUIREMENTS (checked directly against \
the MSL 4.1.0 source, not guessed from a class's short description)
- Every `Modelica.Fluid.*` component declares its working fluid as a \
`replaceable package Medium`, defaulting to an ABSTRACT partial medium with \
no concrete substance data. It must be redeclared to a real medium (e.g. \
`Modelica.Media.Water.StandardWater`) before the component means anything -- \
without this, even a value that "compiles" will fail during translation \
with an unset-constant error deep inside the library's own implementation.
- `Modelica.Fluid.Vessels.OpenTank` additionally requires `height`/ \
`crossArea` (no default at all) and, once it has any real ports \
(`nPorts > 0`), activates `use_portsData=true` by default, which in turn \
requires a per-port `diameter` with no default -- set `use_portsData = \
false` instead of fabricating per-port geometry the source data doesn't \
provide; this switches to the library's own simpler zero-diameter \
treatment.
- `Modelica.Fluid.Valves.ValveIncompressible` requires `dp_nominal`/ \
`m_flow_nominal` (its nominal operating point, no default), AND its \
`opening` is a genuine undriven `input Real` control signal (0=closed, \
1=open) -- if no real control signal is available to wire to it, it needs \
an explicit value (e.g. `opening = 1.0`, fully open) or the component's \
own flow equations are structurally indeterminate, independent of \
anything else being correct.
- `Modelica.Fluid.Machines.PrescribedPump` requires `N_nominal` (nominal \
rotational speed, no default).
- Every `Modelica.Fluid` component needs an `inner Modelica.Fluid.System \
system;` declared somewhere in the model (once per model, not once per \
component) for ambient-condition defaults -- without it, translation \
degrades gracefully in a GUI tool (silently auto-generating one) but a \
headless `simulate()` call may not.
- Two-port components (`port_a`/`port_b`, e.g. valves, pumps) each need \
BOTH ports connected to something with a real, distinct driving condition \
-- a component whose both ports are boundary-sourced with the IDENTICAL \
default pressure has zero driving differential, an outright indeterminate \
flow direction, not merely "a component with no data." Any two components \
being boundary-conditioned as substitutes for a real network connection \
need genuinely different pressure/temperature values from each other, not \
just "a value."

WHEN A CLASS'S OWN REQUIREMENTS AREN'T ALREADY KNOWN
Before assuming a bare instantiation of an unfamiliar MSL class is enough, \
check its actual declaration (via the compiler's own introspection, or by \
reading the class's source in the installed library) for parameters with \
no default value (`fixed=true` and no `=` in the declaration) and for any \
`replaceable`/`redeclare` requirement -- these are the two shapes of \
"looks fine, fails at translation" gap found repeatedly in this pipeline's \
own history, and they generalize to library classes in every physical \
domain, not only `Modelica.Fluid`.

RENDERING REAL BEHAVIOR, NOT JUST A COMMENT
A structured behavior (a trigger: property/operator/value/unit, and an \
action: type/target) can often be rendered as a real `when <condition> \
then <action>; end when;` block once the trigger property and action \
target are confidently resolved to real Modelica variables/instances -- \
prefer this over a `// {reason}` comment whenever the resolution is \
unambiguous. When it is NOT unambiguous (the property name doesn't clearly \
match any real variable, or the action implies a component/port this \
pipeline doesn't know how to address), render the comment -- do not guess \
a variable name into existence, since a wrong-but-confident `when` clause \
either fails to compile or, worse, compiles and silently does the wrong \
physical thing.
"""
