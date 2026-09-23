import { AlertTriangle, Check, HelpCircle, Loader2, Play, RotateCcw } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { STAGES } from '../constants'

const STYLES = {
  pending: { ring: 'var(--border-strong)', fg: 'var(--text-dim)', bg: 'transparent' },
  active: { ring: 'var(--accent)', fg: '#fff', bg: 'var(--accent)' },
  awaiting: { ring: 'var(--amber)', fg: '#fff', bg: 'var(--amber)' },
  done: { ring: 'var(--green)', fg: '#fff', bg: 'var(--green)' },
  error: { ring: 'var(--red)', fg: '#fff', bg: 'var(--red)' },
}

function Icon({ state }) {
  if (state === 'active') return <Loader2 className="h-4 w-4 animate-spin" />
  if (state === 'awaiting') return <HelpCircle className="h-4 w-4" />
  if (state === 'done') return <Check className="h-4 w-4" strokeWidth={3} />
  if (state === 'error') return <AlertTriangle className="h-4 w-4" />
  return <span className="h-1.5 w-1.5 rounded-full bg-current" />
}

function stageKeyFromName(name = '') {
  const value = name.toLowerCase()
  if (value.startsWith('merge')) return 'merge'
  if (value.startsWith('clarif')) return 'clarify'
  if (value.includes('stage 1:')) return 'stage_1'
  if (value.includes('stage 2:')) return 'stage_2'
  if (value.includes('stage 3:')) return 'stage_3'
  if (value.includes('stage 4:')) return 'stage_4'
  return null
}

function stageMetrics(logs) {
  const result = {}
  let currentStage = null
  for (const event of logs) {
    if (event.event === 'stage_start') currentStage = stageKeyFromName(event.name)
    if (event.event !== 'llm_call' || !currentStage) continue
    result[currentStage] = {
      backend: event.backend,
      model: event.model,
      cost: Number(event.cumulative_spent_usd || 0),
      inputTokens: Number(event.input_tokens || 0),
      outputTokens: Number(event.output_tokens || 0),
    }
  }
  return result
}

function StageIcon({ state, style, stage, metric, edge }) {
  const [showDetails, setShowDetails] = useState(false)
  const timerRef = useRef(null)

  useEffect(() => () => clearTimeout(timerRef.current), [])

  const beginHover = () => {
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => setShowDetails(true), 5000)
  }
  const endHover = () => {
    clearTimeout(timerRef.current)
    setShowDetails(false)
  }
  const position = edge === 'first' ? 'left-0' : edge === 'last' ? 'right-0' : 'left-1/2 -translate-x-1/2'
  const isLocal = metric?.backend === 'ollama'

  return (
    <div className="relative" onMouseEnter={beginHover} onMouseLeave={endHover} onFocus={beginHover} onBlur={endHover}>
      <div
        tabIndex={0}
        aria-label={`${stage.label} stage details`}
        className="flex h-9 w-9 items-center justify-center rounded-full transition-colors duration-300"
        style={{
          background: style.bg,
          color: style.fg,
          border: `1.5px solid ${style.ring}`,
        }}
      >
        <Icon state={state} />
      </div>
      {showDetails && (
        <div className={`absolute bottom-full z-40 mb-3 w-60 rounded-xl border border-[var(--border)] bg-[var(--panel)] p-3 text-left shadow-xl ${position}`}>
          <div className="text-[12px] font-semibold text-[var(--text)]">{stage.label}</div>
          {metric ? (
            <div className="mt-2 space-y-1.5 text-[11px] text-[var(--text-muted)]">
              <div className="flex justify-between gap-3"><span>Model</span><span className="font-mono text-right text-[var(--text)]">{metric.model}</span></div>
              <div className="flex justify-between gap-3"><span>Execution</span><span className="text-[var(--text)]">{isLocal ? 'Local' : 'Cloud'}</span></div>
              <div className="flex justify-between gap-3"><span>Estimated API cost</span><span className="font-mono text-[var(--text)]">${metric.cost.toFixed(6)}</span></div>
              {(metric.inputTokens > 0 || metric.outputTokens > 0) && (
                <div className="border-t border-[var(--border)] pt-1.5 text-[10px] text-[var(--text-dim)]">
                  {metric.inputTokens.toLocaleString()} input Â· {metric.outputTokens.toLocaleString()} output tokens
                </div>
              )}
              {isLocal && <div className="text-[10px] text-[var(--text-dim)]">Local inference has no API charge.</div>}
            </div>
          ) : (
            <div className="mt-2 text-[11px] text-[var(--text-dim)]">No model call has been recorded for this stage yet.</div>
          )}
        </div>
      )}
    </div>
  )
}

export default function PipelineStepper({ states, onRunStage, logs = [], disabled = false }) {
  const metrics = useMemo(() => stageMetrics(logs), [logs])
  return (
    <div className="flex items-start">
      {STAGES.map((stage, i) => {
        const state = states[i] || 'pending'
        const style = STYLES[state]
        const isLast = i === STAGES.length - 1
        const dependencyReady = i === 0 || states[i - 1] === 'done'
        const canRun = !disabled && state !== 'active' && dependencyReady
        return (
          <div key={stage.key} className={`flex items-center ${isLast ? '' : 'flex-1'}`}>
            <div className="flex flex-col items-center gap-2 px-1">
              <StageIcon
                state={state}
                style={style}
                stage={stage}
                metric={metrics[stage.key]}
                edge={i === 0 ? 'first' : isLast ? 'last' : 'middle'}
              />
              <div className="text-center">
                <div
                  className="text-[13px] font-semibold"
                  style={{ color: state === 'pending' ? 'var(--text-dim)' : 'var(--text)' }}
                >
                  {stage.label}
                </div>
                <div className="hidden text-[11px] text-[var(--text-dim)] sm:block">{stage.hint}</div>
                <button
                  type="button"
                  disabled={!canRun}
                  onClick={() => onRunStage(stage.key)}
                  className="mt-2 inline-flex items-center gap-1 rounded-md border border-[var(--border-strong)] px-2 py-1 text-[10.5px] font-medium text-[var(--text-muted)] transition-colors hover:border-[var(--accent)] hover:text-[var(--accent)] disabled:cursor-not-allowed disabled:opacity-35"
                >
                  {state === 'done' ? <RotateCcw className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                  {state === 'done' ? 'Re-run' : 'Run'}
                </button>
              </div>
            </div>
            {!isLast && (
              <div
                className="mx-2 mt-[-22px] h-[2px] flex-1 rounded-full transition-colors duration-500"
                style={{ background: state === 'done' ? 'var(--green)' : 'var(--border)' }}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
