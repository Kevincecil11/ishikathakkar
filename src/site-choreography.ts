import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/dist/ScrollTrigger"
import { initLogoPhysics } from "./logo-physics"
import { initSmoothScroll } from "./smooth-scroll"
import { initPremiumMotion } from "./premium-motion"

gsap.registerPlugin(ScrollTrigger)

/** Progressive motion: the static site is complete without any of this.
 * Reduced Motion keeps native scrolling and final, unanimated content.
 */
export function startSiteChoreography() {
  const root = document.documentElement
  root.dataset.motionEngine = "gsap-" + gsap.version
  const preference = window.matchMedia("(prefers-reduced-motion: reduce)")
  initLogoPhysics(preference)
  if (preference.matches) {
    root.classList.remove("motion-on")
    root.classList.add("motion-ready")
    return
  }
  root.classList.add("motion-on")
  initPremiumMotion(initSmoothScroll())
}
