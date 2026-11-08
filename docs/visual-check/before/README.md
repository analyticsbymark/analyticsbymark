# BEFORE screenshots (re-brand d9b6c8f)

Live preview :8011; fixture (disposable, /tmp/abm-eval-fixture) :8012. Cookie consent hidden via injected CSS in capture page only (it was visible on every page). Viewport 390x844 / 1440x900; `_full` = full-page. Overflow check: scrollWidth <= innerWidth+1 passed for all states; 0 console errors; only failed requests are aborted `/livereload/` polls (benign). Dark set via palette localStorage + body `data-md-color-scheme=slate`.

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
| blog_dark_1440.png | /blog/ (live, no posts), dark, 1440px | Empty ~300px gap between H1 and newsletter card (no posts); announcement icon shows image-placeholder glyph |
| blog_dark_390.png | /blog/ (live, no posts), dark, 390px | Empty ~300px gap between H1 and newsletter card (no posts); announcement icon shows image-placeholder glyph |
| blog_light_1440.png | /blog/ (live, no posts), light, 1440px | Empty ~300px gap between H1 and newsletter card (no posts); announcement icon shows image-placeholder glyph |
| blog_light_390.png | /blog/ (live, no posts), light, 390px | Empty ~300px gap between H1 and newsletter card (no posts); announcement icon shows image-placeholder glyph |
| fxblogarchive_dark_1440.png | fixture archive 2026, dark, 1440px | ok, no defects seen |
| fxblogarchive_dark_1440_full.png | fixture archive 2026, dark, 1440px full page | ok, no defects seen |
| fxblogarchive_dark_390.png | fixture archive 2026, dark, 390px | ok, no defects seen |
| fxblogarchive_dark_390_full.png | fixture archive 2026, dark, 390px full page | ok, no defects seen |
| fxblogarchive_light_1440.png | fixture archive 2026, light, 1440px | ok, no defects seen |
| fxblogarchive_light_1440_full.png | fixture archive 2026, light, 1440px full page | ok, no defects seen |
| fxblogarchive_light_390.png | fixture archive 2026, light, 390px | ok, no defects seen |
| fxblogarchive_light_390_full.png | fixture archive 2026, light, 390px full page | ok, no defects seen |
| fxblogcategory_dark_1440.png | fixture category AI Agents, dark, 1440px | ok, no defects seen |
| fxblogcategory_dark_390.png | fixture category AI Agents, dark, 390px | ok, no defects seen |
| fxblogcategory_dark_390_full.png | fixture category AI Agents, dark, 390px full page | ok, no defects seen |
| fxblogcategory_light_1440.png | fixture category AI Agents, light, 1440px | ok, no defects seen |
| fxblogcategory_light_390.png | fixture category AI Agents, light, 390px | ok, no defects seen |
| fxblogcategory_light_390_full.png | fixture category AI Agents, light, 390px full page | ok, no defects seen |
| fxblogindex_dark_1440.png | fixture :8012 blog index, dark, 1440px | ok, no defects seen |
| fxblogindex_dark_1440_full.png | fixture :8012 blog index, dark, 1440px full page | ok, no defects seen |
| fxblogindex_dark_390.png | fixture :8012 blog index, dark, 390px | ok, no defects seen |
| fxblogindex_dark_390_full.png | fixture :8012 blog index, dark, 390px full page | ok, no defects seen |
| fxblogindex_light_1440.png | fixture :8012 blog index, light, 1440px | ok, no defects seen |
| fxblogindex_light_1440_full.png | fixture :8012 blog index, light, 1440px full page | ok, no defects seen |
| fxblogindex_light_390.png | fixture :8012 blog index, light, 390px | ok, no defects seen |
| fxblogindex_light_390_full.png | fixture :8012 blog index, light, 390px full page | ok, no defects seen |
| fxblogpost_dark_1440.png | fixture blog post (series, copy-prompt, table), dark, 1440px | 390: table and code/prompt blocks clip at right edge (copy button overlaps text); icons show placeholder glyphs |
| fxblogpost_dark_1440_full.png | fixture blog post (series, copy-prompt, table), dark, 1440px full page | 390: table and code/prompt blocks clip at right edge (copy button overlaps text); icons show placeholder glyphs |
| fxblogpost_dark_390.png | fixture blog post (series, copy-prompt, table), dark, 390px | 390: table and code/prompt blocks clip at right edge (copy button overlaps text); icons show placeholder glyphs |
| fxblogpost_dark_390_full.png | fixture blog post (series, copy-prompt, table), dark, 390px full page | 390: table and code/prompt blocks clip at right edge (copy button overlaps text); icons show placeholder glyphs |
| fxblogpost_light_1440.png | fixture blog post (series, copy-prompt, table), light, 1440px | 390: table and code/prompt blocks clip at right edge (copy button overlaps text); icons show placeholder glyphs |
| fxblogpost_light_1440_full.png | fixture blog post (series, copy-prompt, table), light, 1440px full page | 390: table and code/prompt blocks clip at right edge (copy button overlaps text); icons show placeholder glyphs |
| fxblogpost_light_390.png | fixture blog post (series, copy-prompt, table), light, 390px | 390: table and code/prompt blocks clip at right edge (copy button overlaps text); icons show placeholder glyphs |
| fxblogpost_light_390_full.png | fixture blog post (series, copy-prompt, table), light, 390px full page | 390: table and code/prompt blocks clip at right edge (copy button overlaps text); icons show placeholder glyphs |
| fxstarthere_dark_1440.png | fixture start-here, dark, 1440px | ok, no defects seen |
| fxstarthere_dark_390.png | fixture start-here, dark, 390px | ok, no defects seen |
| fxstarthere_light_1440.png | fixture start-here, light, 1440px | ok, no defects seen |
| fxstarthere_light_390.png | fixture start-here, light, 390px | ok, no defects seen |
| home_dark_1440.png | / home, dark, 1440px | List bullets show tofu boxes (emoji glyph missing in this Chrome); announcement close icon renders as overlapping glyph at 1440 |
| home_dark_1440_full.png | / home, dark, 1440px full page | List bullets show tofu boxes (emoji glyph missing in this Chrome); announcement close icon renders as overlapping glyph at 1440 |
| home_dark_390.png | / home, dark, 390px | List bullets show tofu boxes (emoji glyph missing in this Chrome); announcement close icon renders as overlapping glyph at 1440 |
| home_dark_390_full.png | / home, dark, 390px full page | List bullets show tofu boxes (emoji glyph missing in this Chrome); announcement close icon renders as overlapping glyph at 1440 |
| home_light_1440.png | / home, light, 1440px | List bullets show tofu boxes (emoji glyph missing in this Chrome); announcement close icon renders as overlapping glyph at 1440 |
| home_light_1440_full.png | / home, light, 1440px full page | List bullets show tofu boxes (emoji glyph missing in this Chrome); announcement close icon renders as overlapping glyph at 1440 |
| home_light_390.png | / home, light, 390px | List bullets show tofu boxes (emoji glyph missing in this Chrome); announcement close icon renders as overlapping glyph at 1440 |
| home_light_390_full.png | / home, light, 390px full page | List bullets show tofu boxes (emoji glyph missing in this Chrome); announcement close icon renders as overlapping glyph at 1440 |
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
| starthere_dark_1440.png | /start-here/ (live, no posts), dark, 1440px | Same as blog: empty page body, no posts |
| starthere_dark_390.png | /start-here/ (live, no posts), dark, 390px | Same as blog: empty page body, no posts |
| starthere_light_1440.png | /start-here/ (live, no posts), light, 1440px | Same as blog: empty page body, no posts |
| starthere_light_390.png | /start-here/ (live, no posts), light, 390px | Same as blog: empty page body, no posts |
