/**
 * Exposure Logger - Track experiment exposures
 * Logs when users are exposed to experiment variants
 * Prevents duplicate exposure logging per page
 */
(function() {
  'use strict';

  class ExposureLogger {
    constructor(eventLogger, config) {
      this.eventLogger = eventLogger;
      this.config = config || {};
      this.exposureLog = new Map(); // Track logged exposures
    }

    /**
     * Log experiment exposure
     * @param {string} experimentName - Name of the experiment
     * @param {*} variant - Variant value assigned
     * @param {object} metadata - Additional metadata
     */
    logExposure(experimentName, variant, metadata = {}) {
      try {
        // Check if already logged for this page
        const exposureKey = this.getExposureKey(experimentName);
        if (this.hasLogged(exposureKey)) {
          this.logDebug(`Skipping duplicate exposure: ${experimentName}`);
          return;
        }

        // Prepare exposure metadata
        const exposureMetadata = {
          experiment_name: experimentName,
          variant: String(variant),
          ...metadata
        };

        // Log to both Statsig and GA4
        this.eventLogger.logEvent('experiment_exposure', variant, exposureMetadata);

        // Send to GA4 as user property (for segmentation)
        this.setGA4UserProperty(experimentName, variant);

        // Mark as logged
        this.exposureLog.set(exposureKey, {
          variant,
          timestamp: Date.now()
        });

        this.logDebug(`Logged exposure: ${experimentName} = ${variant}`);
      } catch (error) {
        console.error('[Statsig ExposureLogger] Error logging exposure:', error);
      }
    }

    /**
     * Check if exposure has been logged
     */
    hasLogged(exposureKey) {
      return this.exposureLog.has(exposureKey);
    }

    /**
     * Generate exposure key (experiment + page)
     */
    getExposureKey(experimentName) {
      const pagePath = window.location.pathname;
      return `${experimentName}|${pagePath}`;
    }

    /**
     * Set GA4 user property for experiment variant
     * Allows segmenting all GA4 data by experiment
     */
    setGA4UserProperty(experimentName, variant) {
      try {
        if (!this.config.googleAnalytics?.enabled) {
          return;
        }

        if (typeof gtag === 'undefined') {
          return;
        }

        // Set user property for this experiment
        const propertyName = `exp_${experimentName}`;
        gtag('set', 'user_properties', {
          [propertyName]: String(variant)
        });

        this.logDebug(`Set GA4 user property: ${propertyName} = ${variant}`);
      } catch (error) {
        // Silent failure for GA4
        this.logDebug('Failed to set GA4 user property:', error);
      }
    }

    /**
     * Reset exposure log (called on page navigation)
     */
    reset() {
      this.exposureLog.clear();
      this.logDebug('Reset exposure log');
    }

    /**
     * Debug logging
     */
    logDebug(message, data) {
      const loggingLevel = this.config.client?.options?.loggingLevel;
      if (loggingLevel === 'debug' || loggingLevel === 'info') {
        if (data) {
          console.log(`[Statsig ExposureLogger] ${message}`, data);
        } else {
          console.log(`[Statsig ExposureLogger] ${message}`);
        }
      }
    }
  }

  // Expose ExposureLogger class
  window.StatsigTracker = window.StatsigTracker || {};
  window.StatsigTracker.ExposureLogger = ExposureLogger;

})();
