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
import { useEffect, useRef, useState } from 'react'

function timeOf(ts) {
  try {
    return new Date(ts).toLocaleTimeString([], { hour12: false })
  } catch {
    return ''
  }
}

function describe(e) {
  switch (e.event) {
    case 'run_started':
      return { icon: PlayCircle, color: 'var(--accent)', title: 'Pipeline run started' }
    case 'stage_start':
      return { icon: PlayCircle, color: 'var(--blue)', title: `Started — ${e.name}` }
    case 'stage_end':
      return e.ok
        ? { icon: CheckCircle2, color: 'var(--green)', title: `${e.name}`, sub: `done in ${e.elapsed_seconds}s` }
        : {
            icon: XCircle,
            color: 'var(--red)',
            title: `${e.name} failed`,
            sub: `${e.error_type}: ${e.error_message}`,
          }
    case 'llm_call':
      return {
        icon: Brain,
        color: 'var(--violet)',
        title: `${e.model} → ${e.schema}`,
        sub: `stage ${e.stage} · ${e.backend}${e.cumulative_spent_usd ? ` · $${e.cumulative_spent_usd}` : ''}`,
      }
    case 'validation_attempt':
      if (e.status === 'PASSED')
        return { icon: CheckCircle2, color: 'var(--green)', title: `${e.tool} passed`, sub: `attempt ${e.attempt}` }
      if (e.status === 'UNAVAILABLE')
        return { icon: AlertCircle, color: 'var(--text-dim)', title: `${e.tool} unavailable`, sub: e.detail }
      return {
        icon: AlertCircle,
        color: 'var(--amber)',
        title: `${e.tool} found ${e.issue_count ?? e.error_count ?? 0} issue(s)`,
        sub: `attempt ${e.attempt}`,
        detail: e.issues || e.errors,
      }
    case 'clarification_requested':
      return {
        icon: HelpCircle,
        color: 'var(--amber)',
        title: `Stage 2 has ${e.questions?.length ?? 0} question(s) for you`,
        sub: 'waiting on human review',
      }
    case 'clarification_answered':
      return { icon: MessageSquareText, color: 'var(--accent)', title: 'Answers submitted', sub: 'resuming Stage 2' }
    default:
      return { icon: ChevronRight, color: 'var(--text-dim)', title: e.event }
  }
}

function LogLine({ e }) {
  const [open, setOpen] = useState(false)
  const { icon: Icon, color, title, sub, detail } = describe(e)
  return (
    <div className="fade-up group px-3 py-1.5">
      <button
        type="button"
        className="flex w-full items-start gap-2.5 text-left"
        onClick={() => detail && setOpen((o) => !o)}
      >
        <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0" style={{ color }} />
        <span className="shrink-0 font-mono text-[11px] text-[var(--text-dim)]">{timeOf(e.ts)}</span>
        <span className="min-w-0 flex-1">
          <span className="text-[12.5px] text-[var(--text)]">{title}</span>
          {sub && <span className="ml-2 text-[11.5px] text-[var(--text-muted)]">{sub}</span>}
        </span>
        {detail && (
          <ChevronRight
            className={`h-3.5 w-3.5 shrink-0 text-[var(--text-dim)] transition-transform ${open ? 'rotate-90' : ''}`}
          />
        )}
      </button>
      {open && detail && (
        <pre className="font-mono ml-6 mt-1.5 max-h-40 overflow-auto rounded-lg border border-[var(--border)] bg-[var(--bg-soft)] p-2 text-[11px] whitespace-pre-wrap text-[var(--text-muted)]">
          {detail}
        </pre>
      )}
    </div>
  )
}

export default function LogPanel({ logs }) {
  const scrollRef = useRef(null)
  const pinnedRef = useRef(true)

  useEffect(() => {
    const el = scrollRef.current
    if (el && pinnedRef.current) el.scrollTop = el.scrollHeight
  }, [logs])

  return (
    <div className="card flex h-full flex-col overflow-hidden rounded-xl">
      <div className="flex items-center justify-between border-b border-[var(--border)] bg-[var(--bg-soft)] px-4 py-2.5">
        <div className="flex items-center gap-2">
          <span className="text-[12.5px] font-semibold text-[var(--text)]">Activity log</span>
          <span className="font-mono text-[10.5px] text-[var(--text-dim)]">run.jsonl</span>
        </div>
        <span className="font-mono text-[11px] text-[var(--text-dim)]">{logs.length} events</span>
      </div>
      <div
        ref={scrollRef}
        onScroll={(ev) => {
          const el = ev.currentTarget
          pinnedRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 40
        }}
        className="flex-1 divide-y divide-[var(--border)]/60 overflow-y-auto"
      >
        {logs.length === 0 && (
          <div className="flex h-full items-center justify-center text-sm text-[var(--text-dim)]">
            Logs will appear here once the run starts.
          </div>
        )}
        {logs.map((e, i) => (
          <LogLine key={i} e={e} />
        ))}
      </div>
    </div>
  )
}
