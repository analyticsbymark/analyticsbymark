(function () {
  // Add all your Sidecar experiment IDs here
  const EXPERIMENTS = [
    "abm_dev_landing_cta_text",
    // "another-experiment-id",
    // "third-experiment-id",
  ];

  function hideTargets() {
    document.querySelectorAll("[data-ab-hide]").forEach((el) => el.classList.remove("ab-ready"));
  }

  function revealTargets() {
    document.querySelectorAll("[data-ab-hide]").forEach((el) => el.classList.add("ab-ready"));
  }

  function activateAll() {
    const sc = window.StatsigSidecar;
    if (!sc || typeof sc.activateExperiment !== "function") return false;

    // Hide before Sidecar mutates DOM to avoid "default then swap" flash
    hideTargets();

    // Activate all experiments (Sidecar applies Visual Editor actions)
    EXPERIMENTS.forEach((id) => sc.activateExperiment(id));

    // Give Sidecar one tick to apply, then reveal
    setTimeout(revealTargets, 0);

    return true;
  }

  // Wait for Sidecar to load, then activate
  (function wait() {
    if (!activateAll()) setTimeout(wait, 25);
  })();

  // MkDocs Material instant navigation: re-apply after internal page swaps
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(() => {
      activateAll();
    });
  }
})();
