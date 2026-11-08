# Dummy blog evaluation (branch dummy_blog_posts, build /tmp/abm_E, served :8013, now stopped)

Light+dark, 390x844 and 1440x900. Consent overlay hidden by injected CSS in my own page only. `_full` = full page. Social cards copied as `socialcard_*.png` (1200x630).

## Checks
- (a) 100 states measured (13 page sets + 12 posts, 4 states each, plus extras): 0 horizontal overflow, 0 console errors, 0 failed requests. 3 navigations timed out once (Chrome busy) and were retaken cleanly.
- (b) Heroes: all 12 are 1200x630, render at ~1.9 aspect, correct alt text, none broken. 1 lazy image on loss-ratio-dash had not loaded after 0.8s; the file serves 200 and is 2200x1240, so it is a timing artifact.
- (c) Series banner on parts 1-4 lists 4 correct links with aria-current on the right part. Featured card = newest post (3 years of notes). Related/prev-next sensible. rating-api-python and cat-modelling-inputs have no related links.
- (d) Internal links in all 12 articles incl. anchors: 0 broken (46 llms URLs also resolve).
- (e) JSON-LD valid on all 12 (BlogPosting + BreadcrumbList). headline, datePublished, dateModified, url match visible title/dates. image is the hero webp.
- (f) llms.txt: 12 post lines, all labelled Sample content. blog/index.json: 12 entries, newest first, all URLs resolve, required keys present.
- (g) sitemap.xml excludes /start-here/, /showcase/, /blog-authoring-guide/; includes 12 posts, pages 2/3, categories.
- (h) Every post has exactly one H1, a visible "Sample post" admonition, description 151-159 chars.
- (i) No duplicate titles or descriptions.
- (j) Contrast: agent summary 11.1-14.5, tags 11.9-15.7 in both themes. All pass.
- (k) Copy buttons: all 4 blocks copy exact code text (clipboard equals code, status "Copied") in all 4 states. Download SKILL.md not clicked.

## Defects
| Page | Theme/width | Severity | File |
|---|---|---|---|
| blog index/page 2/3, category, archive social cards | n/a | low-med: default Material blue card, off-brand; pages 2 and 3 share the index card; category/archive cards show generic site blurb | socialcard_blogindex.png, socialcard_category.png, socialcard_archive.png |
| posts with author avatar | both/1440 | low: avatar is a wide hero webp squashed into a tiny circle, unrecognisable | postseries2_dark_1440.png |
| posts with updated=created | all | low: metadata shows the same date twice | postseries2_dark_1440.png |
| all pages | all | low: icons (announce close, footer, avatar-metadata) still render as placeholder glyphs; sidebar chevrons tiny | postseries2_dark_1440.png, blogindex_light_1440.png |
| rating-api-python, cat-modelling-inputs | all | low: no related posts block | n/a |
| featured card | light | info: Sample-post admonition shows in the excerpt | blogindex_light_1440.png |

## Not verified
- Download SKILL.md click (avoids writing to the shared Chrome downloads).
- JSON-LD against Google Rich Results (only structural check).
- Rendering of /llms.txt in a real agent; whether the dummy guard blocks production builds (not exercised).
- Not every PNG reviewed at full resolution.

## Files

| File | Shows | Verdict |
|---|---|---|
| archive2025_dark_1440.png | /blog/archive/2025/, dark, 1440px | ok, no defects seen |
| archive2025_dark_1440_full.png | /blog/archive/2025/, dark, 1440px full | ok, no defects seen |
| archive2025_dark_390.png | /blog/archive/2025/, dark, 390px | ok, no defects seen |
| archive2025_dark_390_full.png | /blog/archive/2025/, dark, 390px full | ok, no defects seen |
| archive2025_light_1440.png | /blog/archive/2025/, light, 1440px | ok, no defects seen |
| archive2025_light_1440_full.png | /blog/archive/2025/, light, 1440px full | ok, no defects seen |
| archive2025_light_390.png | /blog/archive/2025/, light, 390px | ok, no defects seen |
| archive2025_light_390_full.png | /blog/archive/2025/, light, 390px full | ok, no defects seen |
| blogindex_dark_1440.png | /blog/ page 1, dark, 1440px | Featured card is the newest post. Sidebar chevrons tiny |
| blogindex_dark_1440_full.png | /blog/ page 1, dark, 1440px full | Featured card is the newest post. Sidebar chevrons tiny |
| blogindex_dark_390.png | /blog/ page 1, dark, 390px | Featured card is the newest post. Sidebar chevrons tiny |
| blogindex_dark_390_full.png | /blog/ page 1, dark, 390px full | Featured card is the newest post. Sidebar chevrons tiny |
| blogindex_light_1440.png | /blog/ page 1, light, 1440px | Featured card is the newest post. Sidebar chevrons tiny |
| blogindex_light_1440_full.png | /blog/ page 1, light, 1440px full | Featured card is the newest post. Sidebar chevrons tiny |
| blogindex_light_390.png | /blog/ page 1, light, 390px | Featured card is the newest post. Sidebar chevrons tiny |
| blogindex_light_390_full.png | /blog/ page 1, light, 390px full | Featured card is the newest post. Sidebar chevrons tiny |
| blogpage2_dark_1440.png | /blog/page/2/, dark, 1440px | ok, no defects seen |
| blogpage2_dark_1440_full.png | /blog/page/2/, dark, 1440px full | ok, no defects seen |
| blogpage2_dark_390.png | /blog/page/2/, dark, 390px | ok, no defects seen |
| blogpage2_dark_390_full.png | /blog/page/2/, dark, 390px full | ok, no defects seen |
| blogpage2_light_1440.png | /blog/page/2/, light, 1440px | ok, no defects seen |
| blogpage2_light_1440_full.png | /blog/page/2/, light, 1440px full | ok, no defects seen |
| blogpage2_light_390.png | /blog/page/2/, light, 390px | ok, no defects seen |
| blogpage2_light_390_full.png | /blog/page/2/, light, 390px full | ok, no defects seen |
| blogpage3_dark_1440.png | /blog/page/3/, dark, 1440px | ok, no defects seen |
| blogpage3_dark_1440_full.png | /blog/page/3/, dark, 1440px full | ok, no defects seen |
| blogpage3_dark_390.png | /blog/page/3/, dark, 390px | ok, no defects seen |
| blogpage3_dark_390_full.png | /blog/page/3/, dark, 390px full | ok, no defects seen |
| blogpage3_light_1440.png | /blog/page/3/, light, 1440px | ok, no defects seen |
| blogpage3_light_1440_full.png | /blog/page/3/, light, 1440px full | ok, no defects seen |
| blogpage3_light_390.png | /blog/page/3/, light, 390px | ok, no defects seen |
| blogpage3_light_390_full.png | /blog/page/3/, light, 390px full | ok, no defects seen |
| blogtags_dark_1440.png | /blog/tags/, dark, 1440px | ok |
| blogtags_dark_1440_full.png | /blog/tags/, dark, 1440px full | ok |
| blogtags_dark_390.png | /blog/tags/, dark, 390px | ok |
| blogtags_dark_390_full.png | /blog/tags/, dark, 390px full | ok |
| blogtags_light_1440.png | /blog/tags/, light, 1440px | ok |
| blogtags_light_1440_full.png | /blog/tags/, light, 1440px full | ok |
| blogtags_light_390.png | /blog/tags/, light, 390px | ok |
| blogtags_light_390_full.png | /blog/tags/, light, 390px full | ok |
| categorydataeng_dark_1440.png | category Data Engineering, dark, 1440px | ok, no defects seen |
| categorydataeng_dark_1440_full.png | category Data Engineering, dark, 1440px full | ok, no defects seen |
| categorydataeng_dark_390.png | category Data Engineering, dark, 390px | ok, no defects seen |
| categorydataeng_dark_390_full.png | category Data Engineering, dark, 390px full | ok, no defects seen |
| categorydataeng_light_1440.png | category Data Engineering, light, 1440px | ok, no defects seen |
| categorydataeng_light_1440_full.png | category Data Engineering, light, 1440px full | ok, no defects seen |
| categorydataeng_light_390.png | category Data Engineering, light, 390px | ok, no defects seen |
| categorydataeng_light_390_full.png | category Data Engineering, light, 390px full | ok, no defects seen |
| copybuttons_dark_1440.png | prompts post, first copy-prompt button after click, dark, 1440px | ok, no defects seen |
| copybuttons_dark_390.png | prompts post, first copy-prompt button after click, dark, 390px | ok, no defects seen |
| copybuttons_light_1440.png | prompts post, first copy-prompt button after click, light, 1440px | ok, no defects seen |
| copybuttons_light_390.png | prompts post, first copy-prompt button after click, light, 390px | ok, no defects seen |
| postcfochart_dark_1440.png | post with images (cfo-chart), dark, 1440px | Images render, alt present. Related/prev-next sensible |
| postcfochart_dark_1440_full.png | post with images (cfo-chart), dark, 1440px full | Images render, alt present. Related/prev-next sensible |
| postcfochart_dark_390.png | post with images (cfo-chart), dark, 390px | Images render, alt present. Related/prev-next sensible |
| postcfochart_dark_390_full.png | post with images (cfo-chart), dark, 390px full | Images render, alt present. Related/prev-next sensible |
| postcfochart_light_1440.png | post with images (cfo-chart), light, 1440px | Images render, alt present. Related/prev-next sensible |
| postcfochart_light_1440_full.png | post with images (cfo-chart), light, 1440px full | Images render, alt present. Related/prev-next sensible |
| postcfochart_light_390.png | post with images (cfo-chart), light, 390px | Images render, alt present. Related/prev-next sensible |
| postcfochart_light_390_full.png | post with images (cfo-chart), light, 390px full | Images render, alt present. Related/prev-next sensible |
| postnewest_dark_1440.png | newest post (3 years of notes), dark, 1440px | ok, no defects seen |
| postnewest_dark_1440_full.png | newest post (3 years of notes), dark, 1440px full | ok, no defects seen |
| postnewest_dark_390.png | newest post (3 years of notes), dark, 390px | ok, no defects seen |
| postnewest_dark_390_full.png | newest post (3 years of notes), dark, 390px full | ok, no defects seen |
| postnewest_light_1440.png | newest post (3 years of notes), light, 1440px | ok, no defects seen |
| postnewest_light_1440_full.png | newest post (3 years of notes), light, 1440px full | ok, no defects seen |
| postnewest_light_390.png | newest post (3 years of notes), light, 390px | ok, no defects seen |
| postnewest_light_390_full.png | newest post (3 years of notes), light, 390px full | ok, no defects seen |
| postprofiling_dark_1440.png | data-profiling-agent post, dark, 1440px | ok, no defects seen |
| postprofiling_dark_1440_full.png | data-profiling-agent post, dark, 1440px full | ok, no defects seen |
| postprofiling_dark_390.png | data-profiling-agent post, dark, 390px | ok, no defects seen |
| postprofiling_dark_390_full.png | data-profiling-agent post, dark, 390px full | ok, no defects seen |
| postprofiling_light_1440.png | data-profiling-agent post, light, 1440px | ok, no defects seen |
| postprofiling_light_1440_full.png | data-profiling-agent post, light, 1440px full | ok, no defects seen |
| postprofiling_light_390.png | data-profiling-agent post, light, 390px | ok, no defects seen |
| postprofiling_light_390_full.png | data-profiling-agent post, light, 390px full | ok, no defects seen |
| postprompts_dark_1440.png | prompts post (copy buttons, summary), dark, 1440px | Summary block legible; 4 copy blocks work |
| postprompts_dark_1440_full.png | prompts post (copy buttons, summary), dark, 1440px full | Summary block legible; 4 copy blocks work |
| postprompts_dark_390.png | prompts post (copy buttons, summary), dark, 390px | Summary block legible; 4 copy blocks work |
| postprompts_dark_390_full.png | prompts post (copy buttons, summary), dark, 390px full | Summary block legible; 4 copy blocks work |
| postprompts_light_1440.png | prompts post (copy buttons, summary), light, 1440px | Summary block legible; 4 copy blocks work |
| postprompts_light_1440_full.png | prompts post (copy buttons, summary), light, 1440px full | Summary block legible; 4 copy blocks work |
| postprompts_light_390.png | prompts post (copy buttons, summary), light, 390px | Summary block legible; 4 copy blocks work |
| postprompts_light_390_full.png | prompts post (copy buttons, summary), light, 390px full | Summary block legible; 4 copy blocks work |
| postseries2_dark_1440.png | series part 2 (sqlmodel), dark, 1440px | Series banner and part 2 links correct. Avatar is a cropped wide hero image (low); two identical date rows |
| postseries2_dark_1440_full.png | series part 2 (sqlmodel), dark, 1440px full | Series banner and part 2 links correct. Avatar is a cropped wide hero image (low); two identical date rows |
| postseries2_dark_390.png | series part 2 (sqlmodel), dark, 390px | Series banner and part 2 links correct. Avatar is a cropped wide hero image (low); two identical date rows |
| postseries2_dark_390_full.png | series part 2 (sqlmodel), dark, 390px full | Series banner and part 2 links correct. Avatar is a cropped wide hero image (low); two identical date rows |
| postseries2_light_1440.png | series part 2 (sqlmodel), light, 1440px | Series banner and part 2 links correct. Avatar is a cropped wide hero image (low); two identical date rows |
| postseries2_light_1440_full.png | series part 2 (sqlmodel), light, 1440px full | Series banner and part 2 links correct. Avatar is a cropped wide hero image (low); two identical date rows |
| postseries2_light_390.png | series part 2 (sqlmodel), light, 390px | Series banner and part 2 links correct. Avatar is a cropped wide hero image (low); two identical date rows |
| postseries2_light_390_full.png | series part 2 (sqlmodel), light, 390px full | Series banner and part 2 links correct. Avatar is a cropped wide hero image (low); two identical date rows |
| socialcard_archive.png | social card | default blue, off-brand |
| socialcard_blogindex.png | social card | default blue, off-brand |
| socialcard_category.png | social card | default blue, off-brand |
| socialcard_post_apostrophe.png | social card | on-brand ledger card, text fits |
| socialcard_post_longtitle.png | social card | on-brand ledger card, text fits |
| starthere_dark_1440.png | /start-here/, dark, 1440px | ok, no defects seen |
| starthere_dark_390.png | /start-here/, dark, 390px | ok, no defects seen |
| starthere_dark_390_full.png | /start-here/, dark, 390px full | ok, no defects seen |
| starthere_light_1440.png | /start-here/, light, 1440px | ok, no defects seen |
| starthere_light_390.png | /start-here/, light, 390px | ok, no defects seen |
| starthere_light_390_full.png | /start-here/, light, 390px full | ok, no defects seen |
| summaryexpanded_dark_1440.png | prompts post, "Summary for agents" expanded, dark, 1440px | Contrast 13.9 to 14.5 |
| summaryexpanded_dark_390.png | prompts post, "Summary for agents" expanded, dark, 390px | Contrast 13.9 to 14.5 |
| summaryexpanded_light_1440.png | prompts post, "Summary for agents" expanded, light, 1440px | Contrast 13.9 to 14.5 |
| summaryexpanded_light_390.png | prompts post, "Summary for agents" expanded, light, 390px | Contrast 13.9 to 14.5 |
| tagpython_dark_1440.png | /tags/#tag:python, dark, 1440px | Anchor works, TOC highlights tag |
| tagpython_dark_1440_full.png | /tags/#tag:python, dark, 1440px full | Anchor works, TOC highlights tag |
| tagpython_dark_390.png | /tags/#tag:python, dark, 390px | Anchor works, TOC highlights tag |
| tagpython_dark_390_full.png | /tags/#tag:python, dark, 390px full | Anchor works, TOC highlights tag |
| tagpython_light_1440.png | /tags/#tag:python, light, 1440px | Anchor works, TOC highlights tag |
| tagpython_light_1440_full.png | /tags/#tag:python, light, 1440px full | Anchor works, TOC highlights tag |
| tagpython_light_390.png | /tags/#tag:python, light, 390px | Anchor works, TOC highlights tag |
| tagpython_light_390_full.png | /tags/#tag:python, light, 390px full | Anchor works, TOC highlights tag |
