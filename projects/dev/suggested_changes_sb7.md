# Suggested Changes — `spacex.md` to SQLModel-style Tutorial Flow

Analysis of the SQLModel (`sqlmodel.tiangolo.com`) and FastAPI tutorial styles mapped to
your current `spacex.md` and SB7 BrandScript. Each suggestion names the SQLModel pattern
it borrows and the SB7 element it serves.

---

## What Makes the SQLModel Tutorials Work

Before the suggestions, it is worth naming the patterns explicitly. The SQLModel docs
are aspirational because they do three things your current tutorial does not:

1. **Problem-first teaching.** Every feature is introduced by showing what breaks without
   it. The reader feels the pain before they see the fix. This is SB7 **Character + Problem**.
2. **Scaffolded voice.** Tiangolo writes as if he is sitting next to you. "Oh, no! Let's
   understand that better." "A mental trick you can use to remember..." This is SB7 **Guide**.
3. **Earned celebration.** Each section closes with a small win. "Now you know how to
   handle nested JSON. " This is SB7 **Success** at the micro level — not just at the end.

Your current tutorial explains the solution well. It does not yet make the reader feel the
problem, hear a guide, or feel the wins as they go.


## 2. Introduce Each Section with a Rhetorical Question

**SQLModel pattern:** Section headers are often framed as questions the reader is already
asking. "So, what is that `back_populates` argument?" "Why Aren't We Getting More Data?"
This makes the reader feel understood before the explanation starts.

**Current state:** Section headers are descriptive labels — "3.1 safe_get()", "4. Transform".
They tell you what is there, not why you need it.

**Suggestion — add a one-sentence question or hook after each `##` heading:**

- Section 3.1: *"APIs are inconsistent. How do you stop one bad record from crashing the
  whole pipeline?"*
- Section 3.2: *"The API returns 100 records at a time. How do you get all of them without
  writing the same loop twice?"*
- Section 4: *"The data comes back as deeply nested JSON. How do you flatten it into clean
  rows your team can actually use?"*

These do not need to be long. One sentence each is enough to make the reader lean in.

**SB7 element:** Character, Internal Problem (they feel stuck), Guide (you understand
what they are about to encounter).

---

## 3. Use "Notice That..." Callouts Instead of Annotation Popups for Key Moments

**SQLModel pattern:** Tiangolo uses a recurring "Notice that..." sentence inline to pull
the reader's eye to the single most important thing on a code block. It is conversational,
not a formal admonition. "Notice that we have Spider-Boy there — that means the relationship
loaded correctly." This creates a guide voice without breaking the flow.

**Current state:** Key observations are buried either in annotation popups (easy to miss)
or in dense prose after the block.

**Suggestion:** After each major code block, add one "Notice that..." sentence before any
further explanation. Examples:

- After the `SpaceXLaunch` model: *"Notice that every field is `str | None = None` except
  `launch_name`. That one missing name is the only thing that should stop a record entirely."*
- After `safe_get`: *"Notice that the function never raises an exception. It returns `None`
  and lets the model decide whether that is acceptable — separation of concerns."*
- After `parse_launch`: *"Notice that validation happens in a single line. If the data does
  not fit the contract, you find out here — not three steps downstream in someone else's
  dashboard."*

**SB7 element:** Guide (Authority — you have seen these details, you know which ones matter).

---

## 4. Show the Failure Before the Fix in Section 3.1 (safe_get)

**SQLModel pattern:** The `back_populates` page shows the broken version first — the code
without `back_populates`, the unexpected output — and only then introduces the fix. The
reader experiences the problem, not just reads about it.

**Current state:** `safe_get` is introduced as a solution. The problem (KeyError on nested
JSON) is described in prose but never demonstrated.

**Suggestion — add a "before" code block:**

```markdown
### The problem it solves

Here is what happens without it:

```python
rocket_family = launch["rocket"]["configuration"]["families"][0]["name"]
```

If `families` is an empty list, or `configuration` is `null`, this raises a `TypeError`
and your entire script stops. One bad record out of 300 ends the run.

Then introduce `safe_get` as the fix. The contrast does the teaching for you.

This mirrors the insurance analogy you already have ("Ever been sent an excel file with
missing data") but makes it executable — the reader can see the crash, not just imagine it.

**SB7 element:** External Problem, Failure, Guide (Empathy — "I know this one").

---

## 5. Add a "Mental Trick" Block for the SQLModel Schema Section

**SQLModel pattern:** Tiangolo uses a "mental trick" sentence to make abstract concepts
sticky. "A mental trick you can use to remember: `back_populates` must match the attribute
name on the other model." Simple, but it makes the concept transferable.

**Current state:** Section 2 explains what each field group does but gives no memory hook
or mental model for the `str | None = None` pattern.

**Suggestion — add a tip admonition after the schema:**

```markdown
!!! tip "Mental model for optional fields"
    Ask yourself: "If this field is missing, should the whole record be rejected?"
    If yes — remove the `None` default. If no — keep it.
    In this dataset, only `launch_name` is non-negotiable. Everything else is best-effort.
```

This is the kind of rule a senior analyst would tell a junior over their shoulder — which
is exactly the Guide role in SB7.

**SB7 element:** Guide (Authority + Plan — giving them a reusable decision framework).

---

## 6. Close Each Major Section with a Small Win

**SQLModel pattern:** Sections end with a short celebratory or affirming sentence. "Now
you know how to use `back_populates`. " "That's it, you can now filter by multiple
conditions." These micro-successes build momentum and keep the reader going.

**Current state:** Sections end when the explanation ends. There is no emotional punctuation.

**Suggestion:** Add one closing sentence per major section (##) that names what the reader
now has:

- After Section 2: *"The schema is the contract. Everything from here builds on it."*
- After Section 3: *"You now have two tools that make every messy API more manageable."*
- After Section 4: *"Every API record is now mapped, validated, and either accepted or
  rejected cleanly."*
- After Section 5: *"The pipeline is complete. Run it once, get a clean CSV."*

These do not need emojis. The tone is yours — but the rhythm is borrowed from SQLModel.

**SB7 element:** Success (at the micro level, building to the final "What You've Built").

---

## 7. Replace the Duplicate Annotation Pattern with Inline Teaching Prose

**SQLModel pattern:** Code blocks are short and focused. The teaching happens in the prose
around them — not in popups that the reader may never click. When Tiangolo wants to explain
a line, he writes a sentence pointing at it, not a numbered popup.

**Current state:** The `--8<--` annotation include pulls in popup content, and then the
prose below repeats the same content. The reader sees every explanation twice. This makes
the page feel like documentation, not teaching.

**Suggestion — Option A (recommended):**

Keep the annotation popups for quick technical reference. Rewrite all the prose below each
code block to add _context_ rather than restate the explanation. The popup answers "what
does this do." The prose answers "why does this matter and where will you use this again."

Example rewrite for the prose after `safe_get`:

Before (current): *"The function takes `data` (a dict or list), a `*keys` path, and a
`default` value..."*

After: *"The reason this function exists is that APIs lie. A field that appears in 99% of
records will be missing from the other 1%. Without `safe_get`, that 1% ends your run. With
it, you get a `None` and the model decides what to do — which is where the decision belongs."*

**SB7 element:** Guide (teaching through experience, not specification).

---

## 8. Add "Full File Preview" Expandable Sections

**SQLModel pattern:** Every code snippet is accompanied by a "Full file preview" link or
expandable block. This keeps individual examples short and focused while giving readers
who want the full context a path to get it.

**Current state:** The "sneak peak at all the code" collapsible at the top covers this, but
it appears before the reader knows why they should care. It also uses a line range include
for the whole file, which is not broken into sections.

**Suggestion:**

Move the full-file collapsible to the bottom as "The complete script" rather than the top.
Add a brief "Full section preview" collapsible at the end of each major section (2, 3, 4, 5)
showing only the code for that section — using the existing `--8<--` line range syntax you
already have.

This mirrors the SQLModel pattern of "here is the focused snippet, here is the full context
if you want it" without requiring the reader to hold the whole file in their head.

**SB7 element:** Plan (clarity — the reader always knows where they are and how the pieces
connect).

---

## 9. Add Domain Transfer Callouts at Four Specific Points

**SQLModel pattern:** Tiangolo regularly steps back to say "this pattern works anywhere" —
not just in his toy example. It makes the tutorial feel like training, not a one-off demo.

**Current state:** The insurance domain transfer is mentioned in the intro and the closing
"What You've Built" section but absent throughout the body. The reader has to make the leap
themselves.

**Suggestion — four `!!! tip` admonitions:**

After Section 2 (Schema):
> Think of this as designing a bordereaux or claims extract template — you decide the
> columns and types before any data arrives. The schema is the agreement, not the result.

After Section 3.1 (safe_get):
> This is the same problem you face when a broker submission has missing fields. Rather
> than crashing the whole import, you handle gaps gracefully and keep the pipeline running.

After Section 4 (Transform):
> Flattening nested JSON into a validated flat table is exactly what you do when you
> process a Lloyd's market message or a reinsurance slip into your data warehouse.

After Section 5.1 (get_spacex_data):
> The cache-first pattern here — read from file if it exists, call the API if it does not —
> mirrors how you avoid re-querying a slow actuarial database when the underlying data
> has not changed.

**SB7 element:** Plan + Philosophy (neutral dataset, insurance professionals apply it
themselves).

---

## 10. Fix the Broken CTA and Typos

The newsletter CTA at the bottom uses `(#)` as a dead link. This needs a real URL or
a MkDocs anchor once the newsletter signup section exists on the site.

Typos identified in the current file:

| Location | Issue |
|---|---|
| Line 15 | "stastic" -> "static" |
| Line 18 | "sneak peak" -> "sneak peek" |
| Line 136 | "launch_stauts_id" -> "launch_status_id" (prose description) |
| Line 145 | "opererator_name" -> "operator_name" |
| Line 155 | "contect" -> "context" |
| Line 160 | "trying th accomplish" -> "trying to accomplish" |
| Line 209 | "previes" -> "preview" |
| Line 219 | Missing closing quote: `"Falcon 9` -> `"Falcon 9"` |
| Line 227 | Unclosed backtick mid-sentence |
| Section 3.2 | Header numbered 3.1 again — should be 3.2 |

---

## Summary — Priority Order

| # | Change | SQLModel Pattern | SB7 Element | Effort |
|---|---|---|---|---|
| 1 | Problem-first opening with fragile code example | Show broken before fixed | Character, Problem, Failure | Medium |
| 2 | Rhetorical question openers per section | "Why aren't we getting...?" | Character, Internal Problem | Low |
| 3 | "Notice that..." inline callouts on key code | Inline attention direction | Guide (Authority) | Low |
| 4 | Before/after for safe_get | Broken code then fix | Problem, Failure, Guide | Medium |
| 5 | "Mental trick" tip block for optional fields | Mental framework sentence | Guide, Plan | Low |
| 6 | Small-win closing sentence per section | Micro-celebration per section | Success (micro) | Low |
| 7 | Rewrite post-code prose as context not restatement | Teaching prose not docs | Guide (voice) | Medium |
| 8 | Full file preview collapsibles per section | Full file preview pattern | Plan (clarity) | Low |
| 9 | Domain transfer admonitions x4 | "This pattern works anywhere" | Plan, Philosophy | Low |
| 10 | Fix CTA link and typos | — | Quality | Low |
