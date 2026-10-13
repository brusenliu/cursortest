export default function Preview({ svg, picture, movable, showGuide, center, radius, onCenter, onPositionStart, onPositionEnd }) {
  function pointFromEvent(event) {
    const rect = event.currentTarget.getBoundingClientRect()
    const x = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width))
    const y = Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height))
    return {
      x: Math.round(x * 1000) / 1000,
      y: Math.round(y * 1000) / 1000,
    }
  }

  function finishGesture() {
    onPositionEnd?.()
  }

  function onPointerDown(event) {
    if (!movable || event.button !== 0) return
    event.currentTarget.setPointerCapture(event.pointerId)
    onPositionStart?.()
    onCenter(pointFromEvent(event))
  }

  function onPointerMove(event) {
    if (!movable || !event.currentTarget.hasPointerCapture(event.pointerId)) return
    onCenter(pointFromEvent(event))
  }

  function onKeyDown(event) {
    if (!movable) return
    const step = event.shiftKey ? 0.02 : 0.005
    const next = { ...center }
    if (event.key === 'ArrowLeft') next.x -= step
    else if (event.key === 'ArrowRight') next.x += step
    else if (event.key === 'ArrowUp') next.y -= step
    else if (event.key === 'ArrowDown') next.y += step
    else return
    event.preventDefault()
    onPositionStart?.()
    onCenter({
      x: Math.min(1, Math.max(0, Math.round(next.x * 1000) / 1000)),
      y: Math.min(1, Math.max(0, Math.round(next.y * 1000) / 1000)),
    })
    onPositionEnd?.()
  }

  return (
    <main className="stage-wrap">
      <div
        className={`stage${movable ? ' is-radial' : ''}`}
        style={{ aspectRatio: `${picture.width} / ${picture.height}` }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={finishGesture}
        onPointerCancel={finishGesture}
        onKeyDown={onKeyDown}
        tabIndex={movable ? 0 : -1}
        aria-label={movable ? '拖动以移动中心' : picture.kind === 'lines' ? '线纹预览' : '波点预览'}
      >
        <div className="checker" dangerouslySetInnerHTML={{ __html: svg }} />
        {showGuide && (
          <svg className="guide" viewBox={`0 0 ${picture.width} ${picture.height}`} aria-hidden="true">
            <circle
              cx={center.x * picture.width}
              cy={center.y * picture.height}
              r={radius}
              fill="none"
              stroke="#0d99ff"
              strokeWidth="1.5"
              strokeDasharray="5 4"
            />
          </svg>
        )}
        {movable && (
          <span
            className="handle"
            style={{ left: `${center.x * 100}%`, top: `${center.y * 100}%` }}
            aria-hidden="true"
          />
        )}
      </div>
    </main>
  )
}
