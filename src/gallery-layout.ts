/** Larger edge-to-edge thumbnails; the viewer always opens the complete image.
 * Cropping is a preview treatment only. Sources and their order are preserved.
 */
export function initGalleryLayout() {
  // Measure the original Indravansh layout at this exact width, with the live
  // fonts. Other results panels inherit its size; Indravansh itself is unchanged.
  const panel = document.querySelector<HTMLElement>("[data-outcome-panel]")
  const reference = document.querySelector<HTMLTemplateElement>("template[data-outcome-reference]")
  if (panel && reference) {
    const size = () => {
      const probe = reference.content.firstElementChild?.cloneNode(true) as HTMLElement | undefined
      if (!probe) return
      probe.setAttribute("aria-hidden", "true")
      Object.assign(probe.style, {
        position: "absolute", visibility: "hidden", pointerEvents: "none",
        width: panel.getBoundingClientRect().width + "px", left: "-10000px", margin: "0",
      })
      panel.parentElement?.append(probe)
      panel.style.setProperty("--outcome-height", probe.getBoundingClientRect().height + "px")
      probe.remove()
    }
    let previousWidth = 0
    new ResizeObserver(() => {
      const width = panel.getBoundingClientRect().width
      if (width !== previousWidth) { previousWidth = width; size() }
    }).observe(panel)
    document.fonts?.ready.then(size)
    document.fonts?.addEventListener("loadingdone", size)
    size()
  }
  const allLinks: HTMLAnchorElement[] = []
  document.querySelectorAll<HTMLElement>(".uploaded-gallery").forEach(gallery => {
    const figures = Array.from(gallery.querySelectorAll<HTMLElement>("figure"))
    if (!figures.length) return
    gallery.classList.add("proof-board")
    let frame = 0
    const layout = () => {
      frame = 0
      const width = gallery.clientWidth
      if (width < 1) return
      const gap = 8
      const columns = Math.min(figures.length,
        width >= 1200 ? 6 : width >= 900 ? 5 : width >= 650 ? 4 : width >= 420 ? 3 : 2)
      const cellWidth = (width - gap * (columns - 1)) / columns
      const rowHeight = Math.min(300, Math.max(140, cellWidth * 1.15))
      gallery.style.setProperty("--proof-columns", String(columns))
      gallery.style.setProperty("--proof-row-height", `${rowHeight}px`)
      gallery.style.setProperty("--proof-gap", `${gap}px`)
      gallery.dataset.galleryLayout = "edge-to-edge-thumbnails"
      gallery.dataset.galleryItems = String(figures.length)
      window.dispatchEvent(new Event("portfolio:layout"))
    }
    const queue = () => { if (!frame) frame = requestAnimationFrame(layout) }
    new ResizeObserver(queue).observe(gallery)
    window.addEventListener("resize", queue, { passive: true })
    figures.forEach((figure, index) => {
      const link = figure.querySelector<HTMLAnchorElement>("a")
      if (link) {
        link.setAttribute("aria-label", `Enlarge project image ${index + 1} of ${figures.length}`)
        allLinks.push(link)
      }
    })
    layout()
  })
  allLinks.push(...document.querySelectorAll<HTMLAnchorElement>(".project-banner a"))
  allLinks.push(...document.querySelectorAll<HTMLAnchorElement>(".poster-photo a"))
  if (!allLinks.length) return
  const dialog = document.createElement("dialog")
  dialog.className = "portfolio-image-viewer"
  dialog.setAttribute("aria-label", "Project image detail")
  const header = document.createElement("div")
  header.className = "viewer-header"
  const status = document.createElement("span")
  status.setAttribute("aria-live", "polite")
  const close = document.createElement("button")
  close.type = "button"; close.textContent = "Close"
  close.addEventListener("click", () => dialog.close())
  header.append(status, close)
  const image = document.createElement("img")
  image.className = "viewer-image"
  const controls = document.createElement("div")
  controls.className = "viewer-controls"
  const previous = document.createElement("button"), next = document.createElement("button")
  previous.type = next.type = "button"
  previous.textContent = "Previous"; next.textContent = "Next"
  controls.append(previous, next)
  dialog.append(header, image, controls); document.body.append(dialog)
  // A photo can appear as a banner and a thumbnail, but appears once in Next.
  const unique = allLinks.filter((link, index, links) =>
    links.findIndex(other => (other.dataset.original || other.href) === (link.dataset.original || link.href)) === index)
  let active = 0, opener: HTMLAnchorElement | null = null, oldOverflow = ""
  const show = (index: number) => {
    active = (index + unique.length) % unique.length
    const link = unique[active]
    image.src = link.dataset.original || link.href
    image.alt = link.querySelector("img")?.alt || "Supplied project image"
    status.textContent = `Image ${active + 1} of ${unique.length}`
  }
  allLinks.forEach(link => link.addEventListener("click", event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return
    event.preventDefault(); opener = link
    show(unique.findIndex(other => (other.dataset.original || other.href) === (link.dataset.original || link.href)))
    oldOverflow = document.body.style.overflow
    document.body.style.overflow = "hidden"; dialog.showModal()
  }))
  previous.addEventListener("click", () => show(active - 1))
  next.addEventListener("click", () => show(active + 1))
  dialog.addEventListener("keydown", event => {
    if (event.key === "ArrowLeft") { event.preventDefault(); show(active - 1) }
    if (event.key === "ArrowRight") { event.preventDefault(); show(active + 1) }
  })
  dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close() })
  dialog.addEventListener("close", () => {
    document.body.style.overflow = oldOverflow
    opener?.focus({ preventScroll: true })
  })
}
