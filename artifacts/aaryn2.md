# Relay Table Mobile Layout Fix - Agent Handoff

**Date:** December 11, 2025  
**Issue:** Expanded relay content appearing in wrong column; green oval badges on rank numbers  
**Root Cause:** Mobile CSS grid transformation breaking table colspan behavior

---

## The Problem

On mobile devices, the relay tables display incorrectly:
1. The rank number appears inside a green oval badge instead of as a plain bold number
2. The expanded swimmer details (stroke, name, split time) appear under column 1 (Rank) instead of spanning all columns
3. The layout is broken because `colspan="4"` is being ignored

---

## Root Cause Analysis

The main `style.css` file contains mobile styles that **transform table rows into CSS grid layouts**. This is likely around line 1145 or similar:

```css
@media (max-width: 768px) {
    .table tbody tr {
        display: grid;
        grid-template-columns: 32px 1fr auto;
        /* ... other grid styles ... */
    }
    
    .table tbody td {
        border: none;
        padding: 0;
    }
}
```

### Why This Breaks Relay Tables

When you set `display: grid` on a `<tr>`:

1. **`colspan` is completely ignored** - The HTML `<td colspan="4">` attribute only works when the element has `display: table-cell`. Once you change the `<tr>` to `display: grid`, each `<td>` becomes a grid item and colspan has no effect.

2. **The expanded content becomes a single grid cell** - Instead of spanning all 4 columns, the `<td colspan="4">` containing the swimmer details becomes just the first grid cell (under the Rank column).

3. **The green oval badge** - There's likely a style that adds `background-color`, `border-radius: 50%` or similar to create pill/oval badges for rank numbers, possibly using pseudo-elements or direct styling on `.rank-cell`.

---

## The Solution

### Option 1: Exclude Relay Tables from Grid Transformation (Recommended)

Find every instance in `style.css` where `.table` rows are converted to grid, and add `:not(.table-relay)` to exclude relay tables:

**Before:**
```css
@media (max-width: 768px) {
    .table tbody tr {
        display: grid;
        grid-template-columns: 32px 1fr auto;
    }
}
```

**After:**
```css
@media (max-width: 768px) {
    .table:not(.table-relay) tbody tr {
        display: grid;
        grid-template-columns: 32px 1fr auto;
    }
}
```

### Option 2: Override with Higher Specificity (Current Fix)

The `relay-table-fix.css` file uses `!important` declarations to force relay tables back to proper table display:

```css
@media (max-width: 768px) {
    .table-relay tr,
    .table-relay .relay-row {
        display: table-row !important;
    }
    
    .table-relay th,
    .table-relay td {
        display: table-cell !important;
    }
    
    .table-relay .relay-details-row.show {
        display: table-row !important;
    }
}
```

---

## Files That Need Changes

### 1. `docs/css/style.css`

Search for these patterns and add `:not(.table-relay)` exclusions:

- `.table tbody tr` with `display: grid`
- `.table tbody td` with grid-related styles
- `.table tr` or `.table td` mobile transformations
- Any rank/badge styling that creates ovals (look for `border-radius: 50%`, green backgrounds on rank cells)

### 2. `rebuild_relay_pages.py` (if regenerating)

The inline `<style>` block in the generated HTML already has correct styles, but they're being overridden by `style.css`. Either:
- Fix `style.css` to exclude relay tables (preferred)
- Or increase specificity in the Python-generated inline styles

### 3. Other table pages that might have similar issues

Any page using expandable rows with `colspan` will break if the mobile grid transformation is applied. Check:
- Individual event pages with expandable content
- Any tables with merged cells
- Tables that rely on `colspan` or `rowspan`

---

## Search Patterns to Find Problem Areas

In `style.css`, search for:

```
display: grid
display:grid
grid-template-columns
.table tbody tr
.table tr {
.table td {
@media.*768
```

Each match in a mobile media query that affects `.table` elements needs the `:not(.table-relay)` exclusion.

---

## Testing Checklist

After making changes, verify on mobile (or mobile emulator):

- [ ] Rank column shows plain bold numbers (no green oval)
- [ ] Clicking a relay row expands to show swimmer details
- [ ] Expanded content spans the full width of the table
- [ ] Swimmer rows show: `BK  Logan Radomsky SR    30.98` (stroke left, name left, time right)
- [ ] Meet name appears below swimmers, left-aligned
- [ ] Collapsing works correctly
- [ ] Desktop layout still works correctly

---

## Why The Fix Works

By forcing `display: table-row` and `display: table-cell` on relay table elements:

1. **`colspan="4"` works again** - Table-cell display respects the colspan attribute
2. **Expanded content spans full width** - The single `<td>` with colspan="4" now properly spans all columns
3. **Flexbox inside the cell works** - The `.relay-split-row` elements use flexbox for the stroke/name/time layout, which works fine inside a table-cell

The grid transformation is useful for other tables (converting them to card-like layouts on mobile), but it fundamentally breaks tables that rely on colspan for expandable rows.

---

## Summary

| Problem | Cause | Fix |
|---------|-------|-----|
| Green oval on rank | CSS styling `.rank-cell` with background/border-radius | Remove badge styles from `.table-relay .rank-cell` |
| Expanded content in wrong column | `display: grid` on `<tr>` ignores `colspan` | Exclude `.table-relay` from grid transformation |
| Layout broken | Grid cells don't merge like table cells | Force `display: table-row` / `display: table-cell` |

The cleanest fix is adding `:not(.table-relay)` to the grid transformation selectors in `style.css` rather than fighting specificity wars with `!important` overrides.