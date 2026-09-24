import {
  Check,
  ChartLine,
  ChevronsLeft,
  ChevronsRight,
  ClipboardCheck,
  Copy,
  FileCode2,
  FileText,
  FolderTree,
  GitBranch,
  HelpCircle,
  Loader2,
  Maximize2,
  RotateCcw,
  X,
  ZoomIn,
  ZoomOut,
} from 'lucide-react'
import { useCallback, useEffect, useId, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import mermaid from 'mermaid'
import { getArtifact } from '../api'
import { useZoomPan } from '../hooks/useZoomPan'
import CodeBlock, { languageForFilename } from './CodeBlock'
import FileBrowser from './FileBrowser'
import MarkdownView from './MarkdownView'

const TABS = [
  { key: 'files', label: 'Files', icon: FolderTree, kind: 'files', ready: 'Source uploads', locked: 'Source uploads' },
  { key: 'understanding', label: 'Understanding', icon: FileText, kind: 'markdown', ready: 'From Read', locked: 'Unlocks at Read' },
  { key: 'clarified', label: 'Questions', icon: HelpCircle, kind: 'clarifications', ready: 'Answers on record', locked: 'Unlocks at Confirm' },
  { key: 'diagram', label: 'Flow diagram', icon: GitBranch, kind: 'diagram', ready: 'System flow', locked: 'Unlocks at Combine' },
  { key: 'sysml', label: 'SysML v2', icon: FileCode2, kind: 'code', ready: 'Generated model', locked: 'Unlocks at Design' },
  { key: 'modelica', label: 'Modelica', icon: FileCode2, kind: 'code', ready: 'Compiled bundle', locked: 'Unlocks at Build' },
  { key: 'result', label: 'Result', icon: ChartLine, kind: 'result', ready: 'Simulation plots', locked: 'Unlocks at Build' },
  { key: 'validation', label: 'Validation', icon: ClipboardCheck, kind: 'validation', ready: 'Independent review', locked: 'Unlocks at Verify' },
]

// The file browser reads the project folder directly, so it has nothing to wait
// for and is never "not generated yet" the way a stage artifact is.
const ALWAYS_AVAILABLE = new Set(['files'])

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
  const { scale, min, max, step, viewportRef, changeScale, handlers } = useZoomPan({ min: 1, max: 5, step: 0.25 })

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const onKeyDown = (event) => {
      if (event.key === 'Escape') onClose()
      if (event.key === '+' || event.key === '=') changeScale(scale + step)
      if (event.key === '-') changeScale(scale - step)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [onClose, scale, step, changeScale])

  return createPortal(
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
              onClick={() => changeScale(scale - step)}
              disabled={scale <= min}
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
              onClick={() => changeScale(scale + step)}
              disabled={scale >= max}
              className="rounded-lg border border-[var(--border)] p-2 text-[var(--text-muted)] hover:bg-[var(--bg-soft)] disabled:opacity-35"
              aria-label="Zoom in"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => changeScale(min)}
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
          {...handlers}
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
      </div>
    </div>,
    document.body,
  )
}

const CHECK_STYLE = {
  pass: { fg: 'var(--green)', label: 'pass' },
  fail: { fg: '#ef4444', label: 'fail' },
  not_evaluable: { fg: '#eab308', label: 'not evaluable' },
}

// Every acceptance check, passes included: a run is easy to read as broadly
// working when only its failures are listed, and the count is what says how
// much of the brief the trajectory actually demonstrated.
function CheckResults({ items }) {
  if (!items || items.length === 0) return null
  const passed = items.filter((i) => i.outcome === 'pass').length
  return (
    <div className="mt-4">
      <div className="text-[11px] font-semibold uppercase tracking-wide text-[var(--text-dim)]">
        Acceptance checks — {passed}/{items.length} passed
      </div>
      <ul className="mt-1.5 space-y-1.5">
        {items.map((item, i) => {
          const style = CHECK_STYLE[item.outcome] || CHECK_STYLE.not_evaluable
          return (
            <li key={i} className="text-[13px] leading-relaxed text-[var(--text)]">
              <span className="font-semibold" style={{ color: style.fg }}>
                {style.label}
              </span>
              <span className="ml-2">{item.name}</span>
              {item.expression && (
                <code className="ml-2 rounded bg-[var(--surface-2,rgba(127,127,127,0.12))] px-1 py-0.5 text-[12px]">
                  {item.expression}
                </code>
              )}
              {item.observed && (
                <div className="mt-0.5 pl-1 text-[12.5px] text-[var(--text-dim)]">{item.observed}</div>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}

const OUTCOME_STYLE = {
  confirmed: { label: 'Confirmed suggestion', fg: 'var(--green)', bg: '#edf3ec' },
  changed_by_human: { label: 'Overridden', fg: 'var(--amber)', bg: '#faf1de' },
  carried_over: { label: 'Carried over', fg: 'var(--blue)', bg: '#eaf1f4' },
  answered: { label: 'Answered', fg: 'var(--green)', bg: '#edf3ec' },
  unanswered: { label: 'Not answered', fg: 'var(--red)', bg: '#f8eae7' },
}

// Confirm (Merge's clarify pause) writes every question it raises to
// clarified_answers.json -- the artifact `data.decisions` below comes from.
// Design (Stage 2) can raise its OWN follow-up questions on the first SysML
// draft, but never persists them anywhere: they only ever exist as
// `clarification_requested` / `clarification_answered` events in the run
// log (see reasoner_pipeline.py `execute_reasoner_stage_2`), so they have to
// be recovered from the same `logs` the Activity panel already streams.
function stage2Decisions(logs = []) {
  const decisions = []
  let pending = null
  for (const event of logs) {
    if (event.event === 'clarification_requested' && event.stage === 2) {
      pending = event.questions || []
    } else if (event.event === 'clarification_answered' && event.stage === 2 && pending) {
      const answers = event.answers || {}
      for (const q of pending) {
        const given = (answers[q.id] || '').trim()
        const suggested = (q.suggested_value || '').trim()
        const outcome = !given ? 'unanswered' : !suggested ? 'answered' : given === suggested ? 'confirmed' : 'changed_by_human'
        decisions.push({ id: q.id, question: q.question, suggested: q.suggested_value, answer: given, outcome, origin: 'Design' })
      }
      pending = null
    }
  }
  if (pending) {
    for (const q of pending) {
      decisions.push({ id: q.id, question: q.question, suggested: q.suggested_value, answer: '', outcome: 'unanswered', origin: 'Design' })
    }
  }
  return decisions
}

function ClarificationsView({ data, logs }) {
  const confirmDecisions = (data?.decisions || []).map((d) => ({ ...d, suggested: d.merge_suggested, origin: 'Confirm' }))
  const decisions = [...confirmDecisions, ...stage2Decisions(logs)]
  if (decisions.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-[var(--text-dim)]">
        <HelpCircle className="h-6 w-6 opacity-40" />
        <span className="text-[13px]">No open questions were raised for this brief.</span>
      </div>
    )
  }
  return (
    <div className="fade-up flex flex-col gap-3 px-5 py-4">
      {decisions.map((d, i) => {
        const style = OUTCOME_STYLE[d.outcome] || OUTCOME_STYLE.answered
        const showSuggested = d.suggested && d.suggested !== d.answer
        return (
          <div key={d.id || i} className="rounded-xl border border-[var(--border)] px-4 py-3">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <span className="mr-2 rounded-full bg-[var(--bg-soft)] px-1.5 py-0.5 text-[10px] font-semibold text-[var(--text-dim)]">
                  {d.origin}
                </span>
                <span className="text-[13px] font-medium text-[var(--text)]">{d.question}</span>
              </div>
              <span
                className="shrink-0 rounded-full px-2 py-0.5 text-[10.5px] font-semibold"
                style={{ background: style.bg, color: style.fg }}
              >
                {style.label}
              </span>
            </div>
            <div className="mt-2 text-[12.5px] text-[var(--text-muted)]">
              <span className="text-[var(--text-dim)]">Answer — </span>
              <span className="text-[var(--text)]">{d.answer || '—'}</span>
            </div>
            {showSuggested && (
              <div className="mt-1 text-[11.5px] text-[var(--text-dim)]">
                Suggested: <span className="line-through">{d.suggested}</span>
              </div>
            )}
          </div>
        )
      })}
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
      <CheckResults items={report.check_results} />
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

// Injects rendered Mermaid SVG markup and resizes it by setting real pixel
// width/height (derived from its own viewBox), not a CSS transform: a
// transform only repaints the element bigger/smaller, it does not grow the
// scrollable-overflow area of an `overflow-auto` ancestor in this layout, so
// wheel-zooming in never gave the viewport anything to actually scroll or
// drag-pan through. Real layout sizing does.
function SvgCanvas({ svg, scale = 1, onSize }) {
  const ref = useRef(null)
  const naturalSizeRef = useRef(null)

  useEffect(() => {
    if (!ref.current) return
    ref.current.innerHTML = svg || ''
    const svgEl = ref.current.querySelector('svg')
    if (!svgEl) return
    const box = svgEl.viewBox?.baseVal
    const natural = box?.width ? { width: box.width, height: box.height } : svgEl.getBBox()
    naturalSizeRef.current = natural.width && natural.height ? natural : null
    if (naturalSizeRef.current) {
      svgEl.style.width = `${naturalSizeRef.current.width * scale}px`
      svgEl.style.height = `${naturalSizeRef.current.height * scale}px`
      onSize?.(naturalSizeRef.current)
    }
  }, [svg]) // eslint-disable-line react-hooks/exhaustive-deps -- onSize is stable per caller; svg is the real trigger

  useEffect(() => {
    const svgEl = ref.current?.querySelector('svg')
    const natural = naturalSizeRef.current
    if (!svgEl || !natural) return
    svgEl.style.width = `${natural.width * scale}px`
    svgEl.style.height = `${natural.height * scale}px`
  }, [scale])

  return <div ref={ref} className="inline-block" aria-label="System flow diagram" />
}

// A diagram is usually bigger than the panel showing it. Scale it down (never
// up) to fit within the viewport on first render, so the whole thing is
// visible instead of only the top-left corner at native size.
function fitScaleFor(viewport, size, padding = 32) {
  if (!viewport || !size?.width || !size?.height) return 1
  const availableWidth = Math.max(1, viewport.clientWidth - padding)
  const availableHeight = Math.max(1, viewport.clientHeight - padding)
  return Math.min(1, availableWidth / size.width, availableHeight / size.height)
}

function ZoomToolbar({ zoom, onMaximize }) {
  const { scale, min, max, zoomOut, zoomIn, reset } = zoom
  return (
    <div className="absolute right-3 top-3 flex items-center gap-0.5 rounded-lg border border-[var(--border)] bg-[var(--panel)]/95 p-1 shadow-sm backdrop-blur-sm">
      <button
        type="button"
        onClick={zoomOut}
        disabled={scale <= min}
        className="rounded-md p-1.5 text-[var(--text-muted)] hover:bg-[var(--bg-soft)] disabled:opacity-35"
        aria-label="Zoom out"
      >
        <ZoomOut className="h-3.5 w-3.5" />
      </button>
      <span className="w-11 text-center font-mono text-[10.5px] text-[var(--text-muted)]">
        {Math.round(scale * 100)}%
      </span>
      <button
        type="button"
        onClick={zoomIn}
        disabled={scale >= max}
        className="rounded-md p-1.5 text-[var(--text-muted)] hover:bg-[var(--bg-soft)] disabled:opacity-35"
        aria-label="Zoom in"
      >
        <ZoomIn className="h-3.5 w-3.5" />
      </button>
      <button
        type="button"
        onClick={reset}
        className="rounded-md p-1.5 text-[var(--text-muted)] hover:bg-[var(--bg-soft)]"
        aria-label="Fit diagram to window"
        title="Fit to window"
      >
        <RotateCcw className="h-3.5 w-3.5" />
      </button>
      {onMaximize && (
        <button
          type="button"
          onClick={onMaximize}
          className="rounded-md p-1.5 text-[var(--text-muted)] hover:bg-[var(--bg-soft)]"
          aria-label="Open full screen"
          title="Open full screen"
        >
          <Maximize2 className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  )
}

function DiagramModal({ svg, onClose }) {
  const zoom = useZoomPan({ min: 0.1, max: 5, step: 0.25 })
  const { scale, min, step, viewportRef, changeScale, setFit, handlers } = zoom
  const didFitRef = useRef(false)

  const handleSize = useCallback(
    (size) => {
      if (didFitRef.current) return
      didFitRef.current = true
      setFit(Math.max(min, fitScaleFor(viewportRef.current, size, 80)))
    },
    [min, setFit, viewportRef],
  )

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const onKeyDown = (event) => {
      if (event.key === 'Escape') onClose()
      if (event.key === '+' || event.key === '=') changeScale(scale + step)
      if (event.key === '-') changeScale(scale - step)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [onClose, scale, step, changeScale])

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="System flow diagram viewer"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div className="flex h-[94vh] w-[96vw] max-w-[1800px] flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">
        <div className="flex shrink-0 items-center justify-between gap-4 border-b border-[var(--border)] bg-white px-4 py-3">
          <div className="text-[13px] font-semibold text-[var(--text)]">System flow diagram</div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--text)] px-3 py-2 text-[12px] font-semibold text-white hover:opacity-85"
          >
            <X className="h-4 w-4" /> Close
          </button>
        </div>
        <div className="relative flex-1 overflow-hidden bg-[#e8eaed]">
          <div
            ref={viewportRef}
            className="h-full cursor-grab touch-none select-none overflow-auto p-10 active:cursor-grabbing"
            {...handlers}
          >
            <SvgCanvas svg={svg} scale={scale} onSize={handleSize} />
          </div>
          <ZoomToolbar zoom={zoom} />
        </div>
      </div>
    </div>,
    document.body,
  )
}

function MermaidView({ code }) {
  const reactId = useId()
  const renderIdRef = useRef(`system-flow-${reactId.replace(/:/g, "")}`)
  const [error, setError] = useState(null)
  const [svg, setSvg] = useState(null)
  const [maximized, setMaximized] = useState(false)
  const zoom = useZoomPan({ min: 0.1, max: 5, step: 0.25 })
  const { scale, min, viewportRef, setFit, handlers } = zoom
  const didFitRef = useRef(false)

  const handleSize = useCallback(
    (size) => {
      if (didFitRef.current) return
      didFitRef.current = true
      setFit(Math.max(min, fitScaleFor(viewportRef.current, size, 40)))
    },
    [min, setFit, viewportRef],
  )

  useEffect(() => {
    let cancelled = false
    setError(null)
    setSvg(null)
    didFitRef.current = false

    const render = async () => {
      try {
        mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'default' })
        await mermaid.parse(code)
        const result = await mermaid.render(renderIdRef.current, code)
        if (!cancelled) setSvg(result.svg)
      } catch (renderError) {
        if (!cancelled) setError(renderError?.message || String(renderError))
      }
    }
    render()
    return () => {
      cancelled = true
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

  if (!svg) return null

  return (
    <>
      <div className="fade-up relative h-full overflow-hidden bg-white">
        <div
          ref={viewportRef}
          className="h-full cursor-grab touch-none select-none overflow-auto px-5 py-6 active:cursor-grabbing"
          {...handlers}
        >
          <SvgCanvas svg={svg} scale={scale} onSize={handleSize} />
        </div>
        <ZoomToolbar zoom={zoom} onMaximize={() => setMaximized(true)} />
      </div>
      {maximized && <DiagramModal svg={svg} onClose={() => setMaximized(false)} />}
    </>
  )
}
export default function ArtifactViewer({ projectId, available, refreshToken, logs }) {
  const [tab, setTab] = useState('understanding')
  const [cache, setCache] = useState({})
  const [loading, setLoading] = useState(false)
  const [modelicaFilename, setModelicaFilename] = useState(null)
  const [collapsed, setCollapsed] = useState(false)

  useEffect(() => {
    setCache({})
    setModelicaFilename(null)
  }, [projectId])

  useEffect(() => {
    setCache({})
    setModelicaFilename(null)
  }, [refreshToken])

  useEffect(() => {
    if (ALWAYS_AVAILABLE.has(tab) || !available[tab] || cache[tab]) return
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
    <div className="card flex h-full overflow-hidden rounded-xl">
      <nav
        className={`flex ${collapsed ? 'w-14' : 'w-56'} shrink-0 flex-col overflow-y-auto border-r border-[var(--border)] bg-[var(--bg-soft)] py-3 transition-[width] duration-200`}
      >
        <div className={`mb-1 flex items-center ${collapsed ? 'justify-center px-1' : 'justify-between px-3'}`}>
          {!collapsed && (
            <span className="text-[10.5px] font-semibold tracking-wider text-[var(--text-dim)] uppercase">
              Outputs
            </span>
          )}
          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            aria-label={collapsed ? 'Expand outputs panel' : 'Collapse outputs panel'}
            className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-[var(--text-dim)] transition-colors hover:bg-[var(--panel)] hover:text-[var(--text)]"
          >
            {collapsed ? <ChevronsRight className="h-3.5 w-3.5" /> : <ChevronsLeft className="h-3.5 w-3.5" />}
          </button>
        </div>
        <div className="flex flex-col gap-0.5 px-2">
          {TABS.map((t) => {
            const isActive = t.key === tab
            const isAvailable = ALWAYS_AVAILABLE.has(t.key) || available[t.key]
            return (
              <button
                key={t.key}
                type="button"
                onClick={() => setTab(t.key)}
                title={collapsed ? t.label : undefined}
                className={`flex items-center gap-2.5 rounded-lg py-2 text-left transition-colors ${collapsed ? 'justify-center px-2' : 'px-3'}`}
                style={{
                  background: isActive ? 'var(--panel)' : 'transparent',
                  border: `1px solid ${isActive ? 'var(--border-strong)' : 'transparent'}`,
                }}
              >
                <span className="relative flex h-5 w-5 shrink-0 items-center justify-center">
                  <t.icon
                    className="h-4 w-4"
                    style={{ color: isActive ? 'var(--accent)' : 'var(--text-dim)' }}
                  />
                  <span
                    className="absolute -bottom-0.5 -right-0.5 h-1.5 w-1.5 rounded-full border border-[var(--bg-soft)]"
                    style={{ background: isAvailable ? 'var(--green)' : 'var(--border-strong)' }}
                  />
                </span>
                {!collapsed && (
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-[12.5px] font-medium text-[var(--text)]">{t.label}</span>
                    <span className="block truncate text-[10.5px] text-[var(--text-dim)]">
                      {isAvailable ? t.ready : t.locked}
                    </span>
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </nav>

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-center justify-between gap-2 border-b border-[var(--border)] px-4 py-2.5">
          <div className="min-w-0">
            <div className="text-[12.5px] font-semibold text-[var(--text)]">{active.label}</div>
            {displayedFilename && (
              <span className="font-mono block min-w-0 truncate text-[11px] text-[var(--text-dim)]">
                {displayedFilename}
              </span>
            )}
          </div>
          <CopyButton text={content} />
        </div>

        <div className="flex-1 overflow-auto">
          {loading && (
            <div className="flex h-full items-center justify-center gap-2 text-sm text-[var(--text-dim)]">
              <Loader2 className="h-4 w-4 animate-spin" /> loading…
            </div>
          )}
          {!loading && !ALWAYS_AVAILABLE.has(tab) && !available[tab] && (
            <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-[var(--text-dim)]">
              <active.icon className="h-6 w-6 opacity-40" />
              <span className="text-[13px]">Not generated yet</span>
            </div>
          )}
          {active.kind === 'files' && <FileBrowser projectId={projectId} refreshToken={refreshToken} />}
          {!loading && available[tab] && content && active.kind === 'markdown' && <MarkdownView text={content} />}
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
              <CodeBlock
                code={content}
                language={languageForFilename(displayedFilename) || (tab === 'sysml' ? 'sysml' : 'modelica')}
              />
            </div>
          )}
          {!loading && available[tab] && data && active.kind === 'clarifications' && (
            <ClarificationsView data={data} logs={logs} />
          )}
          {!loading && available[tab] && data && active.kind === 'validation' && (
            <ValidationView data={data} />
          )}
          {!loading && available[tab] && data && active.kind === 'result' && (
            <ResultView projectId={projectId} data={data} />
          )}
        </div>
      </div>
    </div>
  )
}
