# CSS Audit Report: Tanque Verde Swimming Records

**Generated:** December 12, 2025  
**Purpose:** Identify CSS duplication, divergence, and inconsistencies across all HTML pages  
**Goal:** Harmonize patterns into a consistent design system

---

## Executive Summary

After a deep audit of all HTML files in `docs/`, I found **significant inconsistencies** in how similar data elements are styled across different page types. Key issues include:

1. **15+ different class names for displaying swim times**
2. **Grade badges defined in CSS but redefined inline in relay pages with different colors**
3. **Duplicate expand/collapse arrow implementations** (`.expand-arrow` vs `.relay-arrow`)
4. **Inconsistent date formatting classes** (4+ different patterns)
5. **Mobile font inconsistencies** between boys/girls in same table (mentioned issue)
6. **Location styling differs between page types**

---

## 1. SWIMMER NAMES

### Current Usage Patterns

| Context | Class/Pattern | Font Size | Font Weight |
|---------|--------------|-----------|-------------|
| Top10 cards | `.top10-athlete` | 1rem | 500 |
| Overall records | `.record-athlete` | 1rem | 600 |
| Relay tables | `.split-swimmer` | 0.85rem (mobile) | 500 |
| Relay summary | `.relay-names-cell` | 0.8rem (mobile) | normal |
| By-grade tables | `<td>` plain | 0.95rem (mobile) | 600 |
| Senior cards | `.card-title` | Bootstrap default | 600 |
| Index compact | `.swimmer-name` | flexible | 500 |

### Issues
- **No consistent base class** for swimmer names
- Font weights vary from 500 to 600
- Mobile sizes vary from 0.8rem to 0.95rem

### Recommendation
Create a unified `.swimmer-name` class hierarchy:
```css
.swimmer-name { font-weight: 500; }
.swimmer-name-bold { font-weight: 600; }
.swimmer-name-primary { /* for record holders */ }
```

---

## 2. TIMES

### Current Usage Patterns

| Context | Class/Pattern | Font Family | Font Size | Color |
|---------|--------------|-------------|-----------|-------|
| Generic | `.time` | Courier New | inherit | inherit |
| Top10 cards | `.top10-time` | Courier New | 1.05rem | `--tvhs-dark-green` |
| Overall records line | `.record-time` | Courier New | 1.3rem | `--tvhs-primary` |
| Relay splits | `.split-time` | Courier New | 0.8rem (mobile) | `--tvhs-primary` |
| Record cards | `.time-value` | Courier New | 1.1rem | `--tvhs-primary` |
| Previous records | `.time-value-small` | Courier New | 0.95rem | #666 |
| Relay main | `.time-cell` | Courier New | 0.95rem | `--tvhs-primary` |
| Table inline | `<span class="time">` | Courier New | inherit | inherit |
| Relay line-1 | `.relay-line-1 .time-value` | not specified | 1.1rem | `--tvhs-primary` |

### Issues
- **MAJOR:** 9+ different time-related classes doing similar things
- Font sizes range from 0.8rem to 1.3rem
- Colors vary between `--tvhs-primary`, `--tvhs-dark-green`, and #666
- Mobile responsive rules scattered across multiple selectors

### Recommendation
Create a time display system:
```css
.time-display { font-family: 'Courier New', monospace; font-weight: bold; }
.time-display--sm { font-size: 0.9rem; }
.time-display--md { font-size: 1.05rem; }
.time-display--lg { font-size: 1.3rem; }
.time-display--muted { color: #666; }
.time-display--primary { color: var(--tvhs-primary); }
```

---

## 3. GRADE BADGES (Classes)

### CSS Definition (lines 21-62 in style.css)
```css
.grade-badge { padding: 0.2rem 0.5rem; font-size: 0.75rem; ... }
.grade-fr { background: #e3f2fd; color: #1565c0; border: 1px solid #90caf9; }
.grade-so { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
.grade-jr { background: #fff3e0; color: #e65100; border: 1px solid #ffcc80; }
.grade-sr { background: #fce4ec; color: #c2185b; border: 1px solid #f48fb1; }
```

### INLINE OVERRIDE in girls-relays.html (lines 140-158)
```css
.grade-fr { background: #28a745; color: white; }
.grade-so { background: #17a2b8; color: white; }
.grade-jr { background: #ffc107; color: #333; }
.grade-sr { background: #dc3545; color: white; }
```

### Issues
- **CRITICAL DIVERGENCE:** Main CSS uses pastel badges, relay pages use bold/saturated Bootstrap-style colors
- Relay page inline styles completely override the main CSS design
- Grade badges appear inconsistent between pages

### Recommendation
1. Remove inline styles from relay pages
2. Choose ONE palette (recommend pastel for better readability)
3. Ensure all pages use the same grade-badge definitions

---

## 4. EVENT NAMES

### Current Usage Patterns

| Context | Class | Styling |
|---------|-------|---------|
| Records line | `.event-name` | font-weight: bold; color: `--tvhs-dark-green` |
| Record cards | `.record-row .event-name` | font-weight: bold; color: `--tvhs-dark-green`; font-size: 0.95rem |
| Class records (index) | `<h6 style="color: #2C5F2D;">` | Inline styles! |
| Class records (index) | `<h6 style="color: #808080;">` | Different inline for girls! |
| Event section | `.event-heading` | font-size: 1.25rem; border-left: 4px solid |
| Top10 headers | `.top10-event-header` | background: `--tvhs-primary`; color: white |

### Issues
- Inline styles for gender-specific coloring (boys green, girls gray) in class records section
- No semantic distinction between event name display and event section headers

### Recommendation
```css
.event-name { /* inline event name in a row */ }
.event-header { /* section header for an event */ }
.event-header--boys { color: var(--tvhs-primary); }
.event-header--girls { color: #808080; }
```

---

## 5. LOCATION / MEET

### Current Usage Patterns

| Context | Class | Display Mode |
|---------|-------|--------------|
| Record cards (hidden) | `.record-location-hidden` | Collapsed, expands on click |
| Top10 expanded | `.record-meet` | Static, shown when expanded |
| Relay expanded | `.relay-meet-row` | Static in expanded section |
| Relay compact index | `.relay-meet` | Static with left border |
| Table mobile | `td::before { content: "📍 "; }` | Pseudo-element prefix |

### Issues
- Inconsistent use of 📍 emoji (sometimes in pseudo, sometimes in content)
- Different collapse/expand patterns
- `.record-meet` styled differently in different contexts

### Recommendation
Create unified location display:
```css
.meet-location { /* base location display */ }
.meet-location::before { content: "📍 "; }
.meet-location--collapsible { /* for expandable rows */ }
```

---

## 6. DATES

### Current Usage Patterns

| Context | Class | Font Size | Color |
|---------|-------|-----------|-------|
| Top10 cards | `.top10-date` | 0.85rem | #666 |
| Overall records | `.record-date` | 0.85rem | #666 |
| Record cards | `.date-value` | 0.85rem | #666 |
| Relay tables | `.date-cell` | 0.7rem (mobile) | #666 |
| Tables mobile | `td:nth-child(4)` | 0.75rem | #666 |
| Previous records | `<small class="text-muted">` | Bootstrap small | muted |

### Issues
- 4+ different class names for the same concept
- Mobile font sizes vary (0.7rem to 0.75rem)
- Some use `.date-value`, some use `.record-date`, some use `.date-cell`

### Recommendation
Consolidate to:
```css
.date-display { font-size: 0.85rem; color: #666; }
@media (max-width: 768px) { .date-display { font-size: 0.75rem; } }
```

---

## 7. RELAY SWIMMER + SPLIT

### Current Definition in style.css (lines 1854-1923)
- `.relay-split-row` - flex container
- `.split-stroke` - italic, gray, left-aligned
- `.split-swimmer` - flex: 1, weight 500
- `.split-time` - monospace, bold, right-aligned

### DUPLICATE Definition in girls-relays.html (lines 92-175)
- Same class names, similar styles
- Adds `.stroke-abbrev` and `.stroke-full` for mobile abbreviations
- Different flex-basis values

### Issues
- **DUPLICATION:** Relay pages duplicate split row styles inline
- `.stroke-abbrev` / `.stroke-full` only defined inline, not in main CSS
- Inconsistent gap/padding values

### Recommendation
1. Move all relay split styles to main CSS
2. Add stroke abbreviation classes to main CSS
3. Remove inline `<style>` blocks from relay pages

---

## 8. SECTION HEADERS

### Current Patterns

| Class | Usage | Background | Text Color |
|-------|-------|------------|------------|
| `.section-header` | Collapsible sections (index, overall) | `--tvhs-primary` | white |
| `.gender-header` | Boys/Girls section | `--tvhs-primary` | white |
| `.relay-header` | Relay subsection in overall | `--tvhs-primary` | white |
| `.top10-event-header` | Event headers in top10 | `--tvhs-primary` | white |
| `.event-heading` | Event sections (by-grade) | `--bg-light` | inherit |
| `.page-header` | Page title sticky | gradient | white |

### Issues
- `.section-header`, `.gender-header`, `.relay-header`, `.top10-event-header` all have same green background
- Redundant definitions
- `.event-heading` has different styling (gray background, left border)

### Recommendation
Create a header hierarchy:
```css
.section-header { /* full-width green header, collapsible */ }
.section-header--event { /* event-specific variant */ }
.subsection-header { /* for nested sections like relay in overall */ }
```

---

## 9. EXPANDING SECTIONS (Arrow Indicators)

### Current Patterns

| Class | File | Transform |
|-------|------|-----------|
| `.expand-arrow` | style.css | rotate(180deg) on `.expanded` |
| `.relay-arrow` | girls-relays.html inline | rotate(180deg) on `.expanded` |
| `.toggle-icon` | Used in section headers | No rotation defined! |

### Issues
- **DUPLICATE:** `.expand-arrow` and `.relay-arrow` are identical
- `.toggle-icon` has no rotation animation
- Inconsistent markup patterns for expand/collapse

### Recommendation
Unify to single `.expand-indicator` class:
```css
.expand-indicator { 
  transition: transform 0.2s ease;
  color: #999;
}
.expanded .expand-indicator { transform: rotate(180deg); }
```

---

## 10. RANK / PLACE

### Current Patterns

| Context | Class | Styling |
|---------|-------|---------|
| Top10 cards | `.top10-rank` | flex: 0 0 28px; font-weight: bold; color: `--tvhs-primary` |
| Relay tables | `.rank-cell` | width: 40px; font-weight: bold; color: `--tvhs-primary` |
| Index relay cards | `.rank-badge` | font-size: 1.2rem; flex-shrink: 0 |
| Mobile 6-col tables | `td:first-child` with green circle | background: `--tvhs-primary`; border-radius: 50% |
| State finishes | `.place-badge` with `.place-1`, `.place-2`, `.place-3`, `.place-top10` |

### Issues
- Rank display varies by context (circle on mobile, number elsewhere)
- Place badges only used on index page for state finishes
- No consistency between rank and place concepts

### Recommendation
```css
.rank-display { /* base rank number styling */ }
.rank-display--circle { /* circular badge variant */ }
.place-badge { /* for competition placements */ }
.place-badge--1 { /* gold */ }
.place-badge--2 { /* silver */ }
.place-badge--3 { /* bronze */ }
```

---

## 11. RECORD BROKEN INDICATORS

### Current Patterns

| Class | Usage | Background |
|-------|-------|------------|
| `.badge-sr` | School Record (state highlights, inline) | gold gradient |
| `.badge-class-record` | Class record indicator | silver gradient |
| 🏆 emoji | In senior cards after time | (inline text) |
| `<span class="badge badge-sr">` | Sometimes uses Bootstrap badge + custom | |

### Issues
- Mix of CSS badges and emoji indicators
- Sometimes `<span class="badge badge-sr">`, sometimes just `.badge-sr`
- No consistent pattern for "this is a record"

### Recommendation
Create record indicator system:
```css
.record-indicator { /* base */ }
.record-indicator--school { background: gold gradient; }
.record-indicator--class { background: silver gradient; }
.record-indicator--personal { /* for PB */ }
```

---

## 12. PERSONAL BESTS (PB Badges)

### Current Pattern (style.css lines 94-129)
```css
.badge-pb { padding: 0.2rem 0.6rem; border-radius: 4px; ... }
.badge-pb.pb-black { background: #000000; }
.badge-pb.pb-darkgray { background: #404040; }
.badge-pb.pb-gray { background: #666666; }
.badge-pb.pb-mediumgray { background: #808080; color: #000; }
.badge-pb.pb-lightgray { background: #888888; color: #fff; }
.badge-pb.pb-verylightgray { background: #aaaaaa; color: #000; }
```

### Issues
- Good system, but naming is confusing (pb-lightgray vs pb-verylightgray)
- No documentation of what improvement thresholds map to which color
- Inconsistent text colors (some white, some black)

### Recommendation
Document the gradient system:
```css
/* PB Improvement Badges - Darker = Bigger Improvement
 * pb-huge: > 5 sec/50y improvement (black)
 * pb-large: 3-5 sec/50y (darkgray)
 * pb-medium: 2-3 sec/50y (gray)
 * pb-small: 1-2 sec/50y (mediumgray)
 * pb-minor: < 1 sec/50y (lightgray)
 */
```

---

## 13. PREVIOUS RECORDS

### Current Pattern
In record cards:
```html
<div class="record-prev-section">
  <span class="record-label-small">Previous:</span>
  <span class="time-value-small">1:45.73</span>
  <span class="swimmer-name">Name</span>
</div>
```

### Issues
- Uses `.record-label-small` only for "Previous:"
- Time uses `.time-value-small` vs `.time-value`
- Consistent pattern, but class names are too specific

### Recommendation
Good as-is, but could simplify:
```css
.previous-record { /* container */ }
.previous-record__label { /* "Previous:" text */ }
.previous-record__time { /* time display */ }
```

---

## 14. SWIMMER CARDS (Seniors)

### Current Pattern
`.senior-card` with internal structure:
- `.card-title` - swimmer name
- `.records-section` - green background for school records
- `.records-header` - section label
- `.events-section` - list of events

### Issues
- Uses Bootstrap `.card` as base
- `.records-section` has inline gradient background
- Times use generic `.time` class inside `<small>` tags

### Recommendation
Good structure, but:
1. Consolidate time display to unified class
2. Document the card structure for reuse

---

## 15. TABLES

### Current Structure

| Type | Marker Class | Columns |
|------|--------------|---------|
| By-grade records | `.table-5col` | Grade, Time, Athlete, Date, Meet |
| Top10 lists | `.table-6col` | Rank, Time, Athlete, Year, Date, Meet |
| Relay top10 | `.table-relay` | Rank, Time, Relay Names, Date |

### Mobile Transformations
- `.table-5col` and `.table-6col` → Grid layout
- `.table-relay` → Keeps table display (for colspan support)

### Issues
- Mobile card transformation only works for non-relay tables
- Different mobile handling adds complexity
- Grid template areas hardcoded to column positions

### Recommendation
Document clearly:
```css
/* Table Types:
 * .table-5col - Grade | Time | Athlete | Date | Meet (records by grade)
 * .table-6col - Rank | Time | Athlete | Year | Date | Meet (top10 lists)  
 * .table-relay - Rank | Time | Relay Names | Date (relay tables)
 */
```

---

## 16. THE SPECIFIC BUG: Boys/Girls Different Fonts on Mobile

### Location
This was mentioned: "girls and boys in the same table have different fonts (Season best Times on mobile)"

### Analysis
Looking at the annual page `2024-25.html` lines 162-213:
- The table uses generic `.table` class without `.table-5col` or `.table-6col`
- Times are styled with `<span class="time">` inside `<td>`
- Grade badges inline with swimmer names

The `.time` class (line 1783) only sets:
```css
.time { font-family: 'Courier New', monospace; font-weight: bold; }
```

No font-size is specified, so it inherits from parent. On mobile, if the table transforms differently, the inherited size could vary.

### Root Cause
The annual page tables don't have the specific mobile transformation classes (`.table-5col`, `.table-6col`), so they get default Bootstrap responsive behavior rather than the custom card layout.

### Fix
Add `.table-5col` or appropriate class to annual page season best times table, OR ensure `.time` has explicit sizing across all breakpoints.

---

## 17. INCONSISTENCY SUMMARY TABLE

| Element | # of Variants | Recommendation |
|---------|---------------|----------------|
| Times | 9+ classes | Consolidate to `.time-display` system |
| Dates | 4+ classes | Consolidate to `.date-display` |
| Swimmer names | 6+ classes | Consolidate to `.swimmer-name` |
| Event names | 3+ classes | Keep `.event-name` + `.event-header` |
| Grade badges | 2 color schemes | Remove relay page overrides |
| Expand arrows | 2 identical classes | Merge to `.expand-indicator` |
| Section headers | 5+ classes | Reduce to 2-3 semantic variants |
| Relay splits | Duplicated inline | Move to main CSS |
| Locations | 4+ patterns | Consolidate to `.meet-location` |

---

## 18. RECOMMENDED ACTION PLAN

### Phase 1: Quick Wins (No visual change, cleanup only)
1. Remove inline `<style>` blocks from relay pages (use main CSS)
2. Merge `.expand-arrow` and `.relay-arrow` into single class
3. Add `.stroke-abbrev`/`.stroke-full` to main CSS

### Phase 2: Consolidation (Minor refactoring)
1. Create unified `.time-display` class hierarchy
2. Create unified `.date-display` class
3. Standardize `.swimmer-name` class usage
4. Document grade badge color scheme (pick one)

### Phase 3: Design System (Larger effort)
1. Create documented component library
2. Establish naming conventions (BEM or similar)
3. Add CSS custom properties for all color/size variations
4. Create mobile-first responsive utilities

---

## 19. FILES REQUIRING CHANGES

| File | Priority | Changes Needed |
|------|----------|----------------|
| `css/style.css` | HIGH | Add missing classes, document patterns |
| `records/girls-relays.html` | HIGH | Remove inline styles (170+ lines) |
| `records/boys-relays.html` | HIGH | Remove inline styles (likely similar) |
| `annual/*.html` | MEDIUM | Add table type classes |
| `index.html` | MEDIUM | Use consistent class names |
| `records/overall.html` | LOW | Already uses main CSS well |
| `top10/*.html` | LOW | Already uses main CSS well |

---

## Appendix: Class Name Reference

### Times
- `.time` - Generic, bold monospace
- `.time-value` - Primary color, 1.1rem
- `.time-value-small` - Muted color, 0.95rem
- `.time-cell` - Table cell, monospace
- `.top10-time` - Dark green, 1.05rem
- `.record-time` - Primary, 1.3rem
- `.split-time` - Right-aligned in splits

### Swimmers
- `.swimmer-name` - Generic (index)
- `.top10-athlete` - Top10 cards
- `.record-athlete` - Overall records
- `.split-swimmer` - Relay splits
- `.relay-names-cell` - Relay summary
- `.relay-names` - Relay names (short)

### Dates
- `.date-value` - Record cards
- `.date-cell` - Relay tables
- `.top10-date` - Top10 cards
- `.record-date` - Overall records

### Headers
- `.section-header` - Main collapsible
- `.gender-header` - Boys/Girls
- `.relay-header` - Relay section
- `.top10-event-header` - Event in top10
- `.event-heading` - Event section

---

*Report generated as part of CSS harmonization initiative*

