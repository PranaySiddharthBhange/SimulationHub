const CONFIG = {
  created: { label: 'Ready to run', color: 'var(--text-muted)', bg: 'var(--bg-soft)' },
  stage1_ready: { label: 'Extraction complete', color: 'var(--green)', bg: 'var(--green-soft)' },
  ready: { label: 'Stage complete', color: 'var(--green)', bg: 'var(--green-soft)' },
  running: { label: 'Running', color: 'var(--blue)', bg: 'var(--blue-soft)' },
  awaiting_input: { label: 'Needs your input', color: 'var(--amber)', bg: 'var(--amber-soft)' },
  done: { label: 'Complete', color: 'var(--green)', bg: 'var(--green-soft)' },
  error: { label: 'Failed', color: 'var(--red)', bg: 'var(--red-soft)' },
  interrupted: { label: 'Interrupted', color: 'var(--text-muted)', bg: 'var(--bg-soft)' },
}

export default function StatusPill({ status, size = 'md' }) {
  const c = CONFIG[status] || CONFIG.created
  const live = status === 'running' || status === 'awaiting_input'
  const pad = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-3 py-1 text-xs'
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full font-medium tracking-wide ${pad}`}
      style={{ color: c.color, background: c.bg, border: `1px solid ${c.color}2a` }}
    >
      <span className="relative inline-flex h-1.5 w-1.5 rounded-full" style={{ color: c.color, background: c.color }}>
        {live && <span className="pulse-dot absolute inset-0" />}
      </span>
      {c.label}
    </span>
  )
}
