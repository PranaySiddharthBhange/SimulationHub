import {
  AlertCircle,
  Brain,
  CheckCircle2,
  ChevronRight,
  HelpCircle,
  MessageSquareText,
  PlayCircle,
  XCircle,
} from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'

function elapsedSince(prevTs, ts) {
  if (!prevTs || !ts) return null
  const deltaMs = new Date(ts) - new Date(prevTs)
  if (!Number.isFinite(deltaMs) || deltaMs < 0) return null
  return deltaMs / 1000
}

function formatElapsed(seconds) {
  if (seconds == null) return null
  if (seconds < 1) return '<1s'
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  const minutes = Math.floor(seconds / 60)
  const secs = Math.round(seconds % 60)
  return `${minutes}m ${secs}s`
}

function timeOf(ts) {
  try {
    return new Date(ts).toLocaleTimeString([], { hour12: false })
  } catch {
    return null
  }
}

function describe(e) {
  switch (e.event) {
    case 'run_started':
      return { icon: PlayCircle, color: 'var(--accent)', title: 'Pipeline run started' }
    case 'stage_start':
      return { icon: PlayCircle, color: 'var(--blue)', title: `Started — ${e.name}`, meta: [{ label: 'Stage', value: e.name }] }
    case 'stage_end':
      return e.ok
        ? {
            icon: CheckCircle2,
            color: 'var(--green)',
            title: `${e.name}`,
            meta: [{ label: 'Duration', value: `${e.elapsed_seconds}s` }],
          }
        : {
            icon: XCircle,
            color: 'var(--red)',
            title: `${e.name} failed`,
            meta: [
              { label: 'Error type', value: e.error_type },
              { label: 'Message', value: e.error_message },
            ],
          }
    case 'llm_call':
      return {
        icon: Brain,
        color: 'var(--violet)',
        title: `${e.model} → ${e.schema}`,
        meta: [
          { label: 'Stage', value: e.stage },
          { label: 'Backend', value: e.backend },
          { label: 'Input tokens', value: e.input_tokens != null ? e.input_tokens.toLocaleString() : null },
          { label: 'Output tokens', value: e.output_tokens != null ? e.output_tokens.toLocaleString() : null },
          { label: 'Call cost', value: e.call_spent_usd != null ? `$${e.call_spent_usd}` : null },
          { label: 'Cumulative cost', value: e.cumulative_spent_usd != null ? `$${e.cumulative_spent_usd}` : null },
        ],
      }
    case 'validation_attempt':
      if (e.status === 'PASSED')
        return {
          icon: CheckCircle2,
          color: 'var(--green)',
          title: `${e.tool} passed`,
          meta: [{ label: 'Attempt', value: e.attempt }],
        }
      if (e.status === 'UNAVAILABLE')
        return {
          icon: AlertCircle,
          color: 'var(--text-dim)',
          title: `${e.tool} unavailable`,
          meta: [{ label: 'Detail', value: e.detail }],
        }
      return {
        icon: AlertCircle,
        color: 'var(--amber)',
        title: `${e.tool} found ${e.issue_count ?? e.error_count ?? 0} issue(s)`,
        meta: [{ label: 'Attempt', value: e.attempt }],
        detail: e.issues || e.errors,
      }
    case 'validation_report':
      return e.verdict === 'invalid'
        ? {
            icon: XCircle,
            color: 'var(--red)',
            title: 'Validation verdict: Invalid',
            meta: [{ label: 'Issues', value: e.issue_count ?? 0 }],
          }
        : {
            icon: CheckCircle2,
            color: 'var(--green)',
            title: `Validation verdict: ${e.verdict || 'complete'}`,
            meta: [{ label: 'Issues', value: e.issue_count ?? 0 }],
          }
    case 'clarification_requested':
      return {
        icon: HelpCircle,
        color: 'var(--amber)',
        title: `Stage 2 has ${e.questions?.length ?? 0} question(s) for you`,
        meta: [{ label: 'Status', value: 'waiting on human review' }],
        detail: e.questions,
      }
    case 'clarification_answered':
      return {
        icon: MessageSquareText,
        color: 'var(--accent)',
        title: 'User input submitted',
        meta: [{ label: 'Answers', value: Object.keys(e.answers || {}).length }],
        detail: e.answers,
      }
    default:
      return { icon: ChevronRight, color: 'var(--text-dim)', title: e.event }
  }
}

function formatDetail(detail) {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item, index) => {
        if (typeof item === 'string') return `${index + 1}. ${item}`
        if (item?.question) {
          const options = item.options?.length ? `\n   Options: ${item.options.join(' | ')}` : ''
          return `${index + 1}. ${item.question}${options}`
        }
        return `${index + 1}. ${JSON.stringify(item, null, 2)}`
      })
      .join('\n\n')
  }
  if (detail && typeof detail === 'object') {
    return Object.entries(detail)
      .map(([key, value]) => `${key}\n${typeof value === 'object' && value !== null ? JSON.stringify(value, null, 2) : String(value)}`)
      .join('\n\n')
  }
  return String(detail ?? '')
}

function LogLine({ e, elapsed }) {
  const [open, setOpen] = useState(false)
  const { icon: Icon, color, title, meta, detail } = describe(e)
  const rows = [
    { label: 'Time', value: timeOf(e.ts) },
    { label: 'Took', value: elapsed },
    ...(meta || []),
  ].filter((row) => row.value != null && row.value !== '')

  return (
    <div className="fade-up group px-3 py-1.5">
      <button
        type="button"
        className="flex w-full items-center gap-2.5 text-left"
        onClick={() => setOpen((o) => !o)}
      >
        <Icon className="h-3.5 w-3.5 shrink-0" style={{ color }} />
        <span className="min-w-0 flex-1 truncate text-[12.5px] text-[var(--text)]">{title}</span>
      </button>
      {open && (
        <div className="ml-6 mt-1.5 space-y-2">
          {rows.length > 0 && (
            <dl className="grid grid-cols-[max-content_1fr] gap-x-3 gap-y-1 text-[11.5px]">
              {rows.map((row) => (
                <div key={row.label} className="contents">
                  <dt className="text-[var(--text-dim)]">{row.label}</dt>
                  <dd className="font-mono min-w-0 truncate text-[var(--text-muted)]">{row.value}</dd>
                </div>
              ))}
            </dl>
          )}
          {detail && (
            <pre className="font-mono max-h-40 overflow-auto rounded-lg border border-[var(--border)] bg-[var(--bg-soft)] p-2 text-[11px] whitespace-pre-wrap text-[var(--text-muted)]">
              {formatDetail(detail)}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}

export default function LogPanel({ logs }) {
  const scrollRef = useRef(null)
  const withElapsed = useMemo(
    () =>
      logs.map((e, i) => ({
        e,
        elapsed: formatElapsed(i > 0 ? elapsedSince(logs[i - 1].ts, e.ts) : null),
      })),
    [logs],
  )
  const newestFirst = useMemo(() => [...withElapsed].reverse(), [withElapsed])

  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTo({ top: 0, behavior: 'smooth' })
  }, [logs])

  return (
    <div className="card flex h-full flex-col overflow-hidden rounded-xl">
      <div className="flex items-center justify-between border-b border-[var(--border)] bg-[var(--bg-soft)] px-4 py-2.5">
        <div className="flex items-center gap-2">
          <span className="text-[12.5px] font-semibold text-[var(--text)]">Activity log</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-[11px] text-[var(--text-dim)]">{logs.length} events</span>
        </div>
      </div>
      <div
        ref={scrollRef}
        className="flex-1 divide-y divide-[var(--border)]/60 overflow-y-auto"
      >
        {logs.length === 0 && (
          <div className="flex h-full items-center justify-center text-sm text-[var(--text-dim)]">
            Logs will appear here once the run starts.
          </div>
        )}
        {newestFirst.map(({ e, elapsed }, i) => (
          <LogLine key={`${e.ts || 'event'}-${e.event || 'log'}-${logs.length - i}`} e={e} elapsed={elapsed} />
        ))}
      </div>
    </div>
  )
}
