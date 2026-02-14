# Quick Start: Adding New A/B Tests

**TL;DR:** 5 steps to launch a new experiment.

---

## 1. Create in Statsig Console (5 min)

```
https://console.statsig.com → Experiments → Create New

Name: blog_hero_cta_text
Parameter: button_label
  - Control: "Read Tutorial"
  - Treatment: "Start Now"

Allocation: 0% (we'll ramp after testing)
```

---

## 2. Add to Config (2 min)

**File:** `projects/blog/docs/js/statsig/config/experiments.config.template.js`

```javascript
experiments: {
  cta: {
    hero_button_text: {
      selector: "#hero-cta",               // CSS selector
      experiment: "blog_hero_cta_text",    // Statsig name
      param: "button_label",               // Parameter name
      type: "text",                        // Type of change
      category: "conversion",              // Analytics category
      pages: ["index.html"],               // Where to run
      priority: "critical"                 // Priority level
    }
  }
}
```

**Common Types:**
- `text` - Change text content
- `class` - Add/remove CSS class
- `attr` - Set attribute value
- `html` - Change HTML content
- `style` - Set CSS property

---

## 3. Prepare HTML (1 min)

```html
<!-- Add unique ID and data-hidden -->
<a href="/tutorial" id="hero-cta" class="md-button" data-hidden>
  Read Tutorial
</a>
```

**Critical:** `data-hidden` prevents content flash!

---

## 4. Test Locally (10 min)

```bash
# Start server
cd projects/blog
mkdocs serve

# Open: http://127.0.0.1:8000/
# Check: DevTools → Console
```

**Expected logs:**
```
[Statsig] Applied experiment: blog_hero_cta_text = "Start Now"
[Statsig ExposureLogger] Logged exposure
[Statsig EventLogger] Logged event: experiment_exposure
```

**Test both variants:**
```
http://127.0.0.1:8000/?exp_blog_hero_cta_text=control
http://127.0.0.1:8000/?exp_blog_hero_cta_text=treatment
```

---

## 5. Deploy & Monitor (ongoing)

```bash
# Commit
git add .
git commit -m "feat: add hero CTA text experiment"
git push

# Update production secret (GitHub)
Settings → Secrets → EXPERIMENT_CONFIG_JSON_BLOG_PROD

# Ramp in Statsig Console
10% → monitor 24h → 50% → wait for significance → decide
```

**Monitor:** Statsig Console → Your Experiment → Results

---

## Common Patterns

### Button Text Test
```javascript
{
  selector: "#cta-button",
  experiment: "button_text_test",
  param: "text",
  type: "text",
  category: "conversion",
  pages: ["index.html"],
  priority: "critical"
}
```

### Sticky Navigation Test
```javascript
{
  selector: "body",
  experiment: "sticky_nav_test",
  param: "enabled",
  type: "class",
  className: "md-tabs--sticky",
  category: "navigation",
  pages: ["*"],
  priority: "high"
}
```

### Layout Density Test
```javascript
{
  selector: "[data-exp='pagination']",
  experiment: "posts_per_page",
  param: "count",
  type: "attr",
  attr: "data-posts-count",
  category: "blog-layout",
  pages: ["blog/index.html"],
  priority: "medium"
}
```

---

## Troubleshooting

**Experiment not applying?**
```javascript
// Browser console
console.log(document.querySelector("#your-selector")); // Check selector
console.log(window.StatsigClient.instance.getExperiment("your_experiment")); // Check value
```

**Content flash?**
- Add `data-hidden` attribute
- Check CSS has `[data-hidden] { visibility: hidden !important; }`

**Events not logging?**
- Check `enableAutoClick: true` in config
- Check Network tab for POST to statsig.com
- Disable ad blocker

---

## Full Documentation

📖 **Complete Guide:** `HOW_TO_ADD_EXPERIMENTS.md` (in this directory)

📊 **Implementation Details:** `../../../PHASE3_IMPLEMENTATION.md`

🔧 **Technical Reference:** `tracking/README.md`

---

**Questions?** Check the full guide or Statsig docs: https://docs.statsig.com
