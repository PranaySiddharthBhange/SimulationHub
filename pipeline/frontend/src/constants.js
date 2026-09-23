export const STAGES = [
  { key: 'stage_1', label: 'Understand', hint: 'Local model reads every document' },
  { key: 'merge', label: 'Merge', hint: 'Resolve entities into one brief' },
  { key: 'clarify', label: 'Clarify', hint: 'Confirm unresolved engineering decisions' },
  { key: 'stage_2', label: 'SysML v2', hint: 'Human-reviewed generation' },
  { key: 'stage_3', label: 'Modelica', hint: 'Real omc compile + simulate' },
  { key: 'stage_4', label: 'Validate', hint: 'Independent review of the real result vs. the brief' },
]

export const STAGE_INDEX = Object.fromEntries(STAGES.map((s, i) => [s.key, i]))
