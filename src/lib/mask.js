import { starPath } from './geometry.js'

export function rasterizeStar(width, height) {
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, width, height)
  ctx.fillStyle = '#ffffff'
  const radius = Math.min(width, height) * 0.36
  ctx.fill(new Path2D(starPath(width / 2, height / 2, radius, 5, 0)))
  return ctx.getImageData(0, 0, width, height)
}

export function rasterizeImage(image, width, height) {
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, width, height)
  const scale = Math.max(width / image.width, height / image.height)
  const w = image.width * scale
  const h = image.height * scale
  ctx.drawImage(image, (width - w) / 2, (height - h) / 2, w, h)
  return ctx.getImageData(0, 0, width, height)
}
