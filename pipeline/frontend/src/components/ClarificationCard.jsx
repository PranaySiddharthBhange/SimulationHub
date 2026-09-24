import { CheckCircle2, HelpCircle, UserRoundCog } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

export default function ClarificationCard({ clarifications, stage, onSubmit, onUseDefaults, busy }) {
  const [answers, setAnswers] = useState({})
  const hasDefaults = clarifications.length > 0 && clarifications.every((c) => c.suggested_value?.trim())
  // Two different asks share this card: decisions Merge could not make, and
  // decisions it already made from the evidence and wants signed off. Counting
  // them separately keeps the header honest about what is actually required.
  const openCount = clarifications.filter((c) => !c.resolved).length
  const resolvedCount = clarifications.length - openCount
  const clarificationSignature = clarifications
    .map((c) => `${c.id}|${c.question}|${c.suggested_value}|${(c.options || []).join('\u001f')}`)
    .join('\u001e')
  const previousSignature = useRef(null)

  useEffect(() => {
    if (previousSignature.current === clarificationSignature) return
    previousSignature.current = clarificationSignature
    setAnswers(Object.fromEntries(clarifications.map((c) => [c.id, c.suggested_value])))
  }, [clarificationSignature, clarifications])

  const setAnswer = (id, value) => setAnswers((a) => ({ ...a, [id]: value }))

  return (
    <div
      className="fade-up flex h-full flex-col overflow-hidden rounded-xl border bg-[#fdfaf4]"
      style={{ borderColor: 'var(--border-strong)', borderLeft: '3px solid var(--amber)' }}
    >
      <div className="flex shrink-0 items-center gap-3 border-b border-[var(--border)] px-5 py-3.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#faf1de] text-[var(--amber)]">
          <UserRoundCog className="h-4.5 w-4.5" />
        </div>
        <div>
          <div className="text-sm font-semibold text-[var(--text)]">
            {openCount > 0
              ? stage === 'clarify' ? 'Merge needs a decision' : 'SysML generation needs a decision'
              : 'Confirm the decisions Merge made'}
          </div>
          <div className="text-[12px] text-[var(--text-muted)]">
            {openCount > 0 && (
              <>
                {openCount} open question{openCount > 1 ? 's' : ''} the evidence does not settle.{' '}
              </>
            )}
            {resolvedCount > 0 && (
              <>
                {resolvedCount} conflict{resolvedCount > 1 ? 's' : ''} already resolved from the evidence,
                shown so you can confirm or overrule {resolvedCount > 1 ? 'them' : 'it'}.{' '}
              </>
            )}
            {hasDefaults ? 'Accept the suggested values, or change any of them.' : 'Provide an answer for each question to continue.'}
          </div>
        </div>
      </div>

      <div className="min-h-0 flex-1 divide-y divide-[var(--border)] overflow-y-auto">
        {clarifications.map((c) => (
          <div key={c.id} className="px-5 py-4" style={c.resolved ? { background: 'rgba(34,197,94,0.04)' } : undefined}>
            <div className="mb-1.5 flex items-center gap-1.5">
              {c.resolved ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-[var(--green,#16a34a)]" />
                  <span className="text-[10.5px] font-semibold uppercase tracking-wide text-[var(--green,#16a34a)]">
                    Resolved from evidence -- confirm or change
                  </span>
                </>
              ) : (
                <>
                  <HelpCircle className="h-3.5 w-3.5 shrink-0 text-[var(--amber)]" />
                  <span className="text-[10.5px] font-semibold uppercase tracking-wide text-[var(--amber)]">
                    Open question -- your decision
                  </span>
                </>
              )}
            </div>
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
                        <span
                          className="ml-1.5 text-[10px] font-normal"
                          style={{ color: c.resolved ? 'var(--green,#16a34a)' : 'var(--amber)' }}
                        >
                          {c.resolved ? 'resolved' : 'suggested'}
                        </span>
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
              {!c.options?.length && c.suggested_value?.trim() && (
                <span className="shrink-0 text-[11px] text-[var(--text-dim)]">
                  suggested: <span className="text-[var(--amber)]">{c.suggested_value}</span>
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="flex shrink-0 items-center justify-end gap-2 border-t border-[var(--border)] px-5 py-3.5">
        {hasDefaults && (
          <button
            type="button"
            disabled={busy}
            onClick={onUseDefaults}
            className="rounded-lg border border-[var(--border-strong)] px-3.5 py-2 text-[12.5px] font-medium text-[var(--text-muted)] transition-colors hover:text-[var(--text)] disabled:opacity-50"
          >
            {openCount === 0 ? 'Confirm all' : 'Accept all suggested defaults'}
          </button>
        )}
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
