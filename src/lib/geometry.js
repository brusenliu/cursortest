function fmt(n) {
  return (Math.round(n * 100) / 100).toFixed(2)
}

function rotateAround(x, y, cx, cy, deg) {
  if (!deg) return [x, y]
  const rad = (deg * Math.PI) / 180
  const c = Math.cos(rad)
  const s = Math.sin(rad)
  const dx = x - cx
  const dy = y - cy
  return [cx + dx * c - dy * s, cy + dx * s + dy * c]
}

export function circlePath(cx, cy, r) {
  const x1 = fmt(cx - r)
  const x2 = fmt(cx + r)
  const y = fmt(cy)
  const rr = fmt(r)
  return `M ${x1} ${y} A ${rr} ${rr} 0 1 0 ${x2} ${y} A ${rr} ${rr} 0 1 0 ${x1} ${y} Z`
}

function ellipsePath(cx, cy, rx, ry, rotation) {
  const rad = (rotation * Math.PI) / 180
  const c = Math.cos(rad)
  const s = Math.sin(rad)
  const x1 = cx + rx * c
  const y1 = cy + rx * s
  const x2 = cx - rx * c
  const y2 = cy - rx * s
  const sx = fmt(rx)
  const sy = fmt(ry)
  const rot = fmt(rotation || 0)
  return `M ${fmt(x1)} ${fmt(y1)} A ${sx} ${sy} ${rot} 1 0 ${fmt(x2)} ${fmt(y2)} A ${sx} ${sy} ${rot} 1 0 ${fmt(x1)} ${fmt(y1)} Z`
}

export function starPath(cx, cy, r, points, rotation = 0) {
  const n = Math.max(3, Math.round(points) || 5)
  const inner = r * 0.42
  const rot = ((rotation || 0) * Math.PI) / 180
  let d = ''
  for (let i = 0; i < n * 2; i++) {
    const a = rot - Math.PI / 2 + (i * Math.PI) / n
    const rr = i % 2 === 0 ? r : inner
    const x = cx + Math.cos(a) * rr
    const y = cy + Math.sin(a) * rr
    d += `${i === 0 ? 'M' : 'L'} ${fmt(x)} ${fmt(y)} `
  }
  return `${d}Z`
}

function squarePath(cx, cy, size, rotation) {
  const pts = [
    [cx - size, cy - size],
    [cx + size, cy - size],
    [cx + size, cy + size],
    [cx - size, cy + size],
  ].map(([x, y]) => rotateAround(x, y, cx, cy, rotation))
  return `M ${fmt(pts[0][0])} ${fmt(pts[0][1])} L ${fmt(pts[1][0])} ${fmt(pts[1][1])} L ${fmt(pts[2][0])} ${fmt(pts[2][1])} L ${fmt(pts[3][0])} ${fmt(pts[3][1])} Z`
}

function heartPath(cx, cy, r, rotation) {
  const s = r / 12
  const raw = [
    ['M', 16, 28],
    ['C', 16, 28, 4, 20, 4, 12],
    ['C', 4, 8, 7, 5, 10.5, 5],
    ['C', 13, 5, 15, 6.5, 16, 8.5],
    ['C', 17, 6.5, 19, 5, 21.5, 5],
    ['C', 25, 5, 28, 8, 28, 12],
    ['C', 28, 20, 16, 28, 16, 28],
  ]
  const map = (x, y) => {
    const lx = (x - 16) * s
    const ly = (y - 16.5) * s
    const [rx, ry] = rotateAround(cx + lx, cy + ly, cx, cy, rotation)
    return `${fmt(rx)} ${fmt(ry)}`
  }
  return `${raw
    .map((cmd) => {
      if (cmd[0] === 'M') return `M ${map(cmd[1], cmd[2])}`
      return `C ${map(cmd[1], cmd[2])} ${map(cmd[3], cmd[4])} ${map(cmd[5], cmd[6])}`
    })
    .join(' ')} Z`
}

/** SVG path for one dot. Canvas Path2D uses the same string. */
export function dotPath(dot) {
  const { x, y, size, shape, rotation = 0 } = dot
  switch (shape) {
    case 'ring':
    case 'circle':
      return circlePath(x, y, size)
    case 'ellipse':
      return ellipsePath(x, y, size, Math.max(0.4, size * (dot.ellipseRatio || 0.62)), rotation)
    case 'star':
      return starPath(x, y, size, dot.starPoints || 5, rotation)
    case 'square':
      return squarePath(x, y, size, rotation)
    case 'heart':
      return heartPath(x, y, size, rotation)
    default:
      return circlePath(x, y, size)
  }
}
