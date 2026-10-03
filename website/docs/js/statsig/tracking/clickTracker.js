/**
 * Click Tracker - Automatic click tracking
 * Uses event delegation to track clicks on configured selectors
 * Extracts metadata from clicked elements
 */
(function() {
  'use strict';

  class ClickTracker {
    constructor(eventLogger, config) {
      this.eventLogger = eventLogger;
      this.config = config || {};
      this.selectors = this.config.tracking?.clickSelectors || [];
      this.isInitialized = false;
    }

    /**
     * Initialize click tracking
     */
    init() {
      if (this.isInitialized) {
        this.logDebug('Click tracker already initialized');
        return;
      }

      // Use event delegation on document.body
      document.body.addEventListener('click', this.handleClick.bind(this), true);

      this.isInitialized = true;
      this.logDebug('Click tracker initialized', { selectors: this.selectors });
    }

    /**
     * Handle click events
     */
    handleClick(event) {
      try {
        const target = event.target;

        // Check if target matches any of our selectors
        const matchedElement = this.findMatchingElement(target);
        if (!matchedElement) {
          return;
        }

        // Extract click metadata
        const clickMetadata = this.extractClickMetadata(matchedElement);

        // Determine event name based on element type
        const eventName = this.determineEventName(matchedElement, clickMetadata);

        // Log the click event
        this.eventLogger.logEvent(eventName, null, clickMetadata);

      } catch (error) {
        console.error('[Statsig ClickTracker] Error handling click:', error);
      }
    }

    /**
     * Find element matching configured selectors
     * Walks up the DOM tree to find a match
     */
    findMatchingElement(element) {
      let current = element;
      let depth = 0;
      const maxDepth = 5; // Prevent infinite loops

      while (current && current !== document.body && depth < maxDepth) {
        // Check each configured selector
        for (const selector of this.selectors) {
          if (current.matches && current.matches(selector)) {
            return current;
          }
        }
        current = current.parentElement;
        depth++;
      }

      return null;
    }

    /**
     * Extract metadata from clicked element
     */
    extractClickMetadata(element) {
      const metadata = {
        element_type: element.tagName.toLowerCase(),
        element_id: element.id || undefined,
        element_class: element.className || undefined,
        element_selector: this.getElementSelector(element)
      };

      // Extract text content (truncated)
      const text = this.getElementText(element);
      if (text) {
        metadata.element_text = text;
      }

      // Extract link URL if anchor
      if (element.tagName === 'A') {
        metadata.link_url = element.href;
        metadata.link_target = element.target || '_self';
      }

      // Extract data-track attribute if present
      const dataTrack = element.getAttribute('data-track');
      if (dataTrack) {
        metadata.data_track = dataTrack;
      }

      // Extract experiment data if present
      const expKey = element.getAttribute('data-exp-key');
      if (expKey) {
        metadata.experiment_key = expKey;
      }

      return metadata;
    }

    /**
     * Get element selector (ID or class-based)
     */
    getElementSelector(element) {
      if (element.id) {
        return `#${element.id}`;
      }

      if (element.className && typeof element.className === 'string') {
        const firstClass = element.className.split(' ')[0];
        return `.${firstClass}`;
      }

      return element.tagName.toLowerCase();
    }

    /**
     * Get element text content (truncated to 50 chars)
     */
    getElementText(element) {
      let text = element.textContent || element.innerText || '';
      text = text.trim();

      if (text.length > 50) {
        text = text.substring(0, 50) + '...';
      }

      return text || undefined;
    }

    /**
     * Determine event name based on element characteristics
     */
    determineEventName(element, metadata) {
      // Check for experiment interaction
      if (metadata.experiment_key) {
        return 'experiment_interaction';
      }

      // Check for data-track attribute
      if (metadata.data_track) {
        return metadata.data_track; // Use custom event name
      }

      // Check element class for specific types
      if (element.classList.contains('md-button')) {
        return 'cta_clicked';
      }

      if (element.classList.contains('md-social__link')) {
        return 'social_share_clicked';
      }

      if (element.closest('.md-nav')) {
        return 'nav_click';
      }

      // Default
      return 'click';
    }

    /**
     * Destroy click tracker (remove event listener)
     */
    destroy() {
      if (!this.isInitialized) {
        return;
      }

      document.body.removeEventListener('click', this.handleClick.bind(this), true);
      this.isInitialized = false;
      this.logDebug('Click tracker destroyed');
    }

    /**
     * Debug logging
     */
    logDebug(message, data) {
      const loggingLevel = this.config.client?.options?.loggingLevel;
      if (loggingLevel === 'debug' || loggingLevel === 'info') {
        if (data) {
          console.log(`[Statsig ClickTracker] ${message}`, data);
        } else {
          console.log(`[Statsig ClickTracker] ${message}`);
        }
      }
    }
  }

  // Expose ClickTracker class
  window.StatsigTracker = window.StatsigTracker || {};
  window.StatsigTracker.ClickTracker = ClickTracker;

})();
