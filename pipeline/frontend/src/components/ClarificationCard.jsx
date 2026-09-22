import { UserRoundCog } from 'lucide-react'
import { useEffect, useState } from 'react'

export default function ClarificationCard({ clarifications, onSubmit, onUseDefaults, busy }) {
  const [answers, setAnswers] = useState({})

  useEffect(() => {
    setAnswers(Object.fromEntries(clarifications.map((c) => [c.id, c.suggested_value])))
  }, [clarifications])

  const setAnswer = (id, value) => setAnswers((a) => ({ ...a, [id]: value }))

  return (
    <div
      className="fade-up overflow-hidden rounded-xl border bg-[#fdfaf4]"
      style={{ borderColor: 'var(--border-strong)', borderLeft: '3px solid var(--amber)' }}
    >
      <div className="flex items-center gap-3 border-b border-[var(--border)] px-5 py-3.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#faf1de] text-[var(--amber)]">
          <UserRoundCog className="h-4.5 w-4.5" />
        </div>
        <div>
          <div className="text-sm font-semibold text-[var(--text)]">Stage 2 needs a decision</div>
          <div className="text-[12px] text-[var(--text-muted)]">
            The model paused on {clarifications.length} genuinely open question
            {clarifications.length > 1 ? 's' : ''} before writing the SysML model. Pick an answer, or accept its
            suggestion.
          </div>
        </div>
      </div>

      <div className="divide-y divide-[var(--border)]">
        {clarifications.map((c) => (
          <div key={c.id} className="px-5 py-4">
            <div className="text-[13.5px] font-medium text-[var(--text)]">{c.question}</div>
            <div className="mt-1 text-[12px] leading-relaxed text-[var(--text-muted)]">{c.reasoning}</div>

            {c.options?.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {c.options.map((opt) => {
                  const active = answers[c.id] === opt
                  const isSuggested = opt === c.suggested_value
                  return (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => setAnswer(c.id, opt)}
                      className="rounded-full border px-3 py-1.5 text-[12px] font-medium transition-colors"
                      style={
                        active
                          ? { borderColor: 'var(--amber)', background: '#faf1de', color: 'var(--accent-strong)' }
                          : { borderColor: 'var(--border-strong)', color: 'var(--text-muted)' }
                      }
                    >
                      {opt}
                      {isSuggested && (
                        <span className="ml-1.5 text-[10px] font-normal text-[var(--amber)]">suggested</span>
                      )}
                    </button>
                  )
                })}
              </div>
            )}

            <div className="mt-3 flex items-center gap-2">
              <input
                value={answers[c.id] ?? ''}
                onChange={(ev) => setAnswer(c.id, ev.target.value)}
                placeholder={c.suggested_value}
                className="font-mono w-full max-w-md rounded-lg border border-[var(--border-strong)] bg-white px-3 py-1.5 text-[12.5px] text-[var(--text)] outline-none focus:border-[var(--amber)]"
              />
              {!c.options?.length && (
                <span className="shrink-0 text-[11px] text-[var(--text-dim)]">
                  suggested: <span className="text-[var(--amber)]">{c.suggested_value}</span>
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-end gap-2 border-t border-[var(--border)] px-5 py-3.5">
        <button
          type="button"
          disabled={busy}
          onClick={onUseDefaults}
          className="rounded-lg border border-[var(--border-strong)] px-3.5 py-2 text-[12.5px] font-medium text-[var(--text-muted)] transition-colors hover:text-[var(--text)] disabled:opacity-50"
        >
          Accept all suggested defaults
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => onSubmit(answers)}
          className="rounded-lg px-4 py-2 text-[12.5px] font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          style={{ background: 'var(--amber)' }}
        >
          {busy ? 'Submitting…' : 'Submit my answers'}
        </button>
      </div>
    </div>
  )
}
