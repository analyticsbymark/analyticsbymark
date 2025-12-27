// (function () {
//   const CLIENT_KEY = "client-o5NxMKGrDvcZ6sfYbs2081B5l63hu6dpI80652s6XE6";
//   const EXPERIMENT = "abm_dev_landing_button_text";
//   const PARAM = "button_label";
//   const DEFAULT = "Start the Blog tutorial";
//   const BUTTON_ID = "hero-cta-dev";
//
//   const STABLE_ID_KEY = "statsig_stable_id_v1";
//   const LABEL_CACHE_KEY = "statsig_btn_label_v1";
//   const LABEL_CACHE_TS_KEY = "statsig_btn_label_ts_v1";
//   const CACHE_TTL_MS = 6 * 60 * 60 * 1000; // 6h
//
//   function stableId() {
//     let v = localStorage.getItem(STABLE_ID_KEY);
//     if (!v) {
//       v = crypto?.randomUUID?.() || (Math.random().toString(16).slice(2) + Date.now());
//       localStorage.setItem(STABLE_ID_KEY, v);
//     }
//     return v;
//   }
//
//   function getButton() {
//     return document.getElementById(BUTTON_ID);
//   }
//
//   function revealWithLabel(label) {
//     const el = getButton();
//     if (!el) return;
//
//     el.textContent = label;
//     el.removeAttribute("data-hidden");
//   }
//
//   function cacheGetFreshLabel() {
//     const label = localStorage.getItem(LABEL_CACHE_KEY);
//     if (!label) return null;
//
//     const ts = Number(localStorage.getItem(LABEL_CACHE_TS_KEY) || "0");
//     if (!ts) return null;
//
//     if (Date.now() - ts > CACHE_TTL_MS) return null;
//     return label;
//   }
//
//   function cacheSetLabel(label) {
//     localStorage.setItem(LABEL_CACHE_KEY, label);
//     localStorage.setItem(LABEL_CACHE_TS_KEY, String(Date.now()));
//   }
//
//   async function getClientOnce() {
//     if (window.__statsigClientPromise) return window.__statsigClientPromise;
//
//     window.__statsigClientPromise = (async () => {
//       const StatsigClientCtor = window.Statsig?.StatsigClient || window.StatsigClient;
//       if (typeof StatsigClientCtor !== "function") {
//         throw new Error("StatsigClient constructor not found");
//       }
//
//       const client = new StatsigClientCtor(CLIENT_KEY, { userID: stableId() });
//
//       if (typeof client.initializeAsync === "function") await client.initializeAsync();
//       else if (typeof client.initialize === "function") await client.initialize();
//       else throw new Error("No initialize method on Statsig client");
//
//       window.__statsigClient = client;
//       return client;
//     })();
//
//     return window.__statsigClientPromise;
//   }
//
//   async function resolveLabel() {
//     const cached = cacheGetFreshLabel();
//     if (cached) return cached;
//
//     const client = await getClientOnce();
//     const label = client.getExperiment(EXPERIMENT).get(PARAM, DEFAULT);
//
//     cacheSetLabel(label);
//     return label;
//   }
//
//   function hydrate() {
//     const el = getButton();
//     if (!el) return;
//
//     // If we already have a cached label, reveal instantly (no flicker)
//     const cached = cacheGetFreshLabel();
//     if (cached) {
//       revealWithLabel(cached);
//       return;
//     }
//
//     // Otherwise keep hidden until resolved (prevents wrong label)
//     resolveLabel()
//       .then((label) => revealWithLabel(label))
//       .catch(() => {
//         // If Statsig fails, reveal with DEFAULT (still no flicker because it stayed hidden)
//         revealWithLabel(DEFAULT);
//       });
//   }
//
//   // MkDocs Material instant navigation support
//   if (window.document$?.subscribe) {
//     window.document$.subscribe(hydrate);
//   } else {
//     if (document.readyState === "loading") {
//       document.addEventListener("DOMContentLoaded", hydrate);
//     } else {
//       hydrate();
//     }
//   }
// })();

(function () {
  const CLIENT_KEY = "client-o5NxMKGrDvcZ6sfYbs2081B5l63hu6dpI80652s6XE6";
  const STABLE_ID_KEY = "statsig_stable_id_v1";

  function stableId() {
    let v = localStorage.getItem(STABLE_ID_KEY);
    if (!v) {
      v = crypto?.randomUUID?.() || (Math.random().toString(16).slice(2) + Date.now());
      localStorage.setItem(STABLE_ID_KEY, v);
    }
    return v;
  }

  async function getClientOnce() {
    if (window.__statsigClientPromise) return window.__statsigClientPromise;

    window.__statsigClientPromise = (async () => {
      const Ctor = window.Statsig?.StatsigClient || window.StatsigClient;
      if (typeof Ctor !== "function") throw new Error("StatsigClient constructor not found");

      const client = new Ctor(CLIENT_KEY, { userID: stableId() });
      if (typeof client.initializeAsync === "function") await client.initializeAsync();
      else if (typeof client.initialize === "function") await client.initialize();
      else throw new Error("No initialize method on Statsig client");

      return client;
    })();

    return window.__statsigClientPromise;
  }

  function apply(el, binding, value) {
    if (binding.type === "text") {
      el.textContent = value;
    } else if (binding.type === "attr") {
      el.setAttribute(binding.attr, value);
    } else if (binding.type === "class") {
      el.classList.toggle(binding.className, !!value);
    }
    el.removeAttribute("data-hidden");
  }

  function preHideAll(cfg) {
    // Run synchronously: hide targets ASAP so default never flashes
    for (const key of Object.keys(cfg)) {
      const b = cfg[key];
      const el = document.querySelector(b.selector);
      if (el) el.setAttribute("data-hidden", "");
    }
  }

  async function hydrate() {
    const cfg = window.EXPERIMENT_CONFIG;
    if (!cfg || !Object.keys(cfg).length) return;

    // ensure hidden (important on instant navigation where new DOM is swapped in)
    preHideAll(cfg);

    const client = await getClientOnce();

    for (const key of Object.keys(cfg)) {
      const b = cfg[key];
      const el = document.querySelector(b.selector);
      if (!el) continue;

      const fallback = (b.type === "text") ? (el.textContent || "") : "";

      const value = client.getExperiment(b.experiment).get(b.param, fallback);
      apply(el, b, value);
    }
  }

  if (window.document$?.subscribe) {
    window.document$.subscribe(() => hydrate().catch(() => {}));
  } else {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => hydrate().catch(() => {}));
    } else {
      hydrate().catch(() => {});
    }
  }
})();

