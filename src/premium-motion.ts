import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/dist/ScrollTrigger"
import type { SmoothScroller } from "./smooth-scroll"

gsap.registerPlugin(ScrollTrigger)

/* One motion language for the whole site.
 * Type rises out of masks, images wipe open, numbers count to their exact
 * copy, and everything settles on the same expo curve. Splits are reverted
 * once played, so the finished DOM, kerning and accessible text are pristine.
 */
const EASE = "expo.out"
const START = "clamp(top 90%)"
const root = document.documentElement
const claimed = new WeakSet<Element>()
const EXCLUDE = ".hwf-root,.contact-form,dialog,.it-marquee,.curtain,[data-halftone-footer]"

type Cue = { delay?: number; scroll?: boolean; trigger?: Element }

const all = <T extends Element = HTMLElement>(selector: string, scope: ParentNode = document) =>
  Array.from(scope.querySelectorAll<T>(selector)).filter(el => !el.closest(EXCLUDE))
const take = <T extends Element>(items: T[]) => items.filter(el => {
  if (claimed.has(el)) return false
  claimed.add(el)
  return true
})
const trigger = (el: Element, cue: Cue) => cue.scroll === false ? undefined : { trigger: cue.trigger || el, start: START, once: true }

/** Numbers count up and finish on the exact original copy, formatting intact. */
function countUp(el: HTMLElement, cue: Cue = {}) {
  const original = el.textContent || ""
  const match = original.match(/^(\D*?)(\d[\d,]*(?:\.\d+)?)(\D*)$/)
  if (!match) return
  const [, prefix, raw, suffix] = match
  const value = parseFloat(raw.replace(/,/g, ""))
  if (!isFinite(value) || value < 2) return
  const decimals = (raw.split(".")[1] || "").length
  const locale = /^\d{1,2}(,\d{2})+,\d{3}/.test(raw) ? "en-IN" : "en-US"
  const grouped = raw.includes(",")
  const format = (n: number) => n.toLocaleString(locale, {
    minimumFractionDigits: decimals, maximumFractionDigits: decimals, useGrouping: grouped,
  })
  const counter = { n: 0 }
  const width = el.getBoundingClientRect().width
  gsap.to(counter, {
    n: value, duration: 1.9, ease: "power3.out", delay: (cue.delay ?? 0) + 0.15, scrollTrigger: trigger(el, cue),
    onStart() { if (getComputedStyle(el).display !== "flex") el.style.minWidth = width + "px" },
    onUpdate() { el.textContent = prefix + format(decimals ? counter.n : Math.round(counter.n)) + suffix },
    onComplete() { el.textContent = original; el.style.minWidth = "" },
  })
  el.textContent = prefix + format(0) + suffix
}

/* The first screen's entrance is pure CSS (premium-motion.css), so the name and
 * banners paint immediately instead of waiting for this bundle. Script-driven
 * motion here is limited to scroll-linked depth, counters and the header. */
function pageIn() {
  if (document.querySelector(".hero h1.fit")) {
    // Gentle depth: the name drifts and dims as the page moves on.
    gsap.to(".hero h1.fit", {
      yPercent: 18, opacity: 0.35, ease: "none",
      scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: 0.5 },
    })
  }
}

function scrollReveals() {
  take(all(".stub b,.outcome-single .stat b,.stats .stat b")).forEach(el => countUp(el, { scroll: false }))
}

function chrome() {
  const header = document.querySelector<HTMLElement>(".hdr")
  const bar = document.createElement("div")
  bar.className = "it-progress"
  bar.setAttribute("aria-hidden", "true")
  document.body.append(bar)
  const setBar = gsap.quickSetter(bar, "scaleX") as (value: number) => void
  ScrollTrigger.create({
    start: 0, end: "max",
    onUpdate(self) {
      setBar(self.progress)
      if (!header) return
      const y = self.scroll()
      header.classList.toggle("is-scrolled", y > 24)
      if (header.contains(document.activeElement)) { header.classList.remove("is-hidden"); return }
      if (self.direction === 1 && y > 220) header.classList.add("is-hidden")
      else if (self.direction === -1 || y < 120) header.classList.remove("is-hidden")
    },
  })
}

export function initPremiumMotion(scroller: SmoothScroller | null) {
  root.dataset.motion = "premium"
  ;(window as unknown as { __itMotion?: SmoothScroller | true }).__itMotion = scroller || true
  // Dialogs pause inertia so the viewer never fights the page behind it.
  if (scroller) {
    new MutationObserver(() => document.querySelector("dialog[open]") ? scroller.stop() : scroller.start())
      .observe(document.body, { subtree: true, attributes: true, attributeFilter: ["open"] })
  }
  root.classList.add("motion-ready")
  pageIn()
  scrollReveals()
  chrome()
  window.addEventListener("load", () => ScrollTrigger.refresh(), { once: true })
}
