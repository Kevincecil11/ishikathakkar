import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/dist/ScrollTrigger"
import { SplitText } from "gsap/dist/SplitText"
import { ScrambleTextPlugin } from "gsap/dist/ScrambleTextPlugin"
import type { SmoothScroller } from "./smooth-scroll"

gsap.registerPlugin(ScrollTrigger, SplitText, ScrambleTextPlugin)

/* One motion language for the whole site.
 * Type rises out of masks, images wipe open, numbers count to their exact
 * copy, and everything settles on the same expo curve. Splits are reverted
 * once played, so the finished DOM, kerning and accessible text are pristine.
 */
const EASE = "expo.out"
const WIPE = "expo.inOut"
const START = "clamp(top 90%)"
const root = document.documentElement
const fine = window.matchMedia("(hover: hover) and (pointer: fine)")
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
const hasText = (el: Element) => !!el.textContent?.trim()
const trigger = (el: Element, cue: Cue) => cue.scroll === false ? undefined : { trigger: cue.trigger || el, start: START, once: true }
const insideCard = (el: Element) => el.closest(".group-top,.connected-feature,.panel,.next") ? 0.28 : 0

/** Display type: characters rise from a line mask with a slight settle. */
function riseChars(el: HTMLElement, cue: Cue = {}) {
  if (!hasText(el)) return
  let played = false
  SplitText.create(el, {
    type: "lines,chars", mask: "lines", linesClass: "itline", charsClass: "itchar", autoSplit: true,
    onSplit(self) {
      if (played) return
      return gsap.from(self.chars, {
        yPercent: 125, rotate: 5, transformOrigin: "0% 100%",
        duration: 1.25, ease: EASE, stagger: { each: Math.min(0.035, 0.6 / Math.max(self.chars.length, 1)) },
        delay: cue.delay ?? insideCard(el), scrollTrigger: trigger(el, cue),
        onComplete() { played = true; self.revert() },
      })
    },
  })
}

/** Reading text: line by line, like a page being set. */
function riseLines(el: HTMLElement, cue: Cue = {}) {
  if (!hasText(el)) return
  let played = false
  SplitText.create(el, {
    type: "lines", mask: "lines", linesClass: "itline", autoSplit: true,
    onSplit(self) {
      if (played) return
      return gsap.from(self.lines, {
        yPercent: 112, duration: 1.1, ease: EASE, stagger: 0.085,
        delay: cue.delay ?? insideCard(el), scrollTrigger: trigger(el, cue),
        onComplete() { played = true; self.revert() },
      })
    },
  })
}

/** Small mono labels decode into their exact final text. */
function decode(el: HTMLElement, cue: Cue = {}) {
  const text = el.textContent || ""
  if (el.children.length || !text.trim() || text.length > 48) { fadeUp([el], cue); return }
  const tl = gsap.timeline({ delay: cue.delay ?? insideCard(el), scrollTrigger: trigger(el, cue) })
  tl.from(el, { autoAlpha: 0, duration: 0.25, ease: "none" })
    .to(el, {
      duration: Math.min(1.1, 0.45 + text.length * 0.03),
      scrambleText: { text, chars: "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", speed: 0.7, revealDelay: 0.12 },
      ease: "none",
      onComplete() { el.textContent = text },
    }, 0)
}

function fadeUp(items: HTMLElement[], cue: Cue = {}) {
  if (!items.length) return
  gsap.from(items, {
    y: 28, autoAlpha: 0, duration: 1, ease: EASE, stagger: 0.08,
    delay: cue.delay ?? 0, scrollTrigger: trigger(items[0], cue), clearProps: "transform,opacity,visibility",
  })
}

/** Image frames open with a clip wipe while the picture settles from 1.28x.
 * Scale uses the independent CSS `scale` property through a variable, so it
 * never fights existing hover transforms or no-transform gallery rules. */
function wipe(frame: HTMLElement, cue: Cue = {}, keepScale = 1) {
  const image = frame.matches("img") ? null : frame.querySelector<HTMLElement>("img")
  const tl = gsap.timeline({ delay: cue.delay ?? 0, scrollTrigger: trigger(frame, cue) })
  tl.fromTo(frame, { clipPath: "inset(100% 0% 0% 0%)" }, {
    clipPath: "inset(0% 0% 0% 0%)", duration: 1.35, ease: WIPE, clearProps: "clipPath",
  })
  if (image) {
    tl.fromTo(image, { "--it-scale": keepScale * 1.28 }, {
      "--it-scale": keepScale, duration: 1.9, ease: EASE,
      onComplete() { if (keepScale === 1) image.style.removeProperty("--it-scale") },
    }, 0)
  }
  return tl
}

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

/** Batched entrances for cards and tiles, staggered in reading order. */
function batchRise(selector: string) {
  const items = take(all(selector))
  if (!items.length) return
  gsap.set(items, { y: 56, autoAlpha: 0, transition: "none" })
  ScrollTrigger.batch(items, {
    start: START, once: true,
    onEnter: batch => gsap.to(batch, {
      y: 0, autoAlpha: 1, duration: 1.15, ease: EASE, stagger: 0.075,
      clearProps: "transform,opacity,visibility,transition",
    }),
  })
}

function batchWipe(selector: string) {
  const frames = take(all(selector))
  if (!frames.length) return
  frames.forEach(frame => gsap.set(frame, { clipPath: "inset(100% 0% 0% 0%)" }))
  ScrollTrigger.batch(frames, {
    start: START, once: true,
    onEnter: batch => batch.forEach((frame, i) => { wipe(frame as HTMLElement, { scroll: false, delay: i * 0.07 }) }),
  })
}

/* ------------------------------------------------------------ page entrance */
function pageIn(arriving: boolean) {
  const base = arriving ? 0.42 : 0.08
  const hero = document.querySelector<HTMLElement>(".hero h1.fit > span")
  if (hero) {
    claimed.add(hero)
    riseChars(hero, { scroll: false, delay: base })
    take(all(".hero .positioning")).forEach(el => riseLines(el, { scroll: false, delay: base + 0.38 }))
    take(all(".hero-roles li")).forEach((el, i) => riseLines(el, { scroll: false, delay: base + 0.5 + i * 0.08 }))
    const actions = take(all(".hero-actions > a"))
    if (actions.length) gsap.from(actions, {
      y: 22, autoAlpha: 0, scale: 0.94, duration: 1.1, ease: EASE, stagger: 0.09, delay: base + 0.7,
      clearProps: "transform,opacity,visibility",
    })
    const band = document.querySelector<HTMLElement>(".it-marquee")
    if (band) gsap.from(band, { autoAlpha: 0, y: 30, duration: 1.3, ease: EASE, delay: base + 0.85, clearProps: "transform,opacity,visibility" })
    // Gentle depth: the name drifts and dims as the page moves on.
    gsap.to(".hero h1.fit", {
      yPercent: 18, opacity: 0.35, ease: "none",
      scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: 0.5 },
    })
  }
  const article = document.querySelector<HTMLElement>("main > article")
  if (article) {
    const crumbs = take(all(":scope > .crumbs > *", article))
    if (crumbs.length) gsap.from(crumbs, { y: 14, autoAlpha: 0, duration: 0.9, ease: EASE, stagger: 0.08, delay: base, clearProps: "transform,opacity,visibility" })
    const title = article.querySelector<HTMLElement>(":scope > h1.fit > span")
    if (title) { claimed.add(title); riseChars(title, { scroll: false, delay: base + 0.06 }) }
    take(all(":scope > .summary", article)).forEach(el => riseLines(el, { scroll: false, delay: base + 0.42 }))
    take(all(":scope > .meta dt", article)).forEach((el, i) => decode(el, { scroll: false, delay: base + 0.55 + i * 0.08 }))
    take(all(":scope > .meta dd", article)).forEach((el, i) => riseLines(el, { scroll: false, delay: base + 0.6 + i * 0.08 }))
    const panels = take(all(":scope > .project-banner .banner-image", article))
    panels.forEach((panel, i) => {
      const image = panel.querySelector<HTMLElement>("img")
      const safe = panel.hasAttribute("data-safe-frame")
      wipe(panel, { scroll: false, delay: base + 0.5 + i * 0.12 }, safe ? 1 : 1.14)
      if (image && !safe) gsap.fromTo(image, { "--it-y": "-5%" }, {
        "--it-y": "5%", ease: "none",
        scrollTrigger: { trigger: panel, start: "top bottom", end: "bottom top", scrub: 0.6 },
      })
    })
  }
  const about = document.querySelector<HTMLElement>(".about-hero")
  if (about) {
    const crumbs = take(all(".crumbs > *", about))
    if (crumbs.length) gsap.from(crumbs, { y: 14, autoAlpha: 0, duration: 0.9, ease: EASE, stagger: 0.08, delay: base, clearProps: "transform,opacity,visibility" })
    take(all(".statement", about)).forEach(el => riseLines(el, { scroll: false, delay: base + 0.1 }))
  }
}

/* ------------------------------------------------------------ scroll story */
function scrollReveals() {
  // Scroll never gates visibility now. Keep count-ups and subtle hero/banner
  // depth, but not masked type, image wipes, staggered cards or quote fills.
  take(all(".stub b,.outcome-single .stat b,.stats .stat b")).forEach(el => countUp(el))
  const quote = document.querySelector<HTMLElement>(".v1-about .statement")
  if (quote) {
    const split = SplitText.create(quote, { type: "words", wordsClass: "kinetic-word" })
    split.words.forEach(word => {
      if (/^stories/i.test(word.textContent || "")) word.classList.add("kinetic-story")
      if (/^strategy/i.test(word.textContent || "")) word.classList.add("kinetic-strategy")
    })
  }
}

// Kept here as the old choreography reference, not called by the site.
function retiredScrollReveals() {
  // Section rules draw across, then their labels decode.
  take(all(".sec-head")).forEach(head => {
    gsap.fromTo(head, { clipPath: "inset(0% 100% 0% 0%)" }, {
      clipPath: "inset(0% 0% 0% 0%)", duration: 1.3, ease: WIPE, clearProps: "clipPath", scrollTrigger: trigger(head, {}),
    })
  })
  take(all(".category-heading i")).forEach(dot => {
    gsap.from(dot, { scale: 0, rotate: -90, duration: 1.1, ease: "back.out(2.4)", scrollTrigger: trigger(dot, {}), clearProps: "transform" })
  })
  // Colour blocks open like a curtain before their type lands.
  take(all(".group-top,.panel,.connected-feature,.next,.contact-grid")).forEach(block => {
    gsap.fromTo(block, { clipPath: "inset(100% 0% 0% 0% round 8px)" }, {
      clipPath: "inset(0% 0% 0% 0% round 8px)", duration: 1.4, ease: WIPE, clearProps: "clipPath", scrollTrigger: trigger(block, {}),
    })
  })
  take(all(".category-heading h2,.group-top h2,.connected-copy > strong,.contact-intro h2")).forEach(el => riseChars(el))
  take(all([
    ".v1-about .lead", ".group-intro p", "main > article > .row h2", "main > article > .row p",
    ".learned-note blockquote", ".connected-summary", ".connected-result", ".v2-credit-note",
    ".contact-intro > p", ".group-services", ".about-body .copy p", ".client-credit h2", ".client-credit p",
  ].join(","))).forEach(el => riseLines(el))
  take(all([
    "article > .meta dt", ".group-top .mono", ".panel-label .mono", ".sec-head .mono", ".next .mono",
    ".woa-title .mono", ".connected-copy .mono", ".outcome-label .mono", ".brand-source-note",
  ].join(","))).forEach(el => decode(el))
  take(all(".stub b,.outcome-single .stat b,.stats .stat b")).forEach(el => countUp(el))

  batchWipe(".loud-clients .tile,.grid.gallery .tile,.related .tile,.proof-board figure,.connected-photo")
  take(all(".portrait")).forEach(img => {
    gsap.fromTo(img, { clipPath: "inset(100% 0% 0% 0%)" }, {
      clipPath: "inset(0% 0% 0% 0%)", duration: 1.4, ease: WIPE, clearProps: "clipPath", scrollTrigger: trigger(img, {}),
    })
  })
  batchRise(".stub,.identity-tile,.client-tile,.mini-work,.roles li,main > article > .row li,.loud-clients .cap,.studio-more,.stats .stat span,.outcome-single .stat span")

  // The quote fills word by word under the reader's own scroll.
  const quote = document.querySelector<HTMLElement>(".v1-about .statement")
  if (quote && !claimed.has(quote)) {
    claimed.add(quote)
    const split = SplitText.create(quote, { type: "words", wordsClass: "kinetic-word" })
    split.words.forEach(word => {
      if (/^stories/i.test(word.textContent || "")) word.classList.add("kinetic-story")
      if (/^strategy/i.test(word.textContent || "")) word.classList.add("kinetic-strategy")
    })
    gsap.fromTo(split.words, { opacity: 0.14 }, {
      opacity: 1, ease: "none", stagger: 0.12,
      scrollTrigger: { trigger: quote, start: "top 85%", end: "bottom 50%", scrub: 0.6 },
    })
  }
  // Next project title slides in under scroll.
  all<HTMLElement>("a.next b").forEach(title => {
    gsap.fromTo(title, { xPercent: 14 }, {
      xPercent: 0, ease: "none", scrollTrigger: { trigger: title.parentElement, start: "top bottom", end: "top 45%", scrub: 0.6 },
    })
  })
}

/* ------------------------------------------------------------ ambient + touch */
function marquee() {
  document.querySelectorAll<HTMLElement>(".it-marquee").forEach(band => {
    const track = band.querySelector<HTMLElement>(".it-marquee-track")
    if (!track) return
    band.classList.add("is-live")
    const setX = gsap.quickSetter(track, "x", "px") as (value: number) => void
    const skew = gsap.quickTo(track, "skewX", { duration: 0.5, ease: "power3" })
    const watch = ScrollTrigger.create({ trigger: band, start: "top bottom", end: "bottom top" })
    let x = 0, boost = 1, direction = -1
    gsap.ticker.add((_time, deltaMs) => {
      if (!watch.isActive || document.hidden) return
      const velocity = watch.getVelocity()
      if (Math.abs(velocity) > 20) direction = velocity > 0 ? -1 : 1
      boost += (1 + Math.min(Math.abs(velocity) / 260, 7) - boost) * 0.08
      skew(gsap.utils.clamp(-6, 6, velocity / -320))
      const half = track.scrollWidth / 2
      x = gsap.utils.wrap(-half, 0, x + direction * 52 * boost * deltaMs / 1000)
      setX(x)
    })
  })
}

function magnetic() {
  if (!fine.matches) return
  all<HTMLElement>("a.pill,.v2-nav a").forEach(el => {
    const strength = el.matches(".v2-nav a") ? 0.22 : 0.32
    const x = gsap.quickTo(el, "x", { duration: 0.7, ease: "power3" })
    const y = gsap.quickTo(el, "y", { duration: 0.7, ease: "power3" })
    el.addEventListener("pointermove", event => {
      const r = el.getBoundingClientRect()
      x((event.clientX - r.left - r.width / 2) * strength)
      y((event.clientY - r.top - r.height / 2) * strength)
    })
    el.addEventListener("pointerleave", () => { x(0); y(0) })
  })
}

function cursorBadge() {
  if (!fine.matches) return
  const rules: [string, string][] = [
    [".proof-board a,.project-banner a,.poster-photo a", "View"],
    [".loud-clients .card,.grid.gallery .card,.connected-feature", "Open"],
    ["a.next", "Next"],
  ]
  const selector = rules.map(rule => rule[0]).join(",")
  const badge = document.createElement("div")
  badge.className = "it-cursor"
  badge.setAttribute("aria-hidden", "true")
  const label = document.createElement("span")
  badge.append(label)
  document.body.append(badge)
  gsap.set(badge, { xPercent: -50, yPercent: -50, scale: 0, autoAlpha: 0 })
  const x = gsap.quickTo(badge, "x", { duration: 0.55, ease: "power3" })
  const y = gsap.quickTo(badge, "y", { duration: 0.55, ease: "power3" })
  let shown: Element | null = null, seen = false
  window.addEventListener("pointermove", event => {
    if (!seen) { gsap.set(badge, { x: event.clientX, y: event.clientY }); seen = true }
    x(event.clientX); y(event.clientY)
  }, { passive: true })
  document.addEventListener("pointerover", event => {
    const hit = (event.target as Element | null)?.closest?.(selector) || null
    if (hit === shown) return
    shown = hit
    if (hit && !document.querySelector("dialog[open]")) {
      label.textContent = rules.find(rule => hit.matches(rule[0]))?.[1] || "View"
      gsap.to(badge, { scale: 1, autoAlpha: 1, duration: 0.5, ease: EASE, overwrite: "auto" })
    } else {
      gsap.to(badge, { scale: 0, autoAlpha: 0, duration: 0.35, ease: "power3.out", overwrite: "auto" })
    }
  })
  document.addEventListener("pointerleave", () => { shown = null; gsap.to(badge, { scale: 0, autoAlpha: 0, duration: 0.3 }) })
  document.addEventListener("click", () => { if (document.querySelector("dialog[open]")) gsap.set(badge, { scale: 0, autoAlpha: 0 }) }, true)
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
  const curtain = document.querySelector(".curtain")
  const arriving = !!curtain && /\b(hold|lift)\b/.test(curtain.className)
  const fallback = root.classList.contains("motion-fallback")
  const fonts = document.fonts?.ready ?? Promise.resolve()
  const wait = new Promise(resolve => setTimeout(resolve, 900))
  // Dialogs pause inertia so the viewer never fights the page behind it.
  if (scroller) {
    new MutationObserver(() => document.querySelector("dialog[open]") ? scroller.stop() : scroller.start())
      .observe(document.body, { subtree: true, attributes: true, attributeFilter: ["open"] })
  }
  Promise.race([fonts, wait]).then(() => {
    if (!fallback) pageIn(arriving)
    scrollReveals()
    root.classList.add("motion-ready")
    chrome()
    ScrollTrigger.refresh()
  })
  window.addEventListener("load", () => ScrollTrigger.refresh())
}
