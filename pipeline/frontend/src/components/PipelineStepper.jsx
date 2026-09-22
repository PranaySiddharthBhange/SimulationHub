import { AlertTriangle, Check, HelpCircle, Loader2 } from 'lucide-react'
import { STAGES } from '../constants'

const STYLES = {
  pending: { ring: 'var(--border-strong)', fg: 'var(--text-dim)', bg: 'transparent' },
  active: { ring: 'var(--accent)', fg: '#fff', bg: 'var(--accent)' },
  awaiting: { ring: 'var(--amber)', fg: '#fff', bg: 'var(--amber)' },
  done: { ring: 'var(--green)', fg: '#fff', bg: 'var(--green)' },
  error: { ring: 'var(--red)', fg: '#fff', bg: 'var(--red)' },
}

function Icon({ state }) {
  if (state === 'active') return <Loader2 className="h-4 w-4 animate-spin" />
  if (state === 'awaiting') return <HelpCircle className="h-4 w-4" />
  if (state === 'done') return <Check className="h-4 w-4" strokeWidth={3} />
  if (state === 'error') return <AlertTriangle className="h-4 w-4" />
  return <span className="h-1.5 w-1.5 rounded-full bg-current" />
}

export default function PipelineStepper({ states }) {
  return (
    <div className="flex items-start">
      {STAGES.map((stage, i) => {
        const state = states[i] || 'pending'
        const style = STYLES[state]
        const isLast = i === STAGES.length - 1
        return (
          <div key={stage.key} className={`flex items-center ${isLast ? '' : 'flex-1'}`}>
            <div className="flex flex-col items-center gap-2 px-1">
              <div
                className="flex h-9 w-9 items-center justify-center rounded-full transition-colors duration-300"
                style={{
                  background: style.bg,
                  color: state === 'pending' ? style.fg : style.fg,
                  border: `1.5px solid ${style.ring}`,
                }}
              >
                <Icon state={state} />
              </div>
              <div className="text-center">
                <div
                  className="text-[13px] font-semibold"
                  style={{ color: state === 'pending' ? 'var(--text-dim)' : 'var(--text)' }}
                >
                  {stage.label}
                </div>
                <div className="hidden text-[11px] text-[var(--text-dim)] sm:block">{stage.hint}</div>
              </div>
            </div>
            {!isLast && (
              <div
                className="mx-2 mt-[-22px] h-[2px] flex-1 rounded-full transition-colors duration-500"
                style={{ background: state === 'done' ? 'var(--green)' : 'var(--border)' }}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
