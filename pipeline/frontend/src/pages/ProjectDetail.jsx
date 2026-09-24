import { AlertTriangle, Cloud, HardDrive, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import {
  answerClarifications,
  getProject,
  runProject,
  runStage,
  streamLogs,
  useDefaultClarifications as submitDefaultClarifications,
} from '../api'
import ArtifactViewer from '../components/ArtifactViewer'
import ClarificationCard from '../components/ClarificationCard'
import LogPanel from '../components/LogPanel'
import PipelineStageGrid from '../components/PipelineStageGrid'
import StatusPill from '../components/StatusPill'
import TopBar from '../components/TopBar'
import { STAGES, STAGE_INDEX } from '../constants'

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
    // "Simulate" now covers generation + validation together, so it is only
    // done once both artifacts exist.
    if (s.key === 'stage_3' && artifacts?.modelica && artifacts?.validation) return 'done'
    if (status === 'done') return 'done'
    return 'pending'
  })
}

export default function ProjectDetail({ projectId, onNavigateHome }) {
  const [project, setProject] = useState(null)
  const [notFound, setNotFound] = useState(false)
  const [logs, setLogs] = useState([])
  const [logsOpen, setLogsOpen] = useState(false)
  const [clarifyBusy, setClarifyBusy] = useState(false)
  const [refreshToken, setRefreshToken] = useState(0)
  const [streamGeneration, setStreamGeneration] = useState(0)
  const [stage1Backend, setStage1Backend] = useState('ollama')
  const esRef = useRef(null)
  const prevSignature = useRef(null)

  useEffect(() => {
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
    }
    setLogs([])
    setProject(null)
    setNotFound(false)
    prevSignature.current = null

    getProject(projectId)
      .then(setProject)
      .catch(() => setNotFound(true))

    const es = streamLogs(projectId, {
      onLog: (line) => setLogs((prev) => [...prev, line]),
      onStatus: (payload) => {
        setProject((prev) => ({ ...(prev || {}), ...payload }))
        const signature = `${payload.status}:${payload.current_stage}`
        if (signature !== prevSignature.current) {
          prevSignature.current = signature
          getProject(projectId)
            .then(setProject)
            .catch(() => {})
          setRefreshToken((t) => t + 1)
        }
        if (['stage1_ready', 'ready', 'done', 'error'].includes(payload.status)) {
          es.close()
        }
      },
    })
    esRef.current = es
    return () => es.close()
  }, [projectId, streamGeneration])

  useEffect(() => {
    if (project?.stage1_backend) setStage1Backend(project.stage1_backend)
  }, [project?.stage1_backend])

  const handleRun = async () => {
    await runProject(projectId, stage1Backend)
    setStreamGeneration((value) => value + 1)
    getProject(projectId).then(setProject).catch(() => {})
  }

  const handleRunStage = async (stage) => {
    await runStage(projectId, stage, stage1Backend)
    setStreamGeneration((value) => value + 1)
    getProject(projectId).then(setProject).catch(() => {})
  }

  const handleAnswer = async (answers) => {
    setClarifyBusy(true)
    try {
      await answerClarifications(projectId, answers)
    } finally {
      setClarifyBusy(false)
    }
  }

  const handleUseDefaults = async () => {
    setClarifyBusy(true)
    try {
      await submitDefaultClarifications(projectId)
    } finally {
      setClarifyBusy(false)
    }
  }

  if (notFound) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
        <div className="text-[15px] font-semibold text-[var(--text)]">Project not found</div>
        <button
          type="button"
          onClick={onNavigateHome}
          className="rounded-lg px-4 py-2 text-[12.5px] font-semibold text-white"
          style={{ background: 'var(--accent)' }}
        >
          Back to Projects
        </button>
      </div>
    )
  }

  const stepStates = computeStepStates(project)
  const canRun = project && project.status !== 'running' && project.status !== 'awaiting_input'
  const artifacts = project?.artifacts || EMPTY_ARTIFACTS
  const needsClarification = project?.status === 'awaiting_input' && project?.pending_clarifications?.length > 0
  const nextStageIdx = stepStates.findIndex((s) => s !== 'done')
  const nextStageLabel = nextStageIdx >= 0 ? STAGES[nextStageIdx].label : null
  const primaryLabel = !project
    ? 'Run pipeline'
    : project.status === 'created'
      ? 'Run pipeline'
      : ['stage1_ready', 'ready'].includes(project.status)
        ? nextStageLabel
          ? `Continue to ${nextStageLabel}`
          : 'Continue pipeline'
        : 'Re-run'

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <TopBar
        onNavigateHome={onNavigateHome}
        projectName={project?.name || projectId}
        logsCount={logs.length}
        logsOpen={logsOpen}
        onToggleLogs={() => setLogsOpen((v) => !v)}
        primaryLabel={primaryLabel}
        primaryDisabled={!canRun}
        onPrimaryClick={handleRun}
      />

      <div className="flex min-h-0 flex-1">
        <main className="min-w-0 flex-1 overflow-y-auto">
          {!project ? (
            <div className="flex h-full items-center justify-center text-[13px] text-[var(--text-dim)]">
              Loading project…
            </div>
          ) : (
            <div className="fade-up mx-auto flex h-full max-w-[1400px] flex-col gap-5 px-6 py-6">
              <StatusPill status={project.status} />

              <PipelineStageGrid
                states={stepStates}
                onRunStage={handleRunStage}
                logs={logs}
                disabled={project.status === 'running' || project.status === 'awaiting_input'}
                backendSlot={
                  <div className="flex items-center gap-3">
                    <div className="inline-flex rounded-lg border border-[var(--border-strong)] bg-[var(--bg-soft)] p-1">
                      {[
                        ['ollama', 'Local', HardDrive],
                        ['openai', 'Cloud', Cloud],
                      ].map(([value, label, Icon]) => (
                        <button
                          key={value}
                          type="button"
                          disabled={project.status === 'running' || project.status === 'awaiting_input'}
                          onClick={() => setStage1Backend(value)}
                          className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-[11.5px] font-semibold transition-colors disabled:opacity-50"
                          style={{
                            background: stage1Backend === value ? 'var(--panel)' : 'transparent',
                            color: stage1Backend === value ? 'var(--accent)' : 'var(--text-muted)',
                            boxShadow: stage1Backend === value ? '0 1px 2px rgba(38,38,36,.08)' : 'none',
                          }}
                        >
                          <Icon className="h-3.5 w-3.5" />
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                }
              />

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

              <div className="flex min-h-[540px] flex-1 gap-5 pb-2">
                {needsClarification && (
                  <div className="w-1/2 min-w-0">
                    <ClarificationCard
                      clarifications={project.pending_clarifications}
                      stage={project.current_stage}
                      onSubmit={handleAnswer}
                      onUseDefaults={handleUseDefaults}
                      busy={clarifyBusy}
                    />
                  </div>
                )}
                <div className={needsClarification ? 'w-1/2 min-w-0' : 'min-w-0 flex-1'}>
                  <ArtifactViewer projectId={projectId} available={artifacts} refreshToken={refreshToken} logs={logs} />
                </div>
              </div>
            </div>
          )}
        </main>

        {logsOpen && (
          <div className="flex w-[400px] shrink-0 flex-col border-l border-[var(--border)] bg-[var(--bg-soft)]">
            <div className="flex items-center justify-between px-3 pt-3">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-dim)]">
                Activity
              </span>
              <button
                type="button"
                onClick={() => setLogsOpen(false)}
                aria-label="Close activity log"
                className="text-[var(--text-dim)] hover:text-[var(--text)]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="min-h-0 flex-1 p-3">
              <LogPanel logs={logs} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
