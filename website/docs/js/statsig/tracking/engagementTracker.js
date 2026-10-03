/**
 * Engagement Tracker - Track scroll depth and time on page
 * Uses IntersectionObserver for scroll tracking
 * Uses setTimeout for time tracking
 */
(function() {
  'use strict';

  class EngagementTracker {
    constructor(eventLogger, config) {
      this.eventLogger = eventLogger;
      this.config = config || {};
      this.isInitialized = false;

      // Scroll depth tracking
      this.scrollObserver = null;
      this.scrollMarkers = [];
      this.scrollDepthsLogged = new Set();

      // Time on page tracking
      this.timeThresholds = this.config.tracking?.engagementThresholds?.timeOnPage || [10, 30, 60, 120];
      this.timeTrackers = [];
      this.pageLoadTime = Date.now();
      this.isPageVisible = true;
    }

    /**
     * Initialize engagement tracking
     */
    init() {
      if (this.isInitialized) {
        this.logDebug('Engagement tracker already initialized');
        return;
      }

      // Initialize scroll depth tracking
      this.initScrollTracking();

      // Initialize time on page tracking
      this.initTimeTracking();

      // Track page visibility changes
      this.initVisibilityTracking();

      // Log initial page view
      this.logPageView();

      this.isInitialized = true;
      this.logDebug('Engagement tracker initialized');
    }

    /**
     * Initialize scroll depth tracking
     */
    initScrollTracking() {
      try {
        const scrollDepths = this.config.tracking?.engagementThresholds?.scrollDepth || [25, 50, 75, 100];

        // Create invisible marker divs at each percentage
        scrollDepths.forEach(depth => {
          const marker = this.createScrollMarker(depth);
          document.body.appendChild(marker);
          this.scrollMarkers.push(marker);
        });

        // Create IntersectionObserver
        this.scrollObserver = new IntersectionObserver(
          this.handleScrollIntersection.bind(this),
          {
            threshold: 0,
            rootMargin: '0px'
          }
        );

        // Observe all markers
        this.scrollMarkers.forEach(marker => {
          this.scrollObserver.observe(marker);
        });

        this.logDebug('Scroll tracking initialized', { depths: scrollDepths });
      } catch (error) {
        console.error('[Statsig EngagementTracker] Error initializing scroll tracking:', error);
      }
    }

    /**
     * Create scroll marker element
     */
    createScrollMarker(depth) {
      const marker = document.createElement('div');
      marker.setAttribute('data-scroll-marker', depth);
      marker.style.cssText = 'position: absolute; width: 1px; height: 1px; opacity: 0; pointer-events: none;';
      marker.style.top = `${depth}%`;
      return marker;
    }

    /**
     * Handle scroll intersection
     */
    handleScrollIntersection(entries) {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const depth = parseInt(entry.target.getAttribute('data-scroll-marker'));

          // Only log once per depth
          if (!this.scrollDepthsLogged.has(depth)) {
            this.logScrollDepth(depth);
            this.scrollDepthsLogged.add(depth);
          }
        }
      });
    }

    /**
     * Log scroll depth event
     */
    logScrollDepth(percentage) {
      this.eventLogger.logEvent('scroll_depth', percentage, {
        scroll_percentage: percentage
      });

      this.logDebug(`Scroll depth: ${percentage}%`);
    }

    /**
     * Initialize time on page tracking
     */
    initTimeTracking() {
      try {
        this.timeThresholds.forEach(seconds => {
          const timerId = setTimeout(() => {
            // Only log if page is visible
            if (this.isPageVisible) {
              this.logTimeOnPage(seconds);
            }
          }, seconds * 1000);

          this.timeTrackers.push(timerId);
        });

        this.logDebug('Time tracking initialized', { thresholds: this.timeThresholds });
      } catch (error) {
        console.error('[Statsig EngagementTracker] Error initializing time tracking:', error);
      }
    }

    /**
     * Log time on page event
     */
    logTimeOnPage(seconds) {
      this.eventLogger.logEvent('time_on_page', seconds, {
        time_seconds: seconds
      });

      this.logDebug(`Time on page: ${seconds}s`);
    }

    /**
     * Initialize visibility tracking
     * Pause time tracking when tab is hidden
     */
    initVisibilityTracking() {
      try {
        document.addEventListener('visibilitychange', () => {
          this.isPageVisible = !document.hidden;
          this.logDebug(`Page visibility changed: ${this.isPageVisible ? 'visible' : 'hidden'}`);
        });
      } catch (error) {
        console.error('[Statsig EngagementTracker] Error initializing visibility tracking:', error);
      }
    }

    /**
     * Log page view event
     */
    logPageView() {
      this.eventLogger.logEvent('page_view', null, {
        load_time: Date.now() - this.pageLoadTime
      });

      this.logDebug('Page view logged');
    }

    /**
     * Reset engagement tracking (called on page navigation)
     */
    reset() {
      try {
        // Clear time trackers
        this.timeTrackers.forEach(timerId => clearTimeout(timerId));
        this.timeTrackers = [];

        // Clear scroll depths logged
        this.scrollDepthsLogged.clear();

        // Remove scroll markers
        this.scrollMarkers.forEach(marker => {
          if (marker.parentNode) {
            marker.parentNode.removeChild(marker);
          }
        });
        this.scrollMarkers = [];

        // Disconnect observer
        if (this.scrollObserver) {
          this.scrollObserver.disconnect();
          this.scrollObserver = null;
        }

        // Reset state
        this.pageLoadTime = Date.now();
        this.isInitialized = false;

        this.logDebug('Engagement tracker reset');

        // Re-initialize
        this.init();
      } catch (error) {
        console.error('[Statsig EngagementTracker] Error resetting:', error);
      }
    }

    /**
     * Destroy engagement tracker
     */
    destroy() {
      try {
        // Clear time trackers
        this.timeTrackers.forEach(timerId => clearTimeout(timerId));
        this.timeTrackers = [];

        // Remove scroll markers
        this.scrollMarkers.forEach(marker => {
          if (marker.parentNode) {
            marker.parentNode.removeChild(marker);
          }
        });
        this.scrollMarkers = [];

        // Disconnect observer
        if (this.scrollObserver) {
          this.scrollObserver.disconnect();
          this.scrollObserver = null;
        }

        this.isInitialized = false;
        this.logDebug('Engagement tracker destroyed');
      } catch (error) {
        console.error('[Statsig EngagementTracker] Error destroying:', error);
      }
    }

    /**
     * Debug logging
     */
    logDebug(message, data) {
      const loggingLevel = this.config.client?.options?.loggingLevel;
      if (loggingLevel === 'debug' || loggingLevel === 'info') {
        if (data) {
          console.log(`[Statsig EngagementTracker] ${message}`, data);
        } else {
          console.log(`[Statsig EngagementTracker] ${message}`);
        }
      }
    }
  }

  // Expose EngagementTracker class
  window.StatsigTracker = window.StatsigTracker || {};
  window.StatsigTracker.EngagementTracker = EngagementTracker;

})();
