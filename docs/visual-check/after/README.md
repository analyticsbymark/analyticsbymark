# AFTER screenshots (working tree on top of d9b6c8f)

Live :8011; fresh fixture /tmp/abm-eval-fixture2 (4 posts) on :8012, now stopped. Consent hidden by injected CSS in capture page only. 390x844 / 1440x900; `_full` = full page.

Measured on all 64 page states: no horizontal overflow, 0 console errors, 0 failed requests (livereload aborts ignored).

## Earlier defects: before vs after
- #1 empty gap on /blog/ and /start-here/: FIXED (empty-state callout, `blog_*`, `starthere_*`). New minor: footer no longer hugs viewport bottom on those short pages at 1440 (~115px blank under it).
- #2 tofu emoji bullets on home: NOT CHANGED (likely this Chrome has no emoji font).
- #3 icon placeholder glyphs (announce close, footer, code copy): NOT FIXED, still image-placeholder squares; nav toggles on category sidebar show as black bars.
- #4/#5 clipping at 390 (post table/prompt block, spacex code, showcase table): UNCHANGED; inner scroll containers, page itself does not overflow. Toolbar overlap: copy-icon still sits over the right end of the prompt line.

## Features
- Inline newsletter form on post: PASS. One `.abm-post-newsletter` form in main, email input labelled "Email address" (#newsletter-email), Tab goes input -> Subscribe, focus ring visible (`fxpostformfocus_*`). Note: action is still the placeholder `replace-me.usx.list-manage.com` and a honeypot text input has no label (tabindex -1).
- TOC active-section polish: PASS. Active item highlighted with accent bar; text contrast 14.5:1 light, 13.9:1 dark.
- Ledger tag/category headers: PASS. Title + "2 posts" + card grid (`fxblogcategory_*`). Cosmetic: tag chip flush against card title.
- Footer stat strip: PASS on fixture (Posts 4, Last updated September 1, 2026, Series 1; contrast dt 8.1/6.5, dd 12.0/13.9 light/dark); correctly hidden on live site (0 posts). Wraps to 2 rows at 390 (Series alone on row 2).
- Duplicate IDs on fixture post: none.

## Files

| File | Shows | Verdict |
|---|---|---|
| about_dark_1440.png | /about/, dark, 1440px | ok, no defects seen |
| about_dark_1440_full.png | /about/, dark, 1440px full page | ok, no defects seen |
| about_dark_390.png | /about/, dark, 390px | ok, no defects seen |
| about_dark_390_full.png | /about/, dark, 390px full page | ok, no defects seen |
| about_light_1440.png | /about/, light, 1440px | ok, no defects seen |
| about_light_1440_full.png | /about/, light, 1440px full page | ok, no defects seen |
| about_light_390.png | /about/, light, 390px | ok, no defects seen |
| about_light_390_full.png | /about/, light, 390px full page | ok, no defects seen |
| blog_dark_1440.png | /blog/ (live, no posts), dark, 1440px | Empty state fixed ("No posts yet."). Footer floats ~115px above viewport bottom at 1440 (short page). Icon glyph placeholder persists |
| blog_dark_390.png | /blog/ (live, no posts), dark, 390px | Empty state fixed ("No posts yet."). Footer floats ~115px above viewport bottom at 1440 (short page). Icon glyph placeholder persists |
| blog_light_1440.png | /blog/ (live, no posts), light, 1440px | Empty state fixed ("No posts yet."). Footer floats ~115px above viewport bottom at 1440 (short page). Icon glyph placeholder persists |
| blog_light_390.png | /blog/ (live, no posts), light, 390px | Empty state fixed ("No posts yet."). Footer floats ~115px above viewport bottom at 1440 (short page). Icon glyph placeholder persists |
| blogfooter_dark_1440.png | live /blog/ bottom (strip hidden: 0 posts), dark, 1440px | ok, no defects seen |
| blogfooter_dark_390.png | live /blog/ bottom (strip hidden: 0 posts), dark, 390px | ok, no defects seen |
| blogfooter_light_1440.png | live /blog/ bottom (strip hidden: 0 posts), light, 1440px | ok, no defects seen |
| blogfooter_light_390.png | live /blog/ bottom (strip hidden: 0 posts), light, 390px | ok, no defects seen |
| fxblogarchive_dark_1440.png | fixture archive, dark, 1440px | ok, no defects seen |
| fxblogarchive_dark_1440_full.png | fixture archive, dark, 1440px full page | ok, no defects seen |
| fxblogarchive_dark_390.png | fixture archive, dark, 390px | ok, no defects seen |
| fxblogarchive_dark_390_full.png | fixture archive, dark, 390px full page | ok, no defects seen |
| fxblogarchive_light_1440.png | fixture archive, light, 1440px | ok, no defects seen |
| fxblogarchive_light_1440_full.png | fixture archive, light, 1440px full page | ok, no defects seen |
| fxblogarchive_light_390.png | fixture archive, light, 390px | ok, no defects seen |
| fxblogarchive_light_390_full.png | fixture archive, light, 390px full page | ok, no defects seen |
| fxblogcategory_dark_1440.png | fixture category page (AI Agents), dark, 1440px | Header + "2 posts" + 2-col card grid OK; tag chip sits flush against title; nav toggle icons render as black bars |
| fxblogcategory_dark_390.png | fixture category page (AI Agents), dark, 390px | Header + "2 posts" + 2-col card grid OK; tag chip sits flush against title; nav toggle icons render as black bars |
| fxblogcategory_dark_390_full.png | fixture category page (AI Agents), dark, 390px full page | Header + "2 posts" + 2-col card grid OK; tag chip sits flush against title; nav toggle icons render as black bars |
| fxblogcategory_light_1440.png | fixture category page (AI Agents), light, 1440px | Header + "2 posts" + 2-col card grid OK; tag chip sits flush against title; nav toggle icons render as black bars |
| fxblogcategory_light_390.png | fixture category page (AI Agents), light, 390px | Header + "2 posts" + 2-col card grid OK; tag chip sits flush against title; nav toggle icons render as black bars |
| fxblogcategory_light_390_full.png | fixture category page (AI Agents), light, 390px full page | Header + "2 posts" + 2-col card grid OK; tag chip sits flush against title; nav toggle icons render as black bars |
| fxblogcategoryfooter_dark_1440.png | fixture category bottom (stat strip), dark, 1440px | ok, no defects seen |
| fxblogcategoryfooter_dark_390.png | fixture category bottom (stat strip), dark, 390px | ok, no defects seen |
| fxblogcategoryfooter_light_1440.png | fixture category bottom (stat strip), light, 1440px | ok, no defects seen |
| fxblogcategoryfooter_light_390.png | fixture category bottom (stat strip), light, 390px | ok, no defects seen |
| fxblogindex_dark_1440.png | fixture blog index, dark, 1440px | ok, no defects seen |
| fxblogindex_dark_1440_full.png | fixture blog index, dark, 1440px full page | ok, no defects seen |
| fxblogindex_dark_390.png | fixture blog index, dark, 390px | ok, no defects seen |
| fxblogindex_dark_390_full.png | fixture blog index, dark, 390px full page | ok, no defects seen |
| fxblogindex_light_1440.png | fixture blog index, light, 1440px | ok, no defects seen |
| fxblogindex_light_1440_full.png | fixture blog index, light, 1440px full page | ok, no defects seen |
| fxblogindex_light_390.png | fixture blog index, light, 390px | ok, no defects seen |
| fxblogindex_light_390_full.png | fixture blog index, light, 390px full page | ok, no defects seen |
| fxblogindexfooter_dark_1440.png | fixture blog index bottom (stat strip), dark, 1440px | ok, no defects seen |
| fxblogindexfooter_dark_390.png | fixture blog index bottom (stat strip), dark, 390px | ok, no defects seen |
| fxblogindexfooter_light_1440.png | fixture blog index bottom (stat strip), light, 1440px | ok, no defects seen |
| fxblogindexfooter_light_390.png | fixture blog index bottom (stat strip), light, 390px | ok, no defects seen |
| fxblogpost_dark_1440.png | fixture post (series, table, copy-prompt, inline newsletter), dark, 1440px | 390: table/prompt block still clip right (inner scroll) |
| fxblogpost_dark_1440_full.png | fixture post (series, table, copy-prompt, inline newsletter), dark, 1440px full page | 390: table/prompt block still clip right (inner scroll) |
| fxblogpost_dark_390.png | fixture post (series, table, copy-prompt, inline newsletter), dark, 390px | 390: table/prompt block still clip right (inner scroll) |
| fxblogpost_dark_390_full.png | fixture post (series, table, copy-prompt, inline newsletter), dark, 390px full page | 390: table/prompt block still clip right (inner scroll) |
| fxblogpost_light_1440.png | fixture post (series, table, copy-prompt, inline newsletter), light, 1440px | 390: table/prompt block still clip right (inner scroll) |
| fxblogpost_light_1440_full.png | fixture post (series, table, copy-prompt, inline newsletter), light, 1440px full page | 390: table/prompt block still clip right (inner scroll) |
| fxblogpost_light_390.png | fixture post (series, table, copy-prompt, inline newsletter), light, 390px | 390: table/prompt block still clip right (inner scroll) |
| fxblogpost_light_390_full.png | fixture post (series, table, copy-prompt, inline newsletter), light, 390px full page | 390: table/prompt block still clip right (inner scroll) |
| fxblogtags_dark_1440.png | fixture /blog/tags/, dark, 1440px | ok, no defects seen |
| fxblogtags_dark_1440_full.png | fixture /blog/tags/, dark, 1440px full page | ok, no defects seen |
| fxblogtags_dark_390.png | fixture /blog/tags/, dark, 390px | ok, no defects seen |
| fxblogtags_dark_390_full.png | fixture /blog/tags/, dark, 390px full page | ok, no defects seen |
| fxblogtags_light_1440.png | fixture /blog/tags/, light, 1440px | ok, no defects seen |
| fxblogtags_light_1440_full.png | fixture /blog/tags/, light, 1440px full page | ok, no defects seen |
| fxblogtags_light_390.png | fixture /blog/tags/, light, 390px | ok, no defects seen |
| fxblogtags_light_390_full.png | fixture /blog/tags/, light, 390px full page | ok, no defects seen |
| fxfooterstats_dark_1440.png | fixture post bottom: footer stat strip, dark, 1440px | ok, no defects seen |
| fxfooterstats_dark_390.png | fixture post bottom: footer stat strip, dark, 390px | ok, no defects seen |
| fxfooterstats_light_1440.png | fixture post bottom: footer stat strip, light, 1440px | ok, no defects seen |
| fxfooterstats_light_390.png | fixture post bottom: footer stat strip, light, 390px | ok, no defects seen |
| fxpostTOC0_dark_1440.png | fixture post scrolled, TOC active = "Second section", dark, 1440px | ok, no defects seen |
| fxpostTOC0_light_1440.png | fixture post scrolled, TOC active = "Second section", light, 1440px | ok, no defects seen |
| fxpostTOC1_dark_1440.png | fixture post scrolled, TOC active = "Third section", dark, 1440px | ok, no defects seen |
| fxpostTOC1_light_1440.png | fixture post scrolled, TOC active = "Third section", light, 1440px | ok, no defects seen |
| fxpostform_dark_1440.png | fixture post newsletter form centred, dark, 1440px | ok, no defects seen |
| fxpostform_dark_390.png | fixture post newsletter form centred, dark, 390px | ok, no defects seen |
| fxpostform_light_1440.png | fixture post newsletter form centred, light, 1440px | ok, no defects seen |
| fxpostform_light_390.png | fixture post newsletter form centred, light, 390px | ok, no defects seen |
| fxpostformfocus_dark_1440.png | form with keyboard focus on Subscribe button, dark, 1440px | ok, no defects seen |
| fxpostformfocus_dark_390.png | form with keyboard focus on Subscribe button, dark, 390px | ok, no defects seen |
| fxpostformfocus_light_1440.png | form with keyboard focus on Subscribe button, light, 1440px | ok, no defects seen |
| fxpostformfocus_light_390.png | form with keyboard focus on Subscribe button, light, 390px | ok, no defects seen |
| fxstarthere_dark_1440.png | fixture start-here, dark, 1440px | ok, no defects seen |
| fxstarthere_dark_390.png | fixture start-here, dark, 390px | ok, no defects seen |
| fxstarthere_dark_390_full.png | fixture start-here, dark, 390px full page | ok, no defects seen |
| fxstarthere_light_1440.png | fixture start-here, light, 1440px | ok, no defects seen |
| fxstarthere_light_390.png | fixture start-here, light, 390px | ok, no defects seen |
| fxstarthere_light_390_full.png | fixture start-here, light, 390px full page | ok, no defects seen |
| fxtags_dark_1440.png | fixture /tags/, dark, 1440px | ok, no defects seen |
| fxtags_dark_390.png | fixture /tags/, dark, 390px | ok, no defects seen |
| fxtags_dark_390_full.png | fixture /tags/, dark, 390px full page | ok, no defects seen |
| fxtags_light_1440.png | fixture /tags/, light, 1440px | ok, no defects seen |
| fxtags_light_390.png | fixture /tags/, light, 390px | ok, no defects seen |
| fxtags_light_390_full.png | fixture /tags/, light, 390px full page | ok, no defects seen |
| home_dark_1440.png | /, dark, 1440px | ok (tofu bullets, icon placeholder persist) |
| home_dark_1440_full.png | /, dark, 1440px full page | ok (tofu bullets, icon placeholder persist) |
| home_dark_390.png | /, dark, 390px | ok (tofu bullets, icon placeholder persist) |
| home_dark_390_full.png | /, dark, 390px full page | ok (tofu bullets, icon placeholder persist) |
| home_light_1440.png | /, light, 1440px | ok (tofu bullets, icon placeholder persist) |
| home_light_1440_full.png | /, light, 1440px full page | ok (tofu bullets, icon placeholder persist) |
| home_light_390.png | /, light, 390px | ok (tofu bullets, icon placeholder persist) |
| home_light_390_full.png | /, light, 390px full page | ok (tofu bullets, icon placeholder persist) |
| homefooter_dark_1440.png | live home bottom (strip hidden: 0 posts), dark, 1440px | ok, no defects seen |
| homefooter_dark_390.png | live home bottom (strip hidden: 0 posts), dark, 390px | ok, no defects seen |
| homefooter_light_1440.png | live home bottom (strip hidden: 0 posts), light, 1440px | ok, no defects seen |
| homefooter_light_390.png | live home bottom (strip hidden: 0 posts), light, 390px | ok, no defects seen |
| learn_dark_1440.png | /learn/, dark, 1440px | ok, no defects seen |
| learn_dark_390.png | /learn/, dark, 390px | ok, no defects seen |
| learn_dark_390_full.png | /learn/, dark, 390px full page | ok, no defects seen |
| learn_light_1440.png | /learn/, light, 1440px | ok, no defects seen |
| learn_light_390.png | /learn/, light, 390px | ok, no defects seen |
| learn_light_390_full.png | /learn/, light, 390px full page | ok, no defects seen |
| newsletter_dark_1440.png | /newsletter/, dark, 1440px | ok, no defects seen |
| newsletter_dark_390.png | /newsletter/, dark, 390px | ok, no defects seen |
| newsletter_dark_390_full.png | /newsletter/, dark, 390px full page | ok, no defects seen |
| newsletter_light_1440.png | /newsletter/, light, 1440px | ok, no defects seen |
| newsletter_light_390.png | /newsletter/, light, 390px | ok, no defects seen |
| newsletter_light_390_full.png | /newsletter/, light, 390px full page | ok, no defects seen |
| showcase_dark_1440.png | /showcase/, dark, 1440px | ok, no defects seen |
| showcase_dark_1440_full.png | /showcase/, dark, 1440px full page | ok, no defects seen |
| showcase_dark_390.png | /showcase/, dark, 390px | ok, no defects seen |
| showcase_dark_390_full.png | /showcase/, dark, 390px full page | ok, no defects seen |
| showcase_light_1440.png | /showcase/, light, 1440px | ok, no defects seen |
| showcase_light_1440_full.png | /showcase/, light, 1440px full page | ok, no defects seen |
| showcase_light_390.png | /showcase/, light, 390px | ok, no defects seen |
| showcase_light_390_full.png | /showcase/, light, 390px full page | ok, no defects seen |
| spacexdata_dark_1440.png | /learn/data/spacex/, dark, 1440px | ok, no defects seen |
| spacexdata_dark_1440_full.png | /learn/data/spacex/, dark, 1440px full page | ok, no defects seen |
| spacexdata_dark_390.png | /learn/data/spacex/, dark, 390px | ok, no defects seen |
| spacexdata_dark_390_full.png | /learn/data/spacex/, dark, 390px full page | ok, no defects seen |
| spacexdata_light_1440.png | /learn/data/spacex/, light, 1440px | ok, no defects seen |
| spacexdata_light_1440_full.png | /learn/data/spacex/, light, 1440px full page | ok, no defects seen |
| spacexdata_light_390.png | /learn/data/spacex/, light, 390px | ok, no defects seen |
| spacexdata_light_390_full.png | /learn/data/spacex/, light, 390px full page | ok, no defects seen |
| spacexpolicies_dark_1440.png | /learn/spacex/creating_policies/, dark, 1440px | ok, no defects seen |
| spacexpolicies_dark_1440_full.png | /learn/spacex/creating_policies/, dark, 1440px full page | ok, no defects seen |
| spacexpolicies_dark_390.png | /learn/spacex/creating_policies/, dark, 390px | ok, no defects seen |
| spacexpolicies_dark_390_full.png | /learn/spacex/creating_policies/, dark, 390px full page | ok, no defects seen |
| spacexpolicies_light_1440.png | /learn/spacex/creating_policies/, light, 1440px | ok, no defects seen |
| spacexpolicies_light_1440_full.png | /learn/spacex/creating_policies/, light, 1440px full page | ok, no defects seen |
| spacexpolicies_light_390.png | /learn/spacex/creating_policies/, light, 390px | ok, no defects seen |
| spacexpolicies_light_390_full.png | /learn/spacex/creating_policies/, light, 390px full page | ok, no defects seen |
| starthere_dark_1440.png | /start-here/ (live, no posts), dark, 1440px | Empty state fixed ("No posts selected."). Same short-page footer float at 1440 |
| starthere_dark_390.png | /start-here/ (live, no posts), dark, 390px | Empty state fixed ("No posts selected."). Same short-page footer float at 1440 |
| starthere_light_1440.png | /start-here/ (live, no posts), light, 1440px | Empty state fixed ("No posts selected."). Same short-page footer float at 1440 |
| starthere_light_390.png | /start-here/ (live, no posts), light, 390px | Empty state fixed ("No posts selected."). Same short-page footer float at 1440 |
