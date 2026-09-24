import { useCallback, useEffect, useRef, useState } from 'react'

// Wheel-zoom, drag-to-pan and a stable "zoom toward the current center" model
// shared by the plot viewer and the diagram viewer -- both scroll a viewport
// element and scale an inner element by the same factor, so the math for
// keeping the viewport centered on re-scale only needs writing once.
export function useZoomPan({ min = 1, max = 5, step = 0.25, enableKeyboard = false } = {}) {
  const [scale, setScale] = useState(min)
  const viewportRef = useRef(null)
  const dragRef = useRef(null)
  // What "reset"/the fit button returns to. Defaults to `min`, but content
  // that's larger than its viewport (e.g. a big diagram) wants that button
  // to land on a computed fit-to-window scale instead -- see `setFit`.
  const fitRef = useRef(min)

  const changeScale = useCallback(
    (next) => {
      const clamped = Math.max(min, Math.min(max, next))
      const viewport = viewportRef.current
      if (!viewport) {
        setScale(clamped)
        return
      }
      const xRatio = (viewport.scrollLeft + viewport.clientWidth / 2) / viewport.scrollWidth
      const yRatio = (viewport.scrollTop + viewport.clientHeight / 2) / viewport.scrollHeight
      setScale(clamped)
      requestAnimationFrame(() => {
        viewport.scrollLeft = xRatio * viewport.scrollWidth - viewport.clientWidth / 2
        viewport.scrollTop = yRatio * viewport.scrollHeight - viewport.clientHeight / 2
      })
    },
    [min, max],
  )

  const zoomIn = useCallback(() => changeScale(scale + step), [scale, step, changeScale])
  const zoomOut = useCallback(() => changeScale(scale - step), [scale, step, changeScale])
  const reset = useCallback(() => changeScale(fitRef.current), [changeScale])
  const toggle = useCallback(
    () => changeScale(scale === fitRef.current ? fitRef.current * 2 : fitRef.current),
    [scale, changeScale],
  )
  // Records a computed fit-to-window scale as the new "reset" target and
  // jumps straight to it -- called once content first measures its own size.
  const setFit = useCallback(
    (value) => {
      fitRef.current = value
      changeScale(value)
    },
    [changeScale],
  )

  useEffect(() => {
    if (!enableKeyboard) return
    const onKeyDown = (event) => {
      if (event.key === '+' || event.key === '=') changeScale(scale + step)
      if (event.key === '-') changeScale(scale - step)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [enableKeyboard, scale, step, changeScale])

  const handlers = {
    onWheel: (event) => {
      event.preventDefault()
      changeScale(scale + (event.deltaY < 0 ? step : -step))
    },
    onDoubleClick: toggle,
    onPointerDown: (event) => {
      if (event.button !== 0) return
      const viewport = viewportRef.current
      dragRef.current = { x: event.clientX, y: event.clientY, left: viewport.scrollLeft, top: viewport.scrollTop }
      viewport.setPointerCapture(event.pointerId)
    },
    onPointerMove: (event) => {
      if (!dragRef.current) return
      const viewport = viewportRef.current
      viewport.scrollLeft = dragRef.current.left - (event.clientX - dragRef.current.x)
      viewport.scrollTop = dragRef.current.top - (event.clientY - dragRef.current.y)
    },
    onPointerUp: (event) => {
      dragRef.current = null
      if (viewportRef.current?.hasPointerCapture(event.pointerId)) {
        viewportRef.current.releasePointerCapture(event.pointerId)
      }
    },
    onPointerCancel: () => {
      dragRef.current = null
    },
  }

  return { scale, min, max, step, viewportRef, changeScale, zoomIn, zoomOut, reset, setFit, handlers }
}
