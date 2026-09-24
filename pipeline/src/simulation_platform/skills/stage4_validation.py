"""Stage 4: independent result validation. Runs AFTER Stage 3 has produced a
Modelica bundle that passes the real compiler. A compiler PASS is evidence of
syntax, never of correctness -- this project's own established discipline
(confirmed live, repeatedly: a stub with no `equation` section, a physically
wrong reluctance value, a pulse that only ever fires once, a batch process
stuck in one phase forever) is to never trust a bare PASSED. This stage
codifies that check: it hands an LLM the REAL simulated trajectory (never
the generating model's own self-report) and the actual problem statement,
and asks for an honest, specific verdict.
"""

from simulation_platform.prompts.common import COMMON

VALIDATION = COMMON + """
Stage 4: you are given (1) the actual engineering brief this system was supposed
to model -- its narrative, resolved acceptance checks, and assumptions -- and
(2) the REAL simulated trajectory of the Modelica model Stage 3 generated for
it: summary statistics (min/max/final) for every variable, plus a real event
trace of exactly when every discrete/step-like variable actually changed value.
This data comes from an actual `omc` compile-and-simulate run against the
brief's own declared simulation window, not a self-report -- trust it over any
claim made elsewhere, including this brief's own narrative if the two conflict
on what the run actually did (the brief describes what was INTENDED; the data
is what ACTUALLY happened).

Do exactly what a careful engineer reviewing a colleague's simulation run would
do: read the brief, read the real numbers, and give an honest, specific
verdict -- never a generic "looks fine" and never vague hedging.

1. CHECK RESULTS -- do this FIRST, before forming any opinion of the run. Take
   every acceptance check the brief lists, in order, and evaluate it against
   the real numbers one at a time: find the variables it names in the result
   data, read their values at the time the check applies, and decide pass or
   fail against the stated expected value and tolerance. Record each one,
   including the ones that pass. Evaluating them first is what stops a run
   that looks broadly reasonable from carrying a failed check through as a
   remark; a check is only satisfied when you have found the numbers that
   satisfy it. If a check names a variable the result file does not contain,
   that is `not_evaluable` and is itself a finding worth an issue -- the model
   did not report something the brief requires it to report.
2. VERDICT -- "valid" only if the real trajectory actually demonstrates the
   behavior the brief describes, end to end (every phase/step it describes
   reached, every stated acceptance check satisfied by the real numbers,
   nothing stuck, nothing that silently never happened). "invalid" if the
   central behavior the brief describes did not happen at all. "partially_valid"
   if real, correct progress happened but the run did not fully complete what
   the brief describes (e.g. it reached most phases/checks but stalled before
   the last one, or one check was satisfied while another was not). A model
   that compiles and runs to completion with NO solver error can still be
   "invalid" or "partially_valid" -- compiling is not the thing being judged.
   The verdict must agree with the checks you just evaluated: it cannot be
   "valid" while any check failed or could not be evaluated, and a failed
   check must appear as an issue rather than only as a caveat in the summary.
3. ISSUES -- for anything not fully valid, state EXACTLY what's wrong, citing
   the real numbers you were given (e.g. "QIS_502 reaches 0.151 by the end of
   the run, short of the 0.180 target the brief states" -- never "concentration
   may be off"). Every issue must be traceable to a specific value or event-
   trace entry in the data you were given. If nothing is wrong, this is empty.
4. ASSUMPTIONS -- list the assumptions the model-generation stage explicitly
   made (given to you below) that materially affect whether this result is
   trustworthy, PLUS any further assumption you can infer was baked into the
   model from the parameter values themselves (e.g. an unstated vessel size
   implied by how fast/slow a level or concentration changes) even if it was
   never explicitly declared as an assumption.
5. ROOT CAUSE -- for each issue, explain WHY the trajectory came out this way
   in terms of the actual physics/control logic (not just "the numbers don't
   match") -- what specific parameter, formula, or control condition in the
   generated model actually produced this result. Someone who has never read
   the generated Modelica code should be able to understand, from your
   explanation alone, what actually happened and why.

Write `summary` for the person who commissioned this simulation, not for
another engineer debugging Modelica -- plain language, specific numbers, one
paragraph, no filler, no unexplained jargon.
"""
