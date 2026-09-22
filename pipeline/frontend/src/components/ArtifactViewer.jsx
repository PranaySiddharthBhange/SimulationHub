import { Check, ClipboardCheck, Copy, FileCode2, FileText, Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getArtifact } from '../api'

const TABS = [
  { key: 'understanding', label: 'Understanding', icon: FileText, kind: 'prose' },
  { key: 'sysml', label: 'SysML v2', icon: FileCode2, kind: 'code' },
  { key: 'modelica', label: 'Modelica', icon: FileCode2, kind: 'code' },
  { key: 'validation', label: 'Validation', icon: ClipboardCheck, kind: 'validation' },
]

const VERDICT_STYLE = {
  valid: { bg: 'var(--green-soft, rgba(34,197,94,0.15))', fg: 'var(--green)', label: 'Valid' },
  partially_valid: { bg: 'rgba(234,179,8,0.15)', fg: '#eab308', label: 'Partially valid' },
  invalid: { bg: 'rgba(239,68,68,0.15)', fg: '#ef4444', label: 'Invalid' },
}

function ReportSection({ title, items }) {
  if (!items || items.length === 0) return null
  return (
    <div className="mt-4">
      <div className="text-[11px] font-semibold uppercase tracking-wide text-[var(--text-dim)]">{title}</div>
      <ul className="mt-1.5 list-disc space-y-1 pl-5 text-[13px] leading-relaxed text-[var(--text)]">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  )
}

function ValidationView({ projectId, data }) {
  const report = data?.report
  if (!report) return null
  const style = VERDICT_STYLE[report.verdict] || VERDICT_STYLE.partially_valid
  return (
    <div className="fade-up px-5 py-4">
      <span
        className="inline-flex items-center rounded-full px-3 py-1 text-[12px] font-semibold"
        style={{ background: style.bg, color: style.fg }}
      >
        {style.label}
      </span>
      <p className="mt-3 text-[13.5px] leading-relaxed text-[var(--text)]">{report.summary}</p>
      <ReportSection title="Issues" items={report.issues} />
      <ReportSection title="Assumptions" items={report.assumptions} />
      <ReportSection title="Root causes" items={report.root_causes} />
      {data.plots && data.plots.length > 0 && (
        <div className="mt-5">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[var(--text-dim)]">
            Real simulated trajectory
          </div>
          <div className="mt-2 grid grid-cols-1 gap-3">
            {data.plots.map((p) => (
              <img
                key={p}
                src={`/api/projects/${projectId}/artifacts/validation/plot/${p}`}
                alt={p}
                className="w-full rounded-lg border border-[var(--border)]"
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  if (!text) return null
  return (
    <button
      type="button"
      onClick={() => {
        navigator.clipboard.writeText(text).then(() => {
          setCopied(true)
          setTimeout(() => setCopied(false), 1200)
        })
      }}
      className="flex shrink-0 items-center gap-1.5 rounded-md border border-[var(--border-strong)] px-2.5 py-1 text-[11px] text-[var(--text-muted)] transition-colors hover:text-[var(--text)]"
    >
      {copied ? <Check className="h-3 w-3 text-[var(--green)]" /> : <Copy className="h-3 w-3" />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

export default function ArtifactViewer({ projectId, available, refreshToken }) {
  const [tab, setTab] = useState('understanding')
  const [cache, setCache] = useState({})
  const [loading, setLoading] = useState(false)
  const [modelicaFilename, setModelicaFilename] = useState(null)

  useEffect(() => {
    setCache({})
    setModelicaFilename(null)
  }, [projectId])

  useEffect(() => {
    if (!available[tab] || cache[tab]) return
    let cancelled = false
    setLoading(true)
    getArtifact(projectId, tab)
      .then((data) => {
        if (!cancelled && data) setCache((c) => ({ ...c, [tab]: data }))
      })
      .finally(() => !cancelled && setLoading(false))
    return () => {
      cancelled = true
    }
  }, [projectId, tab, available[tab], refreshToken])

  const active = TABS.find((t) => t.key === tab)
  const data = cache[tab]
  const defaultModelicaFile = data?.files?.find((file) => file.role === 'system') || data?.files?.[0]
  const selectedModelicaFile =
    tab === 'modelica'
      ? data?.files?.find((file) => file.filename === modelicaFilename) || defaultModelicaFile
      : null
  const content = selectedModelicaFile?.content || data?.content
  const displayedFilename = selectedModelicaFile?.filename || data?.filename

  return (
    <div className="card flex h-full flex-col overflow-hidden rounded-xl">
      <div className="flex items-center justify-between gap-2 border-b border-[var(--border)] bg-[var(--bg-soft)] px-3 py-2">
        <div className="flex shrink-0 gap-1">
          {TABS.map((t) => {
            const isActive = t.key === tab
            const isAvailable = available[t.key]
            return (
              <button
                key={t.key}
                type="button"
                onClick={() => setTab(t.key)}
                className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[12.5px] font-medium transition-colors"
                style={{
                  background: isActive ? 'var(--panel-2)' : 'transparent',
                  color: isActive ? 'var(--text)' : 'var(--text-dim)',
                }}
              >
                <t.icon className="h-3.5 w-3.5" />
                {t.label}
                {isAvailable && <span className="h-1.5 w-1.5 rounded-full bg-[var(--green)]" />}
              </button>
            )
          })}
        </div>
        <div className="flex min-w-0 items-center gap-2">
          {displayedFilename && (
            <span className="font-mono min-w-0 truncate text-[11px] text-[var(--text-dim)]">{displayedFilename}</span>
          )}
          <CopyButton text={content} />
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        {loading && (
          <div className="flex h-full items-center justify-center gap-2 text-sm text-[var(--text-dim)]">
            <Loader2 className="h-4 w-4 animate-spin" /> loading…
          </div>
        )}
        {!loading && !available[tab] && (
          <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-[var(--text-dim)]">
            <active.icon className="h-6 w-6 opacity-40" />
            <span className="text-[13px]">Not generated yet</span>
          </div>
        )}
        {!loading && available[tab] && content && active.kind === 'prose' && (
          <div className="fade-up whitespace-pre-wrap px-5 py-4 text-[13.5px] leading-relaxed text-[var(--text)]">
            {content}
          </div>
        )}
        {!loading && available[tab] && content && active.kind === 'code' && (
          <div className="fade-up">
            {tab === 'modelica' && data?.files?.length > 1 && (
              <div className="flex flex-wrap gap-1.5 border-b border-[var(--border)] px-4 py-2.5">
                {data.files.map((file) => (
                  <button
                    key={file.filename}
                    type="button"
                    onClick={() => setModelicaFilename(file.filename)}
                    className="rounded-md border px-2.5 py-1 font-mono text-[11px] transition-colors"
                    style={{
                      borderColor:
                        file.filename === selectedModelicaFile?.filename ? 'var(--accent)' : 'var(--border)',
                      color:
                        file.filename === selectedModelicaFile?.filename ? 'var(--accent)' : 'var(--text-dim)',
                    }}
                  >
                    {file.filename}
                  </button>
                ))}
              </div>
            )}
            <pre className="font-mono px-5 py-4 text-[12.5px] leading-relaxed text-[var(--text)]">
              <code>{content}</code>
            </pre>
          </div>
        )}
        {!loading && available[tab] && data && active.kind === 'validation' && (
          <ValidationView projectId={projectId} data={data} />
        )}
      </div>
    </div>
  )
}
