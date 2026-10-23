import { useEffect, useRef, useState } from 'react'
import { PRESETS } from '../lib/presets.js'
import {
  ArrangementIcon,
  IconArrangeGrid,
  IconArrangePoisson,
  IconArrangeRadial,
  IconArrangeRotated,
  IconArrangeSpiral,
  IconArrangeStaggered,
  IconChevron,
  IconColorDual,
  IconColorPalette,
  IconColorSingle,
  IconDice,
  IconDots,
  IconExportPng,
  IconExportSvg,
  IconLineConcentric,
  IconLineDashed,
  IconLineDiag,
  IconLineGrid,
  IconLineHorizontal,
  IconLineParallel,
  IconLineRadial,
  IconLineSpiral,
  IconLineVertical,
  IconLineWave,
  IconLines,
  IconPlus,
  IconRedo,
  IconShapeCircle,
  IconShapeEllipse,
  IconShapeHeart,
  IconShapeRing,
  IconShapeSquare,
  IconShapeStar,
  IconSizeFixed,
  IconSizeLinear,
  IconSizeMask,
  IconSizeRadial,
  IconSizeRandom,
  IconUndo,
  IconUpload,
  LineTypeIcon,
} from './icons.jsx'

const ARRANGEMENTS = [
  { value: 'grid', label: '正网格', Icon: IconArrangeGrid },
  { value: 'staggered', label: '错位网格', Icon: IconArrangeStaggered },
  { value: 'rotated', label: '旋转网格', Icon: IconArrangeRotated },
  { value: 'poisson', label: '随机散布', Icon: IconArrangePoisson },
  { value: 'radial', label: '径向同心', Icon: IconArrangeRadial },
  { value: 'spiral', label: '螺旋', Icon: IconArrangeSpiral },
]

const SIZE_MODES = [
  { value: 'fixed', label: '固定', Icon: IconSizeFixed },
  { value: 'linear', label: '线性渐变', Icon: IconSizeLinear },
  { value: 'radial', label: '径向渐变', Icon: IconSizeRadial },
  { value: 'random', label: '随机', Icon: IconSizeRandom },
  { value: 'mask', label: '按蒙版图形', Icon: IconSizeMask },
]

const SHAPES = [
  { value: 'circle', label: '圆', Icon: IconShapeCircle },
  { value: 'ring', label: '圆环', Icon: IconShapeRing },
  { value: 'ellipse', label: '椭圆', Icon: IconShapeEllipse },
  { value: 'star', label: '星形', Icon: IconShapeStar },
  { value: 'square', label: '方块', Icon: IconShapeSquare },
  { value: 'heart', label: '心形', Icon: IconShapeHeart },
]

const LINE_TYPES = [
  { value: 'grid', label: '正网格', Icon: IconLineGrid },
  { value: 'diag', label: '斜网格', Icon: IconLineDiag },
  { value: 'parallel', label: '平行斜线', Icon: IconLineParallel },
  { value: 'horizontal', label: '横线', Icon: IconLineHorizontal },
  { value: 'vertical', label: '竖线', Icon: IconLineVertical },
  { value: 'radial', label: '放射线', Icon: IconLineRadial },
  { value: 'concentric', label: '同心圆', Icon: IconLineConcentric },
  { value: 'spiral', label: '螺旋线', Icon: IconLineSpiral },
  { value: 'wave', label: '波浪线', Icon: IconLineWave },
  { value: 'dashed', label: '虚线', Icon: IconLineDashed },
]

const COLOR_MODES = [
  { value: 'single', label: '单色', Icon: IconColorSingle },
  { value: 'dual', label: '双色', Icon: IconColorDual },
  { value: 'palette', label: '多色调色板', Icon: IconColorPalette },
]

const MASK_SOURCES = [
  { value: 'star', label: '内置星星', Icon: IconShapeStar },
  { value: 'upload', label: '上传图片', Icon: IconUpload },
]

function Group({ title, children }) {
  const [open, setOpen] = useState(true)
  return (
    <section className={open ? 'group open' : 'group'}>
      <button type="button" className="group-head" aria-expanded={open} onClick={() => setOpen((value) => !value)}>
        <IconChevron open={open} />
        <span>{title}</span>
      </button>
      {open && <div className="group-body">{children}</div>}
    </section>
  )
}

function Slider({ id, label, min, max, step, value, onPreview, onGestureStart, onGestureEnd, suffix = '' }) {
  const [editing, setEditing] = useState(false)

  function commit(raw) {
    const next = Number(raw)
    if (!Number.isFinite(next)) return
    onPreview(Math.min(max, Math.max(min, next)))
  }

  function beginEdit() {
    setEditing(true)
    onGestureStart()
  }

  function startGesture(event) {
    if (event.pointerId != null && event.currentTarget.setPointerCapture) {
      event.currentTarget.setPointerCapture(event.pointerId)
    }
    beginEdit()
  }

  function stopGesture() {
    setEditing(false)
    onGestureEnd()
  }

  return (
    <div className={editing ? 'row is-editing' : 'row'}>
      <label htmlFor={id}>{label}</label>
      <div className="row-control">
        <input
          id={id}
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onPointerDown={startGesture}
          onPointerUp={stopGesture}
          onPointerCancel={stopGesture}
          onKeyDown={startGesture}
          onKeyUp={stopGesture}
          onChange={(event) => commit(event.target.value)}
        />
        <span className="num-wrap">
          <input
            type="number"
            min={min}
            max={max}
            step={step}
            value={value}
            aria-label={`${label}数值`}
            onFocus={beginEdit}
            onPointerDown={beginEdit}
            onBlur={stopGesture}
            onChange={(event) => commit(event.target.value)}
          />
          {suffix && <span className="suffix">{suffix}</span>}
        </span>
      </div>
    </div>
  )
}

function NumberField({ id, label, min, max, value, onPreview, onGestureStart, onGestureEnd, parse }) {
  const [editing, setEditing] = useState(false)

  function startGesture() {
    setEditing(true)
    onGestureStart()
  }

  function stopGesture() {
    setEditing(false)
    onGestureEnd()
  }

  return (
    <div className={editing ? 'row is-editing' : 'row'}>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        className="num-solo"
        type="number"
        min={min}
        max={max}
        value={value}
        onFocus={startGesture}
        onPointerDown={startGesture}
        onBlur={stopGesture}
        onChange={(event) => onPreview(parse(event.target.value))}
      />
    </div>
  )
}

function Segment({ label, value, options, onChange, columns = 3 }) {
  return (
    <div className="segment-block">
      <div className="segment" role="radiogroup" aria-label={label} style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}>
        {options.map((option) => {
          const Glyph = option.Icon
          return (
            <button
              type="button"
              key={option.value}
              role="radio"
              aria-checked={value === option.value}
              className={value === option.value ? 'on' : ''}
              data-value={option.value}
              onClick={() => onChange(option.value)}
            >
              {Glyph && <Glyph />}
              <span>{option.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

function Check({ id, label, checked, onCommit }) {
  return (
    <label className="check" htmlFor={id}>
      <span>{label}</span>
      <input id={id} type="checkbox" checked={checked} onChange={(event) => onCommit(event.target.checked)} />
    </label>
  )
}

function ColorField({ id, label, value, onPreview, onGestureStart, onGestureEnd }) {
  const [editing, setEditing] = useState(false)

  function startGesture() {
    setEditing(true)
    onGestureStart()
  }

  function stopGesture() {
    setEditing(false)
    onGestureEnd()
  }

  return (
    <label className={editing ? 'row color-row is-editing' : 'row color-row'} htmlFor={id}>
      <span>{label}</span>
      <input
        id={id}
        type="color"
        value={value}
        onFocus={startGesture}
        onBlur={stopGesture}
        onChange={(event) => onPreview(event.target.value)}
      />
    </label>
  )
}

export function TopBar({ category, presetName, canUndo, canRedo, onUndo, onRedo, onExportPng, onExportSvg }) {
  const lines = category === 'lines'
  return (
    <header className="topbar">
      <div className="file-title">
        <span className="brand-mark">{lines ? <IconLines /> : <IconDots />}</span>
        <h1>{lines ? '线纹图案生成器' : '波点图案生成器'}</h1>
        <span className="title-sep" aria-hidden="true">/</span>
        <span className="title-preset" title={presetName}>{presetName}</span>
      </div>
      <div className="topbar-history">
        <button type="button" id="undo" onClick={onUndo} disabled={!canUndo} title="撤回（Ctrl+Z）">
          <IconUndo />
          撤回
        </button>
        <button type="button" id="redo" onClick={onRedo} disabled={!canRedo} title="重做（Ctrl+Shift+Z）">
          <IconRedo />
          重做
        </button>
      </div>
      <div className="topbar-export">
        <button type="button" id="export-svg" onClick={onExportSvg}>
          <IconExportSvg />
          导出 SVG
        </button>
        <button type="button" id="export-png" onClick={onExportPng}>
          <IconExportPng />
          导出 PNG
        </button>
      </div>
    </header>
  )
}

export function PresetRail({ category, presetId, onPreset, onCategory }) {
  const listRef = useRef(null)
  const list = PRESETS.filter((preset) => (preset.params.category || 'dots') === category)
  const lines = category === 'lines'

  useEffect(() => {
    const selected = listRef.current?.querySelector(`[data-preset="${presetId}"]`)
    selected?.scrollIntoView({ block: 'nearest' })
  }, [presetId, category])

  return (
    <aside className="rail">
      <div className="rail-sticky">
        <div className="category-switch" role="radiogroup" aria-label="类别">
          <button
            type="button"
            id="category-dots"
            role="radio"
            aria-checked={category === 'dots'}
            className={category === 'dots' ? 'on' : ''}
            onClick={() => onCategory('dots')}
          >
            <IconDots />
            <span>波点</span>
          </button>
          <button
            type="button"
            id="category-lines"
            role="radio"
            aria-checked={category === 'lines'}
            className={category === 'lines' ? 'on' : ''}
            onClick={() => onCategory('lines')}
          >
            <IconLines />
            <span>线纹</span>
          </button>
        </div>
      </div>
      <h2>预设</h2>
      <div className="preset-list" ref={listRef} key={category}>
        {list.map((preset) => (
          <button
            type="button"
            key={preset.id}
            data-preset={preset.id}
            aria-pressed={presetId === preset.id}
            className={presetId === preset.id ? 'on' : ''}
            onClick={() => onPreset(preset.id)}
          >
            <span className="preset-glyph">
              {lines ? <LineTypeIcon type={preset.params.lineType} /> : <ArrangementIcon type={preset.params.arrangement} />}
            </span>
            <span className="preset-name">{preset.name}</span>
          </button>
        ))}
      </div>
    </aside>
  )
}

export function Inspector({ params, presetName, dotCount, onCommit, onPreview, onGestureStart, onGestureEnd, onRandomize, onUpload }) {
  const lines = params.category === 'lines'
  const colorLabel = params.invert ? '底色' : lines ? '线颜色' : '点颜色'

  return (
    <aside className="inspector">
      <div className="inspector-summary">
        <span className="summary-mark">{lines ? <IconLines /> : <IconDots />}</span>
        <span className="summary-name" title={presetName}>{presetName}</span>
        <span className="summary-kind">{lines ? '线纹' : '波点'}</span>
      </div>
      <Group title="画布">
        <NumberField
          id="canvas-width"
          label="宽度"
          min={64}
          max={1600}
          value={params.width}
          onPreview={(width) => onPreview({ width })}
          onGestureStart={onGestureStart}
          onGestureEnd={onGestureEnd}
          parse={(raw) => Number(raw)}
        />
        <NumberField
          id="canvas-height"
          label="高度"
          min={64}
          max={1600}
          value={params.height}
          onPreview={(height) => onPreview({ height })}
          onGestureStart={onGestureStart}
          onGestureEnd={onGestureEnd}
          parse={(raw) => Number(raw)}
        />
        <p id="dot-count">
          {params.width} × {params.height} · {dotCount} {lines ? '条线' : '个点'}
        </p>
        <NumberField
          id="seed"
          label="随机种子"
          min={1}
          max={999999}
          value={params.seed}
          onPreview={(seed) => onPreview({ seed })}
          onGestureStart={onGestureStart}
          onGestureEnd={onGestureEnd}
          parse={(raw) => Number(raw) || 1}
        />
        <button type="button" id="randomize" onClick={onRandomize}>
          <IconDice />
          随机一下
        </button>
        <p className="hint">
          {lines ? '种子会影响多色取色和做旧。' : '种子会影响随机散布、随机大小、调色板取色和做旧。'}
        </p>
      </Group>

      {lines ? (
        <Group title="线型">
          <Segment
            label="线型"
            columns={2}
            value={params.lineType}
            options={LINE_TYPES}
            onChange={(lineType) => onCommit({ lineType })}
          />
          <Slider
            id="line-width"
            label="线宽"
            min={0.5}
            max={16}
            step={0.1}
            value={params.lineWidth}
            onPreview={(lineWidth) => onPreview({ lineWidth })}
            onGestureStart={onGestureStart}
            onGestureEnd={onGestureEnd}
          />
          <Slider
            id="spacing"
            label="间距"
            min={6}
            max={80}
            step={1}
            value={params.spacing}
            onPreview={(spacing) => onPreview({ spacing })}
            onGestureStart={onGestureStart}
            onGestureEnd={onGestureEnd}
          />
          {params.lineType !== 'concentric' && (
            <Slider
              id="angle"
              label="角度"
              min={0}
              max={360}
              step={1}
              suffix="°"
              value={params.angle}
              onPreview={(angle) => onPreview({ angle })}
              onGestureStart={onGestureStart}
              onGestureEnd={onGestureEnd}
            />
          )}
              {params.lineType === 'radial' && (
            <>
              <p className="hint">拖动预览移动中心。</p>
              <Slider
                id="ray-count"
                label="条数"
                min={3}
                max={72}
                step={1}
                value={params.rayCount}
                onPreview={(rayCount) => onPreview({ rayCount })}
                onGestureStart={onGestureStart}
                onGestureEnd={onGestureEnd}
              />
            </>
          )}
          {params.lineType === 'concentric' && <p className="hint">拖动预览移动中心。</p>}
          {params.lineType === 'wave' && (
            <>
              <Slider
                id="wave-amplitude"
                label="波幅"
                min={0}
                max={40}
                step={0.5}
                value={params.waveAmplitude}
                onPreview={(waveAmplitude) => onPreview({ waveAmplitude })}
                onGestureStart={onGestureStart}
                onGestureEnd={onGestureEnd}
              />
              <Slider
                id="wave-length"
                label="波长"
                min={12}
                max={160}
                step={1}
                value={params.waveLength}
                onPreview={(waveLength) => onPreview({ waveLength })}
                onGestureStart={onGestureStart}
                onGestureEnd={onGestureEnd}
              />
            </>
          )}
          {params.lineType === 'dashed' && (
            <>
              <Slider
                id="dash-length"
                label="线段"
                min={2}
                max={40}
                step={1}
                value={params.dashLength}
                onPreview={(dashLength) => onPreview({ dashLength })}
                onGestureStart={onGestureStart}
                onGestureEnd={onGestureEnd}
              />
              <Slider
                id="dash-gap"
                label="间隔"
                min={2}
                max={40}
                step={1}
                value={params.dashGap}
                onPreview={(dashGap) => onPreview({ dashGap })}
                onGestureStart={onGestureStart}
                onGestureEnd={onGestureEnd}
              />
            </>
          )}
        </Group>
      ) : (
      <>
      <Group title="排列">
        <Segment
          label="排列"
          value={params.arrangement}
          options={ARRANGEMENTS}
          onChange={(arrangement) => onCommit({ arrangement })}
        />
        <Slider
          id="spacing"
          label="点间距"
          min={6}
          max={80}
          step={1}
          value={params.spacing}
          onPreview={(spacing) => onPreview({ spacing })}
          onGestureStart={onGestureStart}
          onGestureEnd={onGestureEnd}
        />
        <Slider
          id="angle"
          label="旋转角度"
          min={0}
          max={360}
          step={1}
          suffix="°"
          value={params.angle}
          onPreview={(angle) => onPreview({ angle })}
          onGestureStart={onGestureStart}
          onGestureEnd={onGestureEnd}
        />
        {params.arrangement === 'poisson' && <p className="hint">随机散布用泊松圆盘采样，点与点不会比间距更近。</p>}
        {params.arrangement === 'rotated' && <p className="hint">旋转网格绕画布中心转动，默认 45°。</p>}
      </Group>

      <Group title="点大小">
        <Segment label="点大小" value={params.sizeMode} options={SIZE_MODES} onChange={(sizeMode) => onCommit({ sizeMode })} />
        {params.sizeMode === 'fixed' && (
          <Slider id="size" label="大小" min={0.5} max={36} step={0.5} value={params.size} onPreview={(size) => onPreview({ size })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
        )}
        {params.sizeMode === 'linear' && (
          <>
            <Slider
              id="linear-angle"
              label="渐变角度"
              min={0}
              max={360}
              step={1}
              suffix="°"
              value={params.linearAngle}
              onPreview={(linearAngle) => onPreview({ linearAngle })}
              onGestureStart={onGestureStart}
              onGestureEnd={onGestureEnd}
            />
            <Slider id="size-start" label="起始大小" min={0} max={36} step={0.5} value={params.sizeStart} onPreview={(sizeStart) => onPreview({ sizeStart })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
            <Slider id="size-end" label="结束大小" min={0} max={36} step={0.5} value={params.sizeEnd} onPreview={(sizeEnd) => onPreview({ sizeEnd })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
          </>
        )}
        {params.sizeMode === 'radial' && (
          <>
            <p className="hint">拖动预览移动中心。</p>
            <Slider
              id="radial-radius"
              label="渐变半径"
              min={20}
              max={800}
              step={1}
              value={params.radialRadius}
              onPreview={(radialRadius) => onPreview({ radialRadius })}
              onGestureStart={onGestureStart}
              onGestureEnd={onGestureEnd}
            />
            <Slider id="size-start" label="中心大小" min={0} max={36} step={0.5} value={params.sizeStart} onPreview={(sizeStart) => onPreview({ sizeStart })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
            <Slider id="size-end" label="外围大小" min={0} max={36} step={0.5} value={params.sizeEnd} onPreview={(sizeEnd) => onPreview({ sizeEnd })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
          </>
        )}
        {params.sizeMode === 'random' && (
          <>
            <Slider id="size-min" label="最小" min={0.5} max={30} step={0.5} value={params.sizeMin} onPreview={(sizeMin) => onPreview({ sizeMin })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
            <Slider id="size-max" label="最大" min={0.5} max={36} step={0.5} value={params.sizeMax} onPreview={(sizeMax) => onPreview({ sizeMax })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
          </>
        )}
        {params.sizeMode === 'mask' && (
          <>
            <p className="hint">亮度越高，点越大。可用内置星星，或上传一张黑白图。</p>
            <Segment
              label="蒙版来源"
              columns={2}
              value={params.maskSource}
              options={MASK_SOURCES}
              onChange={(maskSource) => onCommit({ maskSource })}
            />
            <label className="file" htmlFor="mask-file">
              <IconUpload />
              选择黑白图片
              <input
                id="mask-file"
                type="file"
                accept="image/*"
                onChange={(event) => {
                  const file = event.target.files?.[0]
                  if (file) onUpload(file)
                  event.target.value = ''
                }}
              />
            </label>
            <Slider id="mask-min" label="最小" min={0} max={20} step={0.5} value={params.maskMin} onPreview={(maskMin) => onPreview({ maskMin })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
            <Slider id="mask-max" label="最大" min={1} max={36} step={0.5} value={params.maskMax} onPreview={(maskMax) => onPreview({ maskMax })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
          </>
        )}
      </Group>

      <Group title="形状">
        <Segment label="形状" value={params.shape} options={SHAPES} onChange={(shape) => onCommit({ shape })} />
        {params.shape === 'ring' && (
          <Slider id="stroke-width" label="描边粗细" min={0.5} max={12} step={0.5} value={params.strokeWidth} onPreview={(strokeWidth) => onPreview({ strokeWidth })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
        )}
        {params.shape === 'star' && (
          <Slider id="star-points" label="角数" min={3} max={12} step={1} value={params.starPoints} onPreview={(starPoints) => onPreview({ starPoints })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
        )}
        {params.shape === 'ellipse' && (
          <Slider
            id="ellipse-ratio"
            label="长短轴比"
            min={0.3}
            max={1}
            step={0.01}
            value={params.ellipseRatio}
            onPreview={(ellipseRatio) => onPreview({ ellipseRatio })}
            onGestureStart={onGestureStart}
            onGestureEnd={onGestureEnd}
          />
        )}
      </Group>
      </>
      )}

      <Group title="颜色">
        <Segment label="颜色" value={params.colorMode} options={COLOR_MODES} onChange={(colorMode) => onCommit({ colorMode })} />
        {params.colorMode !== 'palette' && (
          <ColorField
            id="dot-color"
            label={colorLabel}
            value={params.dotColor}
            onPreview={(dotColor) => onPreview({ dotColor })}
            onGestureStart={onGestureStart}
            onGestureEnd={onGestureEnd}
          />
        )}
        {params.colorMode === 'palette' && (
          <>
            <p className="hint">{lines ? '每条线从调色板里随机取色。' : '每个点从调色板里随机取色。'}</p>
            <div className="palette">
              {params.palette.map((color, index) => (
                <label key={index} className="swatch">
                  <input
                    type="color"
                    aria-label={`颜色 ${index + 1}`}
                    value={color}
                    onFocus={onGestureStart}
                    onBlur={onGestureEnd}
                    onChange={(event) => {
                      const palette = [...params.palette]
                      palette[index] = event.target.value
                      onPreview({ palette })
                    }}
                  />
                  {params.palette.length > 2 && (
                    <button
                      type="button"
                      aria-label={`删除颜色 ${index + 1}`}
                      onClick={() => onCommit({ palette: params.palette.filter((_, item) => item !== index) })}
                    >
                      ×
                    </button>
                  )}
                </label>
              ))}
              {params.palette.length < 8 && (
                <button type="button" className="text-btn" onClick={() => onCommit({ palette: [...params.palette, '#888888'] })}>
                  <IconPlus />
                  添加颜色
                </button>
              )}
            </div>
          </>
        )}
        <Check id="transparent" label="背景透明" checked={params.transparent} onCommit={(transparent) => onCommit({ transparent })} />
        {!params.transparent && (
          <ColorField
            id="bg-color"
            label="背景颜色"
            value={params.backgroundColor}
            onPreview={(backgroundColor) => onPreview({ backgroundColor })}
            onGestureStart={onGestureStart}
            onGestureEnd={onGestureEnd}
          />
        )}
        {params.colorMode === 'dual' && (
          <p className="hint">{lines ? '双色使用线颜色和背景颜色。' : '双色使用点颜色和背景颜色。'}</p>
        )}
      </Group>

      <Group title="效果">
        <Check id="edge-fade" label="边缘渐隐" checked={params.edgeFade} onCommit={(edgeFade) => onCommit({ edgeFade })} />
        {params.edgeFade && (
          <Slider id="fade-width" label="渐隐宽度" min={10} max={320} step={1} value={params.fadeWidth} onPreview={(fadeWidth) => onPreview({ fadeWidth })} onGestureStart={onGestureStart} onGestureEnd={onGestureEnd} />
        )}
        <Check id="noise" label={lines ? '做旧' : '噪点做旧'} checked={params.noise} onCommit={(noise) => onCommit({ noise })} />
        {params.noise && (
          <>
            <Slider
              id="noise-delete"
              label="删除比例"
              min={0}
              max={0.8}
              step={0.01}
              value={params.noiseDelete}
              onPreview={(noiseDelete) => onPreview({ noiseDelete })}
              onGestureStart={onGestureStart}
              onGestureEnd={onGestureEnd}
            />
            <Slider
              id="noise-jitter"
              label={lines ? '间距抖动' : '大小抖动'}
              min={0}
              max={0.8}
              step={0.01}
              value={params.noiseJitter}
              onPreview={(noiseJitter) => onPreview({ noiseJitter })}
              onGestureStart={onGestureStart}
              onGestureEnd={onGestureEnd}
            />
          </>
        )}
        <Check id="invert" label="反相" checked={params.invert} onCommit={(invert) => onCommit({ invert })} />
        {params.invert && (
          <p className="hint">
            {lines ? '底色铺满画布，线变成镂空。背景透明时，孔是透明的。' : '底色铺满画布，点变成镂空。背景透明时，孔是透明的。'}
          </p>
        )}
        {!lines && <Check id="merge" label="允许点相互融合" checked={params.merge} onCommit={(merge) => onCommit({ merge })} />}
        {!lines && !params.merge && <p className="hint">关闭后，点的直径不会超过间距。</p>}
      </Group>
    </aside>
  )
}
