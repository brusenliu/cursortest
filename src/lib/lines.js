import { circlePath } from './geometry.js'
import { makeRng } from './rng.js'

function clamp(n, min, max) {
  return Math.min(max, Math.max(min, n))
}

function smoothstep(t) {
  const x = clamp(t, 0, 1)
  return x * x * (3 - 2 * x)
}

function fmt(n) {
  return (Math.round(n * 100) / 100).toFixed(2)
}

function linePath(x1, y1, x2, y2) {
  return `M ${fmt(x1)} ${fmt(y1)} L ${fmt(x2)} ${fmt(y2)}`
}

function polyPath(points) {
  return points.map((point, index) => `${index ? 'L' : 'M'} ${fmt(point[0])} ${fmt(point[1])}`).join(' ')
}

/** Clip a segment to an expanded canvas so the stroke still covers the edge. */
function clipSegment(x1, y1, x2, y2, minX, minY, maxX, maxY) {
  let t0 = 0
  let t1 = 1
  const dx = x2 - x1
  const dy = y2 - y1
  const p = [-dx, dx, -dy, dy]
  const q = [x1 - minX, maxX - x1, y1 - minY, maxY - y1]
  for (let i = 0; i < 4; i++) {
    if (Math.abs(p[i]) < 1e-8) {
      if (q[i] < 0) return null
    } else {
      const t = q[i] / p[i]
      if (p[i] < 0) {
        if (t > t1) return null
        if (t > t0) t0 = t
      } else {
        if (t < t0) return null
        if (t < t1) t1 = t
      }
    }
  }
  if (t1 - t0 < 1e-4) return null
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy]
}

function edgeOpacity(x, y, width, height, fadeWidth) {
  const dist = Math.min(x, y, width - x, height - y)
  if (dist <= 0) return 0
  return smoothstep(dist / fadeWidth)
}

function makeStroke(d, style, opacity) {
  return {
    d,
    color: style.color,
    strokeWidth: style.strokeWidth,
    opacity: Math.round(opacity * 1000) / 1000,
    dash: style.dash,
  }
}

function pushStraight(out, x1, y1, x2, y2, style, width, height, fadeWidth, edgeFade) {
  if (!edgeFade) {
    out.push(makeStroke(linePath(x1, y1, x2, y2), style, 1))
    return
  }
  const len = Math.hypot(x2 - x1, y2 - y1)
  const step = Math.max(32, fadeWidth * 0.4)
  const pieces = Math.max(1, Math.ceil(len / step))
  for (let i = 0; i < pieces; i++) {
    const t0 = i / pieces
    const t1 = (i + 1) / pieces
    const sx = x1 + (x2 - x1) * t0
    const sy = y1 + (y2 - y1) * t0
    const ex = x1 + (x2 - x1) * t1
    const ey = y1 + (y2 - y1) * t1
    const opacity = edgeOpacity((sx + ex) / 2, (sy + ey) / 2, width, height, fadeWidth)
    if (opacity <= 0.03) continue
    out.push(makeStroke(linePath(sx, sy, ex, ey), style, opacity))
  }
}

function pushPoly(out, points, style, width, height, fadeWidth, edgeFade) {
  if (points.length < 2) return
  if (!edgeFade) {
    out.push(makeStroke(polyPath(points), style, 1))
    return
  }
  let chunk = [points[0]]
  let length = 0
  const limit = Math.max(32, fadeWidth * 0.4)
  const flush = () => {
    if (chunk.length < 2) return
    const mid = chunk[Math.floor(chunk.length / 2)]
    const opacity = edgeOpacity(mid[0], mid[1], width, height, fadeWidth)
    if (opacity > 0.03) out.push(makeStroke(polyPath(chunk), style, opacity))
  }
  for (let i = 1; i < points.length; i++) {
    const prev = points[i - 1]
    const current = points[i]
    chunk.push(current)
    length += Math.hypot(current[0] - prev[0], current[1] - prev[1])
    if (length >= limit && i < points.length - 1) {
      flush()
      chunk = [current]
      length = 0
    }
  }
  flush()
}

function colorAt(params, rng) {
  if (params.colorMode === 'palette' && params.palette.length) {
    const index = Math.floor(rng() * params.palette.length) % params.palette.length
    return params.palette[index]
  }
  return params.dotColor
}

function dropped(params, rng) {
  return params.noise && rng() < params.noiseDelete
}

function jitterOf(spacing, params, rng) {
  if (!params.noise || params.noiseJitter <= 0) return 0
  return (rng() * 2 - 1) * spacing * params.noiseJitter * 0.35
}

/**
 * Parallel strokes across the canvas.
 * `angleDeg` is the stroke direction: 0 runs left to right, 90 runs top to bottom.
 */
function parallelSegments(width, height, spacing, angleDeg, params, rng) {
  const rad = (angleDeg * Math.PI) / 180
  const dx = Math.cos(rad)
  const dy = Math.sin(rad)
  const nx = -dy
  const ny = dx
  const cx = width / 2
  const cy = height / 2
  const corners = [
    [0, 0],
    [width, 0],
    [0, height],
    [width, height],
  ]
  let min = Infinity
  let max = -Infinity
  for (const [x, y] of corners) {
    const p = (x - cx) * nx + (y - cy) * ny
    if (p < min) min = p
    if (p > max) max = p
  }
  const reach = Math.hypot(width, height)
  const pad = params.lineWidth
  const segments = []
  const start = Math.ceil((min - spacing) / spacing) * spacing
  for (let offset = start; offset <= max + spacing * 0.01; offset += spacing) {
    if (dropped(params, rng)) continue
    const shifted = offset + jitterOf(spacing, params, rng)
    const x0 = cx + nx * shifted
    const y0 = cy + ny * shifted
    const clipped = clipSegment(
      x0 - dx * reach,
      y0 - dy * reach,
      x0 + dx * reach,
      y0 + dy * reach,
      -pad,
      -pad,
      width + pad,
      height + pad,
    )
    if (!clipped) continue
    segments.push({ kind: 'line', coords: clipped, color: colorAt(params, rng) })
  }
  return segments
}

function raySegments(width, height, params, rng) {
  const cx = params.radialCenter.x * width
  const cy = params.radialCenter.y * height
  const count = params.rayCount
  const reach = Math.hypot(width, height) + params.lineWidth
  const pad = params.lineWidth
  const segments = []
  for (let i = 0; i < count; i++) {
    if (dropped(params, rng)) continue
    const spin = params.noise ? (rng() * 2 - 1) * params.noiseJitter * 6 : 0
    const angle = ((params.angle + spin) * Math.PI) / 180 + (i / count) * Math.PI * 2
    const clipped = clipSegment(
      cx,
      cy,
      cx + Math.cos(angle) * reach,
      cy + Math.sin(angle) * reach,
      -pad,
      -pad,
      width + pad,
      height + pad,
    )
    if (!clipped) continue
    segments.push({ kind: 'line', coords: clipped, color: colorAt(params, rng) })
  }
  return segments
}

function ringSegments(width, height, params, rng) {
  const cx = params.radialCenter.x * width
  const cy = params.radialCenter.y * height
  const maxR = Math.hypot(Math.max(cx, width - cx), Math.max(cy, height - cy)) + params.spacing
  const segments = []
  for (let r = params.spacing; r <= maxR; r += params.spacing) {
    if (dropped(params, rng)) continue
    const radius = Math.max(1, r + jitterOf(params.spacing, params, rng))
    segments.push({
      kind: 'ring',
      cx,
      cy,
      radius,
      color: colorAt(params, rng),
    })
  }
  return segments
}

function spiralSegments(width, height, params, rng) {
  const cx = width / 2
  const cy = height / 2
  const maxR = Math.hypot(cx, cy) + params.spacing
  const b = params.spacing / (Math.PI * 2)
  const rot = (params.angle * Math.PI) / 180
  const groups = []
  let group = []
  let theta = 0
  let turn = 0
  let skipping = false
  let guard = 0
  const flush = () => {
    if (group.length > 1) groups.push(group)
    group = []
  }
  while (guard++ < 20000) {
    const radius = b * theta
    if (radius > maxR) break
    const nextTurn = Math.floor(theta / (Math.PI * 2))
    if (nextTurn !== turn) {
      turn = nextTurn
      const skip = dropped(params, rng)
      if (skip !== skipping) flush()
      skipping = skip
    }
    if (!skipping) {
      const wobble = params.noise ? (rng() * 2 - 1) * params.noiseJitter * params.spacing * 0.15 : 0
      const a = theta + rot
      const r = Math.max(0, radius + wobble)
      group.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r])
    }
    theta += 6 / Math.max(radius, b)
  }
  flush()
  const color = colorAt(params, rng)
  return groups.map((points) => ({ kind: 'poly', points, color }))
}

function waveSegments(width, height, params, rng) {
  const amp = params.waveAmplitude
  const wavelength = Math.max(8, params.waveLength)
  const rad = (params.angle * Math.PI) / 180
  const cos = Math.cos(rad)
  const sin = Math.sin(rad)
  const cx = width / 2
  const cy = height / 2
  const reach = Math.hypot(width, height) / 2 + params.spacing + amp + 8
  const count = Math.ceil(reach / params.spacing)
  const step = Math.max(3, wavelength / 12)
  const segments = []
  for (let i = -count; i <= count; i++) {
    if (dropped(params, rng)) continue
    const y0 = i * params.spacing + jitterOf(params.spacing, params, rng)
    const points = []
    for (let x = -reach; x <= reach; x += step) {
      const y = y0 + amp * Math.sin((x / wavelength) * Math.PI * 2)
      const rx = x * cos - y * sin
      const ry = x * sin + y * cos
      points.push([cx + rx, cy + ry])
    }
    const pad = params.lineWidth + amp
    const visible = points.some(
      ([x, y]) => x >= -pad && y >= -pad && x <= width + pad && y <= height + pad,
    )
    if (!visible) continue
    segments.push({ kind: 'poly', points, color: colorAt(params, rng) })
  }
  return segments
}

function collectSegments(params, rng) {
  const { width, height, spacing, angle, lineType } = params
  switch (lineType) {
    case 'diag':
      return [
        ...parallelSegments(width, height, spacing, angle + 45, params, rng),
        ...parallelSegments(width, height, spacing, angle + 135, params, rng),
      ]
    case 'parallel':
    case 'dashed':
      return parallelSegments(width, height, spacing, angle, params, rng)
    case 'horizontal':
      return parallelSegments(width, height, spacing, angle, params, rng)
    case 'vertical':
      return parallelSegments(width, height, spacing, angle + 90, params, rng)
    case 'radial':
      return raySegments(width, height, params, rng)
    case 'concentric':
      return ringSegments(width, height, params, rng)
    case 'spiral':
      return spiralSegments(width, height, params, rng)
    case 'wave':
      return waveSegments(width, height, params, rng)
    case 'grid':
    default:
      return [
        ...parallelSegments(width, height, spacing, angle, params, rng),
        ...parallelSegments(width, height, spacing, angle + 90, params, rng),
      ]
  }
}

function ringOpacity(cx, cy, radius, width, height, fadeWidth) {
  const clearance = Math.min(cx, cy, width - cx, height - cy) - radius
  return smoothstep(clearance / fadeWidth)
}

function segmentsToStrokes(segments, params) {
  const dash =
    params.lineType === 'dashed'
      ? [Math.round(params.dashLength * 100) / 100, Math.round(params.dashGap * 100) / 100]
      : null
  const strokes = []
  for (const segment of segments) {
    const style = { color: segment.color, strokeWidth: params.lineWidth, dash }
    if (segment.kind === 'line') {
      const [x1, y1, x2, y2] = segment.coords
      if (Math.hypot(x2 - x1, y2 - y1) < 12) continue
      pushStraight(strokes, x1, y1, x2, y2, style, params.width, params.height, params.fadeWidth, params.edgeFade)
    } else if (segment.kind === 'poly') {
      pushPoly(strokes, segment.points, style, params.width, params.height, params.fadeWidth, params.edgeFade)
    } else if (segment.kind === 'ring') {
      const opacity = params.edgeFade
        ? ringOpacity(segment.cx, segment.cy, segment.radius, params.width, params.height, params.fadeWidth)
        : 1
      if (opacity <= 0.03) continue
      strokes.push(makeStroke(circlePath(segment.cx, segment.cy, segment.radius), style, opacity))
    }
  }
  return strokes
}

/** Real strokes for the line category. Dots stay in generate.js. */
export function generateLinePicture(raw) {
  const width = clamp(Math.round(raw.width) || 800, 64, 2000)
  const height = clamp(Math.round(raw.height) || 600, 64, 2000)
  const params = {
    ...raw,
    width,
    height,
    spacing: clamp(Number(raw.spacing) || 24, 4, 200),
    angle: Number(raw.angle) || 0,
    lineType: raw.lineType || 'grid',
    lineWidth: clamp(Number(raw.lineWidth) || 1.5, 0.4, 24),
    rayCount: clamp(Math.round(raw.rayCount) || 16, 3, 72),
    waveAmplitude: clamp(Number(raw.waveAmplitude) || 0, 0, 80),
    waveLength: clamp(Number(raw.waveLength) || 48, 8, 240),
    dashLength: clamp(Number(raw.dashLength) || 12, 1, 80),
    dashGap: clamp(Number(raw.dashGap) || 8, 1, 80),
    radialCenter: {
      x: clamp(raw.radialCenter?.x ?? 0.5, 0, 1),
      y: clamp(raw.radialCenter?.y ?? 0.5, 0, 1),
    },
    fadeWidth: clamp(Number(raw.fadeWidth) || 80, 1, Math.max(width, height)),
    noiseDelete: clamp(Number(raw.noiseDelete) || 0, 0, 0.95),
    noiseJitter: clamp(Number(raw.noiseJitter) || 0, 0, 1),
    seed: Number(raw.seed) || 1,
    palette: raw.palette?.length ? raw.palette : ['#1a1a1a'],
    edgeFade: Boolean(raw.edgeFade),
    noise: Boolean(raw.noise),
    dotColor: raw.dotColor || '#1a1a1a',
  }

  const rng = makeRng(params.seed)
  const strokes = segmentsToStrokes(collectSegments(params, rng), params)

  return {
    kind: 'lines',
    dots: [],
    strokes,
    width,
    height,
    background: params.transparent ? null : params.backgroundColor,
    invert: Boolean(params.invert),
    fieldColor: params.dotColor,
  }
}
