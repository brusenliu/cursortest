import { useState } from 'react'
import { IconDots, IconLines } from './icons.jsx'

export default function Preview({
  svg,
  picture,
  movable,
  showGuide,
  center,
  radius,
  category,
  presetName,
  countLabel,
  tuning,
  onCenter,
  onPositionStart,
  onPositionEnd,
}) {
  const [dragging, setDragging] = useState(false)
  const lines = category === 'lines'
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
    setDragging(false)
    onPositionEnd?.()
  }

  function onPointerDown(event) {
    if (!movable || event.button !== 0) return
    event.currentTarget.setPointerCapture(event.pointerId)
    setDragging(true)
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

  const stageClass = [
    'stage',
    movable ? 'is-radial' : '',
    dragging ? 'is-dragging' : '',
    tuning && !dragging ? 'is-live' : '',
  ].filter(Boolean).join(' ')

  return (
    <main className="stage-wrap">
      <div className="stage-frame" key={`${category}:${presetName}`}>
      <div className="stage-meta">
        <p className="stage-path" aria-live="polite">
          {lines ? <IconLines /> : <IconDots />}
          <span>{lines ? '线纹' : '波点'}</span>
          <span className="stage-sep" aria-hidden="true">/</span>
          <span className="stage-name">{presetName}</span>
        </p>
        <p className={movable ? 'stage-aside is-hint' : 'stage-aside'}>
          {dragging ? '正在移动中心' : movable ? `拖动预览移动中心 · ${countLabel}` : countLabel}
        </p>
      </div>
      <div
        className={stageClass}
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
              strokeWidth={dragging ? 2.25 : 1.5}
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
      </div>
    </main>
  )
}
