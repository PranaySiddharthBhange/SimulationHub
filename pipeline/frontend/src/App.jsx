import { AlertTriangle, Play, RotateCcw, Workflow } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import {
  answerClarifications,
  createProject,
  getProject,
  listProjects,
  runProject,
  runStage,
  streamLogs,
  useDefaultClarifications as submitDefaultClarifications,
} from './api'
import ArtifactViewer from './components/ArtifactViewer'
import ClarificationCard from './components/ClarificationCard'
import LogPanel from './components/LogPanel'
import NewProjectModal from './components/NewProjectModal'
import PipelineStepper from './components/PipelineStepper'
import Sidebar from './components/Sidebar'
import StatusPill from './components/StatusPill'
import { STAGES, STAGE_INDEX } from './constants'

const EMPTY_ARTIFACTS = {
  extraction: false,
  understanding: false,
  merged_understanding: false,
  clarified: false,
  sysml: false,
  modelica: false,
  validation: false,
  result: false,
}

function computeStepStates(project) {
  if (!project) return STAGES.map(() => 'pending')
  const { status, current_stage: currentStage, artifacts } = project
  const idx = currentStage != null ? STAGE_INDEX[currentStage] : -1
  return STAGES.map((s, i) => {
    if (status === 'error' && i === idx) return 'error'
    if (status === 'awaiting_input' && s.key === currentStage) return 'awaiting'
    if (idx >= 0 && i < idx) return 'done'
    if (idx >= 0 && i === idx) return 'active'
    if (s.key === 'stage_1' && artifacts?.extraction) return 'done'
    if (s.key === 'merge' && artifacts?.merged_understanding) return 'done'
    if (s.key === 'clarify' && artifacts?.clarified) return 'done'
    if (s.key === 'stage_2' && artifacts?.sysml) return 'done'
    if (s.key === 'stage_3' && artifacts?.modelica) return 'done'
    if (s.key === 'stage_4' && artifacts?.validation) return 'done'
    if (status === 'done') return 'done'
    return 'pending'
  })
}

export default function App() {
  const [projects, setProjects] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [project, setProject] = useState(null)
  const [logs, setLogs] = useState([])
  const [showNewProject, setShowNewProject] = useState(false)
  const [clarifyBusy, setClarifyBusy] = useState(false)
  const [refreshToken, setRefreshToken] = useState(0)
  const [streamGeneration, setStreamGeneration] = useState(0)
  const [stage1Backend, setStage1Backend] = useState('ollama')
  const [logWidth, setLogWidth] = useState(390)
  const esRef = useRef(null)
  const prevSignature = useRef(null)
  const resizingLogs = useRef(false)

  const refreshProjectList = useCallback(() => {
    listProjects().then(setProjects).catch(() => {})
  }, [])

  useEffect(() => {
    refreshProjectList()
    const id = setInterval(refreshProjectList, 4000)
    return () => clearInterval(id)
  }, [refreshProjectList])

  useEffect(() => {
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
    }
    setLogs([])
    setProject(null)
    prevSignature.current = null
    if (!selectedId) return

    getProject(selectedId).then(setProject).catch(() => {})

    const es = streamLogs(selectedId, {
      onLog: (line) => setLogs((prev) => [...prev, line]),
      onStatus: (payload) => {
        setProject((prev) => ({ ...(prev || {}), ...payload }))
        const signature = `${payload.status}:${payload.current_stage}`
        if (signature !== prevSignature.current) {
          prevSignature.current = signature
          getProject(selectedId)
            .then(setProject)
            .catch(() => {})
          refreshProjectList()
          setRefreshToken((t) => t + 1)
        }
        if (['stage1_ready', 'ready', 'done', 'error'].includes(payload.status)) {
          es.close()
        }
      },
    })
    esRef.current = es
    return () => es.close()
  }, [selectedId, refreshProjectList, streamGeneration])

  useEffect(() => {
    if (project?.stage1_backend) setStage1Backend(project.stage1_backend)
  }, [project?.stage1_backend])

  useEffect(() => {
    const onMove = (event) => {
      if (!resizingLogs.current) return
      setLogWidth(Math.max(300, Math.min(680, window.innerWidth - event.clientX - 24)))
    }
    const onUp = () => {
      resizingLogs.current = false
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
    window.addEventListener('pointermove', onMove)
    window.addEventListener('pointerup', onUp)
    return () => {
      window.removeEventListener('pointermove', onMove)
      window.removeEventListener('pointerup', onUp)
    }
  }, [])

  const handleCreate = async (name, files, stage1Backend) => {
    const res = await createProject(name, files, stage1Backend)
    setShowNewProject(false)
    refreshProjectList()
    setSelectedId(res.project_id)
  }

  const handleRun = async () => {
    if (!selectedId) return
    await runProject(selectedId, stage1Backend)
    setStreamGeneration((value) => value + 1)
    getProject(selectedId).then(setProject).catch(() => {})
    refreshProjectList()
  }

  const handleRunStage = async (stage) => {
    if (!selectedId) return
    await runStage(selectedId, stage, stage1Backend)
    setStreamGeneration((value) => value + 1)
    getProject(selectedId).then(setProject).catch(() => {})
    refreshProjectList()
  }

  const handleAnswer = async (answers) => {
    setClarifyBusy(true)
    try {
      await answerClarifications(selectedId, answers)
    } finally {
      setClarifyBusy(false)
    }
  }

  const handleUseDefaults = async () => {
    setClarifyBusy(true)
    try {
      await submitDefaultClarifications(selectedId)
    } finally {
      setClarifyBusy(false)
    }
  }

  const stepStates = computeStepStates(project)
  const canRun = project && project.status !== 'running' && project.status !== 'awaiting_input'
  const artifacts = project?.artifacts || EMPTY_ARTIFACTS

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        projects={projects}
        selectedId={selectedId}
        onSelect={setSelectedId}
        onNewProject={() => setShowNewProject(true)}
      />

      <main className="flex-1 overflow-y-auto">
        {!project && (
          <div className="flex h-full flex-col items-center justify-center gap-4 px-6 text-center">
            <div
              className="flex h-14 w-14 items-center justify-center rounded-2xl"
              style={{ background: 'var(--accent-soft)' }}
            >
              <Workflow className="h-7 w-7 text-[var(--accent)]" />
            </div>
            <h1 className="font-serif text-3xl font-semibold tracking-tight text-[var(--text)]">
              Turn documents into a verified simulation
            </h1>
            <p className="max-w-md text-[13.5px] text-[var(--text-muted)]">
              Upload engineering documents. The pipeline reads them, resolves the brief, asks you about open decisions,
              writes a SysML v2 model, and compiles a verified Modelica simulation.
            </p>
            <button
              type="button"
              onClick={() => setShowNewProject(true)}
              className="mt-2 rounded-lg px-5 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-[var(--accent-strong)]"
              style={{ background: 'var(--accent)' }}
            >
              Start a new project
            </button>
          </div>
        )}

        {project && (
          <div className="fade-up mx-auto flex min-h-full max-w-[1600px] flex-col gap-5 px-6 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="font-serif text-xl font-semibold text-[var(--text)]">
                  {projects.find((p) => p.project_id === selectedId)?.name || selectedId}
                </h1>
                <div className="mt-1 flex items-center gap-2">
                  <StatusPill status={project.status} />
                  <span className="font-mono text-[11px] text-[var(--text-dim)]">{selectedId}</span>
                </div>
              </div>
              <button
                type="button"
                disabled={!canRun}
                onClick={handleRun}
                className="flex items-center gap-2 rounded-lg px-4 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-[var(--accent-strong)] disabled:opacity-40"
                style={{ background: 'var(--accent)' }}
              >
                {['done', 'error', 'interrupted'].includes(project.status) ? (
                  <RotateCcw className="h-4 w-4" />
                ) : (
                  <Play className="h-4 w-4" fill="white" />
                )}
                {project.status === 'created'
                  ? 'Run pipeline'
                  : ['stage1_ready', 'ready'].includes(project.status)
                    ? 'Continue pipeline'
                    : 'Re-run'}
              </button>
            </div>

            <div className="card rounded-xl px-6 py-5">
              <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] pb-4">
                <div>
                  <div className="text-[13px] font-semibold text-[var(--text)]">Understanding backend</div>
                  <div className="mt-0.5 text-[11.5px] text-[var(--text-dim)]">
                    Choose before running or re-running Understand
                  </div>
                </div>
                <div className="inline-flex rounded-lg border border-[var(--border-strong)] bg-[var(--bg-soft)] p-1">
                  {[
                    ['ollama', 'Local Gemma'],
                    ['openai', 'Cloud GPT-5.4'],
                  ].map(([value, label]) => (
                    <button
                      key={value}
                      type="button"
                      disabled={project.status === 'running' || project.status === 'awaiting_input'}
                      onClick={() => setStage1Backend(value)}
                      className="rounded-md px-3 py-1.5 text-[11.5px] font-semibold transition-colors disabled:opacity-50"
                      style={{
                        background: stage1Backend === value ? 'var(--panel)' : 'transparent',
                        color: stage1Backend === value ? 'var(--accent)' : 'var(--text-muted)',
                        boxShadow: stage1Backend === value ? '0 1px 2px rgba(38,38,36,.08)' : 'none',
                      }}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
              <PipelineStepper
                states={stepStates}
                onRunStage={handleRunStage}
                logs={logs}
                disabled={project.status === 'running' || project.status === 'awaiting_input'}
              />
            </div>

            {project.status === 'error' && project.error && (
              <div className="fade-up flex items-start gap-2.5 rounded-xl border border-[#e6cec8] bg-[#f8eae7] px-4 py-3 text-[12.5px] text-[var(--red)]">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                {project.error}
              </div>
            )}

            {project.status === 'interrupted' && project.error && (
              <div className="fade-up flex items-start gap-2.5 rounded-xl border border-[var(--border-strong)] bg-[var(--bg-soft)] px-4 py-3 text-[12.5px] text-[var(--text-muted)]">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                {project.error}
              </div>
            )}

            {project.status === 'awaiting_input' && project.pending_clarifications?.length > 0 && (
              <ClarificationCard
                clarifications={project.pending_clarifications}
                stage={project.current_stage}
                onSubmit={handleAnswer}
                onUseDefaults={handleUseDefaults}
                busy={clarifyBusy}
              />
            )}

            <div className="flex min-h-[540px] flex-1 pb-2">
              <div className="min-w-0 flex-1">
                <ArtifactViewer projectId={selectedId} available={artifacts} refreshToken={refreshToken} />
              </div>
              <button
                type="button"
                aria-label="Resize activity log"
                onPointerDown={() => {
                  resizingLogs.current = true
                  document.body.style.cursor = 'col-resize'
                  document.body.style.userSelect = 'none'
                }}
                className="group mx-1.5 flex w-2 cursor-col-resize items-center justify-center"
              >
                <span className="h-16 w-1 rounded-full bg-[var(--border-strong)] transition-colors group-hover:bg-[var(--accent)]" />
              </button>
              <div className="shrink-0" style={{ width: logWidth }}>
                <LogPanel logs={logs} stage1Backend={stage1Backend} />
              </div>
            </div>
          </div>
        )}
      </main>

      {showNewProject && <NewProjectModal onClose={() => setShowNewProject(false)} onCreate={handleCreate} />}
    </div>
  )
}
