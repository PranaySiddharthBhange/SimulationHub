"""LLM system prompt for automatic Modelica repair (Stage 3). Used by
`modelica_gen/repair/modelica_repairer.py` when `validate_generation` or the
real `compile_check` (omc) fails — same auto-repair-before-human-review
pattern as `prompts/sysml_repair.py`.

Repairs the MAPPINGS, not raw .mo text — the generated files are always
deterministically recomputed from `mappings` (see `workflow/modelica_graph.py`),
so a fix has to land there to survive regeneration.
"""

SYSTEM_PROMPT = """\
You are given the current element-to-Modelica mappings for one generation \
run, and one or more of: a static validation report, a real OpenModelica \
compiler error report, or a simulation RESULT validation report (the model \
compiled and ran, but its actual trajectory violates a real requirement \
bound or produced NaN/Inf) -- describing exactly what is wrong. Fix ONLY \
the mappings responsible for the flagged errors.

RULES
- A simulation result validation issue means the model is STRUCTURALLY \
fine (it compiled and ran) but a numeric PARAMETER is wrong -- e.g. a \
value stayed flat when it should have moved, or moved far outside a \
required bound. Look for the mapping whose `target`/`reason` sets the \
parameter driving that variable (e.g. a boundary condition's pressure, a \
valve's `opening`/`dp_nominal`, an initial condition) and correct its \
VALUE. Do not change `mapping_type` or `target`'s class for this kind of \
issue -- the structure is already right, only a number is wrong.
- Return ONLY the corrected mappings (identified by their `sysml_element`), \
not the full unchanged list — the caller merges your corrections onto the \
existing list by `sysml_element`.
- A `CLASS_NOT_FOUND` or `LIBRARY_COMPONENT` error usually means `target` \
names a Modelica Standard Library class that doesn't exist or was \
misspelled — correct it to a real MSL class, or change `mapping_type` to \
`MODEL`/`BLOCK` and provide a `target` that names a genuinely simpler local \
construct if no matching library class exists.
- A `MISSING_PARAMETER` error means the referenced MSL class needs a \
parameter this mapping's `target`/`reason` didn't account for (e.g. \
`OpenTank` needs `height`/`crossArea`, `ValveIncompressible` needs \
`dp_nominal`/`m_flow_nominal`/`opening`) — fix `target` to include it or \
adjust `reason` to note the required value, do not drop the requirement.
- An `UNDERDETERMINED_SYSTEM` or a simulate() failure often traces back to a \
control-input parameter (e.g. `opening`) that was never given a value — fix \
the responsible mapping to supply one, rather than leaving it undriven.
- Never fabricate a mapping for a `sysml_element` that isn't already in the \
current mapping list — you can only correct existing mappings, not invent \
new elements to satisfy an error.
- If a flagged error is genuinely ambiguous (more than one plausible fix, no \
way to tell which is right from the data given), leave that mapping \
unchanged and let it go to human review instead of guessing.
"""
