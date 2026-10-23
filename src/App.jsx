import { useEffect, useMemo, useRef, useState } from 'react'
import { Inspector, PresetRail, TopBar } from './components/Panel.jsx'
import Preview from './components/Preview.jsx'
import { generatePicture } from './lib/generate.js'
import { rasterizeImage, rasterizeStar } from './lib/mask.js'
import { renderPngCanvas, toSvgString } from './lib/picture.js'
import { PRESETS, cloneParams } from './lib/presets.js'

function clamp(n, min, max) {
  return Math.min(max, Math.max(min, n))
}

function download(filename, href) {
  const link = document.createElement('a')
  link.href = href
  link.download = filename
  link.click()
}

const HISTORY_LIMIT = 50

function sameParams(a, b) {
  const keys = new Set([...Object.keys(a), ...Object.keys(b)])
  for (const key of keys) {
    if (key === 'radialCenter') {
      if (a.radialCenter?.x !== b.radialCenter?.x || a.radialCenter?.y !== b.radialCenter?.y) return false
    } else if (key === 'palette') {
      if (a.palette.length !== b.palette.length || a.palette.some((color, index) => color !== b.palette[index])) return false
    } else if (a[key] !== b[key]) return false
  }
  return true
}

export default function App() {
  const [presetId, setPresetId] = useState(PRESETS[0].id)
  const [params, setParams] = useState(() => cloneParams(PRESETS[0].params))
  const [uploadImage, setUploadImage] = useState(null)
  const paramsRef = useRef(params)
  const presetIdRef = useRef(presetId)
  const uploadImageRef = useRef(uploadImage)
  const gestureRef = useRef(null)
  const historyRef = useRef({ undo: [], redo: [] })
  const [history, setHistory] = useState(historyRef.current)
  const undoRef = useRef(() => {})
  const redoRef = useRef(() => {})

  paramsRef.current = params
  presetIdRef.current = presetId
  uploadImageRef.current = uploadImage

  function commitParams(next) {
    paramsRef.current = next
    setParams(next)
  }

  function setHistoryState(next) {
    historyRef.current = next
    setHistory(next)
  }

  const mask = useMemo(() => {
    if (params.sizeMode !== 'mask') return null
    if (params.maskSource === 'upload' && uploadImage) {
      return rasterizeImage(uploadImage, params.width, params.height)
    }
    return rasterizeStar(params.width, params.height)
  }, [params.sizeMode, params.maskSource, params.width, params.height, uploadImage])

  const picture = useMemo(() => generatePicture(params, mask), [params, mask])
  const svg = useMemo(() => toSvgString(picture), [picture])
  const [tuning, setTuning] = useState(false)
  const category = params.category || 'dots'
  const presetName = PRESETS.find((item) => item.id === presetId)?.name || ''
  const markCount = category === 'lines' ? picture.strokes.length : picture.dots.length

  useEffect(() => {
    const title = category === 'lines' ? '线纹图案生成器' : '波点图案生成器'
    document.title = presetName ? `${title} · ${presetName}` : title
  }, [category, presetName])

  useEffect(() => {
    if (!import.meta.env.DEV) return
    window.__picture = picture
    window.__svg = svg
    window.__exportPng = () => renderPngCanvas(picture).toDataURL('image/png')
    window.__center = params.radialCenter
  }, [picture, svg, params.radialCenter])

  useEffect(() => {
    function onKeyDown(event) {
      const key = event.key.toLowerCase()
      const mod = event.metaKey || event.ctrlKey
      if (!mod || (key !== 'z' && key !== 'y')) return
      const target = event.target
      if (target instanceof HTMLElement) {
        const tag = target.tagName
        const type = target.getAttribute('type')
        const textLike = target.isContentEditable || tag === 'TEXTAREA' || tag === 'SELECT' || (tag === 'INPUT' && !['range', 'checkbox', 'radio', 'color', 'file'].includes(type))
        if (textLike) return
      }
      event.preventDefault()
      if (key === 'y' || (key === 'z' && event.shiftKey)) redoRef.current()
      else undoRef.current()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  function update(partial) {
    const prev = paramsRef.current
    const next = {
      ...prev,
      ...partial,
      radialCenter: partial.radialCenter ? { ...partial.radialCenter } : prev.radialCenter,
      palette: partial.palette ? [...partial.palette] : prev.palette,
    }
    if (partial.arrangement === 'rotated' && prev.arrangement !== 'rotated' && prev.angle === 0 && partial.angle == null) {
      next.angle = 45
    }
    if (partial.colorMode === 'dual' && prev.transparent && partial.transparent == null) {
      next.transparent = false
    }
    if (partial.width != null) next.width = clamp(Math.round(Number(partial.width)) || prev.width, 64, 1600)
    if (partial.height != null) next.height = clamp(Math.round(Number(partial.height)) || prev.height, 64, 1600)
    if (partial.spacing != null) next.spacing = clamp(Number(partial.spacing) || prev.spacing, 6, 80)
    if (partial.seed != null) next.seed = clamp(Math.round(Number(partial.seed)) || 1, 1, 999999)
    if (partial.lineWidth != null) next.lineWidth = clamp(Number(partial.lineWidth) || prev.lineWidth, 0.5, 16)
    if (partial.rayCount != null) next.rayCount = clamp(Math.round(Number(partial.rayCount)) || prev.rayCount, 3, 72)
    if (partial.waveAmplitude != null) next.waveAmplitude = clamp(Number(partial.waveAmplitude) || 0, 0, 40)
    if (partial.waveLength != null) next.waveLength = clamp(Number(partial.waveLength) || prev.waveLength, 12, 160)
    if (partial.dashLength != null) next.dashLength = clamp(Number(partial.dashLength) || prev.dashLength, 2, 40)
    if (partial.dashGap != null) next.dashGap = clamp(Number(partial.dashGap) || prev.dashGap, 2, 40)
    if (
      (partial.lineType === 'parallel' || partial.lineType === 'dashed') &&
      partial.lineType !== prev.lineType &&
      partial.angle == null &&
      !prev.angle
    ) {
      next.angle = 45
    }
    commitParams(next)
  }

  function snapshot() {
    return {
      presetId: presetIdRef.current,
      params: cloneParams(paramsRef.current),
      uploadImage: uploadImageRef.current,
    }
  }

  function sameState(a, b) {
    return a.presetId === b.presetId && a.uploadImage === b.uploadImage && sameParams(a.params, b.params)
  }

  function restore(entry) {
    presetIdRef.current = entry.presetId
    uploadImageRef.current = entry.uploadImage
    setPresetId(entry.presetId)
    setUploadImage(entry.uploadImage)
    commitParams(cloneParams(entry.params))
  }

  function pushUndo(before) {
    setHistoryState({
      undo: [...historyRef.current.undo, before].slice(-HISTORY_LIMIT),
      redo: [],
    })
  }

  function beginGesture() {
    if (gestureRef.current) return
    gestureRef.current = snapshot()
    setTuning(true)
  }

  function endGesture() {
    const start = gestureRef.current
    gestureRef.current = null
    if (!start) return
    setTuning(false)
    if (sameState(start, snapshot())) return
    pushUndo(start)
  }

  function withHistory(apply) {
    const before = snapshot()
    apply()
    if (!sameState(before, snapshot())) pushUndo(before)
  }

  function commitEdit(partial) {
    withHistory(() => update(partial))
  }

  function undo() {
    if (gestureRef.current) return
    const { undo: past, redo } = historyRef.current
    if (!past.length) return
    const current = snapshot()
    const previous = past[past.length - 1]
    setHistoryState({
      undo: past.slice(0, -1),
      redo: [...redo, current].slice(-HISTORY_LIMIT),
    })
    restore(previous)
  }

  function redo() {
    if (gestureRef.current) return
    const { undo: past, redo: future } = historyRef.current
    if (!future.length) return
    const current = snapshot()
    const next = future[future.length - 1]
    setHistoryState({
      undo: [...past, current].slice(-HISTORY_LIMIT),
      redo: future.slice(0, -1),
    })
    restore(next)
  }

  undoRef.current = undo
  redoRef.current = redo

  function applyPreset(id) {
    const preset = PRESETS.find((item) => item.id === id)
    if (!preset) return
    withHistory(() => {
      presetIdRef.current = id
      setPresetId(id)
      commitParams(cloneParams(preset.params))
    })
  }

  function applyCategory(category) {
    if ((paramsRef.current.category || 'dots') === category) return
    const preset = PRESETS.find((item) => (item.params.category || 'dots') === category)
    if (preset) applyPreset(preset.id)
  }

  function randomize() {
    withHistory(() => update({ seed: Math.floor(Math.random() * 999983) + 1 }))
  }

  function onUpload(file) {
    if (!file) return
    const url = URL.createObjectURL(file)
    const image = new Image()
    image.onload = () => {
      URL.revokeObjectURL(url)
      withHistory(() => {
        uploadImageRef.current = image
        setUploadImage(image)
        update({ maskSource: 'upload', sizeMode: 'mask' })
      })
    }
    image.src = url
  }

  function exportPng() {
    const canvas = renderPngCanvas(picture)
    const name = params.category === 'lines' ? '线纹图案.png' : '波点图案.png'
    download(name, canvas.toDataURL('image/png'))
  }

  function exportSvg() {
    const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const name = params.category === 'lines' ? '线纹图案.svg' : '波点图案.svg'
    download(name, url)
    setTimeout(() => URL.revokeObjectURL(url), 1500)
  }

  return (
    <div className="app" data-category={category} data-preset={presetId}>
      <TopBar
        category={category}
        presetName={presetName}
        canUndo={history.undo.length > 0}
        canRedo={history.redo.length > 0}
        onUndo={undo}
        onRedo={redo}
        onExportPng={exportPng}
        onExportSvg={exportSvg}
      />
      <div className="workspace">
      <PresetRail
        category={category}
        presetId={presetId}
        onPreset={applyPreset}
        onCategory={applyCategory}
      />
      <Preview
        svg={svg}
        picture={picture}
        category={category}
        presetName={presetName}
        countLabel={`${markCount} ${category === 'lines' ? '条线' : '个点'}`}
        tuning={tuning}
        movable={
          (params.category === 'lines' && (params.lineType === 'radial' || params.lineType === 'concentric')) ||
          (params.category !== 'lines' && params.sizeMode === 'radial')
        }
        showGuide={params.category !== 'lines' && params.sizeMode === 'radial'}
        center={params.radialCenter}
        radius={params.radialRadius}
        onCenter={(radialCenter) => update({ radialCenter })}
        onPositionStart={beginGesture}
        onPositionEnd={endGesture}
      />
      <Inspector
        params={params}
        presetName={presetName}
        dotCount={markCount}
        onCommit={commitEdit}
        onPreview={update}
        onGestureStart={beginGesture}
        onGestureEnd={endGesture}
        onRandomize={randomize}
        onUpload={onUpload}
      />
      </div>
    </div>
  )
}
