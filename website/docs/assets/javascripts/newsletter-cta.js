/* One-time hatch emphasis for primary buttons that jump to this page's
 * #newsletter form. Each CTA plays once, the first time at least half of it is
 * in view below the sticky header while actually shown (not visibility:hidden,
 * not opacity:0, tab visible). "Once" lasts for the document, so instant
 * navigation back to a page does not replay it; a full reload may.
 * Styles: .abm-cta-emphasis / @keyframes abm-cta-hatch in assets/extra.css.
 */
(() => {
  "use strict";

  if (!("IntersectionObserver" in window)) return;

  const seen = new Set();
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  let observer;
  let keys = new Map();
  let inView = new Set(); // eligible CTAs at least half in view, not yet played
  let watching = false;

  // Intersection is geometry only: an in-view CTA can still be
  // visibility:hidden, opacity:0 (itself or an ancestor) or in a hidden tab.
  const shown = (link) => {
    if (document.visibilityState !== "visible") return false;
    if (link.checkVisibility) return link.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true });
    if (getComputedStyle(link).visibility !== "visible") return false;
    for (let el = link; el; el = el.parentElement) if (getComputedStyle(el).opacity === "0") return false;
    return true;
  };

  // A hidden in-view CTA keeps its one play until it is actually shown. While
  // one is waiting, attribute changes that can reveal it trigger a recheck.
  const check = () => {
    inView.forEach((link) => {
      if (!shown(link)) return;
      inView.delete(link);
      observer.unobserve(link);
      const key = keys.get(link);
      if (seen.has(key)) return;
      seen.add(key);
      if (!reduce.matches) play(link);
    });
    if (inView.size && !watching) {
      mutations.observe(document.documentElement, { attributes: true, subtree: true, attributeFilter: ["class", "style", "hidden"] });
      watching = true;
    } else if (!inView.size && watching) {
      mutations.disconnect();
      watching = false;
    }
  };
  const mutations = new MutationObserver(check);
  document.addEventListener("visibilitychange", check);

  const eligible = (link) => {
    if (link.closest(".md-banner")) return null;
    const url = new URL(link.href, location.href);
    const here = url.origin === location.origin && url.pathname === location.pathname && url.search === location.search;
    return here && url.hash === "#newsletter" && document.getElementById("newsletter") ? url : null;
  };

  const play = (link) => {
    const done = (event) => {
      if (event.animationName !== "abm-cta-hatch") return;
      link.classList.remove("abm-cta-emphasis");
      link.removeEventListener("animationend", done);
      link.removeEventListener("animationcancel", done);
    };
    link.addEventListener("animationend", done);
    link.addEventListener("animationcancel", done);
    link.classList.add("abm-cta-emphasis");
  };

  const enhance = () => {
    if (observer) observer.disconnect();
    mutations.disconnect();
    watching = false;
    inView = new Set();
    keys = new Map();
    const header = document.querySelector(".md-header");
    const top = header ? header.offsetHeight : 0;
    observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && entry.intersectionRatio >= 0.5) inView.add(entry.target);
        else inView.delete(entry.target);
      });
      check();
    }, { rootMargin: `-${top}px 0px 0px 0px`, threshold: 0.5 });

    // Identity: page + id + resolved href + label + occurrence ordinal, so
    // identical CTAs stay distinct and rebuilt nodes map to the same key.
    const counts = new Map();
    document.querySelectorAll(".md-content a.md-button.md-button--primary[href]").forEach((link) => {
      const url = eligible(link);
      if (!url) return;
      const base = [location.pathname + location.search, link.id, url.href, link.textContent.trim()].join("|");
      const ordinal = counts.get(base) || 0;
      counts.set(base, ordinal + 1);
      const key = `${base}|${ordinal}`;
      if (seen.has(key)) return;
      keys.set(link, key);
      observer.observe(link);
    });
  };

  if (typeof document$ !== "undefined") document$.subscribe(enhance);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", enhance, { once: true });
  else enhance();
})();
