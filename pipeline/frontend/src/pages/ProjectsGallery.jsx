import { ArrowRight, Plus, Workflow } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { createProject, listProjects } from '../api'
import NewProjectModal from '../components/NewProjectModal'
import StatusPill from '../components/StatusPill'
import { STAGES, STAGE_INDEX } from '../constants'

function ProjectCard({ project, onOpen }) {
  const stageIdx = STAGE_INDEX[project.current_stage]
  const stageLabel = stageIdx != null ? STAGES[stageIdx].label : null
  return (
    <button
      type="button"
      onClick={() => onOpen(project.project_id)}
      className="card group flex flex-col gap-3 rounded-xl px-5 py-4 text-left transition-colors hover:border-[var(--accent)]"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 truncate font-serif text-[15px] font-semibold text-[var(--text)]">
          {project.name}
        </div>
        <ArrowRight className="mt-0.5 h-4 w-4 shrink-0 text-[var(--text-dim)] opacity-0 transition-opacity group-hover:opacity-100" />
      </div>
      <div className="flex items-center gap-2">
        <StatusPill status={project.status} size="sm" />
        {stageLabel && project.status === 'running' && (
          <span className="truncate text-[11px] text-[var(--text-dim)]">{stageLabel}</span>
        )}
      </div>
    </button>
  )
}

export default function ProjectsGallery({ onOpenProject }) {
  const [projects, setProjects] = useState([])
  const [showNewProject, setShowNewProject] = useState(false)

  const refresh = useCallback(() => {
    listProjects().then(setProjects).catch(() => {})
  }, [])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, 4000)
    return () => clearInterval(id)
  }, [refresh])

  const handleCreate = async (name, files, stage1Backend) => {
    const res = await createProject(name, files, stage1Backend)
    setShowNewProject(false)
    refresh()
    onOpenProject(res.project_id)
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <header className="flex items-center justify-between gap-4 border-b border-[var(--border)] bg-[var(--panel)] px-6 py-5">
        <div className="flex items-center gap-3">
          <div
            className="flex h-9 w-9 items-center justify-center rounded-md border"
            style={{ borderColor: 'var(--border-strong)', color: 'var(--accent)' }}
          >
            <Workflow className="h-4.5 w-4.5" />
          </div>
          <div>
            <div className="font-serif text-[17px] font-semibold tracking-tight text-[var(--text)]">
              SimulationHub
            </div>
            <div className="text-[11px] text-[var(--text-dim)]">Documents to verified simulations</div>
          </div>
        </div>
        <button
          type="button"
          onClick={() => setShowNewProject(true)}
          className="flex items-center gap-2 rounded-lg px-4 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-[var(--accent-strong)]"
          style={{ background: 'var(--accent)' }}
        >
          <Plus className="h-4 w-4" strokeWidth={2.5} />
          New Project
        </button>
      </header>

      <div className="mx-auto w-full max-w-[1200px] flex-1 px-6 py-8">
        <h1 className="font-serif text-xl font-semibold text-[var(--text)]">Projects</h1>
        <p className="mt-1 text-[13px] text-[var(--text-muted)]">
          Every simulation starts here. Open a project to pick up where it left off, or start a new one.
        </p>

        {projects.length === 0 ? (
          <div className="fade-up mt-16 flex flex-col items-center gap-4 text-center">
            <div
              className="flex h-14 w-14 items-center justify-center rounded-2xl"
              style={{ background: 'var(--accent-soft)' }}
            >
              <Workflow className="h-7 w-7 text-[var(--accent)]" />
            </div>
            <h2 className="font-serif text-2xl font-semibold tracking-tight text-[var(--text)]">
              Turn documents into a verified simulation
            </h2>
            <p className="max-w-md text-[13.5px] text-[var(--text-muted)]">
              Upload engineering documents and SimulationHub reads them, resolves the brief, asks you about open
              decisions, writes a SysML v2 model, and compiles a verified Modelica simulation.
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
        ) : (
          <div className="fade-up mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {projects.map((p) => (
              <ProjectCard key={p.project_id} project={p} onOpen={onOpenProject} />
            ))}
          </div>
        )}
      </div>

      {showNewProject && <NewProjectModal onClose={() => setShowNewProject(false)} onCreate={handleCreate} />}
    </div>
  )
}
