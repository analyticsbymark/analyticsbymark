/**
 * User Identity Management
 *
 * Manages stable user IDs for Statsig experimentation.
 * Creates and persists a stable user ID in localStorage.
 */

(function() {
  'use strict';

  const STABLE_ID_KEY = "statsig_stable_id_v1";

  /**
   * Get or create a stable user ID
   * @returns {string} A stable user ID persisted in localStorage
   */
  function getStableUserId() {
    let id = localStorage.getItem(STABLE_ID_KEY);

    if (!id) {
      // Generate a new stable ID using crypto.randomUUID if available,
      // otherwise fall back to Math.random + timestamp
      id = crypto?.randomUUID?.() || (Math.random().toString(16).slice(2) + Date.now());
      localStorage.setItem(STABLE_ID_KEY, id);
    }

    return id;
  }

  /**
   * Clear the stored user ID (useful for testing)
   */
  function clearUserId() {
    localStorage.removeItem(STABLE_ID_KEY);
  }

  // Expose to window for other modules
  window.StatsigUser = {
    getStableUserId: getStableUserId,
    clearUserId: clearUserId
  };
})();
