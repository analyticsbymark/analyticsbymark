/**
 * Statsig Client Management
 *
 * Manages the Statsig client singleton and initialization.
 * Ensures only one client instance is created and shared across the application.
 */

(function() {
  'use strict';

  /**
   * Get or create the Statsig client singleton
   * @param {string} apiKey - Statsig client API key
   * @param {object} options - Optional Statsig client options
   * @returns {Promise<object>} The initialized Statsig client
   */
  async function getStatsigClient(apiKey, options = {}) {
    // Return existing client promise if already initializing/initialized
    if (window.__statsigClientPromise) {
      return window.__statsigClientPromise;
    }

    // Create and store the client promise
    window.__statsigClientPromise = (async () => {
      try {
        // Get the StatsigClient constructor from the global Statsig object
        const Ctor = window.Statsig?.StatsigClient || window.StatsigClient;

        if (typeof Ctor !== "function") {
          throw new Error("StatsigClient constructor not found. Ensure the Statsig SDK is loaded.");
        }

        // Create client with stable user ID
        const userId = window.StatsigUser.getStableUserId();
        const client = new Ctor(apiKey, {
          userID: userId,
          ...options
        });

        // Initialize the client (async)
        if (typeof client.initializeAsync === "function") {
          await client.initializeAsync();
        } else if (typeof client.initialize === "function") {
          await client.initialize();
        } else {
          throw new Error("No initialize method found on Statsig client");
        }

        return client;
      } catch (error) {
        console.error("[Statsig] Failed to initialize client:", error);
        throw error;
      }
    })();

    return window.__statsigClientPromise;
  }

  /**
   * Get or create the Statsig client using synchronous (cache-first) initialization.
   * Returns the client instance immediately — not a promise.
   * Uses localStorage-cached values via initializeSync(), then refreshes in the background.
   * @param {string} apiKey - Statsig client API key
   * @param {object} options - Optional Statsig client options
   * @returns {object} The Statsig client (synchronously initialized)
   */
  function getStatsigClientSync(apiKey, options = {}) {
    // Return existing client if already created
    if (window.__statsigClientInstance) {
      return window.__statsigClientInstance;
    }

    const Ctor = window.Statsig?.StatsigClient || window.StatsigClient;

    if (typeof Ctor !== "function") {
      console.warn("[Statsig] StatsigClient constructor not found. Ensure the Statsig SDK is loaded.");
      return null;
    }

    const userId = window.StatsigUser.getStableUserId();
    const client = new Ctor(apiKey, {
      userID: userId,
      ...options
    });

    // Synchronous init — loads cached values from localStorage instantly
    if (typeof client.initializeSync === "function") {
      client.initializeSync();
      console.log("[Statsig] Using sync initialization (cache-first)");
    } else {
      console.warn("[Statsig] initializeSync not available, falling back to empty state");
    }

    window.__statsigClientInstance = client;

    // Kick off async refresh in the background (updates cache for next visit)
    if (typeof client.initializeAsync === "function") {
      client.initializeAsync().catch(err => {
        console.warn("[Statsig] Background async refresh failed:", err);
      });
    }

    return client;
  }

  /**
   * Get the existing client if already initialized
   * @returns {Promise<object>|null} The client promise or null if not initialized
   */
  function getExistingClient() {
    return window.__statsigClientInstance || window.__statsigClientPromise || null;
  }

  // Expose to window for other modules
  window.StatsigClient = window.StatsigClient || {};
  window.StatsigClient.getClient = getStatsigClient;
  window.StatsigClient.getClientSync = getStatsigClientSync;
  window.StatsigClient.getExistingClient = getExistingClient;
})();
