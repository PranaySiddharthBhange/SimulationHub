import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/** The merged engineering brief, rendered as the document it is.
 *
 *  Merge writes a structured Markdown file -- simulation settings, the brief,
 *  an acceptance-check table, what it resolved against what evidence, and what
 *  is still open. Rendering it as preformatted text hid exactly the parts a
 *  reviewer needs to scan, so the tables and headings are rendered properly and
 *  styled to match the rest of the panel rather than a default document theme.
 */
export default function MarkdownView({ text }) {
  return (
    <div className="fade-up px-5 py-4 text-[13.5px] leading-relaxed text-[var(--text)]">
      <Markdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="mb-3 text-[19px] font-semibold tracking-tight text-[var(--text)]">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="mt-6 mb-2 border-b border-[var(--border)] pb-1 text-[15px] font-semibold text-[var(--text)]">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="mt-4 mb-1.5 text-[13.5px] font-semibold text-[var(--text)]">{children}</h3>
          ),
          p: ({ children }) => <p className="my-2 whitespace-pre-wrap">{children}</p>,
          ul: ({ children }) => <ul className="my-2 list-disc space-y-1 pl-5">{children}</ul>,
          ol: ({ children }) => <ol className="my-2 list-decimal space-y-1 pl-5">{children}</ol>,
          strong: ({ children }) => <strong className="font-semibold text-[var(--text)]">{children}</strong>,
          code: ({ children }) => (
            <code className="font-mono rounded bg-[var(--bg-soft)] px-1 py-0.5 text-[12px] text-[var(--text)]">
              {children}
            </code>
          ),
          // A wrapper so a wide acceptance-check table scrolls on its own
          // instead of stretching the whole panel.
          table: ({ children }) => (
            <div className="my-3 overflow-x-auto rounded-lg border border-[var(--border)]">
              <table className="w-full border-collapse text-[12.5px]">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-[var(--bg-soft)]">{children}</thead>,
          th: ({ children }) => (
            <th className="border-b border-[var(--border)] px-2.5 py-1.5 text-left font-semibold text-[var(--text-dim)]">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border-b border-[var(--border)] px-2.5 py-1.5 align-top">{children}</td>
          ),
          a: ({ children, href }) => (
            <a href={href} className="underline decoration-dotted underline-offset-2">
              {children}
            </a>
          ),
        }}
      >
        {text}
      </Markdown>
    </div>
  )
}
