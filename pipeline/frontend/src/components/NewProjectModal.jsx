import { File, Loader2, UploadCloud, X } from 'lucide-react'
import { useRef, useState } from 'react'

export default function NewProjectModal({ onClose, onCreate }) {
  const [name, setName] = useState('')
  const [stage1Backend, setStage1Backend] = useState('ollama')
  const [files, setFiles] = useState([])
  const [dragging, setDragging] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  const addFiles = (list) => setFiles((f) => [...f, ...Array.from(list)])

  const submit = async () => {
    if (!name.trim() || files.length === 0) return
    setBusy(true)
    setError(null)
    try {
      await onCreate(name.trim(), files, stage1Backend)
    } catch (e) {
      setError(e.message)
      setBusy(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="fade-up w-full max-w-lg overflow-hidden rounded-2xl border border-[var(--border-strong)] bg-[var(--panel)] shadow-2xl">
        <div className="flex items-center justify-between border-b border-[var(--border)] px-5 py-4">
          <div className="text-[15px] font-semibold text-[var(--text)]">New simulation project</div>
          <button type="button" onClick={onClose} className="text-[var(--text-dim)] hover:text-[var(--text)]">
            <X className="h-4.5 w-4.5" />
          </button>
        </div>

        <div className="space-y-4 px-5 py-5">
          <div>
            <label className="mb-1.5 block text-[12px] font-medium text-[var(--text-muted)]">Project name</label>
            <input
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Evaporation Tank System"
              className="w-full rounded-lg border border-[var(--border-strong)] bg-[var(--bg-soft)] px-3 py-2 text-[13.5px] text-[var(--text)] outline-none focus:border-[var(--accent)]"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-[12px] font-medium text-[var(--text-muted)]">
              Document extraction
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setStage1Backend('ollama')}
                className="rounded-lg border px-3 py-2 text-left text-[12px]"
                style={{
                  borderColor: stage1Backend === 'ollama' ? 'var(--accent)' : 'var(--border-strong)',
                  background: stage1Backend === 'ollama' ? 'var(--accent-soft)' : 'transparent',
                }}
              >
                <div className="font-semibold text-[var(--text)]">Local Gemma</div>
                <div className="mt-0.5 text-[11px] text-[var(--text-dim)]">Private text extraction through Ollama</div>
              </button>
              <button
                type="button"
                onClick={() => setStage1Backend('openai')}
                className="rounded-lg border px-3 py-2 text-left text-[12px]"
                style={{
                  borderColor: stage1Backend === 'openai' ? 'var(--accent)' : 'var(--border-strong)',
                  background: stage1Backend === 'openai' ? 'var(--accent-soft)' : 'transparent',
                }}
              >
                <div className="font-semibold text-[var(--text)]">Cloud GPT-5.4</div>
                <div className="mt-0.5 text-[11px] text-[var(--text-dim)]">OpenAI extraction with visual support</div>
              </button>
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-[12px] font-medium text-[var(--text-muted)]">
              Source documents
            </label>
            <div
              onDragOver={(e) => {
                e.preventDefault()
                setDragging(true)
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault()
                setDragging(false)
                addFiles(e.dataTransfer.files)
              }}
              onClick={() => inputRef.current?.click()}
              className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed px-4 py-8 text-center transition-colors"
              style={{
                borderColor: dragging ? 'var(--accent)' : 'var(--border-strong)',
                background: dragging ? 'var(--accent-soft)' : 'transparent',
              }}
            >
              <UploadCloud className="h-6 w-6 text-[var(--text-dim)]" />
              <div className="text-[12.5px] text-[var(--text-muted)]">
                Drop files here, or <span className="text-[var(--accent)]">browse</span>
              </div>
              <div className="text-[11px] text-[var(--text-dim)]">PDF, DOCX, XLSX, CSV, images, code, text</div>
              <input
                ref={inputRef}
                type="file"
                multiple
                hidden
                onChange={(e) => addFiles(e.target.files)}
              />
            </div>

            {files.length > 0 && (
              <div className="mt-2 flex max-h-32 flex-col gap-1 overflow-y-auto">
                {files.map((f, i) => (
                  <div
                    key={`${f.name}-${i}`}
                    className="flex items-center justify-between rounded-lg bg-[var(--bg-soft)] px-2.5 py-1.5 text-[12px] text-[var(--text-muted)]"
                  >
                    <span className="flex min-w-0 items-center gap-1.5 truncate">
                      <File className="h-3.5 w-3.5 shrink-0" /> {f.name}
                    </span>
                    <button
                      type="button"
                      onClick={() => setFiles((fs) => fs.filter((_, idx) => idx !== i))}
                      className="shrink-0 text-[var(--text-dim)] hover:text-[var(--red)]"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {error && <div className="text-[12px] text-[var(--red)]">{error}</div>}
        </div>

        <div className="flex justify-end gap-2 border-t border-[var(--border)] px-5 py-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-[var(--border-strong)] px-4 py-2 text-[12.5px] font-medium text-[var(--text-muted)]"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={!name.trim() || files.length === 0 || busy}
            onClick={submit}
            className="flex items-center gap-2 rounded-lg px-4 py-2 text-[12.5px] font-semibold text-white transition-colors hover:bg-[var(--accent-strong)] disabled:opacity-40"
            style={{ background: 'var(--accent)' }}
          >
            {busy && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
            Create project
          </button>
        </div>
      </div>
    </div>
  )
}
