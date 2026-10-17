import { gsap } from "gsap"

type Body = {
  el: HTMLElement; button: HTMLButtonElement
  x: number; y: number; hx: number; hy: number; vx: number; vy: number; r: number
  tx: number; ty: number; offset: number
  setX: (value: number) => void; setY: (value: number) => void
}

/**
 * A small, real fixed-step spring/impulse simulation, rendered by GSAP.
 * Moving spring targets create a continuous circular orbit, without spinning
 * the logo artwork. Badges retain their own mass, velocity and 2D collisions.
 * No sliders, arrow controls or premium plugin. Sleeps offscreen/when hidden.
 */
export function initLogoPhysics(preference: MediaQueryList) {
  const panel = document.querySelector<HTMLElement>(".logo-playground")
  const plane = panel?.querySelector<HTMLElement>(".logo-stage-area")
  const hub = panel?.querySelector<HTMLElement>(".studio-hub")
  if (!panel || !plane || !hub) return
  const status = panel.querySelector<HTMLElement>(".logo-status")!
  // Keep the runtime preference callback independent of GSAP matchMedia cleanup.
  const physicsPreference = window.matchMedia("(prefers-reduced-motion: reduce)")
  let width = 1, height = 1, visible = false, attached = false, accumulator = 0, frames = 0
  let phase = 0, radius = 1, focusPaused = false
  const angularSpeed = Math.PI * 2 / 84
  let selected: Body | null = null, pointer = -1, keyboardGrab = false
  let offsetX = 0, offsetY = 0, samples: { x: number; y: number; t: number }[] = []
  let obstacle = { left: 0, right: 0, top: 0, bottom: 0 }
  const bodies: Body[] = Array.from(plane.querySelectorAll<HTMLElement>(".logo-body")).map(el => ({
    el, button: el.querySelector<HTMLButtonElement>("button")!,
    x: 0, y: 0, hx: 0, hy: 0, vx: 0, vy: 0, r: 24, tx: 0, ty: 0, offset: 0,
    setX: gsap.quickSetter(el, "x", "px") as (value: number) => void,
    setY: gsap.quickSetter(el, "y", "px") as (value: number) => void,
  }))
  const clamp = (value: number, low: number, high: number) => Math.max(low, Math.min(high, value))
  const announce = (text: string) => { status.textContent = text }
  const targets = (dt = 0) => {
    const moving = !preference.matches && !selected && !focusPaused
    if (moving) phase = (phase + angularSpeed * dt) % (Math.PI * 2)
    for (const b of bodies) {
      const angle = phase + b.offset
      b.hx = width / 2 + Math.cos(angle) * radius
      b.hy = height / 2 + Math.sin(angle) * radius
      b.tx = moving ? -Math.sin(angle) * radius * angularSpeed : 0
      b.ty = moving ? Math.cos(angle) * radius * angularSpeed : 0
    }
    panel.dataset.orbitPhase = phase.toFixed(5)
    panel.dataset.orbitLooping = String(moving)
  }
  const draw = () => {
    for (const b of bodies) {
      b.setX(b.x - b.el.offsetWidth / 2); b.setY(b.y - b.el.offsetHeight / 2)
    }
    panel.dataset.physicsFrames = String(++frames)
  }
  const stop = () => {
    if (attached) gsap.ticker.remove(tick)
    attached = false
    panel.dataset.physicsSleeping = "true"
  }
  const wake = () => {
    if (!attached && visible && !document.hidden) {
      accumulator = 0; gsap.ticker.add(tick); attached = true
      panel.dataset.physicsSleeping = "false"
    }
  }
  const keepInBounds = (b: Body, bounce: boolean) => {
    const restitution = bounce ? 0.58 : 0
    if (b.x < b.r) { b.x = b.r; b.vx = Math.abs(b.vx) * restitution }
    if (b.x > width - b.r) { b.x = width - b.r; b.vx = -Math.abs(b.vx) * restitution }
    if (b.y < b.r) { b.y = b.r; b.vy = Math.abs(b.vy) * restitution }
    if (b.y > height - b.r) { b.y = height - b.r; b.vy = -Math.abs(b.vy) * restitution }
    // Resolve against the fixed parent-company hub, including corner contacts.
    const qx = clamp(b.x, obstacle.left, obstacle.right)
    const qy = clamp(b.y, obstacle.top, obstacle.bottom)
    let dx = b.x - qx, dy = b.y - qy, distance = Math.hypot(dx, dy)
    if (distance < b.r) {
      if (distance < 0.001) {
        const exits = [
          { d: b.x - obstacle.left, x: -1, y: 0 },
          { d: obstacle.right - b.x, x: 1, y: 0 },
          { d: b.y - obstacle.top, x: 0, y: -1 },
          { d: obstacle.bottom - b.y, x: 0, y: 1 },
        ].sort((a, c) => a.d - c.d)
        dx = exits[0].x; dy = exits[0].y; distance = 1
        b.x += dx * (exits[0].d + b.r); b.y += dy * (exits[0].d + b.r)
      } else {
        b.x += dx / distance * (b.r - distance)
        b.y += dy / distance * (b.r - distance)
      }
      const nx = dx / distance, ny = dy / distance, normal = b.vx * nx + b.vy * ny
      if (normal < 0) { b.vx -= (1 + restitution) * normal * nx; b.vy -= (1 + restitution) * normal * ny }
    }
  }
  const contacts = (impulses: boolean) => {
    for (let i = 0; i < bodies.length; i++) for (let j = i + 1; j < bodies.length; j++) {
      const a = bodies[i], b = bodies[j], dx = b.x - a.x, dy = b.y - a.y
      const distance = Math.hypot(dx, dy), sum = a.r + b.r
      if (distance >= sum) continue
      const nx = distance > 0.001 ? dx / distance : 1, ny = distance > 0.001 ? dy / distance : 0
      const ia = a === selected ? 0 : 1, ib = b === selected ? 0 : 1, inverse = ia + ib
      if (!inverse) continue
      const overlap = (sum - distance + 0.02) / inverse
      a.x -= nx * overlap * ia; a.y -= ny * overlap * ia
      b.x += nx * overlap * ib; b.y += ny * overlap * ib
      const speed = (b.vx - a.vx) * nx + (b.vy - a.vy) * ny
      if (impulses && speed < 0) {
        const impulse = -(1.62 * speed) / inverse
        a.vx -= impulse * nx * ia; a.vy -= impulse * ny * ia
        b.vx += impulse * nx * ib; b.vy += impulse * ny * ib
      }
    }
    bodies.forEach(b => keepInBounds(b, impulses && b !== selected))
  }
  const step = (dt: number) => {
    targets(dt)
    for (const b of bodies) {
      if (b === selected) continue
      b.vx = b.tx + (b.vx - b.tx + (b.hx - b.x) * 3.5 * dt) * Math.exp(-2.25 * dt)
      b.vy = b.ty + (b.vy - b.ty + (b.hy - b.y) * 3.5 * dt) * Math.exp(-2.25 * dt)
      b.x += b.vx * dt; b.y += b.vy * dt
      keepInBounds(b, true)
    }
    for (let i = 0; i < 4; i++) contacts(i === 0)
  }
  function tick(_time: number, deltaMs: number) {
    if (!visible || document.hidden) { stop(); return }
    accumulator += Math.min(deltaMs || 16.67, 50) / 1000
    while (accumulator >= 1 / 120) { step(1 / 120); accumulator -= 1 / 120 }
    draw()
    const settled = bodies.every(b => Math.hypot(b.vx, b.vy) < 0.8 && Math.hypot(b.x - b.hx, b.y - b.hy) < 0.65)
    if (!selected && settled && (preference.matches || focusPaused)) {
      bodies.forEach(b => { b.x = b.hx; b.y = b.hy; b.vx = b.vy = 0 })
      draw(); stop()
    }
  }
  const finish = (cancelled = false) => {
    if (!selected) return
    const b = selected
    if (pointer >= 0 && b.button.hasPointerCapture(pointer)) b.button.releasePointerCapture(pointer)
    // Use the latest 90ms, not the whole gesture, so a slow finish stays slow.
    const recent = samples.filter(s => performance.now() - s.t < 90)
    if (!cancelled && !preference.matches && recent.length > 1 && !keyboardGrab) {
      const first = recent[0], last = recent[recent.length - 1], dt = Math.max(16, last.t - first.t) / 1000
      b.vx = clamp((last.x - first.x) / dt, -1500, 1500)
      b.vy = clamp((last.y - first.y) / dt, -1500, 1500)
    } else b.vx = b.vy = 0
    b.button.setAttribute("aria-pressed", "false"); b.el.classList.remove("is-held")
    selected = null; pointer = -1; keyboardGrab = false; samples = []
    panel.classList.remove("is-dragging")
    targets()
    if (preference.matches || cancelled) {
      bodies.forEach(body => { body.x = body.hx; body.y = body.hy; body.vx = body.vy = 0 })
      draw(); stop()
      if (!preference.matches && !focusPaused && visible) wake()
    } else wake()
    announce(`${b.button.dataset.name} released.`)
  }
  const begin = (b: Body, keyboard = false) => {
    if (selected) finish(true)
    selected = b; b.vx = b.vy = 0; keyboardGrab = keyboard
    b.el.classList.add("is-held"); b.button.setAttribute("aria-pressed", "true")
    panel.classList.add("is-dragging")
    announce(`${b.button.dataset.name} grabbed.`); wake()
  }
  for (const b of bodies) {
    b.button.disabled = false
    b.button.addEventListener("dragstart", e => e.preventDefault())
    b.button.addEventListener("pointerdown", e => {
      if (e.button !== 0 || !e.isPrimary) return
      e.preventDefault(); begin(b); pointer = e.pointerId
      focusPaused = false
      const rect = plane.getBoundingClientRect()
      offsetX = e.clientX - rect.left - b.x; offsetY = e.clientY - rect.top - b.y
      samples = [{ x: b.x, y: b.y, t: performance.now() }]
      b.button.setPointerCapture(pointer); b.button.focus({ preventScroll: true }); focusPaused = false
    })
    b.button.addEventListener("pointermove", e => {
      if (selected !== b || e.pointerId !== pointer) return
      const rect = plane.getBoundingClientRect()
      const oldX = b.x, oldY = b.y
      b.x = e.clientX - rect.left - offsetX; b.y = e.clientY - rect.top - offsetY
      keepInBounds(b, false)
      const now = performance.now(), prior = samples[samples.length - 1]
      const dt = Math.max(8, now - (prior?.t ?? now)) / 1000
      b.vx = clamp((b.x - oldX) / dt, -1500, 1500); b.vy = clamp((b.y - oldY) / dt, -1500, 1500)
      samples.push({ x: b.x, y: b.y, t: now }); samples = samples.filter(s => now - s.t < 110)
      for (let i = 0; i < 5; i++) contacts(false)
      draw(); wake()
    })
    b.button.addEventListener("pointerup", e => {
      if (e.pointerId === pointer) { finish(); b.button.blur(); focusPaused = false; wake() }
    })
    b.button.addEventListener("pointercancel", e => { if (e.pointerId === pointer) finish(true) })
    b.button.addEventListener("lostpointercapture", () => { if (selected === b && !keyboardGrab && pointer >= 0) finish(true) })
    b.button.addEventListener("keydown", e => {
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault()
        if (selected === b && keyboardGrab) finish(); else begin(b, true)
      } else if (e.key === "Escape" && selected === b) { e.preventDefault(); finish(true) }
      else if (keyboardGrab && selected === b && e.key.startsWith("Arrow")) {
        e.preventDefault()
        const amount = e.shiftKey ? 28 : 12
        if (e.key === "ArrowLeft") b.x -= amount
        if (e.key === "ArrowRight") b.x += amount
        if (e.key === "ArrowUp") b.y -= amount
        if (e.key === "ArrowDown") b.y += amount
        b.vx = b.vy = 0; keepInBounds(b, false)
        for (let i = 0; i < 5; i++) contacts(false)
        draw(); wake()
      }
    })
    b.button.addEventListener("blur", () => { if (selected === b && keyboardGrab) finish() })
  }
  const layout = () => {
    if (selected) finish(true)
    stop()
    width = plane.clientWidth; height = plane.clientHeight
    const rect = plane.getBoundingClientRect(), h = hub.getBoundingClientRect()
    obstacle = { left: h.left - rect.left - 6, right: h.right - rect.left + 6, top: h.top - rect.top - 6, bottom: h.bottom - rect.top + 6 }
    const diameter = bodies[0].el.offsetWidth, r = diameter / 2
    radius = Math.min(width, height) / 2 - r - 3
    bodies.forEach((b, i) => {
      b.r = r; b.offset = i * Math.PI * 2 / bodies.length - Math.PI / 2
      b.vx = b.vy = 0
    })
    targets()
    bodies.forEach(b => { b.x = b.hx; b.y = b.hy; b.vx = b.tx; b.vy = b.ty })
    for (let i = 0; i < 30; i++) contacts(false)
    draw(); panel.dataset.physicsEngine = "spring-impulse-gsap"; panel.dataset.physicsCount = String(bodies.length)
    panel.dataset.physicsSleeping = "true"
    if (!preference.matches && visible) wake()
  }
  panel.classList.add("physics-ready")
  gsap.set(bodies.map(b => b.el), { xPercent: 0, yPercent: 0 })
  new ResizeObserver(layout).observe(plane)
  const io = new IntersectionObserver(entries => {
    visible = entries[0]?.isIntersecting ?? true
    if (!visible) { if (selected) finish(true); stop() }
    else if (!preference.matches || bodies.some(b => Math.hypot(b.vx, b.vy) > 0.8 || Math.hypot(b.x - b.hx, b.y - b.hy) > 0.65)) wake()
  })
  io.observe(panel)
  document.addEventListener("visibilitychange", () => { if (document.hidden) { finish(true); stop() } else if (visible) wake() })
  const onPreferenceChange = () => {
    finish(true); targets(); bodies.forEach(b => { b.x = b.hx; b.y = b.hy; b.vx = b.vy = 0 }); draw(); stop()
    if (!preference.matches) wake()
  }
  preference.addEventListener("change", onPreferenceChange)
  physicsPreference.onchange = onPreferenceChange
  panel.addEventListener("focusin", () => { if (pointer < 0) { focusPaused = true; targets(); wake() } })
  panel.addEventListener("focusout", e => {
    if (!panel.contains(e.relatedTarget as Node | null)) { focusPaused = false; targets(); if (!preference.matches) wake() }
  })
  window.addEventListener("blur", () => { if (selected) finish(true) })
  layout()
}
