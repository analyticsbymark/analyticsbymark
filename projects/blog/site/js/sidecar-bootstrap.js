(function () {
  const CLIENT_KEY = "client-o5NxMKGrDvcZ6sfYbs2081B5l63hu6dpI80652s6XE6";
  const EXPERIMENT = "abm_dev_landing_button_text";
  const PARAM = "button_label";
  const DEFAULT = "Start the Blog tutorial";
  const BUTTON_ID = "hero-cta-dev";

  function stableId() {
    const k = "statsig_stable_id";
    let v = localStorage.getItem(k);
    if (!v) {
      v = (crypto?.randomUUID?.() || (Math.random().toString(16).slice(2) + Date.now()));
      localStorage.setItem(k, v);
    }
    return v;
  }

  function apply(label) {
    const el = document.getElementById(BUTTON_ID);
    if (el) el.textContent = label;
  }

  async function run() {
    apply(DEFAULT);

    const keys = Object.keys(window).filter(k => k.toLowerCase().includes("statsig"));
    console.log("[statsig] globals:", keys);
    console.log("[statsig] window.Statsig:", window.Statsig);

    // Case A: Statsig namespace exposes StatsigClient class (common)
    const StatsigClientCtor =
      window.Statsig?.StatsigClient ||
      window.StatsigClient;

    if (typeof StatsigClientCtor === "function") {
      const client = new StatsigClientCtor(CLIENT_KEY, { userID: stableId() });

      // different builds use different init names
      if (typeof client.initializeAsync === "function") {
        await client.initializeAsync();
      } else if (typeof client.initialize === "function") {
        await client.initialize();
      } else if (typeof client.initializeAsync === "undefined") {
        console.warn("[statsig] client has no initialize method:", client);
        return;
      }

      const label = client.getExperiment(EXPERIMENT).get(PARAM, DEFAULT);
      apply(label);
      console.log("[statsig] applied label:", label);
      return;
    }

    // Case B: Statsig is a singleton with init + getExperiment
    if (window.Statsig && typeof window.Statsig.getExperiment === "function") {
      // some singletons use initializeAsync, some initialize
      if (typeof window.Statsig.initializeAsync === "function") {
        await window.Statsig.initializeAsync(CLIENT_KEY, { userID: stableId() });
      } else if (typeof window.Statsig.initialize === "function") {
        await window.Statsig.initialize(CLIENT_KEY, { userID: stableId() });
      } else {
        console.warn("[statsig] Statsig singleton has no initialize method:", window.Statsig);
        return;
      }

      const label = window.Statsig.getExperiment(EXPERIMENT).get(PARAM, DEFAULT);
      apply(label);
      console.log("[statsig] applied label:", label);
      return;
    }

    console.warn("[statsig] No compatible Statsig API shape found");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
