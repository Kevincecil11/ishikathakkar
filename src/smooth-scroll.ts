import { gsap } from "gsap"

/** Inertial wheel scrolling on the native document scroller.
 * Same model as Lenis: wheel input sets a target, one GSAP ticker eases the
 * real window scroll toward it. Touch, keyboard, scrollbar, find-in-page and
 * nested scroll areas stay native. Position: sticky and ScrollTrigger keep
 * working because nothing is transformed or wrapped.
 */
export type SmoothScroller = {
  scrollTo(target: number | Element): void
  stop(): void
  start(): void
}

const LAMBDA = 7.2 // about 0.11 of the remaining distance per 60fps frame
const LINE = 16

export function initSmoothScroll(): SmoothScroller | null {
  const root = document.documentElement
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return null
  root.classList.add("it-smooth")
  root.dataset.smoothScroll = "inertia"

  let current = window.scrollY
  let target = current
  let active = false
  let stopped = false
  let tween: gsap.core.Tween | null = null

  const max = () => Math.max(0, root.scrollHeight - window.innerHeight)
  const clamp = (value: number) => Math.min(max(), Math.max(0, value))
  const sync = () => { current = target = window.scrollY }
  const halt = () => { active = false; tween?.kill(); tween = null; sync() }
  const blocked = () => stopped || !!document.querySelector("dialog[open]") || document.body.style.overflow === "hidden"

  const nestedScroller = (node: EventTarget | null) => {
    for (let el = node instanceof Element ? node : null; el && el !== document.body && el !== root; el = el.parentElement) {
      const style = getComputedStyle(el)
      if (/(auto|scroll|overlay)/.test(style.overflowY) && el.scrollHeight > el.clientHeight + 1) return true
    }
    return false
  }

  window.addEventListener("wheel", event => {
    if (event.defaultPrevented || event.ctrlKey || blocked()) return
    if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) return
    if (nestedScroller(event.target)) return
    event.preventDefault()
    const unit = event.deltaMode === 1 ? LINE : event.deltaMode === 2 ? window.innerHeight : 1
    if (tween) { tween.kill(); tween = null; sync() }
    if (!active) sync()
    target = clamp(target + event.deltaY * unit)
    active = true
  }, { passive: false })

  // Any native movement hands control straight back to the browser.
  window.addEventListener("scroll", () => {
    if (!active && !tween) sync()
    else if (active && Math.abs(window.scrollY - current) > 3) halt()
  }, { passive: true })
  window.addEventListener("keydown", event => {
    if (/^(Arrow|Page|Home|End|Space| )/.test(event.key) || event.key === " ") halt()
  })
  window.addEventListener("touchstart", halt, { passive: true })
  window.addEventListener("pointerdown", event => { if (event.target === root) halt() })
  window.addEventListener("resize", () => { target = clamp(target) })

  gsap.ticker.add((_time, deltaMs) => {
    if (!active || tween) return
    const dt = Math.min(deltaMs, 64) / 1000
    current += (target - current) * (1 - Math.exp(-LAMBDA * dt))
    if (Math.abs(target - current) < 0.5) { current = target; active = false }
    window.scrollTo(0, current)
  })

  const scrollTo = (destination: number | Element) => {
    let y = typeof destination === "number" ? destination : 0
    if (destination instanceof Element) {
      const margin = parseFloat(getComputedStyle(destination).scrollMarginTop) || 0
      y = destination.getBoundingClientRect().top + window.scrollY - margin
    }
    halt()
    const proxy = { y: window.scrollY }
    const end = clamp(y)
    const distance = Math.abs(end - proxy.y)
    if (distance < 2) return
    tween = gsap.to(proxy, {
      y: end,
      duration: gsap.utils.clamp(0.9, 1.7, 0.7 + distance / 2600),
      ease: "power4.inOut",
      onUpdate: () => window.scrollTo(0, proxy.y),
      onComplete: () => { tween = null; sync() },
    })
  }

  // Same-page anchors glide; cross-page links keep their native behaviour.
  document.addEventListener("click", event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
    const link = (event.target as Element | null)?.closest?.<HTMLAnchorElement>("a[href*='#']")
    if (!link || link.target === "_blank" || blocked()) return
    const url = new URL(link.href, location.href)
    if (!url.hash || url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search) return
    let id = ""
    try { id = decodeURIComponent(url.hash.slice(1)) } catch { return }
    const destination = id ? document.getElementById(id) : null
    if (!destination) return
    event.preventDefault()
    history.pushState(null, "", url.hash)
    scrollTo(destination)
    if (!destination.hasAttribute("tabindex") && !/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(destination.tagName)) {
      destination.setAttribute("tabindex", "-1")
    }
    destination.focus({ preventScroll: true })
  })

  return {
    scrollTo,
    stop: () => { stopped = true; halt() },
    start: () => { stopped = false; sync() },
  }
}
