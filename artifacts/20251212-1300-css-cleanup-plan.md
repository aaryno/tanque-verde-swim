# CSS Cleanup Plan: Tanque Verde Swimming Website

**Created:** December 12, 2025  
**Based on:** CSS Audit Report  
**Goal:** Eliminate duplication, harmonize styles, improve maintainability

---

## Executive Summary

The website has **~255 lines of inline CSS** in each relay page that duplicates or overrides the main `style.css`. Key issues:

1. **Grade badges**: Two completely different color schemes (pastel in main CSS, saturated in relay pages)
2. **Expand arrows**: Two identical classes (`.expand-arrow` in main CSS, `.relay-arrow` inline)
3. **Relay splits**: Styles defined both inline and in main CSS
4. **Stroke abbreviations**: `.stroke-abbrev` / `.stroke-full` only defined inline

---

## Phase 1: Quick Wins (No Visual Change)

**Goal:** Remove duplication while maintaining current appearance. ~30 min work.

### Task 1.1: Move Missing Classes to `style.css`

Add these classes that only exist inline to the main CSS:

```css
/* Stroke name display (relay splits) - desktop shows full, mobile shows abbrev */
.stroke-abbrev {
  display: none;
}

.stroke-full {
  display: inline;
}

@media (max-width: 768px) {
  .stroke-abbrev {
    display: inline;
  }
  
  .stroke-full {
    display: none;
  }
}
```

### Task 1.2: Merge `.relay-arrow` into `.expand-arrow`

The `.relay-arrow` class in relay pages is identical to `.expand-arrow` in main CSS:

```css
/* Both have same styling - just use .expand-arrow everywhere */
.expand-arrow, .relay-arrow {
  font-size: 0.7rem;
  color: #999;
  transition: transform 0.2s ease;
}
```

### Task 1.3: Add Relay Table Base Styles to `style.css`

These styles exist inline but should be in main CSS:

```css
/* Relay row interactivity */
.relay-row {
  cursor: pointer;
}

.relay-row:hover {
  background-color: #e8f5e9 !important;
}

.table-row-alt {
  background-color: #f8f9fa;
}

/* Details row toggle */
.relay-details-row {
  display: none !important;
}

.relay-details-row.show {
  display: table-row !important;
}

.relay-details-row td {
  background: #f8f9fa !important;
  padding: 0.75rem 1rem !important;
  text-align: left !important;
}
```

---

## Phase 2: Resolve Grade Badge Divergence

**Goal:** Pick ONE color scheme for grade badges. ~15 min work.

### Current Conflict

**Main CSS (pastel, outlined):**
```css
.grade-fr { background: #e3f2fd; color: #1565c0; border: 1px solid #90caf9; }
.grade-so { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
.grade-jr { background: #fff3e0; color: #e65100; border: 1px solid #ffcc80; }
.grade-sr { background: #fce4ec; color: #c2185b; border: 1px solid #f48fb1; }
```

**Relay Pages (saturated, no border):**
```css
.grade-fr { background: #28a745; color: white; }
.grade-so { background: #17a2b8; color: white; }
.grade-jr { background: #ffc107; color: #333; }
.grade-sr { background: #dc3545; color: white; }
```

### Recommendation: Keep Pastel (Main CSS)

**Reasons:**
- Better readability on both light and dark backgrounds
- Softer aesthetic fits the site's overall design
- Already used on more pages (only relay pages override)

**Action:** Remove grade badge overrides from relay pages (lines 140-158).

---

## Phase 3: Strip Inline Styles from Relay Pages

**Goal:** Remove the `<style>` blocks from `girls-relays.html` and `boys-relays.html`. ~20 min work.

### What to Remove

Both files have ~255 lines of inline CSS (lines 18-275). After completing Phases 1 and 2, we can remove this entire block.

### What to Keep

The files also have Bootstrap and main CSS imports - keep those:

```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
```

### HTML Class Updates

In the relay pages, change:
- `.relay-arrow` → `.expand-arrow` (if not aliased in CSS)

---

## Phase 4: Generator Script Updates

**Goal:** Ensure `rebuild_relay_pages.py` generates clean HTML without inline styles.

### Files to Modify

1. `rebuild_relay_pages.py` - Remove inline style block generation
2. Verify the HTML template doesn't embed styles

---

## Implementation Checklist

### Step 1: Update `style.css` (Add missing classes)
- [ ] Add `.stroke-abbrev` / `.stroke-full` with mobile toggle
- [ ] Add `.relay-row` hover and cursor styles
- [ ] Add `.relay-details-row` toggle styles
- [ ] Add `.table-row-alt` striping style
- [ ] Alias `.relay-arrow` to `.expand-arrow` OR add `.relay-arrow` styles

### Step 2: Choose Grade Badge Scheme
- [ ] Decision: Keep pastel (main CSS) - **Recommended**
- [ ] Document the decision in a CSS comment

### Step 3: Clean Relay Pages
- [ ] Remove `<style>` block from `girls-relays.html` (lines 18-275)
- [ ] Remove `<style>` block from `boys-relays.html` (lines 18-275)
- [ ] Test pages still render correctly

### Step 4: Update Generator
- [ ] Modify `rebuild_relay_pages.py` to not output inline styles
- [ ] Regenerate relay pages to verify

### Step 5: Test
- [ ] Desktop view - all pages
- [ ] Mobile view - relay pages specifically
- [ ] Expand/collapse functionality
- [ ] Grade badge colors consistent across site

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `docs/css/style.css` | ADD classes | +40 lines |
| `docs/records/girls-relays.html` | REMOVE inline styles | -257 lines |
| `docs/records/boys-relays.html` | REMOVE inline styles | -257 lines |
| `rebuild_relay_pages.py` | UPDATE template | TBD |

---

## Future Improvements (Out of Scope)

These are identified in the audit but not critical for this cleanup:

1. **Consolidate time display classes** - 9+ classes doing similar things
2. **Consolidate date display classes** - 4+ classes for dates
3. **Consolidate swimmer name classes** - 6+ different patterns
4. **Add table type classes to annual pages** - Fix mobile font issue
5. **Document PB badge thresholds** - Add CSS comments explaining gradient

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Relay pages look different after cleanup | Test in browser before committing |
| Generator overwrites clean HTML | Update generator first OR after |
| Mobile layout breaks | Test on real device or DevTools |
| Grade badge color change noticed | Minimal - relay pages rarely viewed |

---

## Time Estimate

| Phase | Estimated Time |
|-------|----------------|
| Phase 1: Quick Wins | 30 minutes |
| Phase 2: Grade Badges | 15 minutes |
| Phase 3: Strip Inline Styles | 20 minutes |
| Phase 4: Generator Updates | 30 minutes |
| Testing | 15 minutes |
| **Total** | **~2 hours** |

---

*Plan created as part of CSS harmonization initiative*

