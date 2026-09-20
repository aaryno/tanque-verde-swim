# 2026-27 landing page — mobile layout fix

**Branch:** `worker/tv-swim-landing-2026-09-20` (PR #3, on top of `0d1c513a`)
**Scope:** layout only. No swim result, swimmer name, meet, date or record value was
touched, and the page's content and section structure are unchanged.

> **Second pass.** The first pass fixed the schedule (commit `bdd5444`, kept) but
> *asserted* that the reported `<h1>`/paragraph clipping was a harness artifact without
> demonstrating it, and proved "no other page moved" from a **sample of nine** pages.
> Both gaps are closed below: the harness artifact is now **reproduced on demand with
> committed screenshots**, the dispatch's ⭐ control page is shown to have been **equally
> affected**, and the no-movement proof now covers **all 62 pages of the site**. The
> tooling that produced every number is committed under `artifacts/tools/`.

---

## Item 3 — "a clipped `<h1>` suggests something is forcing a width. Find what."

**What is forcing a width: the measuring harness, not the page.** Three independent
lines of evidence, each re-runnable.

### 1 · The reported symptom reproduces exactly — and only — at a 500px layout viewport

The dispatch rendered "at 390x2800 via headless Chrome". Run literally on this machine
(`artifacts/tools/repro_clamped_harness.py`), Chrome **refuses the requested window
width**:

```
$ chrome --headless=new --window-size=390,2800 http://127.0.0.1:8801/index.html
document.documentElement.clientWidth = 500      <-- asked for 390
window.innerWidth                    = 500
screenshot size                      = (500, 4585)
h1   left=8  right=492
lead left=9  right=491
```

Chrome on macOS clamps a window to a platform minimum, so `--window-size=390` lays out at
**500px** and the capture is 500px wide. Crop that 500px render down to 390 — which is
what a "390px screenshot" from this harness amounts to — and you get the dispatch's three
symptoms, precisely:

| file | what it shows |
|---|---|
| `repro-harness-index-500px-uncropped.png` | the real render: `Tanque Verde High School` **whole**, centred, with margin on both sides |
| `repro-harness-index-500px-cropped-to-390.png` | the same pixels cropped to 390: `...High Schoo` **clipped mid-word**, the lead paragraph running off the edge, the schedule's `Where` column gone |

The `<h1>` is centred, so a crop bites into the middle of a word. That is why it looked
like a page defect rather than a cropped capture.

### 2 · The ⭐ control does not exonerate the harness — it was cropped too

The dispatch's strongest argument was that `/records/overall.html` "lays out perfectly at
the IDENTICAL width and settings". It does not. Run through the **same** clamped harness:

```
/records/overall.html   clientWidth = 500   elements extending past x=390: 4
    <H3> 9..491   'Boys Relay Records'
    <H3> 9..491   'Girls Relay Records'
    <P>  8..492   '© 2026 Tanque Verde High School Swimming'
    <P>  8..492   'Generated on September 20, 2026 | ...'
```

The control renders at 500px and loses content to a 390 crop as well — see
`repro-harness-control-overall-500px-cropped-to-390.png`, where the **Boys/Girls toggle in
the navbar is sliced in half at the right edge**. It merely *looked* clean because record
cards are left-weighted: grade, time and athlete all sit in the first 200px, so the crop
removes empty margin. The landing page's centred hero had something there to lose.

So "the control is fine, therefore it is the page" does not hold. Both pages were being
measured at 500px; only one of them showed it.

### 3 · At a true 390px viewport the heading and paragraph never overflow — at any phone width

Measured with CDP `Emulation.setDeviceMetricsOverride {mobile: true}`
(`artifacts/tools/measure_mobile_layout.py`), on the **unfixed** page `0d1c513`:

| viewport | `h1` right edge | `scrollWidth` | elements past an edge |
|---|---|---|---|
| 320 | 312 | 320 | 1 — the schedule date |
| 360 | 352 | 360 | 1 — the schedule date |
| 375 | 367 | 375 | 1 — the schedule date |
| **390** | **382** | **390** | **1 — the schedule date** |
| 412 | 404 | 412 | 1 — the schedule date |
| 430 | 422 | 430 | 1 — the schedule date |
| 576 | 550 | 576 | 0 |

The `<h1>` right edge is always `viewport − 8` (the container's padding). It has
`white-space: normal`, `overflow-x: visible`, and `scrollWidth == clientWidth` — it is not
clipped, not truncated, and not overflowing. Same for both `p.lead` elements. Across every
width the **only** element outside the viewport was the schedule date, which is the defect
that was fixed.

### 4 · CSS audit — nothing forces a width on the hero

- `grep -n "min-width:" docs/css/style.css` → 5 hits: `.grade-badge` (2.5rem),
  `.relay-*` rank chips (30px / 25px), `.split-*` (3rem). **None is an ancestor of the
  `<h1>`**, and a `min-width` on a badge cannot widen a block-level heading.
- `body { max-width: 100vw }` (style.css:94) is a **cap, not a floor** — it can only make
  the page narrower, never wider than the viewport.
- The dispatch flagged two `white-space: nowrap` rules to check. Both are irrelevant to
  this markup:
  - style.css:264 → `.relay-line-1 .date-value` — the landing page has no `.relay-line-1`.
  - style.css:740 → `.top10-time` — the landing page has no `.top10-time`.

  (The nowrap that *did* matter was Bootstrap's `.text-nowrap` on the schedule's date
  cell, interacting with the 32px grid track — analysed below, and fixed.)

### 5 · The hero pixels are byte-identical before and after

Strongest single statement that item 3 needed no code change: the hero region of the
landing page rendered at a true 390px viewport, before and after the fix, is the **same
PNG**:

```
3e09814894de58e5...  artifacts/screenshots/true390-before-index-hero.png
3e09814894de58e5...  artifacts/screenshots/true390-after-index-hero.png
```

**Conclusion on item 3: there is no heading or paragraph overflow to fix.** Changing the
hero would have been a change with no defect behind it, on a page whose content was
reviewed and approved. The finding is recorded instead, with the means to re-check it.

### 6 · Other real-user states, all clean

States the first pass never exercised, on the fixed page:

```
portrait 390, hero expanded        vw= 390 scrollW= 390  CLEAN
portrait 390, hero COLLAPSED       vw= 390 scrollW= 390  CLEAN     (returning visitor)
portrait 320, hero COLLAPSED       vw= 320 scrollW= 320  CLEAN
landscape 844x390                  vw= 844 scrollW= 844  CLEAN
portrait 390, all sections toggled vw= 390 scrollW= 390  CLEAN
```

---

## What was actually wrong

Measured, not inferred, at a **true 390 x 844 mobile viewport** (Chrome via CDP
`Emulation.setDeviceMetricsOverride`, `mobile: true`), against a local server of `docs/`.

`scripts/generate_landing_page.py` emitted the schedule as:

```html
<table class="table table-sm align-middle">
```

Every other table on the site declares a **shape class** — `table-5col`, `table-6col`,
`table-relay`, `table-comparison` — and `docs/css/style.css` keys the mobile
stacked-card layout off that class inside `@media (max-width: 576px)`. The schedule
declared none, so it fell into the *generic* card grid at style.css:1418:

```css
.table:not(.table-relay) tbody tr {
  display: grid;
  grid-template-columns: 32px 1fr auto;   /* Grade/Rank | Time | ... */
}
```

That grid is shaped for **record** tables. A 3-column `Date | Meet | Where` table lands
in the wrong slots. Measured on the `Oct 23-24` row:

| cell | lands in | measured result |
|---|---|---|
| `Date` (`.text-nowrap`) | the fixed **32px** first track, `display:flex; justify-content:center` | `<strong>Oct 23-24</strong>` is **70.6px** wide in a **32px** track, centred, so it spills ~19px past each side: `left = -2.3px` |
| `Meet` | the **Time** slot | typeset `Courier New, 18.4px, rgb(44,95,45)` — meet names rendered as if they were swim times |
| `Where` | the **Athlete** slot (`grid-column: 2 / 4`) | third track computed to `0px`; the column had no track of its own |

The date spilling to `left = -2.3px` is the real damage. `body { max-width: 100vw }`
carries the deliberate comment *"NO overflow-x - it breaks sticky positioning on Safari"*
(style.css:95), so that spill is **clipped, not scrollable** — the character is simply
gone. `Oct 23-24` rendered on a phone as `ct 23-2`. Content loss, not just ugliness.

### One correction to the reported defect

The dispatch also reported the `<h1>` clipped mid-word and the season paragraph running
off the viewport. **Those were a harness artifact, not page defects** — reproduced,
measured and falsified against the ⭐ control in *Item 3* at the top of this document.
The clamp figure there (**500px**) supersedes the `485px` quoted in commit `bdd5444`'s
message: the exact minimum depends on the machine, the point is that it is not 390.
`before-index-390-clamped485-harness-artifact.png` is the original misleading capture,
kept for the record; every other `true390-*` screenshot is a real 390px viewport.

The schedule was the only genuine defect, and the dispatch's named likely cause was
correct.

---

## The change

**Two files, plus the regenerated page.**

1. `scripts/generate_landing_page.py` — added the shape class, so the next render keeps it:

   ```diff
   -                <table class="table table-sm align-middle">
   +                <table class="table table-sm align-middle table-schedule">
   ```

   `docs/index.html` was **not** hand-edited; it was regenerated by
   `python3 scripts/generate_website.py`.

2. `docs/css/style.css` — one new section inside the **existing**
   `@media (max-width: 576px)` block, placed with the other shape sections (after
   `.table-comparison`, before `.table-relay`). It gives the schedule card a single
   full-width column: date on its own line, meet name + badge, note, then venue with the
   same `📍` pin the record cards already use for location.

### Why this is the site's existing convention, not a new one

The site already has exactly this mechanism, used four times: **a table shape declares
itself with a class, and the 576px block has a section for that shape.** `.table-relay`
opts out of the card grid for colspan support; `.table-comparison` opts a 3-column
`Event | Boys | Girls` table out of it because the record-card slots don't fit it either.
The schedule is the same situation — a 3-column non-record table — and gets the same
treatment. Nothing was invented; a fifth shape was registered.

Two alternatives I rejected:

- **Adding `overflow-x: auto`** to the table wrapper. Explicitly ruled out: style.css:95
  records that this reintroduces a Safari sticky-positioning bug. `.table-responsive` is
  already set to `overflow: visible` at this breakpoint for that reason, and I left it so.
- **Extending the shared selectors** to `.table:not(.table-relay):not(.table-schedule)`,
  mirroring how `.table-relay` opts out. This is arguably the more native mechanism, but
  it edits 8 selectors that style 60+ existing pages, and "no other page moved" would then
  rest only on screenshots. The additive, scoped block cannot touch another page *by
  construction* (see proof below), so I took that instead.

---

## Validation

### Determinism — not regressed

Re-run in this pass, from a clean tree:

```
$ git status --short          # clean before
$ python3 scripts/generate_website.py     # run 1
$ git status --short          # STILL CLEAN -- the committed docs/index.html is
                              # exactly what the generator produces (item 5)
$ cp -R docs /tmp/gen1
$ python3 scripts/generate_website.py     # run 2
$ diff -r /tmp/gen1 docs
(no output)
IDENTICAL: all 133 files byte-for-byte
```

The clean `git status` after run 1 is the proof for **item 5**: the markup fix lives in
`scripts/generate_landing_page.py`, not in hand-edited HTML, so the next render cannot
erase it.

### `verify_oldest_record()` still returns `oldest`

Build output, second run:

```
🏠 Generating Season Landing Page...
  oldest-record check: oldest -> "the oldest record on the Tanque Verde boys books"
  next-oldest standing boys record: 50 Freestyle (Oct 23, 2021)
```

And the superlative is still printed on the page:

> The open school record he took down — 5:04.10, set by Joseph Breinholt on Oct 24, 2015 —
> was **the oldest record on the Tanque Verde boys books**. It had stood longer than any
> other boys school record, individual or relay. The next-oldest still standing is the
> 50 Freestyle record from Oct 23, 2021.

### The overflow is gone

At a true 390px viewport, after the fix:

```
document.documentElement.scrollWidth = 390   (viewport 390)
elements past either viewport edge: (none)

ok  "Sep 3"      L=21 R=58        ok  "Oct 15"     L=21 R=65
ok  "Sep 10"     L=21 R=66        ok  "Oct 17"     L=21 R=65
ok  "Sep 19"     L=21 R=66        ok  "Oct 23–24"  L=21 R=90
ok  "Sep 24"     L=21 R=66        ok  "Oct 29"     L=21 R=65
ok  "Oct 1"      L=21 R=56        ok  "Nov 6–7"    L=21 R=76
```

All ten dates fully inside the viewport (was `left = -2.3px`). The meet-name cell is back
to body type: `"Segoe UI", ... 15.2px, weight 600` (was `Courier New 18.4px green`).

Checked across widths — `scrollWidth` equals the viewport and zero elements overflow at
**320, 360, 390, 430, 576, 577, 768 and 1280px**.

### Proof that no other page moved

Three independent arguments:

1. **The class exists on one page.** `grep -rln 'table-schedule' docs/ scripts/` returns
   exactly `docs/css/style.css`, `docs/index.html`, `scripts/generate_landing_page.py`.
   No other page carries the class, so the new rules cannot select anything on one.
2. **The CSS is confined to mobile.** All 7 occurrences of `table-schedule` in style.css
   are inside `@media (max-width: 576px)` (verified by brace-matching the file). Above
   576px the class selects nothing at all.
3. **Every page of the site re-rendered, and 61 of 62 are the same PNG.** Not a sample —
   the whole site. Each non-archive page was rendered at a true 390px mobile viewport
   before (`0d1c513`) and after (`bdd5444`) and the full-page PNGs hashed
   (`artifacts/tools/render_all_pages.py`):

   | section | pages | pixel-identical | changed |
   |---|---|---|---|
   | `/` (the landing page) | 1 | 0 | **1 — intended** |
   | `/records/` | 5 | 5 | 0 |
   | `/top10/` | 40 | 40 | 0 |
   | `/annual/` | 15 | 15 | 0 |
   | `/seniors/` | 1 | 1 | 0 |
   | **total** | **62** | **61** | **1** |

   Spot values, SHA-256 of the full-page PNG:

   | page | before | after | |
   |---|---|---|---|
   | `/index.html` | `10e81efa1119a0d9` | `5e4f9e3712b11455` | changed (intended) |
   | `/records/overall.html` ⭐ | `bced5b5bfcf2dc3c` | `bced5b5bfcf2dc3c` | identical |
   | `/records/boys-bygrade.html` | `c3f19f09cff9bd8d` | `c3f19f09cff9bd8d` | identical |
   | `/records/boys-relays.html` | `a8cd520819606fc0` | `a8cd520819606fc0` | identical |
   | `/top10/boys-alltime.html` | `ccd1e2317a7d1370` | `ccd1e2317a7d1370` | identical |
   | `/annual/2026-27.html` | `0cff69ac70f05c00` | `0cff69ac70f05c00` | identical |
   | `/seniors/class-of-2026.html` | `5905b71b4f0e0025` | `5905b71b4f0e0025` | identical |

   That covers every shape in the stylesheet — `.table-5col`, `.table-6col`,
   `.table-relay`, `.table-comparison` — and the hand-maintained seniors page.
   The only page whose pixels moved is the one the order asked me to fix, and within it
   the only region that moved is the schedule (the hero crop is byte-identical, above).

   Independently: a full `generate_website.py` run rewrote all 133 files and git reports
   **one changed line** across the whole of `docs/` (the class attribute in `index.html`).

#### One pre-existing condition, observed and left alone

`/annual/*.html` has 5 elements a few px outside the viewport at 320–430px — Bootstrap
`.row` negative gutter margins (`left = -3px`). It measures **identically before and
after** my change, `scrollWidth` still equals the viewport, and it is not the landing
page. Out of scope for a landing-page layout fix; flagged here so it is on the record
rather than silently absorbed into my before/after.

#### A second pre-existing condition, for Aaryn — not changed here

Every page on the site, the new landing page included, ships:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0,
      maximum-scale=1.0, user-scalable=no">
```

`maximum-scale=1.0, user-scalable=no` **disables pinch-zoom on a phone**. Given that this
order exists because Aaryn and the parents read this site on a phone, that is worth
knowing: a parent who cannot read the 13.6px venue line has no way to enlarge it.

It is **not** a regression from this PR — it is in all four generators
(`generate_website.py:111`, `generate_annual_pages.py:754`,
`rebuild_relay_pages.py:268`, `generate_landing_page.py:192`) and on all **62** pages, so
the landing page is following the site's existing convention, which is what this order
asked for. Removing it would change every page on the site, which this order explicitly
forbids. Flagged for a separate decision, deliberately left alone.

### No record data touched

```
$ git diff --stat -- records/ data/
(no output — untouched)
```

Full changed-file list: `docs/css/style.css`, `docs/index.html`,
`scripts/generate_landing_page.py`.

---

## Screenshots

In `artifacts/screenshots/`. Everything prefixed `true390-` is a **real** 390px mobile
viewport; everything prefixed `repro-harness-` is the clamped 500px harness, kept
deliberately so the item-3 finding is checkable rather than asserted.

**The defect and the fix** (true 390px):

| file | what |
|---|---|
| `before-index-schedule-390.png` | **before** — schedule: dates clipped off the left edge, meet names typeset as monospace green swim times |
| `after-index-schedule-390.png` | **after** — stacked cards: date, meet + badge, note, 📍 venue |
| `true390-before-index-full.png` / `true390-after-index-full.png` | the whole landing page, before and after |
| `true390-before-index-hero.png` / `true390-after-index-hero.png` | the hero — **byte-identical**, `3e09814894de58e5…`; item 3 needed no change |

**Item 3 — the harness artifact, reproduced**:

| file | what |
|---|---|
| `repro-harness-index-500px-uncropped.png` | `--window-size=390` actually renders 500px wide; the `<h1>` is whole |
| `repro-harness-index-500px-cropped-to-390.png` | the same pixels cropped to 390 — the reported `...High Schoo` mid-word clip, reproduced on demand |
| `repro-harness-control-overall-500px-uncropped.png` | the ⭐ control in the same harness — also 500px |
| `repro-harness-control-overall-500px-cropped-to-390.png` | control cropped to 390 — the **Boys/Girls toggle is sliced in half**; it was cropped too, it just had nothing to lose |
| `before-index-390-clamped485-harness-artifact.png` | the first pass's clamped capture, kept for continuity |

**Controls, before and after, true 390px** (each pair byte-identical):

| file | |
|---|---|
| `true390-before-overall.png` / `true390-after-overall.png` | ⭐ `/records/overall.html`, the control named in the dispatch |
| `true390-before-top10-boys-alltime.png` / `true390-after-top10-boys-alltime.png` | `/top10/` |
| `true390-before-annual-2026-27.png` / `true390-after-annual-2026-27.png` | `/annual/` |

The other 56 control pages are not shipped as images — every before/after pair is
byte-identical, so a second copy tells a reviewer nothing the hash table does not. Regenerate
any of them with the tooling below.

## Tooling (committed, so every number here is re-runnable)

`artifacts/tools/` — stdlib only, no pip install, drives the installed Google Chrome over
CDP:

| file | |
|---|---|
| `cdp.py` | minimal CDP client (raw-socket WebSocket; no `websockets` dependency) |
| `measure_mobile_layout.py` | renders one page at a true mobile viewport and reports every element outside it, plus named probes for the `h1`, leads, schedule and each date cell |
| `render_all_pages.py` | renders a list of pages at 390px and writes `hashes.json` — the 62-page proof |
| `repro_clamped_harness.py` | reproduces the dispatch's `--window-size=390` harness and reports the width Chrome actually used |

```bash
python3 -m http.server 8801 --directory docs &
python3 artifacts/tools/measure_mobile_layout.py http://127.0.0.1:8801/index.html
python3 artifacts/tools/repro_clamped_harness.py http://127.0.0.1:8801/index.html /tmp/x.png
```

## How to reproduce

```bash
python3 -m http.server 8801 --directory docs &
python3 artifacts/tools/measure_mobile_layout.py http://127.0.0.1:8801/index.html
```

⚠️ **`--window-size=390` is not a 390px viewport.** Chrome enforces a platform minimum
window width — 500px on this machine — and silently lays out wider than it captures, so a
"390px screenshot" taken that way is a 500px render cropped to 390. That is what produced
the `<h1>` clipping in the dispatch, and it will do it again to the next person who
measures this site that way. Use CDP `Emulation.setDeviceMetricsOverride
{width: 390, mobile: true}` (what `measure_mobile_layout.py` does), and check
`document.documentElement.clientWidth` is really 390 before trusting anything you see.

Then judge by `document.scrollingElement.scrollWidth` and by element rects against the
viewport, not by eye alone — a clipped capture and a clipped layout look identical in a
PNG, which is the whole lesson of this ticket.
