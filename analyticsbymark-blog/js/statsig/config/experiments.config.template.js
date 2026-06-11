/**
 * Statsig Experiments Configuration Template
 *
 * SECURITY: This config is exposed in the built site. Keep experiment names obfuscated.
 *
 * For local development:
 * 1. Copy this file to experiments.config.js
 * 2. Update the apiKey if needed (client keys are safe to expose)
 * 3. Enable/disable experiments as needed for testing
 *
 * For production:
 * - This template is replaced by GitHub Actions with secrets
 * - Use obfuscated experiment names (exp_001, exp_002, etc.)
 * - Remove strategic metadata (category, priority, hypothesis)
 * - Keep mapping of real names in EXPERIMENT_MAPPING.md (private, not in repo)
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
      loggingLevel: "debug"  // Use "none" in production
    }
  },

  // Feature flags (gates) - not yet implemented
  featureFlags: {},

  // Experiments - organized by domain for internal organization only
  // NOTE: Use obfuscated experiment names (exp_001, exp_002) in production
  experiments: {
    // Domain: CTA/Conversion elements
    cta: {
      // Internal reference: hero_cta_text
      // Real experiment: Hero CTA button text optimization
      exp_001: {
        selector: "#hero-cta-dev",
        experiment: "exp_2024_01_alpha",  // Obfuscated Statsig experiment name
        param: "text",                     // Generic parameter name
        type: "text",
        pages: ["index.html"]
        // REMOVED: category, priority, hypothesis, expectedLift
      }
    },

    // Domain: Navigation
    navigation: {
      // Example: Sticky navigation test
      // exp_002: {
      //   selector: "body",
      //   experiment: "exp_2024_02_beta",
      //   param: "enabled",
      //   type: "class",
      //   className: "md-tabs--sticky",
      //   pages: ["*"]
      // }
    },

    // Domain: Blog layout
    blog: {
      // Example: Pagination count test
      // exp_003: {
      //   selector: "[data-exp='pagination']",
      //   experiment: "exp_2024_03_gamma",
      //   param: "count",
      //   type: "attr",
      //   attr: "data-pagination-count",
      //   pages: ["blog/index.html"],
      //   fallback: "5"
      // }
    },

    // Domain: Visual
    visual: {},

    // Domain: Content
    content: {}
  },

  // Event tracking configuration
  tracking: {
    enableAutoClick: false,   // Disabled in local dev
    enableEngagement: false,  // Disabled in local dev
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
      enabled: false,           // Disabled in local dev
      sendExposures: false,
      sendCustomEvents: false,
      prefix: "statsig_"
    }
  }
};
