# Event Tracking System

Phase 3 implementation - Comprehensive event tracking for Statsig experiments and user engagement.

## Architecture

```
tracking/
├── eventLogger.js        - Core event logging (Statsig + GA4 bridge)
├── exposureLogger.js     - Log experiment exposures
├── clickTracker.js       - Automatic click tracking
├── engagementTracker.js  - Scroll depth + time on page
└── init.js              - Tracking initialization orchestrator
```

## Module Details

### eventLogger.js (213 lines)
**Purpose:** Centralized event logging infrastructure

**Key Features:**
- Logs to both Statsig SDK and Google Analytics 4
- Automatic metadata enrichment (page, user, viewport, timing)
- Event deduplication to prevent duplicate logs
- Graceful GA4 failure handling (ad blocker safe)
- Debug logging support

**API:**
```javascript
const logger = new EventLogger(client, config);
logger.logEvent(eventName, value, metadata);
```

### exposureLogger.js (125 lines)
**Purpose:** Track experiment exposures

**Key Features:**
- Logs when users see experiment variants
- Prevents duplicate exposures per page
- Sets GA4 user properties for segmentation
- Resets on page navigation

**API:**
```javascript
const exposureLogger = new ExposureLogger(eventLogger, config);
exposureLogger.logExposure(experimentName, variant, metadata);
```

### clickTracker.js (214 lines)
**Purpose:** Automatic click tracking

**Key Features:**
- Event delegation pattern (performance optimized)
- Tracks configured selectors: `[data-track]`, `.md-button`, `a.md-social__link`
- Extracts rich metadata from clicked elements
- Smart event naming based on context

**API:**
```javascript
const clickTracker = new ClickTracker(eventLogger, config);
clickTracker.init();
```

### engagementTracker.js (272 lines)
**Purpose:** Scroll depth and time on page tracking

**Key Features:**
- Scroll depth using IntersectionObserver (25%, 50%, 75%, 100%)
- Time on page using setTimeout (10s, 30s, 60s, 120s)
- Respects page visibility (pauses when tab hidden)
- Resets state on page navigation

**API:**
```javascript
const engagementTracker = new EngagementTracker(eventLogger, config);
engagementTracker.init();
```

### init.js (138 lines)
**Purpose:** Tracking system orchestrator

**Key Features:**
- Reads config and initializes enabled trackers
- Waits for Statsig client before starting
- Subscribes to instant navigation events
- Handles errors gracefully

**API:**
```javascript
await window.StatsigTracker.init();
```

## Events Logged

### Experiment Events
- `experiment_exposure` - When variant shown to user
- `experiment_interaction` - Click on experiment element

### Engagement Events
- `scroll_depth` - Milestones: 25%, 50%, 75%, 100%
- `time_on_page` - Thresholds: 10s, 30s, 60s, 120s
- `page_view` - Page loaded/navigated

### Interaction Events
- `nav_click` - Navigation link clicked
- `cta_clicked` - CTA button clicked
- `social_share_clicked` - Social media link clicked
- `click` - Generic click (fallback)

## Metadata Structure

### Common Fields (All Events)
Automatically enriched by eventLogger:
```javascript
{
  page_path: "/index.html",
  page_url: "https://...",
  page_title: "Document Title",
  timestamp: 1707300000000,
  session_duration: 45,
  user_id: "stable-user-abc123",
  viewport_width: 1920,
  viewport_height: 1080,
  referrer: "https://google.com"
}
```

### Exposure-Specific
```javascript
{
  experiment_name: "abm_dev_landing_button_text",
  variant: "Get Started Now",
  experiment_key: "hero_button_text",
  experiment_category: "conversion",
  selector: "#hero-cta-dev"
}
```

### Click-Specific
```javascript
{
  element_type: "a",
  element_id: "hero-cta-dev",
  element_class: "md-button md-button--primary",
  element_selector: "#hero-cta-dev",
  element_text: "Get Started Now",
  link_url: "https://...",
  link_target: "_self",
  data_track: "custom-event-name", // if present
  experiment_key: "hero_button_text" // if present
}
```

### Engagement-Specific
```javascript
{
  scroll_percentage: 50,     // For scroll_depth events
  time_seconds: 30,          // For time_on_page events
  load_time: 1234           // For page_view events
}
```

## Configuration

Tracking behavior is controlled by `window.EXPERIMENT_CONFIG.tracking`:

```javascript
tracking: {
  // Enable/disable automatic click tracking
  enableAutoClick: true,

  // Enable/disable engagement tracking (scroll + time)
  enableEngagement: true,

  // Selectors for automatic click tracking
  clickSelectors: [
    "[data-track]",        // Custom tracking attribute
    ".md-button",          // Material buttons
    "a.md-social__link"    // Social share links
  ],

  // Engagement tracking thresholds
  engagementThresholds: {
    scrollDepth: [25, 50, 75, 100],    // Percentages
    timeOnPage: [10, 30, 60, 120]      // Seconds
  },

  // Google Analytics 4 integration
  googleAnalytics: {
    enabled: true,              // Send to GA4
    sendExposures: true,        // Send exposure events
    sendCustomEvents: true,     // Send custom events
    prefix: "statsig_"          // Event name prefix
  }
}
```

## Testing

### Local Testing

1. **Enable debug logging:**
   ```javascript
   client: {
     options: {
       loggingLevel: "debug"
     }
   }
   ```

2. **Start local server:**
   ```bash
   cd /home/cooperm/analyticsbymark/projects/blog
   mkdocs serve
   ```

3. **Open browser DevTools → Console**

4. **Expected console output:**
   ```
   [Statsig Tracking] Initializing tracking system...
   [Statsig Tracking] EventLogger initialized
   [Statsig Tracking] ExposureLogger initialized
   [Statsig Tracking] ClickTracker initialized
   [Statsig Tracking] EngagementTracker initialized
   [Statsig Tracking] Tracking system initialized successfully

   [Statsig ExposureLogger] Logged exposure: abm_dev_landing_button_text = Get Started Now
   [Statsig EventLogger] Logged event: experiment_exposure

   [Statsig ClickTracker] Tracked click: #hero-cta-dev
   [Statsig EventLogger] Logged event: experiment_interaction

   [Statsig EngagementTracker] Scroll depth: 25%
   [Statsig EventLogger] Logged event: scroll_depth

   [Statsig EngagementTracker] Time on page: 10s
   [Statsig EventLogger] Logged event: time_on_page
   ```

### Verification Checklist

- [ ] Exposure logged when experiment variant applied
- [ ] Click events logged for tracked elements
- [ ] Scroll depth milestones logged (25%, 50%, 75%, 100%)
- [ ] Time on page thresholds logged (10s, 30s, 60s, 120s)
- [ ] Events sent to Statsig (check Network tab)
- [ ] Events sent to GA4 (if enabled)
- [ ] Instant navigation resets tracking state
- [ ] No console errors

### Statsig Console Verification

1. Navigate to Statsig dashboard → Metrics → Events
2. Filter by event name (e.g., `experiment_exposure`)
3. Verify events appear with correct metadata
4. Check user_id matches stable ID from localStorage

### GA4 Verification

1. Navigate to GA4 property → Configure → DebugView
2. Perform actions on site
3. Verify prefixed events appear (e.g., `statsig_experiment_exposure`)
4. Check event parameters are captured correctly

## Performance

**Bundle Size:** ~28 KB unminified (~8-10 KB gzipped)

**Initialization Time:** < 100ms (async, non-blocking)

**Runtime Overhead:** Negligible (event delegation, passive observers)

## Error Handling

The tracking system is designed to fail gracefully:

1. **Statsig client unavailable** → Tracking disabled, site works normally
2. **GA4 blocked** → GA4 fails silently, Statsig continues
3. **Tracking init fails** → Error logged, experiments still work
4. **Individual tracker fails** → Other trackers continue working

All errors are logged to console but don't break the site.

## Instant Navigation Support

The tracking system fully supports MkDocs Material instant navigation:

1. **Page loads** → Tracking initialized
2. **User clicks internal link** → Navigation event fires
3. **document$ emits** → Tracking system resets
4. **New content loaded** → Tracking re-initializes
5. **New exposures logged** → Process continues

## Integration with Bootstrap

The bootstrap.js file has two integration points:

**1. Exposure Logging (line ~109):**
Called after applying experiment variant:
```javascript
if (window.StatsigTracker?.exposureLogger) {
  window.StatsigTracker.exposureLogger.logExposure(...);
}
```

**2. Tracking Initialization (line ~160):**
Called after experiments initialized:
```javascript
if (window.StatsigTracker?.init) {
  window.StatsigTracker.init().catch(error => { ... });
}
```

## Troubleshooting

### No events logged
- Check if tracking enabled in config
- Verify Statsig client initialized
- Check browser console for errors

### GA4 events not appearing
- Check if GA4 blocked by ad blocker (expected, OK)
- Verify `googleAnalytics.enabled: true`
- Check if gtag function exists

### Duplicate events
- Check deduplication logic
- Verify page navigation resets state

### Scroll tracking not working
- Verify page has sufficient height
- Check if IntersectionObserver supported
- Inspect DOM for scroll markers

## Implementation Date

**Completed:** February 7, 2026
**Total Lines:** 962 lines across 5 modules
**Total Size:** ~28 KB unminified

## See Also

- [Phase 3 Implementation Guide](/home/cooperm/analyticsbymark/projects/blog/PHASE3_IMPLEMENTATION.md)
- [Statsig Documentation](https://docs.statsig.com)
- [GA4 Events Guide](https://developers.google.com/analytics/devguides/collection/ga4/events)
