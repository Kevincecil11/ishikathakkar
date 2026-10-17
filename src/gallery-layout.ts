/** Justified rows: every photograph stays whole and rows share clean edges.
 * Preserve source order; choose row breaks by original image aspect ratios.
 */
export function initGalleryLayout() {
  document.querySelectorAll<HTMLElement>(".uploaded-gallery").forEach(gallery => {
    const figures = Array.from(gallery.querySelectorAll<HTMLElement>("figure"))
    if (!figures.length) return
    let frame = 0, lastWidth = -1
    const ratio = (figure: HTMLElement) => {
      const image = figure.querySelector<HTMLImageElement>("img")!
      return Number(image.getAttribute("width")) / Number(image.getAttribute("height")) || image.naturalWidth / image.naturalHeight || 1
    }
    const layout = () => {
      frame = 0
      const width = gallery.clientWidth
      if (width < 1 || Math.abs(width - lastWidth) < 1) return
      lastWidth = width
      const gap = 12, count = figures.length
      const target = width >= 1100 ? 360 : width >= 750 ? 310 : width >= 500 ? 270 : 240
      const maxItems = width < 540 ? 2 : width < 900 ? 3 : 4
      const costs = new Array<number>(count + 1).fill(Infinity)
      const breaks = new Array<number>(count).fill(1)
      costs[count] = 0
      for (let start = count - 1; start >= 0; start--) {
        let sum = 0
        for (let size = 1; size <= Math.min(maxItems, count - start); size++) {
          sum += ratio(figures[start + size - 1])
          const height = (width - gap * (size - 1)) / sum
          const deviation = (height - target) / target
          const lonePenalty = size === 1 && count > 1 && width > 540 ? 1.25 : 0
          const cost = deviation * deviation + lonePenalty + costs[start + size]
          if (cost < costs[start]) { costs[start] = cost; breaks[start] = size }
        }
      }
      const rows = document.createDocumentFragment()
      for (let start = 0; start < count;) {
        const size = breaks[start], row = document.createElement("div")
        row.className = "gallery-row"
        let sum = 0
        for (let i = start; i < start + size; i++) sum += ratio(figures[i])
        const height = (width - gap * (size - 1)) / sum
        row.style.height = height + "px"
        for (let i = start; i < start + size; i++) {
          figures[i].style.flex = `${ratio(figures[i]) * 100} 1 0%`
          row.append(figures[i])
        }
        rows.append(row); start += size
      }
      gallery.replaceChildren(rows)
      gallery.classList.add("is-justified")
      gallery.dataset.galleryLayout = "justified-no-crop"
      window.dispatchEvent(new Event("portfolio:layout"))
    }
    const queue = () => { if (!frame) frame = requestAnimationFrame(layout) }
    new ResizeObserver(queue).observe(gallery)
    figures.forEach(figure => {
      const image = figure.querySelector<HTMLImageElement>("img")!
      if (!image.getAttribute("width") && !image.complete) image.addEventListener("load", () => { lastWidth = -1; queue() }, { once: true })
    })
    layout()
  })
}
