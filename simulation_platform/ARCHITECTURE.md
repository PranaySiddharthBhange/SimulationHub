# Architecture: reason about the experiment, then prove the result

The old architecture lost meaning before it reached the modeling stages. Stage 1
made seven extraction calls for each document without the other documents, then
merged nouns and values through rigid schemas and fixed precedence rules. Later
stages treated that lossy result as authoritative. Fixed generators produced five
SysML files and many Modelica classes, sometimes with no governing equations.
Passing tests for those mappings could not establish physical correctness.

The replacement separates three kinds of work: reading evidence, making engineering
judgments, and checking executable results. Only engineering judgment belongs to
the language model. File reading, parser execution, simulation, numeric comparison,
path validation, and cache invalidation are ordinary deterministic code.

## Evidence stays available

`sources.py` reads the original packet without extracting a predefined entity
taxonomy. It retains filenames, PDF pages, spreadsheet row context, formulas and
cached values, document ordering, email chronology, and image evidence. Scanned
pages and diagrams go directly to the multimodal model alongside extracted text.

The complete engineering text and images accompany every reasoning/review call.
No retrieval ranking can hide an approved change from the next stage. Large CSV
trajectories are represented by schema; full input schedules are supplied after
their role is established. Explicitly designated reference tables stay held out
regardless of the model's classification.

For the supplied packets the text context is about 42–51 KB per case. A retrieval
subsystem adds little value at that size. Larger collections need deliberate
scope decomposition; the current implementation reports its context boundary.

## A flexible understanding with a small executable contract

`Understanding.narrative` is the main Stage 1 result. It explains:

- the question being answered and the physical system boundary;
- effective parameter values, units, configuration, and supporting sources;
- the governing balances/constitutive equations and justified simplifications;
- initial conditions, driving inputs, command priorities, and timing semantics;
- expected outputs, independent checks, assumptions, and unresolved questions.

The typed portion is deliberately narrow: simulation settings, table roles, and
numerical acceptance checks. JSON schema constrains the handoff's format without
forcing the engineering explanation into hundreds of entity/mapping records.
Checks are chosen before model generation and can reference actual output variables
through a restricted expression language; arbitrary Python is not executed.

An additional review compares the brief against the complete packet. A conflict
between an old drawing, a measurement, and a later approved change is resolved by
meaning and applicability. There is no universal rule that an XLSX overrides a PDF
or that a more recent file is automatically the released configuration.

## Generate whole models

Stage 2 produces one SysML package in `Model.sysml`. Physical parts, connections,
requirements and behavior belong in the same understandable model. Their exact
structure is chosen for the problem; every extracted noun does not become a part.
The actual SysML v2 kernel checks syntax and name resolution. A model review checks
the engineering meaning against the brief and original documents.

Stage 3 receives that SysML, the brief, and the original packet. It generates a
complete `.mo` file with governing equations and event behavior. For simple
benchmarks, explicit lumped equations can be more appropriate than instantiating
a large fluid/electromagnetic library assembly. Required fidelity comes from the
problem; the runtime contains no tank, ventilation, or magnetic-circuit templates.

Reported upstream corrections rerun understanding and regenerate SysML before
Modelica is attempted again. The previous interpretation and correction are saved
in the same project state file. Downstream work cannot silently freeze a known
error in the first interpretation.

## Success means verified behavior

`READY` requires all applicable layers:

| Layer | What it establishes |
| --- | --- |
| Whole-packet review | Interpretation agrees with the supplied engineering evidence |
| Real SysML parser | The semantic model is syntactically/name-resolution valid |
| Real OpenModelica simulation | Equations initialize and execute over the required experiment |
| Numerical acceptance checks | Actual outputs satisfy source-grounded outcomes and invariants |
| Reference comparisons | Held-out trajectories agree within the declared tolerances |
| Cross-model review | SysML, Modelica and sources describe the same physical system |

Missing outputs, empty checks, nonfinite values, incomplete time coverage, parser
unavailability, and compile-only success cannot pass. Reference mappings and
tolerances are fixed before numerical results are seen; a repair cannot loosen
them or remove checks. Event comparisons handle pre/post-event rows and solver
roundoff. All raw event rows are checked before the requested logging grid is
exported, including both endpoints.

Source data, settings, prompts, upstream output, and generated artifact hashes
participate in cache decisions. Changed/deleted artifacts are regenerated or
revalidated. Regeneration marks previous result reports stale immediately.

## Evaluate independently of the generator

`benchmarks/` is outside production. It contains three explicit mathematical
reference models, the supplied result-table mappings, and fixed evaluation
tolerances. These constants are not available through an import from production
code, and the models are not supplied to the agent.

Offline reference runs exercise the compiler and numeric verifier. Separate agent
runs exercise source understanding and model generation, then use the independent
benchmark tolerances. These are different claims and have different report labels.
An additional tank test pauses during a wait, and another tests simultaneous
commands and commands during shutdown. They cover semantics beyond the original
900-second trace.

No architecture makes an LLM infallible. Shared-context generation and review can
still make correlated mistakes; a reference table may itself be wrong, and a
passing finite set of tests is not a proof for every operating condition. Source
assumptions, unresolved choices, and numerical discrepancies must stay visible.
Further confidence comes from actual agent benchmark runs, parameter perturbations,
additional scenarios, and engineering review—not from more extraction schemas.
