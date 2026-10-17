/** Compact proof sheets: overview fits one viewport; detail is opt-in.
 * Sources stay ordered and whole, except reviewed screenshot-chrome crops.
 */
export function initGalleryLayout() {
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
      const gap = width < 600 ? 8 : 12
      const budget = Math.max(160, Math.min(600, window.innerHeight - 220))
      let best = { columns: 1, rows: figures.length, score: -Infinity }
      for (let columns = 1; columns <= Math.min(figures.length, width < 600 ? 4 : 8); columns++) {
        const rows = Math.ceil(figures.length / columns)
        const cellW = (width - gap * (columns - 1)) / columns
        const cellH = (budget - gap * (rows - 1)) / rows
        if (cellW < 54 || cellH < 32) continue
        let area = 0
        for (const figure of figures) {
          const image = figure.querySelector<HTMLImageElement>("img")!
          const ratio = Number(image.getAttribute("width")) / Number(image.getAttribute("height")) ||
            image.naturalWidth / image.naturalHeight || 1
          area += Math.min(cellW, cellH * ratio) * Math.min(cellH, cellW / ratio)
        }
        const filled = figures.length / (rows * columns)
        const score = area * (0.8 + filled * 0.2)
        if (score > best.score) best = { columns, rows, score }
      }
      const rowHeight = Math.min(280, (budget - gap * (best.rows - 1)) / best.rows)
      gallery.style.setProperty("--proof-columns", String(best.columns))
      gallery.style.setProperty("--proof-row-height", `${rowHeight}px`)
      gallery.style.setProperty("--proof-gap", `${gap}px`)
      gallery.dataset.galleryLayout = "compact-viewport"
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
  allLinks.push(...document.querySelectorAll<HTMLAnchorElement>(".campaign-collage a"))
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
  const original = document.createElement("a")
  original.textContent = "Open original file"
  original.target = "_blank"; original.rel = "noopener"
  controls.append(previous, original, next)
  dialog.append(header, image, controls); document.body.append(dialog)
  let active = 0, opener: HTMLAnchorElement | null = null, oldOverflow = ""
  const show = (index: number) => {
    active = (index + allLinks.length) % allLinks.length
    const link = allLinks[active]
    image.src = link.href
    image.alt = link.querySelector("img")?.alt || "Supplied project image"
    original.href = link.dataset.original || link.href
    status.textContent = `Image ${active + 1} of ${allLinks.length}`
  }
  allLinks.forEach((link, index) => link.addEventListener("click", event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return
    event.preventDefault(); opener = link
    show(index); oldOverflow = document.body.style.overflow
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
