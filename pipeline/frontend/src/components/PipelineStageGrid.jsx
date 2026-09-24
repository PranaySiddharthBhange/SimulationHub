import { AlertTriangle, Check, ChevronDown, HelpCircle, Loader2, Play, RotateCcw } from 'lucide-react'
import { useMemo, useState } from 'react'
import { STAGES } from '../constants'

function stageKeyFromName(name = '') {
  const value = name.toLowerCase()
  if (value.startsWith('merge')) return 'merge'
  if (value.startsWith('clarif')) return 'clarify'
  if (value.includes('stage 1:')) return 'stage_1'
  if (value.includes('stage 2:')) return 'stage_2'
  // Stage 4 (validation) now runs as part of the same "Simulate" step as
  // Stage 3 (see execute_reasoner_stage_3_and_4), so its cost/token spend
  // rolls up into the same 'stage_3' card instead of a separate one.
  if (value.includes('stage 3:') || value.includes('stage 4:')) return 'stage_3'
  return null
}

function stageMetrics(logs) {
  const result = {}
  let currentStage = null
  for (const event of logs) {
    if (event.event === 'stage_start') currentStage = stageKeyFromName(event.name)
    if (event.event !== 'llm_call' || !currentStage) continue
    const prev = result[currentStage] || { cost: 0, inputTokens: 0, outputTokens: 0, calls: 0 }
    result[currentStage] = {
      backend: event.backend,
      model: event.model,
      cost: prev.cost + Number(event.call_spent_usd || 0),
      inputTokens: prev.inputTokens + Number(event.input_tokens || 0),
      outputTokens: prev.outputTokens + Number(event.output_tokens || 0),
      calls: prev.calls + 1,
    }
  }
  return result
}

function formatCost(cost) {
  if (!cost) return '$0.00'
  return cost < 0.01 ? `$${cost.toFixed(6)}` : `$${cost.toFixed(4)}`
}

function cardStatus(state, dependencyReady, prevLabel) {
  switch (state) {
    case 'done':
      return { label: 'Complete', tone: 'green' }
    case 'error':
      return { label: 'Failed', tone: 'red' }
    case 'awaiting':
      return { label: 'Needs input', tone: 'amber' }
    case 'active':
      return { label: 'Running', tone: 'accent' }
    default:
      return dependencyReady
        ? { label: 'Ready', tone: 'accent' }
        : { label: `Waits on ${prevLabel}`, tone: 'muted' }
  }
}

const TONE_STYLES = {
  green: { pillFg: 'var(--green)', pillBg: '#edf3ec' },
  red: { pillFg: 'var(--red)', pillBg: '#f8eae7' },
  amber: { pillFg: 'var(--amber)', pillBg: '#faf1de' },
  accent: { pillFg: 'var(--accent)', pillBg: 'var(--accent-soft)' },
  muted: { pillFg: 'var(--text-dim)', pillBg: 'var(--bg-soft)' },
}

function StageCard({ index, stage, state, dependencyReady, prevLabel, onRun, disabled, metric }) {
  const status = cardStatus(state, dependencyReady, prevLabel)
  const tone = TONE_STYLES[status.tone]
  const canRun = !disabled && state !== 'active' && dependencyReady
  const highlighted = status.tone === 'accent'
  const filledBadge = state === 'done' || state === 'active' || state === 'error' || state === 'awaiting'
  const isLocal = metric?.backend === 'ollama'

  return (
    <div
      className="relative flex min-w-[190px] flex-1 flex-col rounded-xl border px-4 py-4 transition-colors"
      style={{
        borderColor: highlighted ? 'var(--accent)' : 'var(--border)',
        background: highlighted ? 'var(--accent-soft)' : 'var(--panel)',
        boxShadow: highlighted ? '0 1px 3px rgba(194,101,47,.12)' : 'none',
      }}
    >
      <div className="mb-3 flex items-center justify-between gap-2">
        <div
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[12px] font-semibold"
          style={{
            background: filledBadge ? tone.pillFg : 'transparent',
            color: filledBadge ? '#fff' : tone.pillFg,
            border: `1.5px solid ${status.tone === 'muted' ? 'var(--border-strong)' : tone.pillFg}`,
          }}
        >
          {state === 'done' && <Check className="h-3.5 w-3.5" strokeWidth={3} />}
          {state === 'active' && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
          {state === 'error' && <AlertTriangle className="h-3.5 w-3.5" />}
          {state === 'awaiting' && <HelpCircle className="h-3.5 w-3.5" />}
          {state === 'pending' && index + 1}
        </div>
        <span
          className="truncate rounded-full px-2 py-0.5 text-[10.5px] font-semibold"
          style={{ background: tone.pillBg, color: tone.pillFg }}
        >
          {status.label}
        </span>
      </div>

      <div className="text-[14px] font-semibold text-[var(--text)]">{stage.label}</div>
      <div className="mt-1 flex-1 text-[11.5px] leading-snug text-[var(--text-dim)]">{stage.hint}</div>

      {metric && (
        <div className="mt-2 flex items-center justify-between text-[11px]">
          <span className="text-[var(--text-dim)]">{isLocal ? 'Local' : 'Cost'}</span>
          <span className="font-mono font-medium text-[var(--text)]">
            {isLocal ? 'no charge' : formatCost(metric.cost)}
          </span>
        </div>
      )}

      <button
        type="button"
        disabled={!canRun}
        onClick={() => onRun(stage.key)}
        className="mt-3 flex items-center justify-center gap-1.5 rounded-lg border px-3 py-2 text-[12px] font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-40"
        style={
          highlighted
            ? { background: 'var(--accent)', borderColor: 'var(--accent)', color: '#fff' }
            : { background: 'transparent', borderColor: 'var(--border-strong)', color: 'var(--text-muted)' }
        }
      >
        {state === 'done' ? <RotateCcw className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
        {state === 'done' ? 'Re-run' : highlighted ? `Run ${stage.label}` : 'Run'}
      </button>
    </div>
  )
}

export default function PipelineStageGrid({ states, onRunStage, logs = [], disabled = false, backendSlot }) {
  const [collapsed, setCollapsed] = useState(false)
  const metrics = useMemo(() => stageMetrics(logs), [logs])
  const totalCost = useMemo(() => Object.values(metrics).reduce((sum, m) => sum + (m.cost || 0), 0), [metrics])
  const completedCount = states.filter((s) => s === 'done').length
  const nextIdx = states.findIndex((s) => s !== 'done')
  const nextLabel = nextIdx >= 0 ? STAGES[nextIdx].label : null

  return (
    <div className="card rounded-xl px-6 py-5">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] pb-4">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            aria-label={collapsed ? 'Expand pipeline' : 'Collapse pipeline'}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-[var(--border-strong)] text-[var(--text-muted)] transition-colors hover:text-[var(--text)]"
          >
            <ChevronDown className={`h-4 w-4 transition-transform ${collapsed ? '' : 'rotate-180'}`} />
          </button>
          <div>
            <div className="font-serif text-[17px] font-semibold text-[var(--text)]">Pipeline</div>
            <div className="mt-0.5 text-[11.5px] text-[var(--text-dim)]">
              {completedCount} of {STAGES.length} stages complete
              {nextLabel ? ` · ${nextLabel} is next` : ' · Pipeline complete'}
              {totalCost > 0 && ` · ${formatCost(totalCost)} spent so far`}
            </div>
          </div>
        </div>
        {backendSlot}
      </div>

      {!collapsed && (
        <div className="fade-up flex flex-col gap-3 md:flex-row md:flex-wrap">
          {STAGES.map((stage, i) => (
            <StageCard
              key={stage.key}
              index={i}
              stage={stage}
              state={states[i] || 'pending'}
              dependencyReady={i === 0 || states[i - 1] === 'done'}
              prevLabel={i > 0 ? STAGES[i - 1].label : ''}
              onRun={onRunStage}
              disabled={disabled}
              metric={metrics[stage.key]}
            />
          ))}
        </div>
      )}
    </div>
  )
}
