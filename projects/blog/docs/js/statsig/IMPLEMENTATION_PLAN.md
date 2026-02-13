# Phase 3: Event Tracking Implementation Plan

## Context

**Phases 1 & 2 Complete:**
- ✅ Phase 1: Modular architecture (core/, experiments/, tracking/, utils/ directories created)
- ✅ Phase 2: Enhanced configuration system with structured config and validation

**Current State:**
- Statsig client and bootstrap working properly
- Config includes tracking section with all settings (enableAutoClick, enableEngagement, GA4 config)
- Google Analytics GA4 property G-QGKGYMC3V5 already configured in mkdocs.yml
- Empty tracking/ directory ready for implementation
- Bootstrap already parses tracking config but doesn't use it

**Phase 3 Goal:**
Implement comprehensive event tracking to measure experiment performance and user engagement. Track experiment exposures, user clicks, scroll depth, time on page, and send events to both Statsig and Google Analytics 4.

**Why This Matters:**
Without event tracking, we cannot measure experiment success or understand user behavior. Phase 3 provides the data foundation for data-driven decisions about which experiment variants to keep.

---

## Implementation Overview

### Phase 3 Module Architecture

Five new files in `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/tracking/`:

```
tracking/
├── eventLogger.js        - Core event logging (Statsig + GA4 bridge)
├── exposureLogger.js     - Log experiment exposures
├── clickTracker.js       - Automatic click tracking
├── engagementTracker.js  - Scroll depth + time on page
└── init.js              - Tracking initialization orchestrator
```

**Module Responsibilities:**

- **eventLogger.js**: Singleton for centralized event logging. Logs to Statsig via `client.logEvent()`, sends to GA4 via `gtag()` if enabled. Enriches events with common metadata (page, timestamp, user_id).

- **exposureLogger.js**: Tracks experiment exposures. Called from bootstrap.js when variant is applied. Prevents duplicate exposures per page. Sends to both Statsig and GA4.

- **clickTracker.js**: Event delegation on document.body for configured selectors `[data-track]`, `.md-button`, `a.md-social__link`. Extracts click metadata (element, text, href). Respects `enableAutoClick` flag.

- **engagementTracker.js**: Scroll depth tracking (25%, 50%, 75%, 100%) using IntersectionObserver. Time on page tracking (10s, 30s, 60s, 120s) using setTimeout. Resets state on page navigation. Respects `enableEngagement` flag.

- **init.js**: Reads config, waits for Statsig client, initializes enabled trackers, handles errors gracefully.

### Design Patterns

- **IIFE Pattern**: All modules use `(function() { ... })()` like existing code
- **Window Globals**: Expose via `window.StatsigTracker.ModuleName`
- **Singleton**: EventLogger maintains event history for deduplication
- **Observer**: Subscribe to `document$` for instant navigation
- **Graceful Degradation**: Try-catch wrapping, silent GA4 failures

---

## Integration with Bootstrap

**File to Modify:** `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/experiments/bootstrap.js`

**Integration Point 1** - Log exposures after applying variants (line ~106):

```javascript
// Apply the variant to the element
window.StatsigRenderer.applyExperiment(element, binding, value);

// NEW: Log exposure for this experiment
if (window.StatsigTracker?.ExposureLogger) {
  window.StatsigTracker.ExposureLogger.logExposure(
    binding.experiment,
    value,
    {
      experiment_key: key,
      experiment_category: binding.category,
      selector: binding.selector
    }
  );
}
```

**Integration Point 2** - Initialize tracking after bootstrap (line ~143, after `initializeExperiments()`):

```javascript
// Auto-initialize when this module loads
initializeExperiments();

// NEW: Initialize tracking system
if (window.StatsigTracker?.init) {
  window.StatsigTracker.init().catch(error => {
    console.error("[Statsig] Tracking initialization failed:", error);
  });
}
```

---

## Script Load Order

**File to Modify:** `/home/cooperm/analyticsbymark/projects/blog/mkdocs.yml`

Add tracking modules after bootstrap in `extra_javascript` section:

```yaml
extra_javascript:
  - "js/statsig/config/experiments.config.js"
  - "js/statsig/core/user.js"
  - "js/statsig/core/client.js"
  - "js/statsig/experiments/renderer.js"
  - "js/statsig/experiments/bootstrap.js"
  # NEW: Tracking modules
  - "js/statsig/tracking/eventLogger.js"
  - "js/statsig/tracking/exposureLogger.js"
  - "js/statsig/tracking/clickTracker.js"
  - "js/statsig/tracking/engagementTracker.js"
  - "js/statsig/tracking/init.js"
```

---

## Event Naming Convention

**Events sent to Statsig and GA4:**

```
Experiments:
- experiment_exposure          # When variant shown to user
- experiment_interaction       # Click on experiment element

Engagement:
- scroll_depth                # Milestones: 25%, 50%, 75%, 100%
- time_on_page                # Thresholds: 10s, 30s, 60s, 120s
- page_view                   # Page loaded/navigated

Navigation/Interaction:
- nav_click                   # Navigation link clicked
- cta_clicked                 # CTA button clicked
- social_share_clicked        # Social media link clicked
```

**Metadata Structure:**

Common fields (enriched automatically):
- `page_path`, `page_url`, `page_title`
- `timestamp`, `user_id`
- `viewport_width`, `viewport_height`

Exposure-specific:
- `experiment_name`, `variant`, `experiment_category`, `experiment_key`

Click-specific:
- `element_type`, `element_text`, `element_selector`, `link_url`, `data_track`

Engagement-specific:
- `scroll_percentage`, `time_seconds`

---

## Key Implementation Details

### 1. EventLogger Module (Core)

**Purpose:** Centralized event logging to Statsig + GA4

**Key Functions:**
- `logEvent(eventName, value, metadata)` - Main logging function
- `logToStatsig(...)` - Send to Statsig SDK
- `logToGA(...)` - Send to GA4 if enabled
- `enrichMetadata(...)` - Add common fields
- `shouldLogEvent(...)` - Check deduplication

**Error Handling:**
- Try-catch around GA4 calls (may be blocked)
- Silent failures for GA4, log errors for Statsig
- Graceful degradation if client unavailable

**Exposed API:** `window.StatsigTracker.EventLogger`

### 2. ExposureLogger Module

**Purpose:** Track experiment exposures

**Key Functions:**
- `logExposure(experimentName, variant, metadata)` - Log exposure event
- `hasLogged(key)` - Check if already logged (prevent duplicates)

**Deduplication Strategy:** Track by `experimentName + page_path` key

**Integration:** Called from bootstrap.js after applying variant

**Exposed API:** `window.StatsigTracker.ExposureLogger`

### 3. ClickTracker Module

**Purpose:** Automatic click tracking

**Implementation Strategy:**
- Event delegation on `document.body`
- Listen for clicks, check if target matches configured selectors
- Extract metadata from clicked element
- Handle instant navigation (already using delegation, no rebind needed)

**Selectors:** `[data-track]`, `.md-button`, `a.md-social__link`

**Exposed API:** `window.StatsigTracker.ClickTracker`

### 4. EngagementTracker Module

**Purpose:** Scroll depth and time on page tracking

**Scroll Depth Implementation:**
- Use `IntersectionObserver` for performance
- Create invisible marker divs at 25%, 50%, 75%, 100%
- Fire event once when marker intersects viewport
- Reset on page navigation

**Time on Page Implementation:**
- Use `setTimeout` for each threshold (10s, 30s, 60s, 120s)
- Check `document.visibilityState` to pause when tab hidden
- Clear timeouts on page navigation

**Exposed API:** `window.StatsigTracker.EngagementTracker`

### 5. Init Module (Orchestrator)

**Purpose:** Initialize tracking system

**Initialization Sequence:**
1. Read config from `window.EXPERIMENT_CONFIG.tracking`
2. Wait for Statsig client via `getExistingClient()`
3. Initialize EventLogger singleton
4. If `enableAutoClick`: Initialize ClickTracker
5. If `enableEngagement`: Initialize EngagementTracker
6. Subscribe to `document$` for instant navigation support
7. Add beforeunload listener to flush events

**Error Handling:** Continue if individual trackers fail

**Exposed API:** `window.StatsigTracker.init()`

---

## Google Analytics 4 Setup

### Custom Dimensions (Register in GA4 Admin UI)

Navigate to GA4 Property → Configure → Custom Definitions → Create custom dimensions:

| Dimension Name | Scope | Event Parameter | Description |
|---|---|---|---|
| Experiment Name | Event | experiment_name | Statsig experiment ID |
| Variant | Event | variant | Experiment variant value |
| Experiment Category | Event | experiment_category | Category (conversion, etc.) |
| Element Type | Event | element_type | Type of clicked element |
| Element Text | Event | element_text | Text content of element |
| Scroll Percentage | Event | scroll_percentage | Scroll depth % |
| Time Seconds | Event | time_seconds | Time on page in seconds |

**Note:** These are configured in GA4 UI, not in code. Code sends event parameters with these names.

### Event Prefix

All events sent to GA4 are prefixed per config (default: `statsig_`):
- `statsig_experiment_exposure`
- `statsig_scroll_depth`
- etc.

---

## Testing & Verification

### Manual Testing Checklist

**Setup:**
1. Set `loggingLevel: "debug"` in config for console logging
2. Open browser DevTools → Console + Network tabs
3. Filter network by "statsig" and "google-analytics"

**Test Cases:**

| Test | Action | Expected Result |
|------|--------|----------------|
| Exposure Logging | Load homepage | Console: "Logged exposure: hero_button_text"<br>Network: POST to Statsig API |
| Click Tracking | Click hero CTA | Console: "Tracked click: #hero-cta-dev"<br>Event: `experiment_interaction` |
| Scroll Depth | Scroll to 50% | Console: "Scroll depth: 50%"<br>Event: `scroll_depth` |
| Time on Page | Wait 30s | Console: "Time on page: 30s"<br>Event: `time_on_page` |
| GA4 Integration | Any event | Network: POST to google-analytics.com/g/collect |
| Instant Nav | Click internal link | New exposure logged, engagement resets |
| AdBlock Test | Enable AdBlock | Statsig succeeds, GA4 fails silently |
| Config Disabled | Set `enableAutoClick: false` | No click events logged |

### Verification in Statsig Console

1. Go to Statsig dashboard → Metrics → Events
2. Filter by event name (e.g., `experiment_exposure`)
3. Verify events appear with correct metadata
4. Check user_id matches stable ID from localStorage

### Verification in GA4 DebugView

1. GA4 Property → Configure → DebugView
2. Enable debug mode (`loggingLevel: "debug"` in config)
3. Perform actions on site
4. Verify prefixed events appear (e.g., `statsig_experiment_exposure`)
5. Check event parameters are captured correctly

---

## Success Criteria

Phase 3 is complete when:

- [ ] All 5 tracking modules created in `tracking/` directory
- [ ] Bootstrap.js modified with 2 integration points
- [ ] mkdocs.yml updated with 5 new script includes
- [ ] Events visible in Statsig console with correct metadata
- [ ] Events visible in GA4 DebugView (if enabled)
- [ ] Test checklist 100% passed
- [ ] Instant navigation preserves tracking functionality
- [ ] AdBlock doesn't break the site (GA4 fails silently)
- [ ] Debug logs show tracking lifecycle clearly
- [ ] No console errors in production mode (`loggingLevel: "none"`)
- [ ] Performance impact < 50ms per page load

---

## Implementation Sequence

**Recommended order:**

1. **eventLogger.js** (Core infrastructure, ~2 hours)
   - Create singleton with Statsig + GA4 logging
   - Implement metadata enrichment
   - Add debug logging
   - Test manually with browser console

2. **exposureLogger.js** (Exposure tracking, ~1 hour)
   - Create exposure logging function
   - Add deduplication logic
   - Test with existing hero CTA experiment

3. **Integrate with bootstrap.js** (Integration, ~1 hour)
   - Add exposure logging after variant application
   - Add tracking init call after bootstrap
   - Test end-to-end

4. **init.js** (Orchestrator, ~1 hour)
   - Create initialization function
   - Read config and initialize trackers
   - Handle errors gracefully
   - Test initialization sequence

5. **clickTracker.js** (Click tracking, ~2 hours)
   - Implement event delegation
   - Extract click metadata
   - Handle instant navigation
   - Test with various click targets

6. **engagementTracker.js** (Engagement, ~2-3 hours)
   - Implement scroll depth with IntersectionObserver
   - Implement time on page with setTimeout
   - Handle page navigation (reset state)
   - Test milestone logging

7. **Update mkdocs.yml** (Configuration, ~15 min)
   - Add 5 new script includes in correct order
   - Rebuild and verify load order

8. **Testing & Verification** (QA, ~2-3 hours)
   - Run full test checklist
   - Verify in Statsig console
   - Setup GA4 custom dimensions
   - Verify in GA4 DebugView
   - Test with AdBlock enabled
   - Performance profiling

**Total Estimated Time:** 12-15 hours

---

## Critical Files

### Files to Create (5 new files):

1. `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/tracking/eventLogger.js`
   - Core event logging engine
   - Statsig SDK `logEvent()` wrapper
   - GA4 `gtag()` integration
   - Metadata enrichment

2. `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/tracking/exposureLogger.js`
   - Experiment exposure logging
   - Deduplication logic
   - Called from bootstrap.js

3. `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/tracking/clickTracker.js`
   - Automatic click tracking
   - Event delegation pattern
   - Metadata extraction from DOM

4. `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/tracking/engagementTracker.js`
   - Scroll depth tracking (IntersectionObserver)
   - Time on page tracking (setTimeout)
   - State reset on navigation

5. `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/tracking/init.js`
   - Tracking system orchestrator
   - Config reading
   - Conditional initialization based on flags

### Files to Modify (2 files):

1. `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/experiments/bootstrap.js`
   - Add exposure logging call (line ~106)
   - Add tracking init call (line ~143)

2. `/home/cooperm/analyticsbymark/projects/blog/mkdocs.yml`
   - Add 5 tracking scripts to `extra_javascript` (lines ~121-125)

---

## Risk Mitigation

**Risks:**

1. **Statsig client not loaded** → Check existence, provide no-op fallbacks
2. **GA4 blocked by AdBlock** → Wrap in try-catch, fail silently
3. **Performance impact** → Use efficient APIs (IntersectionObserver), batch events
4. **Event duplication** → Track event history, check before logging
5. **Instant nav breaks tracking** → Subscribe to document$, reset state properly

**Rollback Plan:**

If issues arise:
1. Set all tracking flags to `false` in config (immediate mitigation)
2. Remove tracking scripts from mkdocs.yml (5 minutes)
3. Revert bootstrap.js changes (5 minutes)
4. Site returns to Phase 2 state (experiments still work)

---

## Configuration Example

**Enable tracking in production:**

```javascript
tracking: {
  enableAutoClick: true,
  enableEngagement: true,
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
    enabled: true,
    sendExposures: true,
    sendCustomEvents: true,
    prefix: "statsig_"
  }
}
```

**Disable tracking in development:**

```javascript
tracking: {
  enableAutoClick: false,   // Disabled in development
  enableEngagement: false,  // Disabled in development
  googleAnalytics: {
    enabled: false          // Don't pollute GA4 with dev traffic
  }
}
```

This completes the Phase 3 implementation plan for event tracking.
  // Metadata
  _meta: {
    environment: "production",
    version: "1.2.0",
    lastUpdated: "2026-02-06T10:00:00Z"
  },

  // Client configuration
  client: {
    apiKey: "client-xxxxx",
    options: {
      environment: { tier: "production" },
      loggingLevel: "none"
    }
  },

  // Feature flags (gates)
  featureFlags: {
    enable_social_share: {
      flagName: "blog_social_share_enabled",
      defaultValue: false
    }
  },

  // Experiments organized by domain
  experiments: {
    navigation: {
      sticky_tabs: {
        selector: "body",
        experiment: "blog_nav_sticky_tabs",
        param: "enabled",
        type: "class",
        className: "md-tabs--sticky",
        category: "navigation",
        pages: ["*"],
        priority: "high"
      }
    },

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

    blog: {
      pagination_count: {
        selector: "[data-exp='pagination']",
        experiment: "blog_pagination_count",
        param: "count",
        type: "attr",
        attr: "data-pagination-count",
        category: "blog-layout",
        pages: ["blog/index.html"]
      }
    }
  },

  // Event tracking configuration
  tracking: {
    enableAutoClick: true,
    enableEngagement: true,
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
      enabled: true,
      sendExposures: true,
      sendCustomEvents: true,
      prefix: "statsig_"
    }
  }
};
```

### Multi-Environment Configuration

**GitHub Secrets Strategy:**

```
EXPERIMENT_CONFIG_JSON_BLOG_PROD      # Production blog config
EXPERIMENT_CONFIG_JSON_BLOG_STAGING   # Staging blog config
EXPERIMENT_CONFIG_JSON_DEV_PROD       # Production dev site config
EXPERIMENT_CONFIG_JSON_DEV_STAGING    # Staging dev site config
```

**Enhanced GitHub Actions Workflow:**

```yaml
- name: Write experiment configs
  env:
    EXPERIMENT_CONFIG_JSON_BLOG: ${{ secrets.EXPERIMENT_CONFIG_JSON_BLOG_PROD }}
    EXPERIMENT_CONFIG_JSON_DEV: ${{ secrets.EXPERIMENT_CONFIG_JSON_DEV_PROD }}
  run: |
    node - <<'NODE'
    const fs = require("fs");
    const path = require("path");

    function validateConfig(obj) {
      if (!obj.client?.apiKey) throw new Error("Missing client.apiKey");
      if (!obj.experiments) throw new Error("Missing experiments");
      return true;
    }

    function write(outPath, raw) {
      if (!raw || !raw.trim()) return;
      const obj = JSON.parse(raw);
      validateConfig(obj);  // Add validation!
      fs.mkdirSync(path.dirname(outPath), { recursive: true });
      fs.writeFileSync(
        outPath,
        `window.EXPERIMENT_CONFIG = ${JSON.stringify(obj, null, 2)};\n`
      );
      console.log("Wrote", outPath);
    }

    write("projects/blog/docs/js/statsig/config/experiments.config.js", process.env.EXPERIMENT_CONFIG_JSON_BLOG);
    write("projects/dev/docs/js/statsig/config/experiments.config.js", process.env.EXPERIMENT_CONFIG_JSON_DEV);
    NODE
```

---

## 3. Event Tracking Architecture

### Core Components

**Event Tracking Core (`tracking/events.js`):**

```javascript
export class StatsigEventTracker {
  constructor(client, config) {
    this.client = client;
    this.config = config;
  }

  logEvent(eventName, value = null, metadata = {}) {
    const enrichedMetadata = {
      ...metadata,
      timestamp: Date.now(),
      page: window.location.pathname,
      referrer: document.referrer
    };

    this.client.logEvent(eventName, value, enrichedMetadata);

    // Also send to GA if configured
    if (this.config.googleAnalytics?.enabled) {
      this.sendToGoogleAnalytics(eventName, value, enrichedMetadata);
    }
  }

  trackExposure(experimentName, variantName) {
    this.logEvent('experiment_exposure', variantName, {
      experiment: experimentName
    });
  }

  trackClick(element, eventName) {
    this.logEvent(eventName || 'click', null, {
      element_id: element.id,
      element_class: element.className,
      element_text: element.textContent?.slice(0, 50)
    });
  }
}
```

**Automatic Click Tracking (`tracking/click-tracker.js`):**

- Use event delegation for performance
- Track clicks on `[data-track]` elements
- Track experiment element interactions
- Track CTA button clicks

**Engagement Tracking (`tracking/engagement-tracker.js`):**

- Scroll depth: 25%, 50%, 75%, 100%
- Time on page: 10s, 30s, 60s, 120s
- Page views and exits
- Navigation interactions

### Event Naming Convention

**Standard event names:**

```
Experiments:
- experiment_exposure          # Automatic when variant assigned
- experiment_interaction       # Click/interaction with experiment element

Engagement:
- scroll_depth                # Scroll milestones
- time_on_page                # Time milestones
- page_view                   # Page loads
- page_exit                   # User leaves

Navigation:
- nav_click                   # Navigation clicks
- search_performed            # Search queries
- back_to_top_clicked         # Back to top button

Content:
- blog_post_viewed            # Blog post loads
- code_snippet_copied         # Code copying
- external_link_clicked       # External links
- social_share_clicked        # Share buttons

Conversion:
- cta_clicked                 # CTA button clicks
- newsletter_subscribed       # Newsletter signups
```

---

## 4. Google Analytics Integration

### Integration Strategy: Parallel Tracking (Recommended)

**Why parallel tracking:**
- Statsig logs all events (source of truth for experiments)
- Selected events also sent to Google Analytics
- GA receives experiment data as custom dimensions
- Enables analysis in both platforms

**Implementation (`tracking/analytics-bridge.js`):**

```javascript
export class GoogleAnalyticsBridge {
  sendExposure(experimentName, variantName) {
    if (!this.enabled) return;

    gtag('event', 'experiment_exposure', {
      event_category: 'experiment',
      event_label: experimentName,
      experiment_name: experimentName,
      variant_name: variantName,
      non_interaction: true
    });

    // Set as user property for segmentation
    gtag('set', 'user_properties', {
      [`exp_${experimentName}`]: variantName
    });
  }

  sendEvent(eventName, value, metadata) {
    gtag('event', this.config.prefix + eventName, {
      event_category: metadata.category || 'statsig',
      event_label: metadata.label || metadata.page,
      value: value
    });
  }
}
```

**GA4 Custom Dimensions Setup:**

Create these event-scoped dimensions:
1. `experiment_name`
2. `variant_name`

Create user-scoped dimensions for active experiments:
- `exp_blog_pagination_count`
- `exp_blog_nav_sticky_tabs`
- etc.

This allows segmenting all analytics by experiment variant.

---

## 5. Feature Flags vs Experiments

### Decision Framework

**Use Feature Flags when:**
- Gradual rollouts (10% → 50% → 100%)
- Kill switches for broken features
- Ops toggles for expensive features
- Permission-based access (beta features)
- Concluded A/B tests (winner becomes flag)

**Use Experiments when:**
- A/B/n tests requiring statistical significance
- Multivariate testing
- Personalization experiments
- UX optimization with metrics
- Feature comparisons

### Hybrid Approach for Major Features

1. Launch behind feature flag (10% rollout)
2. Within flag, run A/B experiment
3. After winner determined, keep flag for gradual 100% rollout
4. Remove flag once stable, make winner default

---

## 6. Development & Testing Workflow

### Local Development

**Step 1: Generate local config**

```bash
node scripts/testing/generate-local-config.mjs
```

Creates config with:
- All experiments enabled
- Verbose logging enabled
- Tracking disabled (don't pollute production data)

**Step 2: Test with variant overrides**

Add URL parameter support:

```
http://localhost:8000/?exp_blog_pagination_count=10
http://localhost:8000/?exp_hero_button_text=control&exp_sticky_tabs=enabled
```

**Step 3: Use test-specific user ID**

Local development uses `local-test-user-{random}` instead of production stable ID.

### Testing Checklist

Before deploying new experiment:

- [ ] Config validation passes
- [ ] Both variants tested locally
- [ ] No content flicker (anti-flicker works)
- [ ] Mobile viewport testing
- [ ] Instant navigation works
- [ ] Events tracked correctly
- [ ] GA integration verified (DebugView)
- [ ] Fallback behavior works (simulate Statsig failure)
- [ ] Performance impact measured
- [ ] Staging verification complete

---

## 7. Identified Testing Opportunities

Based on codebase exploration, here are the highest-impact experiments to implement:

### Tier 1: High Impact (Implement First)

1. **Hero CTA Button Text** ✅ (already running)
   - Current: "Start the blog tutorial"
   - Test variants: Different action-oriented copy

2. **Blog Pagination Count**
   - Current: 5 posts per page
   - Test: 3 vs 5 vs 10 posts per page
   - Metric: Engagement, bounce rate

3. **Navigation Tabs Stickiness**
   - Current: `navigation.tabs.sticky` enabled
   - Test: Sticky vs non-sticky
   - Metric: Navigation interactions, scroll depth

4. **Social Share Button Placement**
   - Current: End of post
   - Test: End vs sticky sidebar vs both
   - Metric: Share click rate

5. **Category Filter UI**
   - Current: Default Material theme style
   - Test: Buttons vs dropdown vs tabs
   - Metric: Category navigation clicks

### Tier 2: Medium Impact

6. **Search Placeholder Text**
   - Test different prompts to encourage usage
   - Metric: Search usage rate

7. **TOC Visibility**
   - Test auto-show vs auto-hide for blog posts
   - Metric: Time on page, scroll depth

8. **Primary Color Scheme**
   - Current: Light `#384D48`, Dark `#5C8076`
   - Test: Different brand colors
   - Metric: Time on site, subjective feedback

9. **Dark Mode Default**
   - Test: Auto vs light default vs dark default
   - Metric: Theme toggle rate, preference signals

10. **Blog Post Metadata Display**
    - Test: Show/hide read time, dates
    - Metric: Post completion rate

---

## 8. Performance Optimization

### Performance Budgets

- **Bundle size:** < 70KB gzipped total
- **Initialization time:** < 500ms (client ready)
- **Time to interactive:** < 1000ms (experiments applied)
- **Flicker rate:** 0% (no visible flicker)
- **Error rate:** < 0.1%

### Optimization Strategies

1. **Lazy loading** - Load experiment modules by page type
2. **Critical path inlining** - Inline hero CTA experiment
3. **Aggressive caching** - 24-hour cache for stable experiments
4. **Priority-based rendering** - Apply critical experiments first
5. **Bundle size management** - Modular imports, tree-shaking

### Performance Monitoring

Track metrics via Statsig events:

```javascript
client.logEvent('statsig_performance', null, {
  init_time: Math.round(initTime),
  apply_time: Math.round(applyTime),
  total_time: Math.round(totalTime)
});
```

---

## 9. Error Handling & Fallback Strategy

### Layered Error Handling

**Level 1: Client initialization failure**
- Return mock client that returns defaults
- Log error event to monitoring
- Site continues working normally

**Level 2: Network timeout**
- 3-second timeout on initialization
- Fall back to cached values or defaults
- No user-facing errors

**Level 3: Experiment application errors**
- Catch errors during DOM manipulation
- Reveal element with default content
- Log error event for monitoring

### Graceful Degradation Principles

1. **Default content in DOM** - Always render default variant
2. **Progressive enhancement** - Experiments enhance, never break
3. **Fail open** - On any error, show default
4. **Silent failures** - Don't show error UI to users
5. **No blocking** - Experiments never block page render

### Fallback Hierarchy

```
1. Cached experiment value (localStorage, 6-24 hour TTL)
   ↓
2. Statsig server response (network call)
   ↓
3. Experiment default value (from config)
   ↓
4. DOM default content (already rendered)
```

---

## 10. Implementation Phases

### Phase 1: Core Infrastructure Refactoring (Week 1)

**Goal:** Modularize existing code without changing behavior

**Tasks:**
1. Create new directory structure `docs/js/statsig/`
2. Refactor `sidecar-bootstrap.js` into modules:
   - `core/client.js` - Extract client initialization
   - `core/user.js` - Extract stable ID management
   - `core/cache.js` - Extract caching logic
   - `experiments/renderer.js` - Extract DOM manipulation
   - `experiments/bootstrap.js` - Main orchestrator
3. Update `mkdocs.yml` to reference new bootstrap path
4. Test locally - verify existing experiment works identically
5. Deploy to staging for verification

**Success Criteria:**
- Hero CTA experiment works identically to before
- No regressions in behavior
- Clean modular code structure

**Files to Modify:**
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/sidecar-bootstrap.js` → refactor into modules
- `/home/cooperm/analyticsbymark/projects/blog/mkdocs.yml` → update `extra_javascript` paths

---

### Phase 2: Enhanced Configuration System (Week 2)

**Goal:** Scale configuration to support 10+ experiments

**Tasks:**
1. Design enhanced config structure (documented above)
2. Create validation script: `scripts/experiments/validate-config.mjs`
3. Update GitHub Actions workflow to:
   - Write to new config path
   - Add validation step (fail build if invalid)
   - Support multi-environment (prod/staging)
4. Convert current simple config to new structured format
5. Update bootstrap.js to consume new config structure
6. Add feature flag infrastructure (no active flags yet)
7. Create local dev config generator
8. Test entire workflow: local → staging → production

**Success Criteria:**
- Config validated in CI/CD
- Experiment works with new config format
- Local development workflow functional
- Staging environment separated from production

**Files to Modify:**
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/experiments.config.js` → new structure
- `/home/cooperm/analyticsbymark/.github/workflows/build.yml` → enhanced with validation
- Create `/home/cooperm/analyticsbymark/scripts/experiments/validate-config.mjs`
- Update bootstrap to read new config structure

---

### Phase 3: Event Tracking Implementation (Week 2-3)

**Goal:** Track experiment exposures and user engagement

**Tasks:**
1. Implement event tracking core: `tracking/events.js`
2. Implement Google Analytics bridge: `tracking/analytics-bridge.js`
3. Add automatic click tracking: `tracking/click-tracker.js`
4. Add engagement tracking: `tracking/engagement-tracker.js`
5. Update bootstrap to initialize tracking system
6. Add `data-track` attributes to key elements
7. Deploy to staging, verify events in Statsig console
8. Configure GA4 custom dimensions
9. Verify events appear in GA4 DebugView
10. Monitor for 1 week, validate data quality

**Success Criteria:**
- Experiment exposures tracked 100% of the time
- Click events captured for key elements
- Engagement metrics (scroll, time) tracked
- Events visible in both Statsig and GA4
- Data quality validated (no duplicates, correct metadata)

**Files to Create:**
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/tracking/events.js`
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/tracking/analytics-bridge.js`
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/tracking/click-tracker.js`
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/tracking/engagement-tracker.js`

**Files to Modify:**
- Bootstrap to initialize tracking
- GA4 configuration to add custom dimensions

---

### Phase 4: Add 5 New Experiments (Week 3-4)

**Goal:** Scale to 6 total experiments (1 existing + 5 new)

**Priority experiments to add:**

1. **Blog Pagination Count** (blog-layout)
   - Selector: `[data-exp="pagination"]`
   - Variants: 3, 5, 10 posts per page
   - Metric: Engagement rate

2. **Navigation Sticky Tabs** (navigation)
   - Selector: `body`
   - Variants: With/without sticky tabs
   - Metric: Navigation click rate

3. **Social Share Button Style** (visual)
   - Selector: `.blog-social-share`
   - Variants: Icon only vs icon + text
   - Metric: Share click rate

4. **Category Filter UI** (blog-layout)
   - Selector: `[data-exp="category-filter"]`
   - Variants: Buttons vs dropdown
   - Metric: Category navigation rate

5. **TOC Visibility** (content)
   - Selector: `.md-sidebar--secondary`
   - Variants: Auto-show vs auto-hide
   - Metric: Time on page, scroll depth

**Tasks:**
1. Create experiment-specific modules:
   - `experiments/navigation.js`
   - `experiments/blog-layout.js`
   - `experiments/visual.js`
   - `experiments/content.js`
2. Add 5 new experiments to Statsig console
3. Update config with new experiments (organized by category)
4. Add `data-exp` attributes to target elements in markdown/HTML
5. Add `data-hidden` to prevent flicker
6. Test locally with URL parameter overrides
7. Deploy to staging for verification
8. Monitor for issues, validate experiments apply correctly
9. Production deploy after 1 week of staging validation

**Success Criteria:**
- 6 experiments running simultaneously
- No performance degradation
- No flicker or UI issues
- Events tracked for all experiments
- Each experiment has clear success metrics

**Files to Create:**
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/experiments/navigation.js`
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/experiments/blog-layout.js`
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/experiments/visual.js`
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/experiments/content.js`

**Files to Modify:**
- Config to add 5 new experiments
- Markdown files to add `data-exp` and `data-hidden` attributes
- Bootstrap to import new experiment modules

---

### Phase 5: Performance Optimization (Week 4)

**Goal:** Meet performance budgets at scale

**Tasks:**
1. Implement performance monitoring: `utils/performance.js`
2. Add lazy loading for experiment modules by page type
3. Optimize config size (evaluate compression trade-offs)
4. Implement critical experiment inlining for hero CTA
5. Add performance budgets to CI/CD (fail if exceeded)
6. Load test with all experiments enabled
7. Measure and optimize initialization time
8. Verify anti-flicker still works (0% flicker rate)

**Success Criteria:**
- Bundle size < 70KB gzipped
- Initialization time < 500ms (p95)
- Time to interactive < 1000ms (p95)
- No performance regression vs baseline
- Performance budgets enforced in CI

**Files to Create:**
- `/home/cooperm/analyticsbymark/projects/blog/docs/js/statsig/utils/performance.js`

**Files to Modify:**
- Bootstrap to add lazy loading and performance monitoring
- CI/CD to add performance budget checks

---

### Phase 6: Documentation & Training (Week 5)

**Goal:** Enable team to add experiments independently

**Tasks:**
1. Write internal documentation:
   - `docs-internal/experimentation/01-adding-experiments.md`
   - `docs-internal/experimentation/02-event-tracking.md`
   - `docs-internal/experimentation/03-testing-workflow.md`
   - `docs-internal/experimentation/04-feature-flags.md`
   - `docs-internal/experimentation/05-troubleshooting.md`
2. Create architecture overview: `docs-internal/architecture/statsig-setup.md`
3. Create video walkthrough (optional but helpful)
4. Document GA4 analysis workflow
5. Create runbook for common issues
6. Conduct training session with team

**Success Criteria:**
- Team member can add new experiment without assistance
- All common issues documented with solutions
- GA4 analysis workflow clear
- Video walkthrough available for onboarding

**Files to Create:**
- `/home/cooperm/analyticsbymark/docs-internal/experimentation/01-adding-experiments.md`
- `/home/cooperm/analyticsbymark/docs-internal/experimentation/02-event-tracking.md`
- `/home/cooperm/analyticsbymark/docs-internal/experimentation/03-testing-workflow.md`
- `/home/cooperm/analyticsbymark/docs-internal/experimentation/04-feature-flags.md`
- `/home/cooperm/analyticsbymark/docs-internal/experimentation/05-troubleshooting.md`
- `/home/cooperm/analyticsbymark/docs-internal/architecture/statsig-setup.md`

---

### Phase 7: Production Rollout & Monitoring (Week 6)

**Goal:** Deploy to production with confidence

**Tasks:**
1. Final staging verification (all experiments, tracking, performance)
2. Update production GitHub secrets with new config format
3. Deploy to production (`master` → `gh-pages-prod`)
4. Monitor key metrics for 24 hours:
   - Error rate < 0.1%
   - Performance within budgets
   - Events tracking correctly
   - No user complaints
5. Verify all experiments applying correctly
6. Verify GA4 integration working in production
7. Set up alerts in Statsig console:
   - Client initialization failures > 1%
   - Experiment application errors > 0.5%
   - Average initialization time > 1 second
8. Document rollback procedure
9. Celebrate! 🎉

**Success Criteria:**
- Production site stable with new setup
- All metrics within acceptable ranges
- No user-facing issues reported
- Team confident in new system
- Ready to scale to 10+ experiments

**Files to Modify:**
- GitHub secrets (update production config)
- Statsig console (create alerts)

---

## 11. Risk Mitigation

### Key Risks & Mitigation

**Risk 1: Breaking existing experiment during migration**
- **Likelihood:** Medium
- **Impact:** High (broken hero CTA)
- **Mitigation:** Phase 1 is pure refactoring with no behavior change. Extensive testing before each deploy.
- **Rollback:** Keep old `sidecar-bootstrap.js` available, can revert in minutes

**Risk 2: Performance degradation with multiple experiments**
- **Likelihood:** Medium
- **Impact:** Medium (slower page loads)
- **Mitigation:** Performance budgets, lazy loading, monitoring. Load testing before production.
- **Rollback:** Feature flag to disable non-critical experiments

**Risk 3: Event tracking errors polluting analytics**
- **Likelihood:** Low
- **Impact:** Medium (bad data)
- **Mitigation:** Staging environment with separate data. Validate in GA4 DebugView first.
- **Rollback:** Feature flag to disable tracking

**Risk 4: Configuration errors breaking site**
- **Likelihood:** Low
- **Impact:** High (site broken)
- **Mitigation:** Config validation in CI/CD that fails build if invalid. Multiple rounds of testing.
- **Rollback:** GitHub Actions can re-run with previous config secret

**Risk 5: Statsig service downtime**
- **Likelihood:** Very Low
- **Impact:** Low (graceful degradation)
- **Mitigation:** Comprehensive fallback strategy, caching, graceful degradation to defaults.
- **Impact Assessment:** Site works normally with default variants

---

## 12. Success Metrics

### Implementation Success (End of Phase 7)

**Functionality:**
- ✅ 6+ experiments running simultaneously
- ✅ No flicker observed (0% flicker rate)
- ✅ Events tracking correctly in Statsig
- ✅ Events appearing in GA4 with correct dimensions
- ✅ Feature flag infrastructure ready (even if no flags yet)

**Performance:**
- ✅ Page load time < baseline + 200ms
- ✅ Time to interactive < baseline + 300ms
- ✅ Bundle size < 70KB gzipped
- ✅ Initialization time < 500ms (p95)

**Developer Experience:**
- ✅ New team member can add experiment in < 30 minutes
- ✅ Local testing workflow functional and documented
- ✅ Clear error messages when something wrong
- ✅ No manual coordination needed for deployments

**Data Quality:**
- ✅ < 0.1% experiment errors
- ✅ > 99% exposure tracking coverage
- ✅ Event data matches expected volumes
- ✅ GA4 and Statsig data reconcile

### Business Impact (Ongoing)

Track these post-implementation:

**Experimentation Velocity:**
- Number of experiments launched per month
- Time from idea to running experiment
- Experiment iteration rate

**Wins from Experiments:**
- Conversion rate improvements from CTA tests
- Engagement improvements from layout tests
- User satisfaction from UX improvements

**Platform Stability:**
- Zero experiment-related incidents
- No user complaints about experimental features
- Consistent performance across all experiments

---

## 13. Critical Files Reference

### Files to Modify

1. **`/home/cooperm/analyticsbymark/projects/blog/docs/js/sidecar-bootstrap.js`**
   - Current: Monolithic bootstrap script (196 lines)
   - Action: Refactor into modular architecture
   - Phase: 1

2. **`/home/cooperm/analyticsbymark/projects/blog/docs/js/experiments.config.js`**
   - Current: Simple config with 1 experiment
   - Action: Transform to categorized, structured config
   - Phase: 2

3. **`/home/cooperm/analyticsbymark/projects/blog/mkdocs.yml`**
   - Current: References `js/sidecar-bootstrap.js`
   - Action: Update paths to new module structure
   - Phase: 1, 2

4. **`/home/cooperm/analyticsbymark/.github/workflows/build.yml`**
   - Current: Basic config injection
   - Action: Add validation, multi-environment support
   - Phase: 2

5. **`/home/cooperm/analyticsbymark/projects/blog/overrides/partials/integrations/analytics.html`**
   - Current: Loads Statsig CDN only
   - Action: May need updates for GA4 custom dimensions
   - Phase: 3

6. **`/home/cooperm/analyticsbymark/projects/blog/docs/assets/extra.css`**
   - Current: Has `[data-hidden]` anti-flicker CSS
   - Action: Verify styles, may need tweaks
   - Phase: 1

### Files to Create

**Phase 1:**
- `docs/js/statsig/core/client.js`
- `docs/js/statsig/core/user.js`
- `docs/js/statsig/core/cache.js`
- `docs/js/statsig/experiments/bootstrap.js`
- `docs/js/statsig/experiments/renderer.js`

**Phase 2:**
- `docs/js/statsig/config/experiments.config.template.js`
- `scripts/experiments/validate-config.mjs`
- `scripts/testing/generate-local-config.mjs`

**Phase 3:**
- `docs/js/statsig/tracking/events.js`
- `docs/js/statsig/tracking/analytics-bridge.js`
- `docs/js/statsig/tracking/click-tracker.js`
- `docs/js/statsig/tracking/engagement-tracker.js`

**Phase 4:**
- `docs/js/statsig/experiments/navigation.js`
- `docs/js/statsig/experiments/blog-layout.js`
- `docs/js/statsig/experiments/visual.js`
- `docs/js/statsig/experiments/content.js`

**Phase 5:**
- `docs/js/statsig/utils/performance.js`
- `docs/js/statsig/utils/error-handler.js`
- `docs/js/statsig/utils/logger.js`

**Phase 6:**
- `docs-internal/experimentation/01-adding-experiments.md`
- `docs-internal/experimentation/02-event-tracking.md`
- `docs-internal/experimentation/03-testing-workflow.md`
- `docs-internal/experimentation/04-feature-flags.md`
- `docs-internal/experimentation/05-troubleshooting.md`
- `docs-internal/architecture/statsig-setup.md`

---

## 14. Next Steps After Plan Approval

Once this plan is approved, we'll proceed in phases:

**Immediate actions (Phase 1):**
1. Create new directory structure
2. Refactor existing bootstrap into modules
3. Verify existing experiment still works
4. Deploy to staging

**Week 1 deliverables:**
- Modular code architecture
- No change in user-facing behavior
- Foundation for scaling

**Questions to align on before starting:**
1. Do you want to implement all 6 phases, or prioritize certain phases?
2. Should we start with Phase 1 immediately, or review the plan first?
3. Are there specific experiments you want prioritized in Phase 4?
4. Do you have GA4 property access for setting up custom dimensions?
5. Should we create the staging environment (develop → gh-pages-uat) first?

Let me know when you're ready to proceed! 🚀
