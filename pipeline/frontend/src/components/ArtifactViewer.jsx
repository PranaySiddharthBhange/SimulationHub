import {
  Check,
  ChartLine,
  ClipboardCheck,
  Copy,
  FileCode2,
  FileText,
  GitBranch,
  Loader2,
  Maximize2,
  RotateCcw,
  X,
  ZoomIn,
  ZoomOut,
} from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'
import mermaid from 'mermaid'
import { getArtifact } from '../api'

const TABS = [
  { key: 'understanding', label: 'Understanding', icon: FileText, kind: 'prose' },
  { key: 'diagram', label: 'Flow diagram', icon: GitBranch, kind: 'diagram' },
  { key: 'sysml', label: 'SysML v2', icon: FileCode2, kind: 'code' },
  { key: 'modelica', label: 'Modelica', icon: FileCode2, kind: 'code' },
  { key: 'validation', label: 'Validation', icon: ClipboardCheck, kind: 'validation' },
  { key: 'result', label: 'Result', icon: ChartLine, kind: 'result' },
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

function PlotModal({ projectId, plot, onClose }) {
  const [scale, setScale] = useState(1)
  const viewportRef = useRef(null)
  const dragRef = useRef(null)

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const onKeyDown = (event) => {
      if (event.key === 'Escape') onClose()
      if (event.key === '+' || event.key === '=') setScale((value) => Math.min(5, value + 0.25))
      if (event.key === '-') setScale((value) => Math.max(1, value - 0.25))
    }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [onClose])

  const changeScale = (nextScale) => {
    const viewport = viewportRef.current
    if (!viewport) {
      setScale(nextScale)
      return
    }
    const xRatio = (viewport.scrollLeft + viewport.clientWidth / 2) / viewport.scrollWidth
    const yRatio = (viewport.scrollTop + viewport.clientHeight / 2) / viewport.scrollHeight
    setScale(nextScale)
    requestAnimationFrame(() => {
      viewport.scrollLeft = xRatio * viewport.scrollWidth - viewport.clientWidth / 2
      viewport.scrollTop = yRatio * viewport.scrollHeight - viewport.clientHeight / 2
    })
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label={`Plot viewer: ${plot}`}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div className="flex h-[94vh] w-[96vw] max-w-[1800px] flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">
        <div className="flex shrink-0 items-center justify-between gap-4 border-b border-[var(--border)] bg-white px-4 py-3">
          <div className="min-w-0">
            <div className="text-[13px] font-semibold text-[var(--text)]">Simulation graph</div>
            <div className="font-mono truncate text-[11px] text-[var(--text-dim)]">{plot}</div>
          </div>
          <div className="flex shrink-0 items-center gap-1.5">
            <button
              type="button"
              onClick={() => changeScale(Math.max(1, scale - 0.25))}
              disabled={scale <= 1}
              className="rounded-lg border border-[var(--border)] p-2 text-[var(--text-muted)] hover:bg-[var(--bg-soft)] disabled:opacity-35"
              aria-label="Zoom out"
            >
              <ZoomOut className="h-4 w-4" />
            </button>
            <span className="w-14 text-center font-mono text-[11px] text-[var(--text-muted)]">
              {Math.round(scale * 100)}%
            </span>
            <button
              type="button"
              onClick={() => changeScale(Math.min(5, scale + 0.25))}
              disabled={scale >= 5}
              className="rounded-lg border border-[var(--border)] p-2 text-[var(--text-muted)] hover:bg-[var(--bg-soft)] disabled:opacity-35"
              aria-label="Zoom in"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => changeScale(1)}
              className="rounded-lg border border-[var(--border)] p-2 text-[var(--text-muted)] hover:bg-[var(--bg-soft)]"
              aria-label="Fit graph to window"
              title="Fit to window"
            >
              <RotateCcw className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={onClose}
              className="ml-2 inline-flex items-center gap-1.5 rounded-lg bg-[var(--text)] px-3 py-2 text-[12px] font-semibold text-white hover:opacity-85"
            >
              <X className="h-4 w-4" /> Close
            </button>
          </div>
        </div>
        <div
          ref={viewportRef}
          className="relative flex-1 cursor-grab overflow-auto bg-[#e8eaed] active:cursor-grabbing"
          onWheel={(event) => {
            event.preventDefault()
            changeScale(Math.max(1, Math.min(5, scale + (event.deltaY < 0 ? 0.25 : -0.25))))
          }}
          onDoubleClick={() => changeScale(scale === 1 ? 2 : 1)}
          onPointerDown={(event) => {
            if (event.button !== 0) return
            const viewport = viewportRef.current
            dragRef.current = {
              x: event.clientX,
              y: event.clientY,
              left: viewport.scrollLeft,
              top: viewport.scrollTop,
            }
            viewport.setPointerCapture(event.pointerId)
          }}
          onPointerMove={(event) => {
            if (!dragRef.current) return
            const viewport = viewportRef.current
            viewport.scrollLeft = dragRef.current.left - (event.clientX - dragRef.current.x)
            viewport.scrollTop = dragRef.current.top - (event.clientY - dragRef.current.y)
          }}
          onPointerUp={(event) => {
            dragRef.current = null
            if (viewportRef.current?.hasPointerCapture(event.pointerId)) {
              viewportRef.current.releasePointerCapture(event.pointerId)
            }
          }}
          onPointerCancel={() => {
            dragRef.current = null
          }}
        >
          <div
            className="flex items-center justify-center p-6"
            style={{ width: `${scale * 100}%`, height: `${scale * 100}%`, minWidth: '100%', minHeight: '100%' }}
          >
            <img
              src={`/api/projects/${projectId}/artifacts/result/plot/${plot}`}
              alt={plot}
              draggable={false}
              className="max-h-full max-w-full select-none object-contain shadow-lg"
            />
          </div>
        </div>
        <div className="shrink-0 border-t border-[var(--border)] bg-white px-4 py-2 text-center text-[11px] text-[var(--text-dim)]">
          Mouse wheel or +/ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã¢â‚¬Â¹ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ to zoom ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· drag to pan ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· double-click to toggle 200% ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· Esc to close
        </div>
      </div>
    </div>
  )
}

function ValidationView({ data }) {
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
    </div>
  )
}

function ResultView({ projectId, data }) {
  const [activePlot, setActivePlot] = useState(null)
  const plots = data?.plots || []
  if (plots.length === 0) return null
  return (
    <div className="fade-up px-5 py-4">
      <div className="mb-4">
        <div className="text-[13px] font-semibold text-[var(--text)]">Individual simulation graphs</div>
        <div className="mt-1 text-[11.5px] text-[var(--text-dim)]">
          Each changing result variable is plotted separately. Click any graph to open the zoomable viewer.
        </div>
      </div>
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {plots.map((plot) => (
          <button
            key={plot.filename}
            type="button"
            onClick={() => setActivePlot(plot.filename)}
            className="group overflow-hidden rounded-xl border border-[var(--border)] bg-white text-left shadow-sm transition-shadow hover:shadow-md"
          >
            <div className="flex items-center justify-between border-b border-[var(--border)] px-3 py-2">
              <span className="font-mono truncate text-[11px] text-[var(--text-muted)]">{plot.label}</span>
              <span className="inline-flex items-center gap-1 text-[10.5px] font-medium text-[var(--accent)]">
                <Maximize2 className="h-3 w-3" /> Open
              </span>
            </div>
            <img
              src={`/api/projects/${projectId}/artifacts/result/plot/${plot.filename}`}
              alt={plot.label}
              className="w-full transition-transform duration-200 group-hover:scale-[1.01]"
            />
          </button>
        ))}
      </div>
      {activePlot && <PlotModal projectId={projectId} plot={activePlot} onClose={() => setActivePlot(null)} />}
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

function MermaidView({ code }) {
  const containerRef = useRef(null)
  const reactId = useId()
  const renderIdRef = useRef(`system-flow-${reactId.replace(/:/g, "")}`)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setError(null)
    if (containerRef.current) containerRef.current.innerHTML = ''

    const render = async () => {
      try {
        mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'default' })
        await mermaid.parse(code)
        const result = await mermaid.render(renderIdRef.current, code)
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = result.svg
          const svg = containerRef.current.querySelector('svg')
          if (svg) {
            svg.removeAttribute('width')
            svg.style.maxWidth = 'none'
            svg.style.height = 'auto'
          }
        }
      } catch (renderError) {
        if (!cancelled) setError(renderError?.message || String(renderError))
      }
    }
    render()
    return () => {
      cancelled = true
      if (containerRef.current) containerRef.current.innerHTML = ''
    }
  }, [code])

  if (error) {
    return (
      <div className="fade-up space-y-3 px-5 py-4">
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-[12px] text-red-700">
          Mermaid could not render this diagram. The generated source is shown below so it can be corrected safely.
        </div>
        <pre className="overflow-auto rounded-lg bg-[var(--bg-soft)] p-4 font-mono text-[12px] leading-relaxed text-[var(--text)]">
          <code>{code}</code>
        </pre>
      </div>
    )
  }

  return (
    <div className="fade-up h-full overflow-auto bg-white px-5 py-6">
      <div ref={containerRef} className="min-w-max [&_svg]:mx-auto" aria-label="System flow diagram" />
    </div>
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
    setCache({})
    setModelicaFilename(null)
  }, [refreshToken])

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
            <Loader2 className="h-4 w-4 animate-spin" /> loadingÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¦
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
        {!loading && available[tab] && content && active.kind === 'diagram' && <MermaidView code={content} />}
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
          <ValidationView data={data} />
        )}
        {!loading && available[tab] && data && active.kind === 'result' && (
          <ResultView projectId={projectId} data={data} />
        )}
      </div>
    </div>
  )
}
