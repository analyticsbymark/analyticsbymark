/**
 * Statsig Experiments Configuration Template
 *
 * This is a template file for local development.
 * In production, this is replaced by GitHub Actions with secrets.
 *
 * To use for local development:
 * 1. Copy this file to experiments.config.js
 * 2. Update the apiKey if needed (client keys are safe to expose)
 * 3. Enable/disable experiments as needed for testing
 */

window.EXPERIMENT_CONFIG = {
  // Metadata about this configuration
  _meta: {
    environment: "local",
    version: "1.0.0",
    lastUpdated: new Date().toISOString()
  },

  // Statsig client configuration
  client: {
    apiKey: "client-o5NxMKGrDvcZ6sfYbs2081B5l63hu6dpI80652s6XE6",
    options: {
      environment: { tier: "development" },
      // Enable verbose logging in local dev
      loggingLevel: "debug"
    }
  },

  // Feature flags (gates) - not yet implemented
  // These are for on/off toggles, not A/B tests
  featureFlags: {
    // Example:
    // enable_new_feature: {
    //   flagName: "blog_new_feature_enabled",
    //   defaultValue: false
    // }
  },

  // Experiments organized by domain
  experiments: {
    // CTA (Call to Action) experiments
    cta: {
      hero_button_text: {
        selector: "#hero-cta-dev",
        experiment: "abm_dev_landing_button_text",
        param: "button_label",
        type: "text",
        category: "conversion",
        pages: ["index.html"],
        priority: "critical"
      }
    },

    // Navigation experiments
    navigation: {
      // Example experiments (not active yet):
      // sticky_tabs: {
      //   selector: "body",
      //   experiment: "blog_nav_sticky_tabs",
      //   param: "enabled",
      //   type: "class",
      //   className: "md-tabs--sticky",
      //   category: "navigation",
      //   pages: ["*"],
      //   priority: "high"
      // }
    },

    // Blog layout experiments
    blog: {
      // Example experiments (not active yet):
      // pagination_count: {
      //   selector: "[data-exp='pagination']",
      //   experiment: "blog_pagination_count",
      //   param: "count",
      //   type: "attr",
      //   attr: "data-pagination-count",
      //   category: "blog-layout",
      //   pages: ["blog/index.html"],
      //   fallback: "5"
      // }
    },

    // Visual/theming experiments
    visual: {
      // Example experiments (not active yet):
    },

    // Content experiments
    content: {
      // Example experiments (not active yet):
    }
  },

  // Event tracking configuration (Phase 3)
  tracking: {
    enableAutoClick: false,  // Disabled in local dev
    enableEngagement: false, // Disabled in local dev
    clickSelectors: [
      "[data-track]",
      ".md-button",
      "a.md-social__link"
    ],
    engagementThresholds: {
      scrollDepth: [25, 50, 75, 100],
      timeOnPage: [10, 30, 60, 120]
    },
    googleAnalytics: {
      enabled: false,  // Disabled in local dev
      sendExposures: false,
      sendCustomEvents: false,
      prefix: "statsig_"
    }
  }
};
