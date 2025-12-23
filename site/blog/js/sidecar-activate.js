// Wait until Sidecar is available, then activate the experiment
(function () {
  function tryActivate() {
    if (window.StatsigSidecar && window.StatsigSidecar.activateExperiment) {
      window.StatsigSidecar.activateExperiment("abm-blog-cta-text");
      console.info("[Sidecar] Activated experiment: abm-blog-cta-text");
    } else {
      // Retry until Sidecar has loaded
      setTimeout(tryActivate, 50);
    }
  }
  tryActivate();
})();

