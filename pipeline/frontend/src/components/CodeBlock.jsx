import Prism from 'prismjs'
import 'prismjs/components/prism-clike'
import 'prismjs/components/prism-json'
import { useMemo } from 'react'

if (!Prism.languages.modelica) {
  Prism.languages.modelica = Prism.languages.extend('clike', {
    keyword:
      /\b(?:model|class|package|connector|block|function|record|type|operator|extends|import|within|public|protected|equation|algorithm|parameter|constant|input|output|flow|stream|der|initial|final|replaceable|redeclare|annotation|connect|if|then|else|elseif|for|in|while|loop|when|elsewhen|end|partial|each|inner|outer|discrete|encapsulated)\b/,
    builtin: /\b(?:Real|Integer|Boolean|String)\b/,
    boolean: /\b(?:true|false)\b/,
    number: /\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b/,
  })
}

if (!Prism.languages.sysml) {
  Prism.languages.sysml = Prism.languages.extend('clike', {
    keyword:
      /\b(?:package|part|def|attribute|item|action|state|connection|port|interface|import|private|public|protected|redefines|subsets|specializes|in|out|inout|ref|feature|enum|calc|constraint|requirement|satisfy|use|case|view|viewpoint|rendering|metadata|doc|comment|about|language|alias|individual|abstract|variation|succession|first|then|if|else|for|while|loop|return|assign|bind|flow|perform|exhibit|include|allocate|connect|to|from|end)\b/,
    boolean: /\b(?:true|false)\b/,
    number: /\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b/,
  })
}

export const LANGUAGE_BY_EXTENSION = {
  mo: 'modelica',
  mos: 'modelica',
  sysml: 'sysml',
  json: 'json',
  jsonl: 'json',
}

export function languageForFilename(filename = '') {
  const ext = filename.split('.').pop()?.toLowerCase()
  return LANGUAGE_BY_EXTENSION[ext] || null
}

// json files come back as compact text off disk -- indent them before
// highlighting so the browser shows structure instead of one long line.
// A jsonl blob (one JSON object per line) simply fails to parse as a whole
// document, so it's left untouched rather than collapsed into one object.
function prettyPrintIfJson(code, language) {
  if (language !== 'json') return code
  try {
    return JSON.stringify(JSON.parse(code), null, 2)
  } catch {
    return code
  }
}

export default function CodeBlock({ code, language, className = '' }) {
  const source = useMemo(() => prettyPrintIfJson(code, language), [code, language])
  const html = useMemo(() => {
    const grammar = language && Prism.languages[language]
    if (!grammar) return null
    try {
      return Prism.highlight(source || '', grammar, language)
    } catch {
      return null
    }
  }, [source, language])

  if (html == null) {
    return (
      <pre className={`font-mono px-5 py-4 text-[12.5px] leading-relaxed text-[var(--text)] ${className}`}>
        <code>{source}</code>
      </pre>
    )
  }

  return (
    <pre className={`font-mono px-5 py-4 text-[12.5px] leading-relaxed ${className}`}>
      <code className={`language-${language}`} dangerouslySetInnerHTML={{ __html: html }} />
    </pre>
  )
}
