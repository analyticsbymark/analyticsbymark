/**
 * Tracking Initialization - Orchestrates tracking system startup
 * Reads config, waits for client, initializes enabled trackers
 */
(function() {
  'use strict';

  /**
   * Initialize tracking system
   * @returns {Promise<void>}
   */
  async function init() {
    try {
      console.log('[Statsig Tracking] Initializing tracking system...');

      // Get config
      const config = window.EXPERIMENT_CONFIG;
      if (!config) {
        console.warn('[Statsig Tracking] No config found, tracking disabled');
        return;
      }

      // Check if tracking is enabled
      const trackingConfig = config.tracking || {};
      if (!trackingConfig.enableAutoClick && !trackingConfig.enableEngagement) {
        console.log('[Statsig Tracking] Tracking disabled in config');
        return;
      }

      // Wait for Statsig client
      const client = await getExistingClient();
      if (!client) {
        console.warn('[Statsig Tracking] No Statsig client available, tracking disabled');
        return;
      }

      // Initialize EventLogger (core)
      const eventLogger = new window.StatsigTracker.EventLogger(client, config);
      console.log('[Statsig Tracking] EventLogger initialized');

      // Initialize ExposureLogger
      const exposureLogger = new window.StatsigTracker.ExposureLogger(eventLogger, config);
      console.log('[Statsig Tracking] ExposureLogger initialized');

      // Initialize ClickTracker if enabled
      let clickTracker = null;
      if (trackingConfig.enableAutoClick) {
        clickTracker = new window.StatsigTracker.ClickTracker(eventLogger, config);
        clickTracker.init();
        console.log('[Statsig Tracking] ClickTracker initialized');
      }

      // Initialize EngagementTracker if enabled
      let engagementTracker = null;
      if (trackingConfig.enableEngagement) {
        engagementTracker = new window.StatsigTracker.EngagementTracker(eventLogger, config);
        engagementTracker.init();
        console.log('[Statsig Tracking] EngagementTracker initialized');
      }

      // Store references globally for access from bootstrap
      window.StatsigTracker.eventLogger = eventLogger;
      window.StatsigTracker.exposureLogger = exposureLogger;
      window.StatsigTracker.clickTracker = clickTracker;
      window.StatsigTracker.engagementTracker = engagementTracker;

      // Subscribe to instant navigation (if available)
      if (typeof document$ !== 'undefined' && document$.subscribe) {
        document$.subscribe(() => {
          console.log('[Statsig Tracking] Page navigation detected, resetting trackers...');

          // Reset exposure logger
          if (exposureLogger) {
            exposureLogger.reset();
          }

          // Reset engagement tracker
          if (engagementTracker) {
            engagementTracker.reset();
          }
        });
        console.log('[Statsig Tracking] Subscribed to instant navigation');
      }

      // Add beforeunload listener to flush events
      window.addEventListener('beforeunload', () => {
        if (eventLogger) {
          eventLogger.flush();
        }
      });

      console.log('[Statsig Tracking] Tracking system initialized successfully');

    } catch (error) {
      console.error('[Statsig Tracking] Error initializing tracking system:', error);
      // Continue gracefully - don't break the site
    }
  }

  /**
   * Get existing Statsig client (wait if needed)
   * @returns {Promise<object|null>}
   */
  function getExistingClient() {
    return new Promise((resolve) => {
      // Check immediately
      const existing = window.StatsigClient?.getExistingClient?.();
      if (existing) {
        resolve(existing);
        return;
      }

      // Poll for client promise (bootstrap creates it after DOM ready)
      let attempts = 0;
      const maxAttempts = 50; // 5 seconds

      const checkInterval = setInterval(() => {
        attempts++;
        const clientPromise = window.StatsigClient?.getExistingClient?.();
        if (clientPromise) {
          clearInterval(checkInterval);
          resolve(clientPromise);
          return;
        }
        if (attempts >= maxAttempts) {
          clearInterval(checkInterval);
          console.warn('[Statsig Tracking] Timeout waiting for Statsig client');
          resolve(null);
        }
      }, 100);
    });
  }

  // Expose init function
  window.StatsigTracker = window.StatsigTracker || {};
  window.StatsigTracker.init = init;

  // Auto-initialize when this module loads
  init().catch(error => {
    console.error("[Statsig] Tracking initialization failed:", error);
  });

})();
