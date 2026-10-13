import { makeRng } from './rng.js'

function clamp(n, min, max) {
  return Math.min(max, Math.max(min, n))
}

function lerp(a, b, t) {
  return a + (b - a) * t
}

function smoothstep(t) {
  const x = clamp(t, 0, 1)
  return x * x * (3 - 2 * x)
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

function inside(x, y, width, height) {
  return x >= 0 && y >= 0 && x <= width && y <= height
}

function gridPoints(width, height, spacing, angle, staggered) {
  const reach = Math.hypot(width, height) / 2 + spacing
  const n = Math.ceil(reach / spacing)
  const points = []
  for (let j = -n; j <= n; j++) {
    const odd = Math.abs(j % 2) === 1
    for (let i = -n; i <= n; i++) {
      let x = i * spacing
      let y = j * spacing
      if (staggered && odd) x += spacing / 2
      const [rx, ry] = rotateAround(x, y, 0, 0, angle)
      const px = rx + width / 2
      const py = ry + height / 2
      if (inside(px, py, width, height)) points.push({ x: px, y: py })
    }
  }
  return points
}

function poissonPoints(width, height, minDist, rng, angle) {
  const cell = minDist / Math.SQRT2
  const gw = Math.max(1, Math.ceil(width / cell))
  const gh = Math.max(1, Math.ceil(height / cell))
  const grid = new Array(gw * gh).fill(-1)
  const points = []
  const active = []

  const insert = (p) => {
    const index = points.length
    points.push(p)
    active.push(index)
    const gx = clamp(Math.floor(p.x / cell), 0, gw - 1)
    const gy = clamp(Math.floor(p.y / cell), 0, gh - 1)
    grid[gy * gw + gx] = index
  }

  insert({ x: rng() * width, y: rng() * height })

  while (active.length && points.length < 8000) {
    const ai = Math.floor(rng() * active.length)
    const origin = points[active[ai]]
    let found = false
    for (let n = 0; n < 30; n++) {
      const ang = rng() * Math.PI * 2
      const rad = minDist * (1 + rng())
      const q = {
        x: origin.x + Math.cos(ang) * rad,
        y: origin.y + Math.sin(ang) * rad,
      }
      if (!inside(q.x, q.y, width, height)) continue
      const gx = Math.floor(q.x / cell)
      const gy = Math.floor(q.y / cell)
      let ok = true
      for (let y = gy - 2; y <= gy + 2 && ok; y++) {
        for (let x = gx - 2; x <= gx + 2 && ok; x++) {
          if (x < 0 || y < 0 || x >= gw || y >= gh) continue
          const ni = grid[y * gw + x]
          if (ni < 0) continue
          const o = points[ni]
          const dx = o.x - q.x
          const dy = o.y - q.y
          if (dx * dx + dy * dy < minDist * minDist) ok = false
        }
      }
      if (ok) {
        insert(q)
        found = true
        break
      }
    }
    if (!found) active.splice(ai, 1)
  }

  if (!angle) return points
  const cx = width / 2
  const cy = height / 2
  const spun = []
  for (const p of points) {
    const [x, y] = rotateAround(p.x, p.y, cx, cy, angle)
    if (inside(x, y, width, height)) spun.push({ x, y })
  }
  return spun
}

function radialPoints(width, height, spacing, angle) {
  const cx = width / 2
  const cy = height / 2
  const maxR = Math.hypot(cx, cy)
  const rot = (angle * Math.PI) / 180
  const points = [{ x: cx, y: cy }]
  const rings = Math.floor(maxR / spacing)
  for (let ring = 1; ring <= rings; ring++) {
    const r = ring * spacing
    const count = Math.max(6, Math.round((Math.PI * 2 * r) / spacing))
    const shift = ring % 2 ? Math.PI / count : 0
    for (let i = 0; i < count; i++) {
      const a = rot + shift + (i / count) * Math.PI * 2
      const x = cx + Math.cos(a) * r
      const y = cy + Math.sin(a) * r
      if (inside(x, y, width, height)) points.push({ x, y })
    }
  }
  return points
}

function spiralPoints(width, height, spacing, angle) {
  const cx = width / 2
  const cy = height / 2
  const maxR = Math.hypot(cx, cy)
  const b = spacing / (Math.PI * 2)
  const rot = (angle * Math.PI) / 180
  const points = []
  let theta = 0
  let guard = 0
  while (guard++ < 20000) {
    const r = b * theta
    if (r > maxR) break
    if (theta === 0) {
      points.push({ x: cx, y: cy })
    } else {
      const a = theta + rot
      const x = cx + Math.cos(a) * r
      const y = cy + Math.sin(a) * r
      if (inside(x, y, width, height)) points.push({ x, y })
    }
    theta += spacing / Math.max(r, b)
    if (points.length > 12000) break
  }
  return points
}

function layout(params, rng) {
  const { width, height, spacing, angle, arrangement } = params
  switch (arrangement) {
    case 'staggered':
      return gridPoints(width, height, spacing, angle, true)
    case 'rotated':
      return gridPoints(width, height, spacing, angle, false)
    case 'poisson':
      return poissonPoints(width, height, spacing, rng, angle)
    case 'radial':
      return radialPoints(width, height, spacing, angle)
    case 'spiral':
      return spiralPoints(width, height, spacing, angle)
    case 'grid':
    default:
      return gridPoints(width, height, spacing, angle, false)
  }
}

function sampleMask(mask, x, y, width, height) {
  if (!mask?.data) return 0.5
  const mx = clamp(Math.round((x / width) * (mask.width - 1)), 0, mask.width - 1)
  const my = clamp(Math.round((y / height) * (mask.height - 1)), 0, mask.height - 1)
  const i = (my * mask.width + mx) * 4
  const r = mask.data[i]
  const g = mask.data[i + 1]
  const b = mask.data[i + 2]
  return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
}

function projectionRange(width, height, angleDeg) {
  const rad = (angleDeg * Math.PI) / 180
  const dx = Math.cos(rad)
  const dy = -Math.sin(rad)
  const corners = [
    [0, 0],
    [width, 0],
    [0, height],
    [width, height],
  ]
  let min = Infinity
  let max = -Infinity
  for (const [x, y] of corners) {
    const p = x * dx + y * dy
    if (p < min) min = p
    if (p > max) max = p
  }
  if (max - min < 1e-6) max = min + 1
  return { dx, dy, min, max }
}

function sizeAt(point, params, rng, mask, linear) {
  const { width, height } = params
  switch (params.sizeMode) {
    case 'linear': {
      const t = (point.x * linear.dx + point.y * linear.dy - linear.min) / (linear.max - linear.min)
      return lerp(params.sizeStart, params.sizeEnd, clamp(t, 0, 1))
    }
    case 'radial': {
      const cx = params.radialCenter.x * width
      const cy = params.radialCenter.y * height
      const d = Math.hypot(point.x - cx, point.y - cy)
      const radius = Math.max(1, params.radialRadius)
      const t = clamp(d / radius, 0, 1)
      return lerp(params.sizeStart, params.sizeEnd, t)
    }
    case 'random':
      return lerp(params.sizeMin, params.sizeMax, rng())
    case 'mask': {
      const luma = sampleMask(mask, point.x, point.y, width, height)
      return lerp(params.maskMin, params.maskMax, luma)
    }
    case 'fixed':
    default:
      return params.size
  }
}

const SCATTER_SHAPES = new Set(['square', 'ellipse', 'heart', 'star'])

function rotationAt(params, rng) {
  if (!SCATTER_SHAPES.has(params.shape)) return 0
  if (params.arrangement !== 'poisson' && params.sizeMode !== 'random') return 0
  return rng() * 360
}

function colorAt(params, rng) {
  if (params.colorMode === 'palette' && params.palette.length) {
    const index = Math.floor(rng() * params.palette.length) % params.palette.length
    return params.palette[index]
  }
  return params.dotColor
}

/**
 * Build the picture from parameters.
 * `dots` is the only geometry. Preview, PNG and SVG all draw this list.
 */
export function generatePicture(params, mask = null) {
  const width = clamp(Math.round(params.width) || 800, 64, 2000)
  const height = clamp(Math.round(params.height) || 600, 64, 2000)
  const spacing = clamp(Number(params.spacing) || 24, 4, 200)
  const normalized = {
    ...params,
    width,
    height,
    spacing,
    angle: Number(params.angle) || 0,
    size: Math.max(0, Number(params.size) || 0),
    sizeStart: Math.max(0, Number(params.sizeStart) || 0),
    sizeEnd: Math.max(0, Number(params.sizeEnd) || 0),
    sizeMin: Math.max(0, Number(params.sizeMin) || 0),
    sizeMax: Math.max(0, Number(params.sizeMax) || 0),
    maskMin: Math.max(0, Number(params.maskMin) || 0),
    maskMax: Math.max(0, Number(params.maskMax) || 0),
    radialRadius: Math.max(1, Number(params.radialRadius) || 1),
    radialCenter: {
      x: clamp(params.radialCenter?.x ?? 0.5, 0, 1),
      y: clamp(params.radialCenter?.y ?? 0.5, 0, 1),
    },
    strokeWidth: clamp(Number(params.strokeWidth) || 2, 0.5, 40),
    starPoints: clamp(Math.round(params.starPoints) || 5, 3, 16),
    ellipseRatio: clamp(Number(params.ellipseRatio) || 0.62, 0.2, 1),
    fadeWidth: clamp(Number(params.fadeWidth) || 80, 1, Math.max(width, height)),
    noiseDelete: clamp(Number(params.noiseDelete) || 0, 0, 0.95),
    noiseJitter: clamp(Number(params.noiseJitter) || 0, 0, 1),
    seed: Number(params.seed) || 1,
    palette: params.palette?.length ? params.palette : ['#e63946'],
  }

  const rng = makeRng(normalized.seed)
  const points = layout(normalized, rng)
  const linear =
    normalized.sizeMode === 'linear'
      ? projectionRange(width, height, normalized.linearAngle || 0)
      : null

  let dots = points.map((point) => ({
    x: Math.round(point.x * 100) / 100,
    y: Math.round(point.y * 100) / 100,
    size: sizeAt(point, normalized, rng, mask, linear),
    color: colorAt(normalized, rng),
    opacity: 1,
    shape: normalized.shape,
    strokeWidth: normalized.strokeWidth,
    starPoints: normalized.starPoints,
    ellipseRatio: normalized.ellipseRatio,
    rotation: rotationAt(normalized, rng),
  }))

  if (normalized.edgeFade) {
    for (const dot of dots) {
      const dist = Math.min(dot.x, dot.y, width - dot.x, height - dot.y)
      const t = smoothstep(dist / normalized.fadeWidth)
      dot.opacity = Math.round(t * 1000) / 1000
      dot.size *= 0.3 + 0.7 * t
    }
  }

  if (normalized.noise) {
    const kept = []
    for (const dot of dots) {
      if (rng() < normalized.noiseDelete) continue
      const jitter = 1 + (rng() * 2 - 1) * normalized.noiseJitter
      dot.size = Math.max(0, dot.size * jitter)
      kept.push(dot)
    }
    dots = kept
  }

  if (!normalized.merge) {
    const cap = spacing * 0.46
    for (const dot of dots) dot.size = Math.min(dot.size, cap)
  }

  dots = dots.filter((dot) => dot.size >= 0.4 && dot.opacity > 0.03)
  for (const dot of dots) {
    dot.size = Math.round(dot.size * 100) / 100
    dot.rotation = Math.round(dot.rotation * 100) / 100
  }

  return {
    dots,
    width,
    height,
    background: normalized.transparent ? null : normalized.backgroundColor,
    invert: Boolean(normalized.invert),
    fieldColor: normalized.dotColor,
  }
}
