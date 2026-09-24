import { useCallback, useEffect, useState } from 'react'

function parse(hash) {
  const path = hash.replace(/^#/, '') || '/'
  const match = path.match(/^\/projects\/([^/]+)\/?$/)
  if (match) return { name: 'detail', projectId: decodeURIComponent(match[1]) }
  return { name: 'gallery' }
}

export function useHashRoute() {
  const [route, setRoute] = useState(() => parse(window.location.hash))

  useEffect(() => {
    const onHashChange = () => setRoute(parse(window.location.hash))
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  const navigate = useCallback((path) => {
    window.location.hash = path
  }, [])

  return { route, navigate }
}
