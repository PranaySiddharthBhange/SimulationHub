export const STAGES = [
  { key: 'stage_1', label: 'Read', hint: 'Reads every source document' },
  { key: 'merge', label: 'Combine', hint: 'Merges everything into one brief' },
  { key: 'clarify', label: 'Confirm', hint: 'You confirm any open decisions' },
  { key: 'stage_2', label: 'Design', hint: 'Generates the SysML v2 model' },
  { key: 'stage_3', label: 'Simulate', hint: 'Compiles, runs, and verifies the result' },
]

export const STAGE_INDEX = Object.fromEntries(STAGES.map((s, i) => [s.key, i]))
