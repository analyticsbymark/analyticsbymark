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
   * Get URL parameter overrides for experiments
   * Allows testing specific variants via URL parameters like ?exp_2026_02_alpha=true
   * @returns {object} Map of experiment names to override values
   */
  function getUrlOverrides() {
    const params = new URLSearchParams(window.location.search);
    const overrides = {};

    for (const [key, value] of params.entries()) {
      // Check if this looks like an experiment override
      if (key.startsWith('exp_') || key.includes('_experiment') || key.includes('_test')) {
        // Parse the value - handle booleans, numbers, and strings
        let parsedValue = value;
        if (value === 'true') parsedValue = true;
        else if (value === 'false') parsedValue = false;
        else if (!isNaN(value) && value !== '') parsedValue = Number(value);

        overrides[key] = parsedValue;
        console.log(`[Statsig] URL override: ${key} = ${parsedValue}`);
      }
    }

    return overrides;
  }

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
   * Hydrate experiments on the current page (sync-first, cache-based)
   */
  function hydrateExperiments() {
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

      // Synchronous cache-first initialization — no waiting, no hiding
      const client = window.StatsigClient.getClientSync(config.clientKey, config.clientOptions);

      if (!client) {
        // SDK not loaded yet — leave elements visible with default content
        console.warn("[Statsig] Client not available, showing default content");
        return;
      }

      // Get URL parameter overrides for testing
      const urlOverrides = getUrlOverrides();

      // Apply each experiment immediately with cached values (or fallback)
      for (const key of Object.keys(config.experiments)) {
        const binding = config.experiments[key];
        const element = document.querySelector(binding.selector);

        if (!element) {
          // Element not found on this page, skip
          continue;
        }

        // Get the fallback value
        const fallback = binding.fallback || ((binding.type === "text") ? (element.textContent || "") : "");

        // Check for URL override first, then fall back to Statsig
        let value;
        if (urlOverrides.hasOwnProperty(binding.experiment)) {
          value = urlOverrides[binding.experiment];
          console.log(`[Statsig] Using URL override for ${binding.experiment}: ${value}`);
        } else {
          // Get the experiment variant value from Statsig (cached or fallback)
          value = client.getExperiment(binding.experiment).get(binding.param, fallback);
        }

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
    }
  }

  /**
   * Initialize experiments
   */
  function initializeExperiments() {
    // MkDocs Material instant navigation support
    if (window.document$?.subscribe) {
      window.document$.subscribe(() => {
        hydrateExperiments();
      });
    } else {
      // Standard page load
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
          hydrateExperiments();
        });
      } else {
        // Document already loaded
        hydrateExperiments();
      }
    }
  }

  // Auto-initialize when this module loads
  initializeExperiments();
})();
