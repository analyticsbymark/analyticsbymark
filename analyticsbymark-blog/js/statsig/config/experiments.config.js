window.EXPERIMENT_CONFIG = {
  "_meta": {
    "environment": "production",
    "version": "1.0.0",
    "lastUpdated": "2026-02-13T00:00:00Z"
  },
  "client": {
    "apiKey": "client-o5NxMKGrDvcZ6sfYbs2081B5l63hu6dpI80652s6XE6",
    "options": {
      "environment": {
        "tier": "production"
      },
      "loggingLevel": "none"
    }
  },
  "experiments": {
    "cta": {
      "newsletter_value_prop": {
        "selector": "#hero-cta-dev",
        "experiment": "exp_2026_02_beta",
        "param": "text",
        "type": "text",
        "category": "conversion",
        "pages": [
          "index.html"
        ],
        "priority": "critical"
      }
    },
    "navigation": {},
    "blog": {},
    "visual": {},
    "content": {}
  },
  "tracking": {
    "enableAutoClick": true,
    "enableEngagement": true,
    "clickSelectors": [
      "[data-track]",
      ".md-button",
      "a.md-social__link"
    ],
    "engagementThresholds": {
      "scrollDepth": [
        25,
        50,
        75,
        100
      ],
      "timeOnPage": [
        10,
        30,
        60,
        120
      ]
    },
    "googleAnalytics": {
      "enabled": true,
      "sendExposures": true,
      "sendCustomEvents": true,
      "prefix": "statsig_"
    }
  }
};
