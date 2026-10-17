/* Small, dependency-free interface layer: mobile menu and contact form.
 * Both enhance markup that already works without JavaScript. */
(function () {
  "use strict";
  var root = document.documentElement;

  /* ---------- Mobile menu ---------- */
  var header = document.querySelector(".hdr");
  var toggle = header && header.querySelector(".menu-toggle");
  var nav = header && header.querySelector("#site-nav");
  if (toggle && nav) {
    var label = toggle.querySelector(".menu-toggle-label");
    var compact = window.matchMedia("(max-width: 720px)");
    var open = false;
    var focusables = function () {
      return [toggle].concat(Array.prototype.slice.call(nav.querySelectorAll("a[href]")));
    };
    var setOpen = function (next, restoreFocus) {
      if (next === open) return;
      open = next;
      root.classList.toggle("menu-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      if (label) label.textContent = open ? "Close" : "Menu";
      document.body.style.overflow = open ? "hidden" : "";
      if (open) {
        header.classList.remove("is-hidden");
        var first = nav.querySelector("a[href]");
        if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 60);
      } else if (restoreFocus) {
        toggle.focus({ preventScroll: true });
      }
    };
    toggle.setAttribute("aria-label", "Open menu");
    toggle.addEventListener("click", function () { setOpen(!open, true); });
    nav.addEventListener("click", function (event) {
      if (open && event.target.closest && event.target.closest("a[href]")) setOpen(false, false);
    });
    document.addEventListener("keydown", function (event) {
      if (!open) return;
      if (event.key === "Escape") { event.preventDefault(); setOpen(false, true); return; }
      if (event.key !== "Tab") return;
      var items = focusables();
      var index = items.indexOf(document.activeElement);
      if (event.shiftKey && index <= 0) { event.preventDefault(); items[items.length - 1].focus(); }
      else if (!event.shiftKey && index === items.length - 1) { event.preventDefault(); items[0].focus(); }
    });
    var onBreakpoint = function () { if (!compact.matches) setOpen(false, false); };
    if (compact.addEventListener) compact.addEventListener("change", onBreakpoint);
    else if (compact.addListener) compact.addListener(onBreakpoint);
    window.addEventListener("pageshow", function () { setOpen(false, false); });
  }

  /* ---------- Contact form ---------- */
  var form = document.querySelector("form[data-contact-form]");
  if (!form || !window.fetch || !window.FormData) return;
  var button = form.querySelector('button[type="submit"]');
  var buttonLabel = button && button.querySelector(".btn-label");
  var status = form.querySelector(".form-status");
  var idle = buttonLabel ? buttonLabel.textContent : "";
  var busy = false;

  var say = function (state, text) {
    if (!status) return;
    status.textContent = text;
    status.setAttribute("data-state", state);
  };
  form.addEventListener("input", function () {
    if (status && status.getAttribute("data-state") === "error") say("", "");
  });
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (busy) return;
    if (form.reportValidity && !form.reportValidity()) return;
    var data = new FormData(form);
    // Honeypot: real people never tick the hidden box.
    if (data.get("botcheck")) { form.reset(); say("success", "Thank you. Your message is on its way."); return; }
    ["name", "email", "message"].forEach(function (key) {
      var value = data.get(key);
      if (typeof value === "string") data.set(key, value.trim());
    });
    busy = true;
    form.setAttribute("aria-busy", "true");
    if (button) button.disabled = true;
    if (buttonLabel) buttonLabel.textContent = "Sending…";
    say("pending", "Sending your message…");
    var controller = window.AbortController ? new AbortController() : null;
    var timer = controller ? setTimeout(function () { controller.abort(); }, 15000) : 0;
    fetch(form.action, {
      method: "POST",
      headers: { Accept: "application/json" },
      body: data,
      signal: controller ? controller.signal : undefined
    })
      .then(function (response) {
        return response.json().catch(function () { return {}; }).then(function (json) {
          if (!response.ok || !json || json.success !== true) throw new Error("rejected");
        });
      })
      .then(function () {
        form.reset();
        say("success", "Thank you. Your message is on its way, and I'll get back to you soon.");
      })
      .catch(function () {
        say("error", "That didn't go through. Please check your connection and try again.");
      })
      .then(function () {
        if (timer) clearTimeout(timer);
        busy = false;
        form.removeAttribute("aria-busy");
        if (button) button.disabled = false;
        if (buttonLabel) buttonLabel.textContent = idle;
      });
  });
})();
