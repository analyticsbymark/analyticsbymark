/**
 * Event Logger - Core event logging infrastructure
 * Logs events to both Statsig and Google Analytics 4
 * Provides metadata enrichment and deduplication
 */
(function() {
  'use strict';

  class EventLogger {
    constructor(client, config) {
      this.client = client;
      this.config = config || {};
      this.eventHistory = new Map(); // For deduplication
      this.sessionStartTime = Date.now();
    }

    /**
     * Main event logging function
     * @param {string} eventName - Name of the event
     * @param {*} value - Optional event value
     * @param {object} metadata - Event metadata
     */
    logEvent(eventName, value = null, metadata = {}) {
      try {
        // Check if we should log this event (deduplication)
        if (!this.shouldLogEvent(eventName, metadata)) {
          this.logDebug(`Skipping duplicate event: ${eventName}`);
          return;
        }

        // Enrich metadata with common fields
        const enrichedMetadata = this.enrichMetadata(metadata);

        // Log to Statsig
        this.logToStatsig(eventName, value, enrichedMetadata);

        // Log to Google Analytics if enabled
        if (this.config.googleAnalytics?.enabled) {
          this.logToGA(eventName, value, enrichedMetadata);
        }

        // Record in history for deduplication
        this.recordEvent(eventName, enrichedMetadata);

        this.logDebug(`Logged event: ${eventName}`, { value, metadata: enrichedMetadata });
      } catch (error) {
        console.error('[Statsig EventLogger] Error logging event:', error);
      }
    }

    /**
     * Log event to Statsig
     */
    logToStatsig(eventName, value, metadata) {
      try {
        if (!this.client) {
          console.warn('[Statsig EventLogger] No client available for logging');
          return;
        }

        this.client.logEvent(eventName, value, metadata);
      } catch (error) {
        console.error('[Statsig EventLogger] Error logging to Statsig:', error);
        throw error; // Re-throw for Statsig errors (important)
      }
    }

    /**
     * Log event to Google Analytics
     */
    logToGA(eventName, value, metadata) {
      try {
        // Check if gtag is available
        if (typeof gtag === 'undefined') {
          this.logDebug('gtag not available (may be blocked by ad blocker)');
          return;
        }

        // Apply prefix from config
        const prefix = this.config.googleAnalytics?.prefix || 'statsig_';
        const gaEventName = prefix + eventName;

        // Prepare GA4 event parameters
        const eventParams = {
          ...metadata,
          value: value
        };

        // Send to GA4
        gtag('event', gaEventName, eventParams);

        this.logDebug(`Sent to GA4: ${gaEventName}`, eventParams);
      } catch (error) {
        // Silent failure for GA4 (may be blocked by ad blockers)
        this.logDebug('Failed to send to GA4 (expected if ad blocker enabled):', error);
      }
    }

    /**
     * Enrich metadata with common fields
     */
    enrichMetadata(metadata) {
      return {
        ...metadata,
        // Page information
        page_path: window.location.pathname,
        page_url: window.location.href,
        page_title: document.title,

        // Timing
        timestamp: Date.now(),
        session_duration: Math.round((Date.now() - this.sessionStartTime) / 1000),

        // User information
        user_id: this.getUserId(),

        // Viewport
        viewport_width: window.innerWidth,
        viewport_height: window.innerHeight,

        // Referrer
        referrer: document.referrer || 'direct'
      };
    }

    /**
     * Get user ID from localStorage (stable ID set by user.js)
     */
    getUserId() {
      try {
        return localStorage.getItem('statsig-user-id') || 'anonymous';
      } catch (error) {
        return 'anonymous';
      }
    }

    /**
     * Check if event should be logged (deduplication logic)
     */
    shouldLogEvent(eventName, metadata) {
      // Generate deduplication key
      const dedupKey = this.generateDedupKey(eventName, metadata);

      // Check if we've seen this exact event recently
      if (this.eventHistory.has(dedupKey)) {
        const lastSeen = this.eventHistory.get(dedupKey);
        const timeSinceLastSeen = Date.now() - lastSeen;

        // Allow re-logging after 1 second (prevents rapid duplicates)
        return timeSinceLastSeen > 1000;
      }

      return true;
    }

    /**
     * Generate deduplication key for an event
     */
    generateDedupKey(eventName, metadata) {
      // Key based on event name and relevant metadata fields
      const keyParts = [
        eventName,
        metadata.experiment_name || '',
        metadata.element_selector || '',
        metadata.scroll_percentage || '',
        metadata.time_seconds || ''
      ];

      return keyParts.join('|');
    }

    /**
     * Record event in history for deduplication
     */
    recordEvent(eventName, metadata) {
      const dedupKey = this.generateDedupKey(eventName, metadata);
      this.eventHistory.set(dedupKey, Date.now());

      // Clean up old entries (keep last 100)
      if (this.eventHistory.size > 100) {
        const firstKey = this.eventHistory.keys().next().value;
        this.eventHistory.delete(firstKey);
      }
    }

    /**
     * Debug logging (respects config.loggingLevel)
     */
    logDebug(message, data) {
      const loggingLevel = this.config.client?.options?.loggingLevel;
      if (loggingLevel === 'debug' || loggingLevel === 'info') {
        if (data) {
          console.log(`[Statsig EventLogger] ${message}`, data);
        } else {
          console.log(`[Statsig EventLogger] ${message}`);
        }
      }
    }

    /**
     * Flush any pending events (called on page unload)
     */
    flush() {
      this.logDebug('Flushing event logger');
      // Statsig SDK handles its own flushing
    }
  }

  // Expose EventLogger class
  window.StatsigTracker = window.StatsigTracker || {};
  window.StatsigTracker.EventLogger = EventLogger;

})();
