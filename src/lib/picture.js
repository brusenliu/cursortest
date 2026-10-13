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

function dotMarkup(dot) {
  const d = esc(dotPath(dot))
  const opacity = dot.opacity < 0.999 ? ` opacity="${dot.opacity}"` : ''
  if (dot.shape === 'ring') {
    return `<path d="${d}" fill="none" stroke="${esc(dot.color)}" stroke-width="${dot.strokeWidth}" stroke-linecap="round" stroke-linejoin="round"${opacity}/>`
  }
  return `<path d="${d}" fill="${esc(dot.color)}"${opacity}/>`
}

/** Serialize the current picture. The preview mounts this exact string. */
export function toSvgString(picture) {
  const { width, height, dots, background, invert, fieldColor } = picture
  const parts = [
    `<svg id="preview-svg" xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" overflow="hidden" role="img" aria-label="波点预览">`,
  ]
  if (invert) {
    if (background) {
      parts.push(`<rect width="${width}" height="${height}" fill="${esc(background)}"/>`)
    }
    parts.push(
      `<defs><mask id="polka-holes" maskUnits="userSpaceOnUse" x="0" y="0" width="${width}" height="${height}">`,
      `<rect width="${width}" height="${height}" fill="#ffffff"/>`,
    )
    for (const dot of dots) {
      const d = esc(dotPath(dot))
      const opacity = dot.opacity < 0.999 ? ` opacity="${dot.opacity}"` : ''
      if (dot.shape === 'ring') {
        parts.push(
          `<path d="${d}" fill="none" stroke="#000000" stroke-width="${dot.strokeWidth}" stroke-linecap="round" stroke-linejoin="round"${opacity}/>`,
        )
      } else {
        parts.push(`<path d="${d}" fill="#000000"${opacity}/>`)
      }
    }
    parts.push(`</mask></defs>`)
    parts.push(
      `<rect width="${width}" height="${height}" fill="${esc(fieldColor)}" mask="url(#polka-holes)"/>`,
    )
  } else {
    if (background) {
      parts.push(`<rect width="${width}" height="${height}" fill="${esc(background)}"/>`)
    }
    for (const dot of dots) parts.push(dotMarkup(dot))
  }
  parts.push('</svg>')
  return parts.join('')
}

/** Draw the same picture onto a canvas. Used only for the PNG export. */
export function drawPicture(ctx, picture) {
  const { width, height, dots, background, invert, fieldColor } = picture
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
    for (const dot of dots) paintDot(layerCtx, dot)
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
  for (const dot of dots) paintDot(ctx, dot)
}

export function renderPngCanvas(picture) {
  const canvas = document.createElement('canvas')
  canvas.width = picture.width
  canvas.height = picture.height
  const ctx = canvas.getContext('2d', { alpha: true })
  drawPicture(ctx, picture)
  return canvas
}
