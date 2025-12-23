// Wait until Sidecar is available, then activate the experiment
(function () {
  function tryActivate() {
    if (window.StatsigSidecar && window.StatsigSidecar.activateExperiment) {
      window.StatsigSidecar.activateExperiment("abm-dev-landing-cta-text");
      console.info("[Sidecar] Activated experiment: abm-dev-landing-cta");
    } else {
      // Retry until Sidecar has loaded
      setTimeout(tryActivate, 50);
    }
  }
  tryActivate();
})();

