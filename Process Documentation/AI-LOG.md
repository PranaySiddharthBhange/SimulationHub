# AI-LOG.md

## D1 — Installed required local software

- Installed OpenModelica 1.27.1 for local Modelica compilation.
- Installed the official SysML v2 Jupyter kernel in a dedicated Conda environment for local SysML syntax validation.
- Installed the supporting Python and Jupyter packages required to invoke both validators from the application later.

## A2  Initial AI-generated architecture

- **AI output:** AI proposed generating SysML and Modelica directly from the source documents in separate steps.
- **Problem:** Independent generation could produce different components, names, parameters, and connections in the two outputs.
- **Correction:** Added explicit agent contracts and required both generation stages to use the same resolved engineering information.
- **Reason:** SysML and Modelica must describe the same system, and compiler feedback must be traceable to the originating model decision.

## A3 Rejected benchmark-specific generation templates

- **AI output:** AI suggested implementing separate generation rules for the four supplied benchmark systems to reach working outputs quickly.
- **Why it was rejected:** The judges can provide an unseen specification, and case-name-specific rules would demonstrate memorization rather than a reusable modelling product.
- **Replacement:** Use evidence extraction, a typed intermediate representation, and generic component archetypes selected from evidenced roles and compatible interfaces.
- **Evidence:** The product requirements describe the supplied cases as calibration tests and explicitly prioritize generalization over case-specific handling.
- **Human judgment:** Keep the L1 tank case as the first vertical slice while ensuring the architecture does not branch on the benchmark name.

## A4 Rejected silent defaults for missing engineering data

- **AI output:** AI could complete incomplete specifications by inserting plausible standard values so generation could continue without interruption.
- **Why it was rejected:** A plausible value can change the physics, timing, or acceptance result while hiding that the source never supplied it.
- **Replacement:** Add a simulation-readiness check that classifies the model as `ready`, `needs_decision`, or `unsupported_or_conflicting`; material assumptions require a recorded user decision.
- **Evidence:** The hackathon requirements state that missing information must be surfaced or introduced as a stated assumption and that contradictions must not be resolved arbitrarily.
- **Human judgment:** A partial but traceable model is preferable to a complete-looking model built on invented parameters.

## A5 Corrected the proposed Modelica validation gate

- **AI output:** AI treated generated Modelica text and a successful lightweight model check as sufficient evidence that the model compiled.
- **Why it was corrected:** Syntax and `checkModel()` do not prove that OpenModelica can translate, build, initialize, and simulate the equation system.
- **Replacement:** Run the generated files through the real `omc` toolchain, build the model, execute a simulation, capture diagnostics, and return failures to a bounded repair loop.
- **Evidence:** The participant rules define Modelica compilation as a binary live gate, while the implementation plan requires a reproducible compiler command and saved output.
- **Human judgment:** Only the external compiler can declare compilation success; the AI may diagnose and repair failures but cannot waive the gate.
