import { Plus } from 'lucide-react'
import { STAGES, STAGE_INDEX } from '../constants'
import StatusPill from './StatusPill'

export default function Sidebar({ projects, selectedId, onSelect, onNewProject }) {
  return (
    <aside className="flex h-full w-[300px] shrink-0 flex-col border-r border-[var(--border)] bg-[var(--bg-soft)]">
      <div className="flex items-center gap-2.5 px-5 py-5">
        <div
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border text-[13px] font-semibold"
          style={{ borderColor: 'var(--border-strong)', color: 'var(--accent)' }}
        >
          US
        </div>
        <div>
          <div className="font-serif text-[15px] font-semibold tracking-tight text-[var(--text)]">
            Universal Simulation
          </div>
          <div className="text-[10.5px] text-[var(--text-dim)]">Document → SysML → Modelica</div>
        </div>
      </div>

      <div className="px-4 pb-3">
        <button
          type="button"
          onClick={onNewProject}
          className="flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-[var(--accent-strong)] active:opacity-90"
          style={{ background: 'var(--accent)' }}
        >
          <Plus className="h-4 w-4" strokeWidth={2.5} />
          New Project
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-4">
        <div className="px-2 pb-2 text-[10.5px] font-semibold tracking-wider text-[var(--text-dim)] uppercase">
          Projects
        </div>
        <div className="flex flex-col gap-1">
          {projects.length === 0 && (
            <div className="px-2 py-6 text-center text-[12px] text-[var(--text-dim)]">
              No projects yet — create one to begin.
            </div>
          )}
          {projects.map((p) => {
            const isActive = p.project_id === selectedId
            const stageIdx = STAGE_INDEX[p.current_stage]
            const stageLabel = stageIdx != null ? STAGES[stageIdx].label : null
            return (
              <button
                key={p.project_id}
                type="button"
                onClick={() => onSelect(p.project_id)}
                className="rounded-xl px-3 py-2.5 text-left transition-colors"
                style={{
                  background: isActive ? 'var(--panel)' : 'transparent',
                  border: `1px solid ${isActive ? 'var(--border-strong)' : 'transparent'}`,
                }}
              >
                <div className="truncate text-[13px] font-medium text-[var(--text)]">{p.name}</div>
                <div className="mt-1.5 flex items-center gap-2">
                  <StatusPill status={p.status} size="sm" />
                  {stageLabel && p.status === 'running' && (
                    <span className="truncate text-[10.5px] text-[var(--text-dim)]">{stageLabel}</span>
                  )}
                </div>
              </button>
            )
          })}
        </div>
      </div>
    </aside>
  )
}
