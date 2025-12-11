# Relay Card Date Alignment Issue

**Date**: December 11, 2025  
**Issue**: Date is not staying right-justified on the same line as time on mobile devices

---

## Desired Behavior

On mobile devices, to preserve vertical space, the relay card first line should be:

```
🥇 1:41.80                    Oct 24, 2025
└─ Badge   └─ Time (left)     └─ Date (right-justified)
```

All on **ONE LINE** with the date right-justified.

---

## Current Broken Behavior

The date is:
- ❌ NOT right-justified
- ❌ On a NEW LINE (line 2 instead of line 1)
- ❌ LEFT-justified on that new line

Looks like:
```
🥇 1:41.80
Oct 24, 2025  ← Wrong: on new line, left-justified
```

---

## HTML Structure

Located in: `/Users/aaryn/workspaces/swimming/tanque-verde-swim/docs/index.html`

```html
<div class="relay-compact-wrapper">
    <div class="relay-line-1">
        <span class="rank-badge">🥇</span>
        <span class="time-value">1:41.80</span>
        <span class="date-value">Oct 24, 2025</span>
    </div>
    <div class="relay-line-2" onclick="this.parentElement.classList.toggle('expanded')">
        <span class="relay-names-short">Olsson, Olsson, Duerkop, Eftekhar ▼</span>
    </div>
    <div class="relay-expanded-content">
        <!-- Expandable content here -->
    </div>
</div>
```

**Parent Card Context:**
- Wrapped in `.card-body` inside `.card.relay-record-broken`
- `.relay-record-broken` has `background-color: #E8F5E9` (pale green)
- `.relay-compact-wrapper` has `background: rgba(255, 255, 255, 0.5)`

---

## Current CSS

Located in: `/Users/aaryn/workspaces/swimming/tanque-verde-swim/docs/css/style.css`

### Desktop CSS (Working)

```css
.relay-line-1 {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.relay-line-1 .rank-badge {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.relay-line-1 .time-value {
  font-weight: bold;
  font-size: 1.1rem;
  color: var(--tvhs-primary);
  flex-shrink: 0;
}

.relay-line-1 .date-value {
  font-size: 0.85rem;
  color: #666;
  margin-left: auto;  /* Should push to right */
  white-space: nowrap;
}
```

### Mobile CSS (Broken)

```css
@media (max-width: 768px) {
  .relay-line-1 {
    gap: 0.5rem;
  }
  
  .relay-line-1 .rank-badge {
    font-size: 1rem;
  }
  
  .relay-line-1 .time-value {
    font-size: 1rem;
  }
  
  .relay-line-1 .date-value {
    font-size: 0.7rem;
  }
  
  .relay-line-2 {
    font-size: 0.85rem;
  }
}
```

---

## What We've Tried

1. **Initial attempt**: Used `flex-wrap: wrap` which caused date to wrap to new line (incorrect)
2. **Removed flex-wrap**: Date should stay on same line with `margin-left: auto`, but it's still wrapping

---

## Expected Solution

The flexbox layout with `margin-left: auto` on `.date-value` **should** work:
- Badge and Time are `flex-shrink: 0` (won't shrink)
- Date has `margin-left: auto` (should push to right)
- Date has `white-space: nowrap` (won't wrap text)

But something is causing the date to wrap to a new line on mobile.

---

## Possible Causes

1. **Parent container width constraint**: Maybe `.relay-compact-wrapper` or `.card-body` has a width issue?
2. **Bootstrap override**: Bootstrap's card/table styles might be interfering
3. **Font size issue**: Text might be too wide even with smaller font (0.7rem)
4. **Padding/gap interference**: The 0.5rem gap might be causing overflow
5. **Missing flex properties**: May need additional flex properties on mobile

---

## Testing Context

- **File to edit**: `/Users/aaryn/workspaces/swimming/tanque-verde-swim/docs/css/style.css`
- **Section**: Around line 168-188 (relay-compact-wrapper) and mobile section around line 253-263
- **Live site**: https://tanqueverdeswim.org/
- **Page**: Splash page → "📈 2025 Records Broken" section → Boys 200 Medley Relay card

---

## Success Criteria

✅ On mobile (max-width: 768px):
- Badge, Time, and Date are ALL on the same line
- Date is right-justified (flush right)
- No wrapping to second line
- All content stays within the pale green card boundaries

---

## Additional Context

This is part of a relay record card that shows:
- Line 1: Badge | Time | Date
- Line 2: Clickable last names (expandable)
- Expanded: Full names with year badges + meet location

The desktop version works correctly - date is right-justified on the same line. Only mobile has the issue.

---

## Related Files

- HTML: `/Users/aaryn/workspaces/swimming/tanque-verde-swim/docs/index.html` (lines 422-475)
- CSS: `/Users/aaryn/workspaces/swimming/tanque-verde-swim/docs/css/style.css` (lines 168-263)
- Bootstrap: v5.3.0 (loaded via CDN)

