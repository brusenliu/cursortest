import { useId } from 'react'

const stroke = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.5,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
}

export function Icon({ children }) {
  return (
    <svg className="icon" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
      {children}
    </svg>
  )
}

function Dot({ cx, cy, r = 1.15 }) {
  return <circle cx={cx} cy={cy} r={r} fill="currentColor" />
}

export function IconDots() {
  return (
    <Icon>
      <Dot cx="4.4" cy="11.1" r="1.7" />
      <Dot cx="8.15" cy="5.15" r="2.2" />
      <Dot cx="12.35" cy="10.7" r="1.25" />
    </Icon>
  )
}

export function IconLines() {
  return (
    <Icon>
      <path d="M2.4 12.6 9.2 3.4" {...stroke} />
      <path d="M5.6 13.4 13.2 4.4" {...stroke} />
      <path d="M9.2 13.4 13.6 8.2" {...stroke} />
    </Icon>
  )
}

export function IconUndo() {
  return (
    <Icon>
      <path d="M6.5 6.5H3.5V3.5" {...stroke} />
      <path d="M3.8 6.4A4.5 4.5 0 1 1 4.6 11" {...stroke} />
    </Icon>
  )
}

export function IconRedo() {
  return (
    <Icon>
      <path d="M9.5 6.5h3v-3" {...stroke} />
      <path d="M12.2 6.4A4.5 4.5 0 1 0 11.4 11" {...stroke} />
    </Icon>
  )
}

export function IconExportSvg() {
  return (
    <Icon>
      <rect x="2.25" y="2.25" width="11.5" height="11.5" rx="1.75" {...stroke} />
      <path d="M5 10.75 7.15 6.4l1.85 2.15L11.15 5.4" {...stroke} />
    </Icon>
  )
}

export function IconExportPng() {
  return (
    <Icon>
      <rect x="2.25" y="3" width="11.5" height="10" rx="1.5" {...stroke} />
      <circle cx="5.7" cy="6.35" r="1.05" fill="currentColor" />
      <path d="M3.15 11.35 6.1 8.55l1.85 1.6 1.7-1.85 3.15 3.05" {...stroke} />
    </Icon>
  )
}

export function IconDice() {
  return (
    <Icon>
      <rect x="2.25" y="2.25" width="11.5" height="11.5" rx="2" {...stroke} />
      <Dot cx="5.25" cy="5.25" r="0.9" />
      <Dot cx="10.75" cy="5.25" r="0.9" />
      <Dot cx="8" cy="8" r="0.9" />
      <Dot cx="5.25" cy="10.75" r="0.9" />
      <Dot cx="10.75" cy="10.75" r="0.9" />
    </Icon>
  )
}

export function IconUpload() {
  return (
    <Icon>
      <path d="M8 9.75V3.4" {...stroke} />
      <path d="M5.4 5.7 8 3.15l2.6 2.55" {...stroke} />
      <path d="M3.25 10.25v1.35a1.15 1.15 0 0 0 1.15 1.15h7.2a1.15 1.15 0 0 0 1.15-1.15V10.25" {...stroke} />
    </Icon>
  )
}

export function IconPlus() {
  return (
    <Icon>
      <path d="M8 3.25v9.5M3.25 8h9.5" {...stroke} />
    </Icon>
  )
}

export function IconChevron({ open }) {
  return (
    <Icon>
      <path d={open ? 'M4 6.25 8 10.25 12 6.25' : 'M6.25 4 10.25 8 6.25 12'} {...stroke} />
    </Icon>
  )
}

export function IconArrangeGrid() {
  return (
    <Icon>
      <Dot cx="5.15" cy="5.15" />
      <Dot cx="10.85" cy="5.15" />
      <Dot cx="5.15" cy="10.85" />
      <Dot cx="10.85" cy="10.85" />
    </Icon>
  )
}

export function IconArrangeStaggered() {
  return (
    <Icon>
      <Dot cx="4.3" cy="4.4" r="1.05" />
      <Dot cx="10.7" cy="4.4" r="1.05" />
      <Dot cx="7.5" cy="8" r="1.05" />
      <Dot cx="4.3" cy="11.6" r="1.05" />
      <Dot cx="10.7" cy="11.6" r="1.05" />
    </Icon>
  )
}

export function IconArrangeRotated() {
  return (
    <Icon>
      <Dot cx="8" cy="3.15" r="1.15" />
      <Dot cx="12.35" cy="8" r="1.15" />
      <Dot cx="8" cy="12.85" r="1.15" />
      <Dot cx="3.65" cy="8" r="1.15" />
      <Dot cx="8" cy="8" r="1" />
    </Icon>
  )
}

export function IconArrangePoisson() {
  return (
    <Icon>
      <Dot cx="4" cy="4" r="1.2" />
      <Dot cx="11.3" cy="3.7" r="0.95" />
      <Dot cx="7.1" cy="7.6" r="1.35" />
      <Dot cx="12.4" cy="9.3" r="0.8" />
      <Dot cx="4.6" cy="12.2" r="1.05" />
      <Dot cx="9.8" cy="12.7" r="0.75" />
    </Icon>
  )
}

export function IconArrangeRadial() {
  return (
    <Icon>
      <Dot cx="8" cy="8" r="1.45" />
      <Dot cx="8" cy="3.35" r="0.85" />
      <Dot cx="12.05" cy="5.65" r="0.85" />
      <Dot cx="12.05" cy="10.35" r="0.85" />
      <Dot cx="8" cy="12.65" r="0.85" />
      <Dot cx="3.95" cy="10.35" r="0.85" />
      <Dot cx="3.95" cy="5.65" r="0.85" />
    </Icon>
  )
}

export function IconArrangeSpiral() {
  return (
    <Icon>
      <path
        d="M8 8.1c1-.35 1.9.35 2.05 1.35.25 1.35-.7 2.6-2.05 2.95-1.7.45-3.4-.85-3.8-2.6-.45-2.05 1.15-3.95 3.25-4.35 2.5-.45 4.85 1.5 5.25 4.05"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.15"
        strokeLinecap="round"
        strokeDasharray="0.05 3.15"
      />
    </Icon>
  )
}

export function IconLineGrid() {
  return (
    <Icon>
      <path d="M3 3.5h10M3 8h10M3 12.5h10M3.5 3v10M8 3v10M12.5 3v10" {...stroke} />
    </Icon>
  )
}

export function IconLineDiag() {
  const id = `hatch-${useId().replace(/[^a-zA-Z0-9_-]/g, '')}`
  return (
    <Icon>
      <defs>
        <clipPath id={id}>
          <rect x="2.3" y="2.3" width="11.4" height="11.4" rx="1.2" />
        </clipPath>
      </defs>
      <g clipPath={`url(#${id})`}>
        <path d="M-6 4.2h28M-6 8h28M-6 11.8h28" transform="rotate(45 8 8)" {...stroke} />
        <path d="M-6 4.2h28M-6 8h28M-6 11.8h28" transform="rotate(-45 8 8)" {...stroke} />
      </g>
    </Icon>
  )
}

export function IconLineParallel() {
  return (
    <Icon>
      <path d="M3.2 11.6 9.2 3.2" {...stroke} />
      <path d="M6.4 13.2 13 4.6" {...stroke} />
      <path d="M10.2 13.4 13.6 8.8" {...stroke} />
    </Icon>
  )
}

export function IconLineHorizontal() {
  return (
    <Icon>
      <path d="M2.75 4.5h10.5M2.75 8h10.5M2.75 11.5h10.5" {...stroke} />
    </Icon>
  )
}

export function IconLineVertical() {
  return (
    <Icon>
      <path d="M4.5 2.75v10.5M8 2.75v10.5M11.5 2.75v10.5" {...stroke} />
    </Icon>
  )
}

export function IconLineRadial() {
  return (
    <Icon>
      <path d="M8 8 8 2.6M8 8l3.8-3.8M8 8l5.4.1M8 8l3.7 3.8M8 8l-.1 5.4M8 8l-3.8 3.7M8 8 2.6 8M8 8 4.2 4.2" {...stroke} />
      <Dot cx="8" cy="8" r="0.9" />
    </Icon>
  )
}

export function IconLineConcentric() {
  return (
    <Icon>
      <circle cx="8" cy="8" r="2.15" {...stroke} />
      <circle cx="8" cy="8" r="4.7" {...stroke} />
    </Icon>
  )
}

export function IconLineSpiral() {
  return (
    <Icon>
      <path
        d="M8.1 8.2c.7-.5 1.7-.2 2.1.7.5 1.15-.2 2.4-1.35 2.85-1.45.55-3-.35-3.45-1.8-.55-1.8.5-3.65 2.3-4.15 2.15-.6 4.35.7 4.9 2.9"
        {...stroke}
      />
    </Icon>
  )
}

export function IconLineWave() {
  return (
    <Icon>
      <path d="M1.6 6c1.15-1.85 2.15-1.85 3.3 0s2.15 1.85 3.3 0 2.15-1.85 3.3 0 2.15 1.85 3.3 0" {...stroke} />
      <path d="M1.6 10.7c1.15-1.85 2.15-1.85 3.3 0s2.15 1.85 3.3 0 2.15-1.85 3.3 0 2.15 1.85 3.3 0" {...stroke} />
    </Icon>
  )
}

export function IconLineDashed() {
  return (
    <Icon>
      <path d="M2.6 12.2 13.4 4.2" {...stroke} strokeDasharray="2.3 1.7" />
      <path d="M2.6 7.4 10.2 2.4" {...stroke} strokeDasharray="2.3 1.7" />
      <path d="M6.4 13.6 13.4 9" {...stroke} strokeDasharray="2.3 1.7" />
    </Icon>
  )
}

export function IconShapeCircle() {
  return (
    <Icon>
      <circle cx="8" cy="8" r="4.15" fill="currentColor" />
    </Icon>
  )
}

export function IconShapeRing() {
  return (
    <Icon>
      <circle cx="8" cy="8" r="4.35" {...stroke} />
      <circle cx="8" cy="8" r="1.9" {...stroke} />
    </Icon>
  )
}

export function IconShapeEllipse() {
  return (
    <Icon>
      <ellipse cx="8" cy="8" rx="5.1" ry="3.15" fill="currentColor" />
    </Icon>
  )
}

export function IconShapeStar() {
  return (
    <Icon>
      <path
        d="M8 2.55 9.35 6.05h3.7l-3 2.25 1.15 3.6L8 9.7l-3.2 2.2 1.15-3.6-3-2.25h3.7L8 2.55Z"
        fill="currentColor"
      />
    </Icon>
  )
}

export function IconShapeSquare() {
  return (
    <Icon>
      <rect x="3.35" y="3.35" width="9.3" height="9.3" rx="1.1" fill="currentColor" />
    </Icon>
  )
}

export function IconShapeHeart() {
  return (
    <Icon>
      <path
        d="M8 13.15C8 13.15 2.7 9.55 2.7 6.45 2.7 4.7 4 3.45 5.65 3.45c.95 0 1.75.45 2.35 1.25.6-.8 1.4-1.25 2.35-1.25 1.65 0 2.95 1.25 2.95 3 0 3.1-5.3 6.7-5.3 6.7Z"
        fill="currentColor"
      />
    </Icon>
  )
}

export function IconSizeFixed() {
  return (
    <Icon>
      <Dot cx="8" cy="8" r="3.15" />
    </Icon>
  )
}

export function IconSizeLinear() {
  return (
    <Icon>
      <Dot cx="3.5" cy="8.7" r="1.15" />
      <Dot cx="8" cy="8" r="1.9" />
      <Dot cx="12.35" cy="7.15" r="2.55" />
    </Icon>
  )
}

export function IconSizeRadial() {
  return (
    <Icon>
      <Dot cx="8" cy="8" r="2.45" />
      <Dot cx="8" cy="3.15" r="0.8" />
      <Dot cx="12.55" cy="8" r="0.8" />
      <Dot cx="8" cy="12.85" r="0.8" />
      <Dot cx="3.45" cy="8" r="0.8" />
    </Icon>
  )
}

export function IconSizeRandom() {
  return (
    <Icon>
      <Dot cx="4.1" cy="5" r="1.15" />
      <Dot cx="10.4" cy="4.5" r="2.05" />
      <Dot cx="6.2" cy="11" r="1.7" />
      <Dot cx="12.15" cy="11.2" r="0.9" />
    </Icon>
  )
}

export function IconSizeMask() {
  return (
    <Icon>
      <rect x="2.25" y="2.25" width="11.5" height="11.5" rx="1.5" {...stroke} />
      <path d="M8 4.35 8.7 6.15h1.9L9.15 7.3l.55 1.85L8 8.15 6.3 9.15l.55-1.85-1.45-1.15h1.9L8 4.35Z" fill="currentColor" />
    </Icon>
  )
}

export function IconColorSingle() {
  return (
    <Icon>
      <circle cx="8" cy="8" r="3.35" fill="currentColor" />
    </Icon>
  )
}

export function IconColorDual() {
  return (
    <Icon>
      <circle cx="5.7" cy="8" r="2.85" fill="currentColor" />
      <circle cx="10.5" cy="8" r="2.85" {...stroke} />
    </Icon>
  )
}

export function IconColorPalette() {
  return (
    <Icon>
      <Dot cx="3.6" cy="8" r="1.55" />
      <Dot cx="8" cy="8" r="1.55" />
      <Dot cx="12.4" cy="8" r="1.55" />
    </Icon>
  )
}

const ARRANGEMENT_ICONS = {
  grid: IconArrangeGrid,
  staggered: IconArrangeStaggered,
  rotated: IconArrangeRotated,
  poisson: IconArrangePoisson,
  radial: IconArrangeRadial,
  spiral: IconArrangeSpiral,
}

const LINE_ICONS = {
  grid: IconLineGrid,
  diag: IconLineDiag,
  parallel: IconLineParallel,
  horizontal: IconLineHorizontal,
  vertical: IconLineVertical,
  radial: IconLineRadial,
  concentric: IconLineConcentric,
  spiral: IconLineSpiral,
  wave: IconLineWave,
  dashed: IconLineDashed,
}

export function ArrangementIcon({ type }) {
  const Glyph = ARRANGEMENT_ICONS[type] || IconArrangeGrid
  return <Glyph />
}

export function LineTypeIcon({ type }) {
  const Glyph = LINE_ICONS[type] || IconLineGrid
  return <Glyph />
}
