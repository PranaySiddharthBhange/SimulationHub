import { ChevronRight, FileText, Loader2, Play, RotateCcw, Workflow } from 'lucide-react'

export default function TopBar({
  onNavigateHome,
  projectName,
  logsCount,
  logsOpen,
  onToggleLogs,
  primaryLabel,
  primaryBusy = false,
  primaryDisabled = false,
  onPrimaryClick,
}) {
  return (
    <header className="flex h-16 shrink-0 items-center justify-between gap-4 border-b border-[var(--border)] bg-[var(--panel)] px-6">
      <div className="flex min-w-0 items-center gap-3">
        <button type="button" onClick={onNavigateHome} className="flex shrink-0 items-center gap-2.5">
          <div
            className="flex h-8 w-8 items-center justify-center rounded-md border"
            style={{ borderColor: 'var(--border-strong)', color: 'var(--accent)' }}
          >
            <Workflow className="h-4 w-4" />
          </div>
          <div className="text-left">
            <div className="font-serif text-[15px] font-semibold leading-tight text-[var(--text)]">
              SimulationHub
            </div>
            <div className="text-[10.5px] leading-tight text-[var(--text-dim)]">Documents to verified simulations</div>
          </div>
        </button>

        <div className="mx-1 h-7 w-px shrink-0 bg-[var(--border)]" />

        <nav className="flex min-w-0 items-center gap-1.5 text-[13px]">
          <button
            type="button"
            onClick={onNavigateHome}
            className="shrink-0 text-[var(--text-dim)] transition-colors hover:text-[var(--text)]"
          >
            Projects
          </button>
          <ChevronRight className="h-3.5 w-3.5 shrink-0 text-[var(--text-dim)]" />
          <span className="truncate font-medium text-[var(--text)]">{projectName}</span>
        </nav>
      </div>

      <div className="flex shrink-0 items-center gap-3">
        <button
          type="button"
          onClick={onToggleLogs}
          className="flex items-center gap-2 rounded-lg border px-3 py-2 text-[12.5px] font-medium transition-colors"
          style={{
            borderColor: logsOpen ? 'var(--accent)' : 'var(--border-strong)',
            color: logsOpen ? 'var(--accent)' : 'var(--text-muted)',
            background: logsOpen ? 'var(--accent-soft)' : 'transparent',
          }}
        >
          <FileText className="h-3.5 w-3.5" />
          Logs
          <span
            className="rounded-full px-1.5 py-0.5 font-mono text-[10.5px] font-semibold"
            style={{ background: 'var(--bg-soft)', color: 'var(--text-muted)' }}
          >
            {logsCount}
          </span>
        </button>

        <button
          type="button"
          disabled={primaryDisabled}
          onClick={onPrimaryClick}
          className="flex items-center gap-2 rounded-lg px-4 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-[var(--accent-strong)] disabled:opacity-40"
          style={{ background: 'var(--accent)' }}
        >
          {primaryBusy ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : primaryLabel.startsWith('Re-run') ? (
            <RotateCcw className="h-4 w-4" />
          ) : (
            <Play className="h-4 w-4" fill="white" />
          )}
          {primaryLabel}
        </button>
      </div>
    </header>
  )
}
