# Statsig (parked)

**Date:** 2026-10-03 | **Status:** removed from the build, kept in git history

Statsig A/B testing was removed to keep the site simple while there is little traffic.
Revisit once the site has roughly 1,000+ weekly visitors.

## Where it lives
- Git tag `archive/statsig-v1` (commit `744ce46`) holds the complete implementation.
- Paths at that tag: `projects/blog/docs/js/statsig/`, `projects/dev/docs/js/statsig/`,
  `projects/*/overrides/partials/integrations/analytics.html`, `scripts/experiments/`.
- The real (gitignored) config was never committed. It needs `EXPERIMENT_CONFIG_JSON_*`
  secrets, which can be removed from GitHub.

## Restore
```bash
git checkout archive/statsig-v1 -- projects/blog/docs/js/statsig scripts/experiments
```
Then move the files under `website/docs/js/`, add the scripts to `extra_javascript`,
and gate the SDK behind cookie consent before shipping (see `repo_review.md` section 3).
