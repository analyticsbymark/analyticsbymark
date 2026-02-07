/**
 * Statsig Experiments Bootstrap
 *
 * Main orchestrator for Statsig experimentation.
 * Initializes the client, applies experiments, and supports MkDocs Material instant navigation.
 *
 * Supports both legacy (flat) and new (structured) config formats.
 */

(function() {
  'use strict';

  const DEFAULT_CLIENT_KEY = "client-o5NxMKGrDvcZ6sfYbs2081B5l63hu6dpI80652s6XE6";

  /**
   * Parse config and determine format (legacy vs new)
   * @returns {object} { clientKey, clientOptions, experiments }
   */
  function parseConfig() {
    const rawConfig = window.EXPERIMENT_CONFIG;

    if (!rawConfig || !Object.keys(rawConfig).length) {
      return null;
    }

    // Check if this is the new structured format
    const isNewFormat = rawConfig.client && rawConfig.experiments;

    if (isNewFormat) {
      // New format: extract client config and flatten experiments
      const clientKey = rawConfig.client.apiKey || DEFAULT_CLIENT_KEY;
      const clientOptions = rawConfig.client.options || {};

      // Flatten nested experiments object
      const experiments = {};
      for (const [category, categoryExperiments] of Object.entries(rawConfig.experiments)) {
        for (const [key, exp] of Object.entries(categoryExperiments)) {
          experiments[key] = exp;
        }
      }

      return {
        clientKey,
        clientOptions,
        experiments,
        metadata: rawConfig._meta || {},
        tracking: rawConfig.tracking || {}
      };
    } else {
      // Legacy format: use as-is
      return {
        clientKey: DEFAULT_CLIENT_KEY,
        clientOptions: {},
        experiments: rawConfig,
        metadata: {},
        tracking: {}
      };
    }
  }

  /**
   * Hydrate experiments on the current page
   */
  async function hydrateExperiments() {
    try {
      // Parse configuration
      const config = parseConfig();

      if (!config || !Object.keys(config.experiments).length) {
        // No experiments configured
        return;
      }

      // Log config info in debug mode
      if (config.clientOptions.loggingLevel === 'debug') {
        console.log('[Statsig] Config loaded:', {
          environment: config.metadata.environment,
          version: config.metadata.version,
          experimentCount: Object.keys(config.experiments).length
        });
      }

      // Pre-hide all experiment elements synchronously to prevent flicker
      window.StatsigRenderer.preHideExperimentElements(config.experiments);

      // Initialize Statsig client with config options
      const client = await window.StatsigClient.getClient(config.clientKey, config.clientOptions);

      // Apply each experiment
      for (const key of Object.keys(config.experiments)) {
        const binding = config.experiments[key];
        const element = document.querySelector(binding.selector);

        if (!element) {
          // Element not found on this page, skip
          continue;
        }

        // Get the fallback value
        const fallback = binding.fallback || ((binding.type === "text") ? (element.textContent || "") : "");

        // Get the experiment variant value from Statsig
        const value = client.getExperiment(binding.experiment).get(binding.param, fallback);

        // Apply the variant to the element
        window.StatsigRenderer.applyExperiment(element, binding, value);

        // Log exposure for this experiment
        if (window.StatsigTracker?.exposureLogger) {
          window.StatsigTracker.exposureLogger.logExposure(
            binding.experiment,
            value,
            {
              experiment_key: key,
              experiment_category: binding.category,
              selector: binding.selector
            }
          );
        }
      }
    } catch (error) {
      console.error("[Statsig] Hydration failed:", error);
      // On error, ensure elements are revealed with default content
      window.StatsigRenderer.revealAllHiddenElements();
    }
  }

  /**
   * Initialize experiments
   */
  function initializeExperiments() {
    // MkDocs Material instant navigation support
    if (window.document$?.subscribe) {
      window.document$.subscribe(() => {
        hydrateExperiments().catch(error => {
          console.error("[Statsig] Hydration error in instant navigation:", error);
        });
      });
    } else {
      // Standard page load
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
          hydrateExperiments().catch(error => {
            console.error("[Statsig] Hydration error on page load:", error);
          });
        });
      } else {
        // Document already loaded
        hydrateExperiments().catch(error => {
          console.error("[Statsig] Hydration error (immediate):", error);
        });
      }
    }
  }

  // Auto-initialize when this module loads
  initializeExperiments();

  // Initialize tracking system (after experiments initialized)
  if (window.StatsigTracker?.init) {
    window.StatsigTracker.init().catch(error => {
      console.error("[Statsig] Tracking initialization failed:", error);
    });
  }
})();
