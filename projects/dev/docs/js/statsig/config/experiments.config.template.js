/**
 * Statsig Experiments Configuration Template (Dev Site)
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

  // Experiments - organized by domain for internal organization only
  // NOTE: Use obfuscated experiment names (exp_001, exp_002) in production
  experiments: {
    // Domain: CTA/Conversion elements
    cta: {
      // Internal reference: hero_cta_text
      // Real experiment: Hero CTA button text optimization
      exp_001: {
        selector: "#hero-cta-dev",
        experiment: "exp_2026_02_beta",  // Obfuscated Statsig experiment name
        param: "text",                     // Generic parameter name
        type: "text",
        pages: ["index.html"]
      }
    }
  },

  // Event tracking configuration
  tracking: {
    enableAutoClick: true,   // Disabled in local dev
    enableEngagement: true,  // Disabled in local dev
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
