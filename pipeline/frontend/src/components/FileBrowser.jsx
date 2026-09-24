import {
  ChevronRight,
  Download,
  File as FileIcon,
  FileCode2,
  FileJson,
  FileSpreadsheet,
  FileText,
  Folder,
  FolderOpen,
  Image as ImageIcon,
  Loader2,
  RefreshCw,
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { archiveDownloadUrl, fileDownloadUrl, listProjectFiles, previewProjectFile } from '../api'
import CodeBlock, { languageForFilename } from './CodeBlock'
import MarkdownView from './MarkdownView'

function isMarkdown(path = '') {
  return path.split('.').pop()?.toLowerCase() === 'md'
}

const ICON_BY_SUFFIX = {
  mo: FileCode2,
  mos: FileCode2,
  sysml: FileCode2,
  py: FileCode2,
  puml: FileCode2,
  json: FileJson,
  jsonl: FileJson,
  csv: FileSpreadsheet,
  xlsx: FileSpreadsheet,
  png: ImageIcon,
  jpg: ImageIcon,
  jpeg: ImageIcon,
  txt: FileText,
  md: FileText,
  mmd: FileText,
  pdf: FileText,
  docx: FileText,
}

function iconFor(entry) {
  if (entry.type === 'dir') return Folder
  const suffix = entry.name.split('.').pop()?.toLowerCase()
  return ICON_BY_SUFFIX[suffix] || FileIcon
}

function formatSize(bytes) {
  if (bytes == null) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

/** One directory level. Children load on expand, so opening a project does not
 *  walk the whole tree -- an archived Stage 3 run can hold hundreds of files. */
function TreeNode({ projectId, entry, depth, selectedPath, onSelect, refreshToken }) {
  const [open, setOpen] = useState(false)
  const [children, setChildren] = useState(null)
  const [loading, setLoading] = useState(false)
  const Icon = iconFor(entry)
  const isDir = entry.type === 'dir'
  const isSelected = selectedPath === entry.path

  useEffect(() => {
    setOpen(false)
    setChildren(null)
  }, [refreshToken])

  const toggle = () => {
    if (!isDir) {
      onSelect(entry)
      return
    }
    const next = !open
    setOpen(next)
    if (next && children === null) {
      setLoading(true)
      listProjectFiles(projectId, entry.path)
        .then((data) => setChildren(data.entries))
        .catch(() => setChildren([]))
        .finally(() => setLoading(false))
    }
  }

  return (
    <div>
      <div
        className="group flex items-center gap-1.5 rounded-md py-1 pr-2 text-[12.5px]"
        style={{
          paddingLeft: `${depth * 14 + 8}px`,
          background: isSelected ? 'var(--panel-2)' : 'transparent',
          color: isSelected ? 'var(--text)' : 'var(--text-dim)',
        }}
      >
        <button type="button" onClick={toggle} className="flex min-w-0 flex-1 items-center gap-1.5 text-left">
          {isDir ? (
            <ChevronRight
              className="h-3 w-3 shrink-0 transition-transform"
              style={{ transform: open ? 'rotate(90deg)' : 'none' }}
            />
          ) : (
            <span className="w-3 shrink-0" />
          )}
          {isDir && open ? (
            <FolderOpen className="h-3.5 w-3.5 shrink-0" />
          ) : (
            <Icon className="h-3.5 w-3.5 shrink-0" />
          )}
          <span className="truncate">{entry.name}</span>
          {!isDir && <span className="shrink-0 text-[10.5px] opacity-60">{formatSize(entry.size)}</span>}
        </button>
        <a
          href={isDir ? archiveDownloadUrl(projectId, entry.path) : fileDownloadUrl(projectId, entry.path)}
          title={isDir ? 'Download folder as .zip' : 'Download file'}
          className="shrink-0 opacity-0 transition-opacity group-hover:opacity-70 hover:!opacity-100"
        >
          <Download className="h-3.5 w-3.5" />
        </a>
      </div>

      {isDir && open && (
        <div>
          {loading && (
            <div className="flex items-center gap-1.5 py-1 text-[11.5px] text-[var(--text-dim)]" style={{ paddingLeft: `${(depth + 1) * 14 + 22}px` }}>
              <Loader2 className="h-3 w-3 animate-spin" /> loading
            </div>
          )}
          {!loading && children?.length === 0 && (
            <div className="py-1 text-[11.5px] italic opacity-50" style={{ paddingLeft: `${(depth + 1) * 14 + 22}px` }}>
              empty
            </div>
          )}
          {!loading &&
            children?.map((child) => (
              <TreeNode
                key={child.path}
                projectId={projectId}
                entry={child}
                depth={depth + 1}
                selectedPath={selectedPath}
                onSelect={onSelect}
                refreshToken={refreshToken}
              />
            ))}
        </div>
      )}
    </div>
  )
}

export default function FileBrowser({ projectId, refreshToken }) {
  const [entries, setEntries] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null)
  const [preview, setPreview] = useState(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [localToken, setLocalToken] = useState(0)

  const token = `${refreshToken}-${localToken}`

  const load = useCallback(() => {
    setLoading(true)
    setSelected(null)
    setPreview(null)
    listProjectFiles(projectId)
      .then((data) => setEntries(data.entries))
      .catch(() => setEntries([]))
      .finally(() => setLoading(false))
  }, [projectId])

  useEffect(() => {
    load()
  }, [load, refreshToken, localToken])

  useEffect(() => {
    if (!selected || selected.type === 'dir') return
    if (!selected.previewable) {
      setPreview({ unpreviewable: 'binary or large file — use the download button' })
      return
    }
    let cancelled = false
    setPreviewLoading(true)
    previewProjectFile(projectId, selected.path)
      .then((data) => !cancelled && setPreview(data))
      .catch((error) => !cancelled && setPreview({ unpreviewable: error.message }))
      .finally(() => !cancelled && setPreviewLoading(false))
    return () => {
      cancelled = true
    }
  }, [projectId, selected])

  return (
    <div className="flex h-full min-h-0">
      <div className="flex w-[300px] shrink-0 flex-col border-r border-[var(--border)]">
        <div className="flex items-center justify-between gap-2 border-b border-[var(--border)] px-3 py-1.5">
          <span className="text-[11px] font-semibold uppercase tracking-wide text-[var(--text-dim)]">
            Project folder
          </span>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => setLocalToken((value) => value + 1)}
              title="Refresh"
              className="rounded p-1 text-[var(--text-dim)] hover:text-[var(--text)]"
            >
              <RefreshCw className="h-3.5 w-3.5" />
            </button>
            <a
              href={archiveDownloadUrl(projectId)}
              title="Download the whole project as .zip"
              className="flex items-center gap-1 rounded px-1.5 py-1 text-[11px] text-[var(--text-dim)] hover:text-[var(--text)]"
            >
              <Download className="h-3.5 w-3.5" /> All
            </a>
          </div>
        </div>
        <div className="min-h-0 flex-1 overflow-auto py-1">
          {loading && (
            <div className="flex items-center gap-2 px-3 py-2 text-[12px] text-[var(--text-dim)]">
              <Loader2 className="h-3.5 w-3.5 animate-spin" /> loading
            </div>
          )}
          {!loading &&
            entries?.map((entry) => (
              <TreeNode
                key={entry.path}
                projectId={projectId}
                entry={entry}
                depth={0}
                selectedPath={selected?.path}
                onSelect={setSelected}
                refreshToken={token}
              />
            ))}
          {!loading && entries?.length === 0 && (
            <div className="px-3 py-2 text-[12px] italic text-[var(--text-dim)]">no files yet</div>
          )}
        </div>
      </div>

      <div className="flex min-w-0 flex-1 flex-col">
        {!selected && (
          <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-[var(--text-dim)]">
            <Folder className="h-6 w-6 opacity-40" />
            <span className="text-[13px]">Select a file to preview it</span>
            <span className="text-[11.5px] opacity-70">Hover any row to download it</span>
          </div>
        )}
        {selected && (
          <>
            <div className="flex items-center justify-between gap-2 border-b border-[var(--border)] bg-[var(--bg-soft)] px-3 py-1.5">
              <span className="font-mono min-w-0 truncate text-[11px] text-[var(--text-dim)]">{selected.path}</span>
              <a
                href={fileDownloadUrl(projectId, selected.path)}
                className="flex shrink-0 items-center gap-1 rounded-lg px-2 py-1 text-[11.5px] font-medium text-[var(--text-dim)] hover:text-[var(--text)]"
              >
                <Download className="h-3.5 w-3.5" /> Download
              </a>
            </div>
            <div className="min-h-0 flex-1 overflow-auto">
              {previewLoading && (
                <div className="flex h-full items-center justify-center gap-2 text-sm text-[var(--text-dim)]">
                  <Loader2 className="h-4 w-4 animate-spin" /> loading
                </div>
              )}
              {!previewLoading && preview?.unpreviewable && (
                <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-[var(--text-dim)]">
                  <FileIcon className="h-6 w-6 opacity-40" />
                  <span className="text-[13px]">{preview.unpreviewable}</span>
                </div>
              )}
              {!previewLoading && preview?.content != null && isMarkdown(selected.path) && (
                <MarkdownView text={preview.content} />
              )}
              {!previewLoading &&
                preview?.content != null &&
                !isMarkdown(selected.path) &&
                languageForFilename(selected.path) && (
                  <CodeBlock
                    code={preview.content}
                    language={languageForFilename(selected.path)}
                    className="text-[12px]"
                  />
                )}
              {!previewLoading &&
                preview?.content != null &&
                !isMarkdown(selected.path) &&
                !languageForFilename(selected.path) && (
                  <pre className="font-mono whitespace-pre-wrap px-4 py-3 text-[12px] leading-relaxed text-[var(--text)]">
                    {preview.content}
                  </pre>
                )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
