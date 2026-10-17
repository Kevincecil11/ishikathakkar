import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/dist/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

/** A progressive motion layer, not a scroll replacement or a content rewrite. */
export function startSiteChoreography() {
  document.documentElement.dataset.motionEngine = "gsap-" + gsap.version
  const preference = window.matchMedia("(prefers-reduced-motion: reduce)")
  const mm = gsap.matchMedia()
  const quote = document.querySelector<HTMLElement>(".v1-about .statement")
  if (quote && !quote.dataset.kinetic) {
    const exact = quote.textContent || ""
    quote.dataset.kinetic = "true"
    quote.setAttribute("aria-label", exact)
    const fragment = document.createDocumentFragment()
    exact.split(/(\s+)/).forEach(part => {
      if (!part.trim()) { fragment.append(document.createTextNode(part)); return }
      const word = document.createElement("span")
      word.className = "kinetic-word"
      if (/^stories/i.test(part)) word.classList.add("kinetic-story")
      if (/^strategy/i.test(part)) word.classList.add("kinetic-strategy")
      word.textContent = part
      word.setAttribute("aria-hidden", "true")
      fragment.append(word)
    })
    quote.replaceChildren(fragment)
  }
  mm.add("(prefers-reduced-motion: no-preference)", () => {
    const entrance = document.querySelector(".hero h1 > span, article h1 > span, .about-hero h1")
    if (entrance) gsap.fromTo(entrance, { y: 35, opacity: 0 }, { y: 0, opacity: 1, duration: 0.9, ease: "power3.out", clearProps: "transform,opacity" })
    gsap.fromTo(".hero-row > *, .hero-actions", { y: 18, opacity: 0 }, {
      y: 0, opacity: 1, stagger: 0.1, duration: 0.7, delay: 0.18, ease: "power2.out", clearProps: "transform,opacity",
    })
    gsap.utils.toArray<HTMLElement>(".category-heading,.sec-head,.group-top,.client-tile,.mini-work,.row:not(.client-credit),.contact-grid,.summary").forEach(el => {
      gsap.fromTo(el, { y: 25, opacity: 0 }, {
        y: 0, opacity: 1, duration: 0.7, ease: "power2.out", clearProps: "transform,opacity",
        scrollTrigger: { trigger: el, start: "top 94%", once: true },
      })
    })
    if (quote) {
      gsap.fromTo(quote.querySelectorAll(".kinetic-word"), { y: 18, opacity: 0.3 }, {
        y: 0, opacity: 1, duration: 0.65, stagger: 0.045, ease: "power2.out",
        scrollTrigger: { trigger: quote, start: "top 88%", once: true },
        clearProps: "transform,opacity",
      })
      gsap.fromTo(quote.querySelectorAll(".kinetic-story,.kinetic-strategy"), { rotation: -4 }, {
        rotation: 0, duration: 1.2, ease: "elastic.out(1,0.6)",
        scrollTrigger: { trigger: quote, start: "top 86%", once: true },
        clearProps: "transform",
      })
    }
    // Slow, small image shifts on pointer-capable desktops only.
    if (window.matchMedia("(min-width: 900px) and (pointer: fine)").matches) {
      gsap.utils.toArray<HTMLElement>(".story-image img,.project-hero img,.ggrid img").forEach(img => {
        gsap.fromTo(img, { yPercent: -2, scale: 1.04 }, {
          yPercent: 2, scale: 1.04, ease: "none",
          scrollTrigger: { trigger: img.parentElement, start: "top bottom", end: "bottom top", scrub: 0.6 },
        })
      })
    }
    return () => { /* gsap.matchMedia reverts its animations and triggers. */ }
  })
  document.fonts?.ready.then(() => ScrollTrigger.refresh())
  initOrbit(preference)
}

/** GSAP ticker + quickSetter: smooth drag, damped release, and speed control.
 * Pointer Events avoid touch-scroll hijacking. No premium plugin is required.
 */
function initOrbit(preference: MediaQueryList) {
  const panel = document.querySelector<HTMLElement>(".client-ribbon")
  if (!panel) return
  const track = panel.querySelector<HTMLElement>(".orbit-track")
  const windowEl = panel.querySelector<HTMLElement>(".orbit-window")
  const toggle = panel.querySelector<HTMLInputElement>(".reel-toggle")
  if (!track || !windowEl || !toggle) return
  const slots = Array.from(track.querySelectorAll<HTMLElement>(".orbit-slot"))
  panel.classList.add("gsap-orbit")
  panel.dataset.orbitEngine = "gsap"
  panel.querySelectorAll(".reel-control").forEach(x => x.remove())
  const controls = document.createElement("div")
  controls.className = "orbit-controls"
  controls.innerHTML = `<span class="orbit-hint">Drag to rotate</span>
    <div class="orbit-navigation"><button type="button" aria-label="Rotate client logos left">←</button>
    <button type="button" class="orbit-play">Pause</button>
    <button type="button" aria-label="Rotate client logos right">→</button></div>
    <label class="orbit-speed">Speed <input type="range" min="0" max="2" step="0.1" value="0.6" aria-label="Logo rotation speed"></label>`
  panel.append(controls)
  const [left, play, right] = controls.querySelectorAll<HTMLButtonElement>("button")
  const speed = controls.querySelector<HTMLInputElement>("input")!
  windowEl.tabIndex = 0
  windowEl.setAttribute("role", "group")
  windowEl.setAttribute("aria-label", "Interactive client logos. Drag horizontally or use left and right arrow keys to rotate.")
  // All clients stay present to assistive tech; only one cluster is visual.
  const model = { angle: 0, velocity: 0 }
  let paused = preference.matches || toggle.checked, visible = false
  let dragging = false, pointer = -1, lastX = 0, lastY = 0, originX = 0, originY = 0, lastTime = 0
  let dragIntent = false, lastDraw = -1, frame = 0, wakeAttached = false
  let width = 1, height = 1
  const setters = slots.map(slot => ({
    x: gsap.quickSetter(slot, "x", "px"),
    y: gsap.quickSetter(slot, "y", "px"),
  }))
  gsap.set(slots, { xPercent: 0, yPercent: 0, rotation: 0, scale: 1 })
  slots.forEach(slot => {
    slot.style.setProperty("animation", "none", "important")
    const upright = slot.querySelector<HTMLElement>(".orbit-upright")!
    upright.style.setProperty("animation", "none", "important")
  })
  const syncPlay = () => {
    toggle.checked = paused
    play.textContent = paused ? "Play" : "Pause"
    play.setAttribute("aria-label", paused ? "Play client logo rotation" : "Pause client logo rotation")
    panel.dataset.orbitPlaying = String(!paused)
  }
  const render = () => {
    const badge = slots[0]?.offsetWidth || 48
    const rx = width * 0.37, ry = Math.max(20, height / 2 - badge / 2 - 3)
    // Four badges around the circle, cycling every quarter-turn. The center
    // studio pair stays still. This stays readable at 320px, unlike 13 tiny dots.
    const turn = ((model.angle % 360) + 360) % 360
    const group = Math.floor(((model.angle % (360 * Math.ceil(slots.length / 4))) + 360 * Math.ceil(slots.length / 4)) / 360) % Math.ceil(slots.length / 4)
    slots.forEach((slot, i) => {
      const show = Math.floor(i / 4) === group
      slot.style.opacity = show ? "1" : "0"
      slot.style.visibility = show ? "visible" : "hidden"
      if (!show) return
      const theta = (turn + (i % 4) * 90 - 90) * Math.PI / 180
      setters[i].x(width / 2 + Math.cos(theta) * rx - slot.offsetWidth / 2)
      setters[i].y(height / 2 + Math.sin(theta) * ry - slot.offsetHeight / 2)
    })
    panel.dataset.orbitAngle = model.angle.toFixed(2)
  }
  const resize = () => {
    const b = windowEl.getBoundingClientRect(); width = b.width; height = b.height
    render()
  }
  const tick = (_time: number, deltaMs: number) => {
    if (!visible || document.hidden) return
    const delta = Math.min(40, deltaMs || 16.7) / 1000
    if (!dragging) {
      if (Math.abs(model.velocity) > 0.01) {
        model.angle += model.velocity * delta
        model.velocity *= Math.pow(0.07, delta)
      } else model.velocity = 0
      if (!paused && !preference.matches) model.angle += Number(speed.value) * 18 * delta
      // Reduce Motion visitors can explicitly opt in with Play.
      if (!paused && preference.matches && panel.classList.contains("motion-enabled")) model.angle += Number(speed.value) * 18 * delta
    }
    if (model.angle !== lastDraw) { lastDraw = model.angle; render(); frame++ }
    panel.dataset.orbitFrames = String(frame)
    if (paused && !dragging && !model.velocity) detach()
  }
  function detach() { if (wakeAttached) { gsap.ticker.remove(tick); wakeAttached = false } }
  function wake() {
    if (visible && !document.hidden && !wakeAttached) { gsap.ticker.add(tick); wakeAttached = true }
  }
  const rotate = (amount: number) => {
    model.velocity = 0
    gsap.to(model, { angle: model.angle + amount, duration: preference.matches ? 0 : 0.65, ease: "power3.out", overwrite: true, onUpdate: render })
  }
  left.addEventListener("click", () => rotate(-90))
  right.addEventListener("click", () => rotate(90))
  play.addEventListener("click", () => {
    paused = !paused; model.velocity = 0
    if (!paused) panel.classList.add("motion-enabled")
    syncPlay(); wake()
  })
  speed.addEventListener("input", () => {
    if (Number(speed.value) > 0 && !preference.matches) paused = false
    syncPlay(); wake()
  })
  windowEl.addEventListener("keydown", e => {
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") { e.preventDefault(); rotate(e.key === "ArrowLeft" ? -45 : 45) }
  })
  windowEl.addEventListener("pointerdown", e => {
    if (e.button !== 0) return
    gsap.killTweensOf(model)
    pointer = e.pointerId; originX = lastX = e.clientX; originY = lastY = e.clientY
    lastTime = performance.now(); model.velocity = 0; dragIntent = false
    if (e.pointerType !== "touch") { dragging = true; windowEl.setPointerCapture(pointer); panel.classList.add("is-dragging") }
    wake()
  })
  windowEl.addEventListener("pointermove", e => {
    if (e.pointerId !== pointer) return
    const dx = e.clientX - originX, dy = e.clientY - originY
    if (!dragging) {
      if (Math.abs(dy) > 10 && Math.abs(dy) > Math.abs(dx)) { pointer = -1; return }
      if (Math.abs(dx) < 8) return
      dragging = true; windowEl.setPointerCapture(pointer); panel.classList.add("is-dragging")
    }
    dragIntent = true
    const now = performance.now(), diff = e.clientX - lastX
    const scale = 360 / Math.max(300, width * 1.4)
    model.angle += diff * scale
    model.velocity = Math.max(-220, Math.min(220, diff * scale * 1000 / Math.max(12, now - lastTime)))
    lastX = e.clientX; lastY = e.clientY; lastTime = now
    render(); wake()
  })
  const release = (e: PointerEvent) => {
    if (e.pointerId !== pointer) return
    if (windowEl.hasPointerCapture(pointer)) windowEl.releasePointerCapture(pointer)
    pointer = -1; dragging = false
    panel.classList.remove("is-dragging")
    if (preference.matches || paused || !dragIntent) model.velocity = 0
    wake()
  }
  windowEl.addEventListener("pointerup", release)
  windowEl.addEventListener("pointercancel", release)
  const onMotionPreference = () => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches
    paused = reduced; model.velocity = 0
    panel.classList.toggle("motion-enabled", !reduced)
    syncPlay(); render(); wake()
  }
  preference.addEventListener("change", onMotionPreference)
  // A dedicated MQL keeps this state independent of ScrollTrigger's queries.
  const orbitPreference = window.matchMedia("(prefers-reduced-motion: reduce)")
  orbitPreference.onchange = onMotionPreference
  const io = new IntersectionObserver(entries => {
    visible = entries[0]?.isIntersecting ?? true
    if (visible) wake(); else detach()
  })
  io.observe(panel)
  document.addEventListener("visibilitychange", () => { if (document.hidden) detach(); else wake() })
  new ResizeObserver(resize).observe(windowEl)
  syncPlay(); resize()
}
