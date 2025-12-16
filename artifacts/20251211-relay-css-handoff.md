# Relay Page CSS Architecture - Handoff Document

**Date:** December 11, 2025  
**Issue:** Swimmer names in expanded relay details are center-justified instead of left-justified

## Overview

The relay records pages (`boys-relays.html`, `girls-relays.html`) display the top 10 relays for each event with expandable rows that show individual swimmer details including stroke, name, class badge, and split time.

## Files Involved

1. **`rebuild_relay_pages.py`** - Generates the HTML with inline `<style>` block
2. **`docs/css/style.css`** - Main site CSS that can override inline styles
3. **`docs/records/boys-relays.html`** / **`docs/records/girls-relays.html`** - Generated output

## HTML Structure

The expandable relay content has this structure:

```html
<tr class="relay-details-row">
    <td colspan="4">
        <div class="relay-expanded-rows">
            <div class="relay-split-row">
                <span class="split-stroke">
                    <span class="stroke-abbrev">BK</span>
                    <span class="stroke-full">Backstroke</span>
                </span>
                <span class="split-swimmer">Logan Radomsky <span class="grade-badge grade-sr">SR</span></span>
                <span class="split-time">30.98</span>
            </div>
            <!-- ... more swimmers ... -->
            <div class="relay-meet-row">Southern Arizona Regional Qualifier</div>
        </div>
    </td>
</tr>
```

## Current CSS Approach

### Inline Styles (in `rebuild_relay_pages.py`)

The script generates inline CSS in a `<style>` block at the top of each page:

```css
/* Desktop - show full stroke names */
.split-stroke {
    font-style: italic;
    color: #666;
    flex-shrink: 0;
    text-align: left;
    margin-right: 0.5rem;
}

.stroke-abbrev { display: none; }
.stroke-full { display: inline; }

.relay-split-row {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    padding: 0.25rem 0;
    border-bottom: 1px solid #eee;
    white-space: nowrap;
    gap: 0.25rem;
    text-align: left;
}

.split-swimmer {
    font-weight: 500;
    color: #333;
    margin-right: auto;  /* Push time to the right */
}

.split-time {
    font-family: 'Courier New', monospace;
    font-weight: bold;
    color: var(--tvhs-primary, #0a3622);
    min-width: 3rem;
    text-align: right;
}

/* Mobile */
@media (max-width: 768px) {
    .stroke-abbrev { display: inline; }
    .stroke-full { display: none; }
    
    .relay-split-row {
        gap: 0.2rem;
    }
    
    .split-stroke {
        margin-right: 0.3rem;
    }
}
```

### Main CSS Overrides (in `docs/css/style.css`)

The main CSS has mobile-specific styles that transform `.table` elements into a grid/card layout. These override the inline styles:

```css
/* Around line 1145 - Mobile table transforms */
@media (max-width: 768px) {
    .table tbody tr {
        display: grid;
        grid-template-columns: 32px 1fr auto;
        /* ... grid layout ... */
    }
    
    .table tbody td {
        border: none;
        padding: 0;
    }
}
```

**This is the problem.** The `.table` grid styles are being applied to the relay table rows, including the expanded content.

### Attempted Fix (around line 1278 in style.css)

Added overrides specifically for relay tables:

```css
/* Relay expanded content - override grid styles */
.table-relay .relay-details-row td {
    display: block !important;
    grid-row: auto !important;
    grid-column: auto !important;
    text-align: left !important;
    width: 100% !important;
    padding: 0.5rem !important;
    background: #f8f9fa !important;
}

.table-relay .relay-split-row {
    display: flex !important;
    justify-content: flex-start !important;
    text-align: left !important;
}

.table-relay .split-swimmer {
    text-align: left !important;
    margin-right: auto !important;
}
```

## The Core Problem

Despite multiple attempts, the swimmer names remain center-justified. The likely causes:

1. **CSS Specificity:** The main `style.css` rules may have higher specificity than the inline styles or the override rules
2. **Grid Context:** When `.table tbody tr` becomes a grid, child elements may inherit centering
3. **Cascade Order:** The main CSS loads after inline styles and may override them
4. **Hidden Inheritance:** There may be a `text-align: center` on a parent element not being overridden

## Desired Layout

**Desktop:**
```
Backstroke Logan Radomsky SR                    30.98
Breaststroke Titan Flint                        34.18
Butterfly Lukas Baker                           29.66
Freestyle John Deninghoff                       26.78
```

**Mobile:**
```
BK Logan Radomsky SR           30.98
BR Titan Flint                 34.18
FL Lukas Baker                 29.66
FR John Deninghoff             26.78
```

Key requirements:
- Stroke and swimmer name LEFT-justified, packed together
- Split time RIGHT-justified
- Class badges (FR/SO/JR/SR) next to swimmer name
- Full stroke names on desktop, abbreviations on mobile

## Debugging Suggestions

1. **Use DevTools** to inspect `.split-swimmer` and trace where `text-align: center` is coming from
2. **Check computed styles** for the entire ancestor chain from `<td>` down to `.split-swimmer`
3. **Look for grid/flexbox alignment** properties that might be centering content
4. **Consider moving inline styles to main CSS** with higher specificity selectors
5. **Use `!important` strategically** on the left-alignment rules

## Relevant File Locations

- `/Users/aaryn/workspaces/swimming/tanque-verde-swim/rebuild_relay_pages.py` (lines ~350-520 for CSS)
- `/Users/aaryn/workspaces/swimming/tanque-verde-swim/docs/css/style.css` (lines ~1145-1300 for mobile overrides)
- `/Users/aaryn/workspaces/swimming/tanque-verde-swim/docs/records/boys-relays.html` (generated output)

## Notes

- The table uses class `table-relay` to distinguish from other table types
- The expandable row is `.relay-details-row` with a single `<td colspan="4">`
- The show/hide toggle is controlled by adding/removing `.show` class via JavaScript onclick


