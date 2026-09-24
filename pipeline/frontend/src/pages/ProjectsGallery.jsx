import { ArrowRight, ChevronDown, Plus, Search, Workflow } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { createProject, listProjects } from '../api'
import NewProjectModal from '../components/NewProjectModal'
import ProjectIllustration from '../components/ProjectIllustration'
import StatusPill from '../components/StatusPill'

// Cards cycle through the app's own green / blue / accent palette, in that
// order, rather than a random or single color -- keeps a busy grid readable
// while still using colors already defined for status elsewhere in the app.
const CARD_ACCENTS = [
  { fg: 'var(--green)', bg: '#edf3ec' },
  { fg: 'var(--blue)', bg: '#eaf1f4' },
  { fg: 'var(--accent)', bg: 'var(--accent-soft)' },
]

const FILTERS = [
  { key: 'all', label: 'All', match: () => true },
  { key: 'complete', label: 'Complete', match: (p) => p.status === 'done' },
  {
    key: 'in_progress',
    label: 'In progress',
    match: (p) => p.status === 'running' || p.status === 'awaiting_input',
  },
  { key: 'drafts', label: 'Drafts', match: (p) => p.status === 'created' },
]

function relativeTime(iso) {
  if (!iso) return null
  const diffMs = Date.now() - new Date(iso).getTime()
  const mins = Math.round(diffMs / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.round(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.round(hours / 24)
  if (days < 30) return `${days}d ago`
  return `${Math.round(days / 30)}mo ago`
}

function StatTile({ label, value }) {
  return (
    <div className="card rounded-xl px-5 py-4">
      <div className="text-[12px] text-[var(--text-dim)]">{label}</div>
      <div className="mt-1 font-serif text-2xl font-semibold text-[var(--text)]">{value}</div>
    </div>
  )
}

function ProjectCard({ project, accent, onOpen }) {
  return (
    <button
      type="button"
      onClick={() => onOpen(project.project_id)}
      className="card group flex flex-col overflow-hidden rounded-xl text-left transition-colors"
      onMouseEnter={(e) => (e.currentTarget.style.borderColor = accent.fg)}
      onMouseLeave={(e) => (e.currentTarget.style.borderColor = '')}
    >
      <div className="h-32 w-full" style={{ background: accent.bg, color: accent.fg }}>
        <ProjectIllustration complete={project.status === 'done'} className="h-full w-full" />
      </div>

      <div className="flex flex-1 flex-col gap-2 px-5 py-4">
        <div className="flex items-center justify-between gap-2">
          {project.domain ? (
            <span
              className="truncate text-[10.5px] font-semibold tracking-wide uppercase"
              style={{ color: accent.fg }}
            >
              {project.domain}
            </span>
          ) : (
            <span />
          )}
          <StatusPill status={project.status} size="sm" />
        </div>

        <div className="truncate font-serif text-[15px] font-semibold text-[var(--text)]">{project.name}</div>

        <div className="mt-auto flex items-center justify-between gap-2 border-t border-[var(--border)] pt-3 text-[11px] text-[var(--text-dim)]">
          <span className="truncate">
            {project.document_count != null && `${project.document_count} doc${project.document_count === 1 ? '' : 's'}`}
            {project.document_count != null && project.updated_at && ' · '}
            {project.updated_at && `Updated ${relativeTime(project.updated_at)}`}
          </span>
          <span
            className="flex shrink-0 items-center gap-1 font-semibold opacity-0 transition-opacity group-hover:opacity-100"
            style={{ color: accent.fg }}
          >
            Open <ArrowRight className="h-3.5 w-3.5" />
          </span>
        </div>
      </div>
    </button>
  )
}

export default function ProjectsGallery({ onOpenProject }) {
  const [projects, setProjects] = useState([])
  const [showNewProject, setShowNewProject] = useState(false)
  const [filter, setFilter] = useState('all')
  const [query, setQuery] = useState('')
  const [sort, setSort] = useState('updated')

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

  const counts = useMemo(
    () => Object.fromEntries(FILTERS.map((f) => [f.key, projects.filter(f.match).length])),
    [projects],
  )
  const completedCount = counts.complete || 0
  const inProgressCount = counts.in_progress || 0

  const visibleProjects = useMemo(() => {
    const activeFilter = FILTERS.find((f) => f.key === filter) || FILTERS[0]
    const q = query.trim().toLowerCase()
    const filtered = projects.filter((p) => activeFilter.match(p) && (!q || p.name.toLowerCase().includes(q)))
    const sorted = [...filtered]
    if (sort === 'name') {
      sorted.sort((a, b) => a.name.localeCompare(b.name))
    } else {
      sorted.sort((a, b) => new Date(b.updated_at || 0) - new Date(a.updated_at || 0))
    }
    return sorted
  }, [projects, filter, query, sort])

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
          <div className="fade-up flex flex-col gap-6">
            <div>
              <div className="text-[11px] font-semibold tracking-wider text-[var(--text-dim)] uppercase">
                Workspace
              </div>
              <h1 className="mt-1 font-serif text-xl font-semibold text-[var(--text)]">Projects</h1>
              <p className="mt-1 text-[13px] text-[var(--text-muted)]">
                Every simulation starts here. Open a project to pick up where it left off, or start a new one.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <StatTile label="Total projects" value={projects.length} />
              <StatTile label="Complete" value={completedCount} />
              <StatTile label="In progress" value={inProgressCount} />
              <StatTile label="Simulations run" value={completedCount} />
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-1.5">
                {FILTERS.map((f) => {
                  const active = filter === f.key
                  return (
                    <button
                      key={f.key}
                      type="button"
                      onClick={() => setFilter(f.key)}
                      className="rounded-full px-3 py-1.5 text-[12px] font-medium transition-colors"
                      style={{
                        background: active ? 'var(--text)' : 'var(--panel)',
                        color: active ? '#fff' : 'var(--text-muted)',
                        border: `1px solid ${active ? 'var(--text)' : 'var(--border-strong)'}`,
                      }}
                    >
                      {f.label} · {counts[f.key] || 0}
                    </button>
                  )
                })}
              </div>

              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="pointer-events-none absolute top-1/2 left-3 h-3.5 w-3.5 -translate-y-1/2 text-[var(--text-dim)]" />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search projects..."
                    className="w-56 rounded-lg border border-[var(--border-strong)] bg-[var(--panel)] py-1.5 pr-3 pl-8 text-[12.5px] text-[var(--text)] outline-none focus:border-[var(--accent)]"
                  />
                </div>
                <div className="relative">
                  <select
                    value={sort}
                    onChange={(e) => setSort(e.target.value)}
                    className="appearance-none rounded-lg border border-[var(--border-strong)] bg-[var(--panel)] py-1.5 pr-8 pl-3 text-[12.5px] text-[var(--text-muted)] outline-none focus:border-[var(--accent)]"
                  >
                    <option value="updated">Last updated</option>
                    <option value="name">Name (A–Z)</option>
                  </select>
                  <ChevronDown className="pointer-events-none absolute top-1/2 right-2.5 h-3.5 w-3.5 -translate-y-1/2 text-[var(--text-dim)]" />
                </div>
              </div>
            </div>

            {visibleProjects.length === 0 ? (
              <div className="py-16 text-center text-[13px] text-[var(--text-dim)]">No projects match.</div>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {visibleProjects.map((p, i) => (
                  <ProjectCard
                    key={p.project_id}
                    project={p}
                    accent={CARD_ACCENTS[i % CARD_ACCENTS.length]}
                    onOpen={onOpenProject}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {showNewProject && <NewProjectModal onClose={() => setShowNewProject(false)} onCreate={handleCreate} />}
    </div>
  )
}
