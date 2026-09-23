"""Prompt for generating the post-Clarify Mermaid system flow diagram."""

from simulation_platform.prompts.common import COMMON

FLOW_DIAGRAM = COMMON + r"""

You are generating the system's human-readable flow diagram after the Merge
and Clarify stages. The context contains the resolved engineering brief and
the human-confirmed decisions. Generate one complete Mermaid flowchart that
shows the actual system behavior from simulation start through the requested
end condition.

Return only the `MermaidDraft` structured object. Its `code` field must contain
plain Mermaid source, never Markdown fences, prose, or an HTML document.

Use this exact safe syntax:

flowchart TD
    A["Start"] --> B{"Condition?"}
    B -->|Yes| C["Action"]
    B -->|No| B

Diagram requirements:

- Begin with exactly `flowchart TD`.
- Use short alphanumeric node ids such as A, B, C1, N2.
- Put every visible node label in double quotes inside `[...]` or `{...}`.
- Use `<br/>` inside labels for line breaks; do not use literal newlines in a node label.
- Draw the kind of system the brief actually describes. A SEQUENCED system is
  drawn as its flow of states: initial condition, scheduled commands, each
  operating phase, actuator command, sensor or threshold guard, wait duration,
  transition, cycle-back path, any pause/resume or abort/override behavior and
  its priority, and the end/reporting condition -- each of those included only
  where the brief establishes it. A CONTINUOUS, quasi-static or purely
  algebraic system has none of that: draw it as the flow of physical quantity
  through the system instead -- the prescribed input and its schedule, each
  element the quantity passes through, where a path splits and rejoins, the
  quantities computed at each point, and the reported outputs. Do not invent
  states, commands, phases or actuators for a system that has none, and do not
  flatten a genuinely sequenced system into a block diagram.
- Label every decision edge explicitly with `Yes`, `No`, or the actual command
  or event name. Do not leave a condition with an unlabeled branch.
- Keep normal operation and exceptional command paths visibly separate, then
  join them only where the resolved brief says they rejoin.
- Preserve the exact clarified values, units, command times, state names, and
  component aliases chosen by the brief. Do not substitute generic values.
- Do not invent a branch, state, threshold, timing, or component. If the brief
  leaves a question unresolved, show a clearly labeled human-decision node or
  state the unresolved choice in `corrections`; never silently choose one.
- Keep the diagram readable: one action or guard per node, no giant paragraphs,
  and no subgraph syntax unless it is necessary for a clear flow.

Before returning, check that every arrow endpoint exists, every node id is
unique, the source begins with `flowchart TD`, all brackets and quotes balance,
and no Markdown fences or unsupported Mermaid syntax remain.
"""
