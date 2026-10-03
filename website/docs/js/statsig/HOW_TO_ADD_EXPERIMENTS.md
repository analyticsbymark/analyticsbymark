# How to Add New A/B Tests - Step-by-Step Guide

This guide walks you through adding new experiments using the Statsig experimentation system.

---

## Overview: The 5-Step Process

```
1. Create Experiment in Statsig Console
   ↓
2. Configure in experiments.config.js
   ↓
3. Prepare DOM Elements
   ↓
4. Test Locally
   ↓
5. Deploy & Monitor
```

---

## Step 1: Create Experiment in Statsig Console

### 1.1 Log into Statsig
Go to https://console.statsig.com and log into your project.

### 1.2 Create New Experiment

**Navigate:** Experiments → Create New Experiment

**Settings:**
- **Name:** Use descriptive, snake_case naming (e.g., `blog_hero_cta_text`)
- **Type:** Select "Experiment" (not "Feature Flag")
- **Allocation:** Start with 50/50 split between variants

### 1.3 Define Parameters

Parameters are the values that change between variants.

**Example: Text Change Experiment**
```yaml
Parameter Name: button_label
Type: String

Variants:
  - Control: "Read the Tutorial"
  - Treatment: "Start Learning Now"
```

**Example: Layout Experiment**
```yaml
Parameter Name: layout_style
Type: String

Variants:
  - Control: "grid"
  - Treatment: "list"
```

**Example: Number Experiment**
```yaml
Parameter Name: posts_per_page
Type: Number

Variants:
  - Control: 5
  - Treatment_A: 10
  - Treatment_B: 3
```

### 1.4 Set Success Metrics

Define what success looks like:
- Primary: Click-through rate, conversion rate, etc.
- Secondary: Time on page, scroll depth, bounce rate

### 1.5 Start Experiment

Keep it at 0% allocation initially. You'll ramp up after testing.

---

## Step 2: Configure in Code

### 2.1 Identify Experiment Category

Choose the appropriate category:
- `cta` - Call-to-action buttons and conversion elements
- `navigation` - Navigation bars, menus, tabs
- `blog` - Blog-specific layouts and features
- `visual` - Colors, themes, visual styling
- `content` - Content display and organization

### 2.2 Add to Config Template

Edit: `projects/blog/docs/js/statsig/config/experiments.config.template.js`

```javascript
experiments: {
  cta: {
    // Existing experiments...

    // NEW EXPERIMENT
    hero_cta_style: {
      selector: "#hero-cta-btn",           // CSS selector for target element
      experiment: "blog_hero_cta_style",   // Statsig experiment name
      param: "button_style",               // Parameter name from Statsig
      type: "class",                       // Type of change (see types below)
      className: "md-button--primary",     // For type: "class"
      category: "conversion",              // Category for analytics
      pages: ["index.html"],               // Pages where this runs
      priority: "critical"                 // Priority level
    }
  }
}
```

### 2.3 Experiment Configuration Options

#### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `selector` | CSS selector for target element | `"#hero-cta"` |
| `experiment` | Statsig experiment name | `"blog_hero_cta_text"` |
| `param` | Parameter name from Statsig | `"button_label"` |
| `type` | Type of DOM manipulation | `"text"` |
| `category` | Analytics category | `"conversion"` |
| `pages` | Pages where experiment runs | `["index.html"]` or `["*"]` |
| `priority` | Importance level | `"critical"` |

#### Experiment Types

**1. Text Changes** (`type: "text"`)
```javascript
{
  selector: "#hero-heading",
  experiment: "blog_hero_heading_text",
  param: "heading_text",
  type: "text",
  category: "conversion",
  pages: ["index.html"],
  priority: "high"
}
```

**2. CSS Class Changes** (`type: "class"`)
```javascript
{
  selector: "body",
  experiment: "blog_sticky_nav",
  param: "enabled",
  type: "class",
  className: "md-tabs--sticky",  // Class to add if param is truthy
  category: "navigation",
  pages: ["*"],
  priority: "medium"
}
```

**3. Attribute Changes** (`type: "attr"`)
```javascript
{
  selector: "[data-exp='pagination']",
  experiment: "blog_pagination_count",
  param: "count",
  type: "attr",
  attr: "data-pagination-count",  // Attribute to set
  category: "blog-layout",
  pages: ["blog/index.html"],
  priority: "low"
}
```

**4. HTML Changes** (`type: "html"`)
```javascript
{
  selector: ".blog-sidebar",
  experiment: "blog_sidebar_content",
  param: "html_content",
  type: "html",
  category: "content",
  pages: ["blog/*.html"],
  priority: "medium"
}
```

**5. Style Changes** (`type: "style"`)
```javascript
{
  selector: ".blog-card",
  experiment: "blog_card_layout",
  param: "layout_style",
  type: "style",
  styleProperty: "display",  // CSS property to change
  category: "visual",
  pages: ["blog/index.html"],
  priority: "low"
}
```

#### Optional Fields

| Field | Description | Example |
|-------|-------------|---------|
| `fallback` | Default value if Statsig fails | `"Click Here"` |
| `className` | Class to add (for type: "class") | `"md-button--primary"` |
| `attr` | Attribute name (for type: "attr") | `"data-count"` |
| `styleProperty` | CSS property (for type: "style") | `"background-color"` |

### 2.4 Update Production Config

In your GitHub Secrets, update `EXPERIMENT_CONFIG_JSON_BLOG_PROD` to include the new experiment.

**Format (JSON):**
```json
{
  "experiments": {
    "cta": {
      "hero_cta_style": {
        "selector": "#hero-cta-btn",
        "experiment": "blog_hero_cta_style",
        "param": "button_style",
        "type": "class",
        "className": "md-button--primary",
        "category": "conversion",
        "pages": ["index.html"],
        "priority": "critical"
      }
    }
  }
}
```

---

## Step 3: Prepare DOM Elements

### 3.1 Add Target Element

Make sure your HTML has an element matching the selector.

**Example: Text Experiment**
```html
<!-- Add unique ID for targeting -->
<a href="/tutorial" id="hero-cta-btn" class="md-button" data-hidden>
  Read the Tutorial
</a>
```

### 3.2 Add Anti-Flicker Attribute

**Critical:** Add `data-hidden` to prevent content flash before variant loads.

```html
<div id="experiment-target" data-hidden>
  Default content here
</div>
```

The CSS will hide this until the experiment loads:
```css
[data-hidden] {
  visibility: hidden !important;
}
```

### 3.3 Add Tracking Attributes (Optional)

For custom click tracking:
```html
<button id="hero-cta" data-track="custom_event_name" data-exp-key="hero_cta_text">
  Click Me
</button>
```

**Attributes:**
- `data-track` - Custom event name for tracking
- `data-exp-key` - Links click to experiment for `experiment_interaction` events

### 3.4 Page-Specific Experiments

Use the `pages` array to control where experiments run:

```javascript
// Run only on homepage
pages: ["index.html"]

// Run on all blog posts
pages: ["blog/*.html"]

// Run everywhere
pages: ["*"]

// Run on specific pages
pages: ["index.html", "about.html", "blog/tutorial-1.html"]
```

---

## Step 4: Test Locally

### 4.1 Enable Debug Logging

In your local `experiments.config.js`:

```javascript
client: {
  options: {
    loggingLevel: "debug"  // Enable verbose logging
  }
}
```

### 4.2 Start Local Server

```bash
cd projects/blog
source ../../.venv/bin/activate
mkdocs serve
```

### 4.3 Test in Browser

1. **Open:** http://127.0.0.1:8000/
2. **Open DevTools:** Press F12 → Console tab

**Expected Console Output:**
```
[Statsig] Config loaded: {...}
[Statsig] Client initialized
[Statsig Renderer] Pre-hiding experiment elements
[Statsig Renderer] Applied experiment: hero_cta_text = "Start Learning Now"
[Statsig ExposureLogger] Logged exposure: blog_hero_cta_text = "Start Learning Now"
[Statsig EventLogger] Logged event: experiment_exposure
```

### 4.4 Test Both Variants

**Option 1: URL Override**
```
http://127.0.0.1:8000/?exp_blog_hero_cta_text=control
http://127.0.0.1:8000/?exp_blog_hero_cta_text=treatment
```

**Option 2: Force in Statsig Console**
Go to Statsig Console → Experiments → Your Experiment → Overrides → Add your user ID

**Option 3: Clear localStorage**
```javascript
// In browser console
localStorage.clear();
location.reload();
```

### 4.5 Test Tracking Events

**Check exposure logging:**
- Should see `experiment_exposure` event when page loads

**Check click tracking:**
- Click the experiment element
- Should see `experiment_interaction` event with experiment metadata

**Check Network tab:**
- Filter by "statsig"
- Should see POST requests to `api.statsig.com/v1/log_event`

### 4.6 Test Instant Navigation

1. Click an internal link
2. Console should show: `[Statsig Tracking] Page navigation detected, resetting trackers...`
3. New exposure should be logged for the new page

### 4.7 Test Anti-Flicker

1. **Disable cache:** DevTools → Network → Disable cache
2. **Slow 3G:** DevTools → Network → Throttle to Slow 3G
3. **Reload page:** Should NOT see default content flash before variant

If you see a flash:
- Check `data-hidden` attribute is on element
- Check CSS includes anti-flicker rule
- Check element selector is correct

---

## Step 5: Deploy & Monitor

### 5.1 Commit Changes

```bash
git add projects/blog/docs/js/statsig/config/experiments.config.template.js
git add projects/blog/docs/index.md  # Or wherever you added HTML
git commit -m "feat: add hero CTA style experiment

- Add blog_hero_cta_style experiment to test button styling
- Target: #hero-cta-btn element
- Variants: primary vs secondary button style
- Expected lift: 15-20% CTR

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### 5.2 Update Production Config Secret

In GitHub: Settings → Secrets → Update `EXPERIMENT_CONFIG_JSON_BLOG_PROD`

Add your new experiment to the JSON.

### 5.3 Deploy to Staging (If Available)

```bash
git push origin develop
# Wait for GitHub Actions to deploy
# Test on staging URL
```

### 5.4 Deploy to Production

```bash
git checkout main
git merge feature_branch
git push origin main
```

### 5.5 Ramp Up in Statsig Console

1. Go to Statsig Console → Your Experiment
2. Start with 10% allocation
3. Monitor for 24 hours
4. If no issues, increase to 50%
5. Monitor until statistical significance

### 5.6 Monitor Metrics

**Statsig Console:**
- Experiments → Your Experiment → Results
- Check primary metric lift
- Monitor secondary metrics
- Watch for guardrail metrics (error rate, page load time)

**Google Analytics (if enabled):**
- Events → Filter by `statsig_experiment_exposure`
- Segments → Create segment by experiment variant
- Compare metrics across variants

**Key Metrics to Watch:**
- Click-through rate (primary for CTA tests)
- Conversion rate
- Time on page
- Scroll depth
- Bounce rate
- Error rate (should not increase)

### 5.7 Statistical Significance

Wait until:
- **Minimum sample size:** Usually 1000+ users per variant
- **Statistical significance:** p-value < 0.05 (95% confidence)
- **Practical significance:** Lift is meaningful (e.g., >10%)
- **Time window:** At least 1-2 weeks to account for weekday/weekend differences

### 5.8 Make Decision

**If Treatment Wins:**
1. Increase allocation to 100% in Statsig
2. Update config to make treatment the default
3. Remove experiment code (now just standard code)
4. Archive experiment in Statsig

**If Control Wins or No Difference:**
1. Keep control (do nothing)
2. Archive experiment in Statsig
3. Remove experiment code
4. Document learnings

---

## Common Experiment Patterns

### Pattern 1: Button Text Optimization

**Goal:** Find the most compelling CTA text

**Setup:**
```javascript
{
  selector: "#signup-cta",
  experiment: "blog_signup_cta_text",
  param: "button_text",
  type: "text",
  category: "conversion",
  pages: ["index.html"],
  priority: "critical"
}
```

**Statsig Variants:**
- Control: "Sign Up"
- Treatment_A: "Get Started Free"
- Treatment_B: "Start Learning Now"

**Success Metric:** Click-through rate

### Pattern 2: Navigation Layout

**Goal:** Test sticky vs non-sticky navigation

**Setup:**
```javascript
{
  selector: "body",
  experiment: "blog_sticky_nav",
  param: "enabled",
  type: "class",
  className: "md-tabs--sticky",
  category: "navigation",
  pages: ["*"],
  priority: "high"
}
```

**Statsig Variants:**
- Control: false (no sticky nav)
- Treatment: true (sticky nav)

**Success Metrics:** Page views per session, time on site

### Pattern 3: Content Density

**Goal:** Find optimal number of posts per page

**Setup:**
```javascript
{
  selector: "[data-exp='pagination']",
  experiment: "blog_posts_per_page",
  param: "count",
  type: "attr",
  attr: "data-posts-count",
  category: "blog-layout",
  pages: ["blog/index.html"],
  priority: "medium"
}
```

**Statsig Variants:**
- Control: 5
- Treatment_A: 10
- Treatment_B: 3

**Success Metrics:** Engagement rate, pages per session

### Pattern 4: Visual Styling

**Goal:** Test primary color variations

**Setup:**
```javascript
{
  selector: ":root",
  experiment: "blog_primary_color",
  param: "color_hex",
  type: "style",
  styleProperty: "--md-primary-fg-color",
  category: "visual",
  pages: ["*"],
  priority: "low"
}
```

**Statsig Variants:**
- Control: "#384D48"
- Treatment_A: "#2196F3"
- Treatment_B: "#4CAF50"

**Success Metrics:** Time on page, subjective feedback

### Pattern 5: Multi-Element Test

**Goal:** Test entire page redesign

**Approach:** Use multiple coordinated experiments with the same allocation

```javascript
experiments: {
  cta: {
    redesign_hero_cta: {
      selector: "#hero-cta",
      experiment: "blog_homepage_redesign_v2",
      param: "hero_cta_text",
      type: "text",
      // ...
    }
  },
  visual: {
    redesign_hero_style: {
      selector: ".hero-section",
      experiment: "blog_homepage_redesign_v2",
      param: "hero_style",
      type: "class",
      className: "hero--modern",
      // ...
    }
  }
}
```

**Statsig:** Use same experiment for both, different parameters

---

## Experiment Best Practices

### DO ✅

1. **Start Small**
   - Test one thing at a time
   - Small iterations are easier to understand

2. **Define Success First**
   - Know your primary metric before starting
   - Set a minimum detectable effect (MDE)

3. **Test for Long Enough**
   - Minimum 1-2 weeks
   - Wait for statistical significance

4. **Monitor Guardrail Metrics**
   - Page load time
   - Error rate
   - Core Web Vitals

5. **Document Everything**
   - Hypothesis
   - Expected lift
   - Results
   - Learnings

6. **Use Anti-Flicker**
   - Always add `data-hidden` to experiment elements
   - Test with slow network to verify

7. **Test Both Variants**
   - Manually verify both control and treatment work
   - Check on mobile and desktop

### DON'T ❌

1. **Don't Test Too Many Things**
   - Running 10+ experiments simultaneously dilutes traffic
   - Harder to understand interactions

2. **Don't Stop Too Early**
   - Need statistical significance
   - Account for day-of-week effects

3. **Don't Ignore Negative Results**
   - Failed experiments teach you what doesn't work
   - Document and move on

4. **Don't Break Existing Functionality**
   - Always test both variants thoroughly
   - Monitor error rates

5. **Don't Forget Mobile**
   - Test on different screen sizes
   - Mobile users may behave differently

6. **Don't Experiment on Critical Flows Without Testing**
   - Thoroughly test payment, signup, login flows
   - Have rollback plan ready

---

## Troubleshooting

### Issue: Experiment Not Applying

**Check:**
1. Element selector is correct: `document.querySelector("#your-selector")`
2. Page matches `pages` array in config
3. Statsig experiment is running (not paused)
4. Browser console shows experiment loaded
5. Variant value is what you expect

**Debug:**
```javascript
// In browser console
console.log(window.EXPERIMENT_CONFIG);
console.log(window.StatsigClient.instance);
console.log(window.StatsigClient.instance.getExperiment("your_experiment_name"));
```

### Issue: Content Flash (FOUC)

**Check:**
1. Element has `data-hidden` attribute
2. Anti-flicker CSS is loaded
3. Scripts load in correct order (renderer before bootstrap)

**Fix:**
```css
/* In extra.css */
[data-hidden] {
  visibility: hidden !important;
  opacity: 0 !important;
}
```

### Issue: Events Not Logging

**Check:**
1. Tracking enabled in config: `enableAutoClick: true`
2. Element matches tracking selectors
3. Browser console shows tracking initialized
4. Network tab shows POST to Statsig API
5. Ad blocker not blocking requests

**Debug:**
```javascript
// In browser console
console.log(window.StatsigTracker);
console.log(window.StatsigTracker.eventLogger);
console.log(window.StatsigTracker.clickTracker);
```

### Issue: Wrong Variant Assigned

**Check:**
1. User ID is stable (check localStorage)
2. Allocation percentage in Statsig Console
3. No user overrides in Statsig Console

**Reset:**
```javascript
// In browser console
localStorage.removeItem('statsig-user-id');
location.reload();
```

### Issue: Experiment Not in Results

**Check:**
1. Exposures are being logged (check Statsig Events)
2. Enough time has passed (results update hourly)
3. Primary metric is configured correctly
4. Users are actually seeing both variants (check allocation)

---

## Advanced Topics

### Sequential Testing

Test multiple variations sequentially:
1. Test A vs B → B wins
2. Test B vs C → C wins
3. Test C vs D → C wins
4. C is the winner

### Multi-Armed Bandit

Let Statsig automatically allocate more traffic to winning variant:
- Enable "Auto-tune" in Statsig Console
- System will gradually shift traffic to better performers

### Personalization

Use Statsig targeting rules:
- Show different variants based on:
  - Location
  - Device type
  - Time of day
  - User properties

### Experiment Interactions

Be careful when running multiple experiments:
- Experiments on same page may interact
- Use Statsig's "Mutual Exclusion Groups" to prevent conflicts

---

## Resources

### Documentation
- Statsig Docs: https://docs.statsig.com
- This Implementation: `PHASE3_IMPLEMENTATION.md`
- Technical Reference: `tracking/README.md`

### Statsig Console
- Experiments: https://console.statsig.com/experiments
- Metrics: https://console.statsig.com/metrics
- Events: https://console.statsig.com/events

### Google Analytics (if enabled)
- Events: GA4 → Reports → Engagement → Events
- Explorations: GA4 → Explore → Create new exploration

### Support
- Statsig Community: https://statsig.com/slack
- Documentation: Check implementation docs in this repo

---

## Quick Reference

### Experiment Config Template

```javascript
experiment_name: {
  selector: "#element-id",              // Required: CSS selector
  experiment: "statsig_experiment_name", // Required: Statsig name
  param: "parameter_name",              // Required: Parameter from Statsig
  type: "text",                         // Required: text|class|attr|html|style
  category: "conversion",               // Required: Analytics category
  pages: ["index.html"],                // Required: Where to run
  priority: "critical",                 // Required: critical|high|medium|low
  fallback: "default value",            // Optional: Default if Statsig fails
  className: "css-class",               // For type: "class"
  attr: "attribute-name",               // For type: "attr"
  styleProperty: "css-property"         // For type: "style"
}
```

### HTML Template

```html
<element id="unique-id" data-hidden data-track="event_name" data-exp-key="config_key">
  Default content
</element>
```

### Testing Checklist

- [ ] Experiment created in Statsig Console
- [ ] Config added to experiments.config.template.js
- [ ] Production secret updated (EXPERIMENT_CONFIG_JSON)
- [ ] HTML element has unique selector
- [ ] Element has `data-hidden` attribute
- [ ] Local testing passed (both variants work)
- [ ] No content flash observed
- [ ] Events logging correctly
- [ ] Instant navigation works
- [ ] Mobile testing passed
- [ ] Deployed to staging
- [ ] Monitored for 24h on staging
- [ ] Deployed to production at 10% allocation
- [ ] Ramped to 50% after validation
- [ ] Monitoring results in Statsig Console

---

**Last Updated:** February 7, 2026
**Version:** 1.0.0
