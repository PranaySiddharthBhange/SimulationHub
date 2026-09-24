import { useCallback, useEffect, useState } from 'react'

const THEME_EVENT = 'simulationhub:theme-change'

function readCurrentTheme() {
  if (typeof document !== 'undefined') {
    const attr = document.documentElement.getAttribute('data-theme')
    if (attr === 'light' || attr === 'dark') return attr
  }
  return 'light'
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme)
  try {
    localStorage.setItem('theme', theme)
  } catch {
    // localStorage may be unavailable (private mode, blocked storage) -- theme still works for this session.
  }
  window.dispatchEvent(new CustomEvent(THEME_EVENT, { detail: theme }))
}

// The <html data-theme> attribute is set synchronously by an inline script in
// index.html (before React mounts) so the correct theme paints on first
// frame. Every component that calls this hook gets its own React state
// mirroring that attribute, so a `themechange` event keeps every instance in
// sync when any one of them (e.g. the header toggle) flips the theme.
export function useTheme() {
  const [theme, setTheme] = useState(readCurrentTheme)

  useEffect(() => {
    const onThemeChange = (event) => setTheme(event.detail)
    window.addEventListener(THEME_EVENT, onThemeChange)
    return () => window.removeEventListener(THEME_EVENT, onThemeChange)
  }, [])

  const toggleTheme = useCallback(() => {
    setTheme((t) => {
      const next = t === 'dark' ? 'light' : 'dark'
      applyTheme(next)
      return next
    })
  }, [])

  return { theme, toggleTheme }
}
