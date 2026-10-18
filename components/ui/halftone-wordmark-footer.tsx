"use client"

// Supplied halftone footer, adapted for Ishika's existing static portfolio.
// Monochrome pointer-only particles: batched drawing, bounded displacement,
// time-based springs, no colour changes, click rings or grain overlay.
import * as React from "react"

export interface HalftonePalette { background: string; ink: string; warm: string }
export type HalftonePreset = "night" | "paper" | "ember" | "cobalt"
export interface FooterLink { label: string; href?: string; external?: boolean; download?: string }
export interface FooterColumn { title: string; links: FooterLink[] }
export interface HalftoneWordmarkFooterProps {
  wordmark?: string
  label?: string
  meta?: string
  columns?: FooterColumn[]
  backToTop?: boolean
  preset?: HalftonePreset
  palette?: Partial<HalftonePalette>
  dotGap?: number
  radius?: number
  crop?: number
  grain?: number
  interactive?: boolean
  fontFamily?: string
  fontWeight?: number
  monoFamily?: string
  height?: string
  className?: string
}
const PRESETS: Record<HalftonePreset, HalftonePalette> = {
  night: { background: "#0c0c0b", ink: "#e9e4da", warm: "#e9762b" },
  paper: { background: "#efebe3", ink: "#17150f", warm: "#c2361c" },
  ember: { background: "#160a06", ink: "#f2c48c", warm: "#ff5a1f" },
  cobalt: { background: "#0d1b4d", ink: "#dfe7ff", warm: "#ffcd3c" },
}
const DEFAULT_COLUMNS: FooterColumn[] = [
  { title: "Work", links: [{ label: "Index" }, { label: "Archive" }, { label: "Journal" }] },
  { title: "Studio", links: [{ label: "About" }, { label: "Process" }, { label: "Careers" }] },
  { title: "Contact", links: [{ label: "hello@halden.co" }, { label: "+47 22 00 41 00" }] },
]
const SANS_STACK = '"Inter Tight", "Inter Variable", "Inter", "Helvetica Neue", Arial, system-ui, sans-serif'
const MONO_STACK = '"JetBrains Mono", "SF Mono", ui-monospace, Menlo, Consolas, monospace'

// #region halftone
export function hwfHex(hex: string): number[] | null {
  const m = /^#?([0-9a-f]{3}|[0-9a-f]{6})$/i.exec((hex || "").trim())
  if (!m) return null
  const h = m[1].length === 3 ? m[1].split("").map(c => c + c).join("") : m[1]
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]
}
export function hwfRadius(coverage: number, gap: number) {
  return Math.sqrt(Math.max(0, Math.min(1, coverage))) * gap * 0.56
}
export function hwfStep(x: number, y: number, vx: number, vy: number, hx: number, hy: number, px: number, py: number, r: number, dt = 1 / 60) {
  const dx = hx - px, dy = hy - py, d2 = dx * dx + dy * dy
  let tx = hx, ty = hy
  if (r > 0 && d2 < r * r) {
    const d = Math.sqrt(d2) + 0.001, u = d / r, f = r * (.7 + .3 * u * u) - d
    tx += dx / d * f; ty += dy / d * f
  }
  vx += ((tx - x) * 200 - vx * 28) * dt
  vy += ((ty - y) * 200 - vy * 28) * dt
  return [x + vx * dt, y + vy * dt, vx, vy]
}
export function hwfWarmth(x: number, y: number, hx: number, hy: number, span: number) {
  return span > 0 ? Math.min(1, Math.hypot(x - hx, y - hy) / span) : 0
}
export function hwfFitSize(measured: number, width: number) {
  return measured > 0 ? (width / measured) * 100 : 0
}
// #endregion

const HWF_CSS = `
.hwf-root {position:relative;width:100%;overflow:hidden;isolation:isolate;background:var(--hwf-bg);color:var(--hwf-ink);-webkit-font-smoothing:antialiased}
.hwf-root canvas {position:absolute;inset:0;width:100%;height:100%;display:block;max-width:none}
.hwf-top {position:relative;z-index:1;display:grid;grid-template-columns:minmax(0,1.25fr) repeat(3,minmax(0,1fr));gap:24px;padding:clamp(22px,3.4vw,40px) clamp(20px,3.4vw,44px) 0;font-family:var(--hwf-mono);font-size:14px;letter-spacing:.07em;text-transform:uppercase;line-height:1.75}
.hwf-brand strong {display:block;font-weight:500}
.hwf-brand span {opacity:.75}
.hwf-col h3 {margin:0;font:inherit;opacity:.7;font-weight:500}
.hwf-col ul {list-style:none;margin:0;padding:0}
.hwf-col a,.hwf-up {color:inherit;text-decoration:none;opacity:.9;background:none;border:0;padding:0;font:inherit;letter-spacing:inherit;text-transform:inherit;cursor:pointer;background-image:linear-gradient(currentColor,currentColor);background-size:0% 1px;background-repeat:no-repeat;background-position:0 100%;transition:opacity .25s ease,background-size .35s cubic-bezier(.2,.7,.1,1)}
.hwf-col a:hover,.hwf-up:hover {opacity:1;background-size:100% 1px}
.hwf-col a:focus-visible,.hwf-up:focus-visible {outline:2px solid currentColor;outline-offset:4px;opacity:1}
.hwf-rule {position:relative;z-index:1;display:flex;justify-content:flex-end;align-items:center;gap:16px;margin:clamp(18px,2.6vw,30px) clamp(20px,3.4vw,44px) 0;padding-top:12px;border-top:1px solid color-mix(in srgb,var(--hwf-ink) 16%,transparent);font-family:var(--hwf-mono);font-size:14px;letter-spacing:.07em;text-transform:uppercase}
.hwf-sr {position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
@media(max-width:720px){.hwf-top{grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.hwf-brand{grid-column:1/-1}.hwf-top,.hwf-rule{letter-spacing:0}.hwf-col a{display:inline-block;padding:3px 0}}
@media(max-width:360px){.hwf-top{gap:8px;padding-left:16px;padding-right:16px}.hwf-rule{margin-left:16px;margin-right:16px}}
@media(prefers-reduced-motion:reduce){.hwf-col a,.hwf-up{transition:none}}
`

export default function HalftoneWordmarkFooter({
  wordmark = "halden", label = "Halden Studio", meta = "©2026 · Oslo / Lisbon",
  columns = DEFAULT_COLUMNS, backToTop = true, preset = "night", palette,
  dotGap = 6, radius = 80, crop = 0.2, grain = 0.5, interactive = true,
  fontFamily = SANS_STACK, fontWeight = 800, monoFamily = MONO_STACK,
  height = "560px", className = "",
}: HalftoneWordmarkFooterProps) {
  const colors = { ...(PRESETS[preset] || PRESETS.night), ...palette }
  const rootRef = React.useRef<HTMLElement | null>(null)
  const canvasRef = React.useRef<HTMLCanvasElement | null>(null)
  const opts = React.useRef({ colors, dotGap, radius, crop, grain, interactive, fontFamily, fontWeight, wordmark })
  opts.current = { colors, dotGap, radius, crop, grain, interactive, fontFamily, fontWeight, wordmark }
  const key = [wordmark, dotGap, crop, grain, fontFamily, fontWeight, colors.background, colors.ink, colors.warm, interactive, radius].join("|")

  React.useEffect(() => {
    const root = rootRef.current, canvas = canvasRef.current
    if (!root || !canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)")
    let reduced = preference.matches, w = 0, h = 0, dpr = 1
    let px = -1e5, py = -1e5, smoothX = -1e5, smoothY = -1e5, raf = 0, visible = true, awake = true, alive = true
    let lastTime = 0, frames = 0
    let touchRelease: ReturnType<typeof setTimeout> | undefined
    let dots = new Float32Array(0), count = 0

    const layout = () => {
      const o = opts.current, rect = root.getBoundingClientRect()
      w = Math.max(1, Math.round(rect.width)); h = Math.max(1, Math.round(rect.height))
      dpr = Math.min(window.devicePixelRatio || 1, 1.5)
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr)
      const mask = document.createElement("canvas")
      mask.width = w; mask.height = h
      const m = mask.getContext("2d", { willReadFrequently: true })
      if (!m) return
      m.font = `${o.fontWeight} 100px ${o.fontFamily}`
      const word = o.wordmark || " "
      const fit = hwfFitSize(m.measureText(word).width, w * 0.96)
      m.font = `${o.fontWeight} ${fit}px ${o.fontFamily}`
      const box = m.measureText(word), cap = box.actualBoundingBoxAscent || fit * 0.72
      m.fillStyle = "#000"; m.textBaseline = "alphabetic"
      m.fillText(word, (w - box.width) / 2, h + cap * Math.max(0, Math.min(0.6, o.crop)))
      const img = m.getImageData(0, 0, w, h).data
      const gap = Math.max(3, o.dotGap), tmp: number[] = []
      for (let gy = 0; gy < Math.ceil(h / gap); gy++) {
        for (let gx = 0; gx < Math.ceil(w / gap); gx++) {
          let sum = 0
          for (let sy = 0; sy < 3; sy++) for (let sx = 0; sx < 3; sx++) {
            const x = Math.min(w - 1, Math.floor(gx * gap + ((sx + 0.5) * gap) / 3))
            const y = Math.min(h - 1, Math.floor(gy * gap + ((sy + 0.5) * gap) / 3))
            sum += img[(y * w + x) * 4 + 3]
          }
          const cov = sum / (9 * 255)
          if (cov < 0.06) continue
          const hx = gx * gap + gap / 2, hy = gy * gap + gap / 2
          tmp.push(hx, hy, 0, 0, hx, hy, hwfRadius(cov, gap))
        }
      }
      dots = new Float32Array(tmp); count = tmp.length / 7
      root.dataset.hwfDots = String(count)
      root.dataset.hwfEffect = "wide-circular-scatter"
      awake = true; lastTime = 0
    }
    const draw = (now: number) => {
      const o = opts.current
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.fillStyle = o.colors.background; ctx.fillRect(0, 0, w, h)
      const r = o.interactive && !reduced ? Math.min(Math.max(0, o.radius), w * .42) : 0
      const elapsed = lastTime ? Math.min((now - lastTime) / 1000, 0.04) : 1 / 60
      lastTime = now
      if (px > -1e4) {
        const follow = 1 - Math.exp(-elapsed * 22)
        smoothX += (px - smoothX) * follow; smoothY += (py - smoothY) * follow
      } else { smoothX = px; smoothY = py }
      const steps = Math.max(1, Math.ceil(elapsed / (1 / 120))), dt = elapsed / steps
      let moving = Math.abs(px - smoothX) + Math.abs(py - smoothY) > .1, maxOffset2 = 0
      // A single fill for the entire wordmark avoids per-dot colour and draw calls.
      ctx.fillStyle = o.colors.ink; ctx.beginPath()
      for (let i = 0; i < count; i++) {
        const j = i * 7, hx = dots[j + 4], hy = dots[j + 5]
        let x = dots[j], y = dots[j + 1], vx = dots[j + 2], vy = dots[j + 3]
        if (!reduced) {
          const dx = hx - smoothX, dy = hy - smoothY, distance2 = dx * dx + dy * dy
          let tx = hx, ty = hy
          if (r > 0 && distance2 < r * r) {
            const distance = Math.sqrt(distance2) + 0.001, u = distance / r
            // A broad exclusion disc: dots inside the cursor's core move
            // to its rim, fading to zero displacement at the field boundary.
            const force = r * (.7 + .3 * u * u) - distance
            tx += dx / distance * force; ty += dy / distance * force
          }
          for (let step = 0; step < steps; step++) {
            vx += ((tx - x) * 200 - vx * 28) * dt
            vy += ((ty - y) * 200 - vy * 28) * dt
            x += vx * dt; y += vy * dt
          }
          if (Math.abs(vx) + Math.abs(vy) > 0.06) moving = true
          else { vx = 0; vy = 0 }
          dots[j] = x; dots[j + 1] = y; dots[j + 2] = vx; dots[j + 3] = vy
        }
        maxOffset2 = Math.max(maxOffset2, (x - hx) * (x - hx) + (y - hy) * (y - hy))
        const size = dots[j + 6] * 1.6
        ctx.rect(x - size / 2, y - size / 2, size, size)
      }
      ctx.fill()
      awake = !reduced && moving
      root.dataset.hwfFrames = String(++frames)
      root.dataset.hwfAwake = String(awake)
      root.dataset.hwfRadius = r.toFixed(1)
      root.dataset.hwfDisplacement = Math.sqrt(maxOffset2).toFixed(1)
    }
    const loop = (now: number) => {
      raf = 0
      if (!alive || !visible || document.hidden) return
      draw(now)
      if (awake) raf = requestAnimationFrame(loop)
    }
    const wake = () => {
      awake = true
      if (alive && !raf && visible && !document.hidden) { lastTime = 0; raf = requestAnimationFrame(loop) }
    }
    const toLocal = (e: PointerEvent) => {
      const b = canvas.getBoundingClientRect()
      return [e.clientX - b.left, e.clientY - b.top]
    }
    const onMove = (e: PointerEvent) => {
      if (!opts.current.interactive || reduced) return
      const entering = px < -1e4
      ;[px, py] = toLocal(e); wake()
      if (entering) { smoothX = px; smoothY = py }
    }
    const onLeave = (e?: PointerEvent) => {
      // Touch browsers synthesize pointerleave immediately after pointerup.
      // Keep the tap alive for its short pulse rather than cancelling it.
      if (e?.pointerType === "touch" && touchRelease) return
      px = -1e5; py = -1e5; wake()
    }
    const onDown = (e: PointerEvent) => {
      if (e.pointerType !== "touch") return
      if (touchRelease) clearTimeout(touchRelease)
      onMove(e)
    }
    const onUp = (e: PointerEvent) => {
      if (e.pointerType !== "touch") return
      // Let a tap scatter the lettering, then spring back without hijacking
      // normal vertical scrolling or blocking any footer links.
      touchRelease = setTimeout(() => { touchRelease = undefined; onLeave() }, 650)
    }
    const onPreference = () => { reduced = preference.matches; onLeave(); layout(); wake() }
    const onVisibility = () => { if (document.hidden) { cancelAnimationFrame(raf); raf = 0 } else wake() }
    layout(); draw(performance.now()); wake()
    root.addEventListener("pointermove", onMove)
    root.addEventListener("pointerleave", onLeave)
    root.addEventListener("pointerdown", onDown, { passive: true })
    root.addEventListener("pointerup", onUp, { passive: true })
    root.addEventListener("pointercancel", onLeave)
    const ro = new ResizeObserver(() => { layout(); wake() })
    ro.observe(root)
    const io = new IntersectionObserver(entries => {
      visible = entries[0]?.isIntersecting ?? true
      if (visible) wake(); else { cancelAnimationFrame(raf); raf = 0 }
    })
    io.observe(root)
    preference.addEventListener("change", onPreference)
    document.addEventListener("visibilitychange", onVisibility)
    document.fonts?.ready.then(() => { if (alive) { layout(); wake() } })
    return () => {
      alive = false; cancelAnimationFrame(raf); ro.disconnect(); io.disconnect()
      if (touchRelease) clearTimeout(touchRelease)
      root.removeEventListener("pointermove", onMove)
      root.removeEventListener("pointerleave", onLeave)
      root.removeEventListener("pointerdown", onDown)
      root.removeEventListener("pointerup", onUp)
      root.removeEventListener("pointercancel", onLeave)
      preference.removeEventListener("change", onPreference)
      document.removeEventListener("visibilitychange", onVisibility)
    }
  }, [key])
  const toTop = () => window.scrollTo({
    top: 0, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
  })
  return (
    <footer ref={rootRef} className={"hwf-root " + className} style={{
      height, "--hwf-bg": colors.background, "--hwf-ink": colors.ink, "--hwf-mono": monoFamily,
    } as React.CSSProperties}>
      <style>{HWF_CSS}</style>
      <canvas ref={canvasRef} aria-hidden="true" />
      <span className="hwf-sr">{wordmark}</span>
      <div className="hwf-top">
        <div className="hwf-brand"><strong>{label}</strong><span>{meta}</span></div>
        {columns.map(col => (
          <nav className="hwf-col" key={col.title} aria-label={col.title}>
            <h3>{col.title}</h3>
            <ul>{col.links.map(l => <li key={l.label}>
              {l.href ? <a href={l.href} target={l.external ? "_blank" : undefined} rel={l.external ? "noopener noreferrer" : undefined}
                download={l.download}>{l.label}</a> : <span>{l.label}</span>}
            </li>)}</ul>
          </nav>
        ))}
      </div>
      <div className="hwf-rule">{backToTop ? <button type="button" className="hwf-up" onClick={toTop}>Back to top ↑</button> : null}</div>
    </footer>
  )
}
