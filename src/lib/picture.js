import { dotPath } from './geometry.js'

function esc(value) {
  return String(value).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;')
}

function paintDot(ctx, dot) {
  ctx.globalAlpha = dot.opacity
  const path = new Path2D(dotPath(dot))
  if (dot.shape === 'ring') {
    ctx.lineWidth = dot.strokeWidth
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    ctx.strokeStyle = dot.color
    ctx.stroke(path)
  } else {
    ctx.fillStyle = dot.color
    ctx.fill(path)
  }
  ctx.globalAlpha = 1
}

function dotMarkup(dot, mask = false) {
  const d = esc(dotPath(dot))
  const opacity = dot.opacity < 0.999 ? ` opacity="${dot.opacity}"` : ''
  const color = mask ? '#000000' : dot.color
  if (dot.shape === 'ring') {
    return `<path d="${d}" fill="none" stroke="${esc(color)}" stroke-width="${dot.strokeWidth}" stroke-linecap="round" stroke-linejoin="round"${opacity}/>`
  }
  return `<path d="${d}" fill="${esc(color)}"${opacity}/>`
}

function strokeMarkup(stroke, mask = false) {
  const opacity = stroke.opacity < 0.999 ? ` opacity="${stroke.opacity}"` : ''
  const dash = stroke.dash?.length ? ` stroke-dasharray="${stroke.dash.join(' ')}"` : ''
  const color = mask ? '#000000' : stroke.color
  return `<path d="${esc(stroke.d)}" fill="none" stroke="${esc(color)}" stroke-width="${stroke.strokeWidth}" stroke-linecap="round" stroke-linejoin="round"${dash}${opacity}/>`
}

function paintStroke(ctx, stroke) {
  ctx.globalAlpha = stroke.opacity
  ctx.lineWidth = stroke.strokeWidth
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  ctx.strokeStyle = stroke.color
  ctx.setLineDash(stroke.dash || [])
  ctx.stroke(new Path2D(stroke.d))
  ctx.setLineDash([])
  ctx.globalAlpha = 1
}

function geometryMarkup(picture, mask = false) {
  const parts = []
  for (const dot of picture.dots || []) parts.push(dotMarkup(dot, mask))
  for (const stroke of picture.strokes || []) parts.push(strokeMarkup(stroke, mask))
  return parts
}

/** Serialize the current picture. The preview mounts this exact string. */
export function toSvgString(picture) {
  const { width, height, background, invert, fieldColor, kind } = picture
  const label = kind === 'lines' ? '线纹预览' : '波点预览'
  const parts = [
    `<svg id="preview-svg" xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" overflow="hidden" role="img" aria-label="${label}">`,
  ]
  if (invert) {
    if (background) {
      parts.push(`<rect width="${width}" height="${height}" fill="${esc(background)}"/>`)
    }
    parts.push(
      `<defs><mask id="polka-holes" maskUnits="userSpaceOnUse" x="0" y="0" width="${width}" height="${height}">`,
      `<rect width="${width}" height="${height}" fill="#ffffff"/>`,
    )
    parts.push(...geometryMarkup(picture, true))
    parts.push(`</mask></defs>`)
    parts.push(
      `<rect width="${width}" height="${height}" fill="${esc(fieldColor)}" mask="url(#polka-holes)"/>`,
    )
  } else {
    if (background) {
      parts.push(`<rect width="${width}" height="${height}" fill="${esc(background)}"/>`)
    }
    parts.push(...geometryMarkup(picture, false))
  }
  parts.push('</svg>')
  return parts.join('')
}

function paintGeometry(ctx, picture) {
  ctx.save()
  ctx.beginPath()
  ctx.rect(0, 0, picture.width, picture.height)
  ctx.clip()
  for (const dot of picture.dots || []) paintDot(ctx, dot)
  for (const stroke of picture.strokes || []) paintStroke(ctx, stroke)
  ctx.restore()
}

/** Draw the same picture onto a canvas. Used only for the PNG export. */
export function drawPicture(ctx, picture) {
  const { width, height, background, invert, fieldColor } = picture
  ctx.setTransform(1, 0, 0, 1, 0, 0)
  ctx.clearRect(0, 0, width, height)
  ctx.globalCompositeOperation = 'source-over'
  ctx.globalAlpha = 1

  if (invert) {
    const layer = document.createElement('canvas')
    layer.width = width
    layer.height = height
    const layerCtx = layer.getContext('2d')
    layerCtx.fillStyle = fieldColor
    layerCtx.fillRect(0, 0, width, height)
    layerCtx.globalCompositeOperation = 'destination-out'
    paintGeometry(layerCtx, picture)
    if (background) {
      ctx.fillStyle = background
      ctx.fillRect(0, 0, width, height)
    }
    ctx.drawImage(layer, 0, 0)
    return
  }

  if (background) {
    ctx.fillStyle = background
    ctx.fillRect(0, 0, width, height)
  }
  paintGeometry(ctx, picture)
}

export function renderPngCanvas(picture) {
  const canvas = document.createElement('canvas')
  canvas.width = picture.width
  canvas.height = picture.height
  const ctx = canvas.getContext('2d', { alpha: true })
  drawPicture(ctx, picture)
  return canvas
}
