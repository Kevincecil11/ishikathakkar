import * as React from "react"
import { createRoot } from "react-dom/client"
import { ArrowUpRight } from "lucide-react"
import HalftoneWordmarkFooter from "@/components/ui/halftone-wordmark-footer"
import { startSiteChoreography } from "./site-choreography"
import { initGalleryLayout } from "./gallery-layout"

// The combined Pages publisher adds this legacy comparison link after build.
// V2 no longer presents it; the alternate site remains independently hosted.
document.querySelectorAll(".version-switch").forEach(link => link.remove())

const mount = document.querySelector<HTMLElement>("[data-halftone-footer]")
if (mount) {
  const rel = mount.dataset.relative || ""
  const host = document.createElement("div")
  host.className = "w-full"
  // Keep the static, working footer if React or canvas is unavailable.
  if (document.createElement("canvas").getContext("2d")) {
    mount.replaceChildren(host)
    createRoot(host).render(
      <HalftoneWordmarkFooter
        wordmark="SAY HELLO"
        label="Ishika Thakkar"
        meta="©2026 Ishika Thakkar"
        preset="paper"
        palette={{ background: "#E8E8E4", ink: "#121211", warm: "#121211" }}
        columns={[
          { title: "Work", links: [{ label: "The Loud Table", href: rel + "work/the-loud-table/" }, { label: "MTRX", href: rel + "work/mtrx-digital/" }] },
          { title: "About", links: [{ label: "Ishika Thakkar", href: rel + "about/" }] },
          { title: "Contact", links: [{ label: "Get in touch", href: "#contact" }] },
        ]}
        fontFamily={'"Anton", "Impact", "Arial Narrow", sans-serif'}
        fontWeight={400}
        monoFamily={'"IBM Plex Mono", ui-monospace, monospace'}
        height="clamp(360px, 39vw, 560px)"
        dotGap={6}
        radius={220}
        crop={0}
        grain={0}
        interactive={true}
      />
    )
  }
}

function enhanceButtons() {
  document.querySelectorAll<HTMLAnchorElement | HTMLButtonElement>(
    "a.pill, button:not(.hwf-up), a.group-link, .group-top .group-link, a.mini-work"
  ).forEach(button => {
    // Don't alter forms, project cards, the canvas controls or disabled actions.
    if (button.closest(".contact-form,.client-ribbon") || button.matches(":disabled,.it-roll") || button.children.length && !button.matches("a.pill")) return
    const label = button.textContent?.trim()
    if (!label) return
    const hasArrow = /[↗↘→↑]/.test(label)
    const name = label.replace(/\s*[↗↘→↑]\s*$/, "")
    button.classList.add("it-roll")
    // Preserve the accessible name: links/buttons get aria-label, plain spans
    // (labels inside a larger card link) keep a visually hidden text copy.
    const interactive = button.matches("a,button")
    if (interactive && !button.getAttribute("aria-label")) button.setAttribute("aria-label", name)
    const text = document.createElement("span")
    text.className = "it-roll-window"
    text.setAttribute("aria-hidden", "true")
    const track = document.createElement("span")
    track.className = "it-roll-track"
    for (let i = 0; i < 2; i++) {
      const face = document.createElement("span")
      face.className = "it-roll-face"
      face.textContent = name
      track.append(face)
    }
    text.append(track)
    button.replaceChildren(text)
    if (!interactive) {
      const spoken = document.createElement("span")
      spoken.className = "visually-hidden"
      spoken.textContent = name
      button.prepend(spoken)
    }
    if (hasArrow) {
      const icon = document.createElement("span")
      icon.className = "it-roll-icon"
      icon.setAttribute("aria-hidden", "true")
      createRoot(icon).render(<><ArrowUpRight /><ArrowUpRight /></>)
      button.append(icon)
    }
  })
}
enhanceButtons()
function enhanceInlineArrows() {
  document.querySelectorAll<HTMLAnchorElement>("a:not(.it-roll)").forEach(link => {
    if (link.closest(".client-ribbon,.contact-form,.hwf-root")) return
    const walker = document.createTreeWalker(link, NodeFilter.SHOW_TEXT)
    const nodes: Text[] = []
    while (walker.nextNode()) {
      const node = walker.currentNode as Text
      if (!node.parentElement?.closest(".it-roll,svg,.it-arrow") && /[↗↘→↑←]/.test(node.textContent || "")) nodes.push(node)
    }
    for (const node of nodes) {
      const fragment = document.createDocumentFragment()
      for (const part of (node.textContent || "").split(/([↗↘→↑←])/)) {
        if (!/^[↗↘→↑←]$/.test(part)) { fragment.append(document.createTextNode(part)); continue }
        const arrow = document.createElement("span")
        arrow.className = "it-arrow it-arrow-" + ({ "↗": "ne", "↘": "se", "→": "e", "↑": "n", "←": "w" }[part])
        arrow.setAttribute("aria-hidden", "true")
        for (let i = 0; i < 2; i++) {
          const face = document.createElement("span")
          face.className = "it-arrow-face"; face.textContent = part; arrow.append(face)
        }
        fragment.append(arrow)
      }
      node.replaceWith(fragment)
      link.classList.add("it-arrow-link")
    }
  })
}
enhanceInlineArrows()
initGalleryLayout()
startSiteChoreography()
